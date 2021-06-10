from importlib.resources import contents
from operator import mod
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    posts = models.ManyToManyField('Post',blank=True)
    follow = models.ManyToManyField('UserFollowing',blank=True) 

class UserFollowing(models.Model):
    id = models.AutoField(primary_key=True)
    following = models.ForeignKey(User, related_name= 'following', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Post(models.Model):
    id = models.AutoField(primary_key=True)
    contents = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def total_likes(post):
        return len(PostLike.objects.filter(post_id=post))

class PostLike(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    liked_by = models.ForeignKey(User, related_name= 'likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)