from operator import pos
from sre_constants import SUCCESS
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage

from .models import User, Post, UserFollowing, PostLike
from .serializers import PostSerializer


def index(request):
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("all_posts"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("all_posts"))
    else:
        return render(request, "network/register.html")

@api_view(['POST'])
def new_post(request):
    user = User.objects.get(pk=request.user.pk)
    if request.method == "POST":
        data = {
            'created_by': request.user.pk,
            'contents':request.POST.get('post-content'),
        }
        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            post = serializer.save()
            user.posts.add(post)
            user.save()
            return HttpResponseRedirect(reverse("all_posts"))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def all_post(request):

    page = request.GET.get('p', '1')
    posts = Post.objects.order_by('-created_at')

    for post in posts.iterator():
        post.likes = Post.total_likes(post)
        post.save()

    paginator = Paginator(posts, 10)
    try:
        paginated_posts = paginator.page(int(page))
    except ValueError:
        paginated_posts = paginator.page(1)
    except EmptyPage:
        paginated_posts = paginator.page(paginator.num_pages)   
 
    return render(request, 'network/index.html', {
        'posts': paginated_posts
    })

@api_view(['GET'])
def get_pages(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    return Response(data={'pages':paginator.num_pages}, status=status.HTTP_200_OK)

def profile_view(request, profile_id):
    profile = User.objects.get(username=profile_id)
    following = len(profile.follow.all())
    followers = 0
    for u in User.objects.all():
        if u.follow.filter(following=profile):
            followers+=1 

    if request.user.follow.filter(following=profile):
        button_state = False
    else:
        button_state = True

    return render(request, 'network/profile.html', {
        'profile': profile,
        'posts':profile.posts.all(),
        'following': following,
        'followers':followers,
        'is_following':button_state
    })

@api_view(['GET'])
def follow_user(request, profile_id):
    username = request.user.username

    profile = User.objects.get(username=profile_id)
    is_following = request.user.follow.filter(following=profile)

    if not username==profile_id and not is_following:
        try:
            follow_user_object = UserFollowing.objects.get(following=profile)
        except UserFollowing.DoesNotExist:
            follow_user_object = UserFollowing.objects.create(following=profile)

        request.user.follow.add(follow_user_object)
        return Response(status=status.HTTP_201_CREATED)

    elif not username==profile_id and is_following:
        follow_user_object = UserFollowing.objects.get(following=profile)
        request.user.follow.remove(follow_user_object)
        return Response(status=status.HTTP_201_CREATED)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def like_post(request, post_id):
    post = Post.objects.get(pk=post_id)
    unliked = False
    try:
        PostLike.objects.get(post_id=post, liked_by=request.user).delete()
        post.likes -= 1
        post.save()
        unliked = True
        
    except PostLike.DoesNotExist:
        PostLike.objects.create(post_id=post, liked_by=request.user)
        post.likes += 1
        post.save()

    num_likes = Post.total_likes(post)
    
    return Response(data={'likes':num_likes, 'unlike':unliked}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def is_liked(request, post_id):
    post = Post.objects.get(pk=post_id)
    try:
        if PostLike.objects.get(post_id=post, liked_by=request.user):
            unliked = True
    except PostLike.DoesNotExist:
        unliked = False
    return Response(data={'unlike':unliked}, status=status.HTTP_200_OK)

def filtered_posts(request, profile_id):
    profile = User.objects.get(username=profile_id)
    filtered_posts = Post.objects.none()
    for u in profile.follow.all().iterator():
        posts = Post.objects.filter(created_by=u.following)
        filtered_posts = filtered_posts | posts

    return render(request, 'network/index.html', {
        'posts': filtered_posts.order_by('-created_at')
    })


@api_view(['PUT'])
def edit_post(request):
    post_id= request.data.get("post_id")
    post = Post.objects.get(id=post_id)

    content = request.data.get("contents")
    if request.method == "PUT":
        data = {
            "id": post_id,
            "contents": content,
            "created_by": post.created_by.pk,
        }
        serializer = PostSerializer(post, data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors)
        return Response(status=status.HTTP_201_CREATED)