from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db import IntegrityError

from .models import User, AuctionListing, WatchList

user = User.objects.none()

def index(request):
    global user
    items = AuctionListing.objects.all()
    return render(request, "auctions/index.html", {
        'items':items,
        })


def login_view(request):
    global user
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    global user
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create_listing(request):
    global user
    if request.method == "POST":
        user_id = request.user.id
        title = request.POST.get("title")
        description = request.POST.get("description")
        starting_bid = request.POST.get("starting_bid")
        item_picture = request.POST.get("image_url")
        category = request.POST.get("category")
        owner = User.objects.get(id=user_id)

        AuctionListing.objects.create(owner=owner, category=category, title=title, description=description, starting_bid=starting_bid, item_picture=item_picture, active=1)

        return HttpResponseRedirect( reverse("index") )

    return render(request, "auctions/create.html")

def show_item(request, item_id):
    item = AuctionListing.objects.get(id=item_id)

    return render(request, "auctions/item_page.html", {
        'item':item,
    })

def add_to_watchlist(request):
    user_id = request.user.id
    user = User.objects.get(id=user_id)
    item_id = request.POST.get("item_id")
    item_active = True
    
    try:
        watchlist_item = WatchList.objects.get(owner=user, itemID=AuctionListing.objects.get(id=item_id))
        watchlist_item.item_active = not watchlist_item.item_active
        watchlist_item.save()

    except Exception:
        WatchList.objects.create(owner=user, itemID=AuctionListing.objects.get(id=item_id), item_active=item_active)
    
    return HttpResponseRedirect( reverse("item_page", kwargs={"item_id":item_id}) )

def show_watchlist(request):
    user_id = request.user.id
    user = User.objects.get(id=user_id)
    watchlist_items = WatchList.objects.filter(owner=user)
    listings = AuctionListing.objects.filter( pk__in=watchlist_items.values_list('itemID') )

    return render(request, "auctions/watchlist.html", {
        "items": zip(listings, watchlist_items),
    })

