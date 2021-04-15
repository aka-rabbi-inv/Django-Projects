from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class AuctionListing(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="member")
    title =  models.TextField(max_length=15)
    description =  models.TextField()
    starting_bid =  models.FloatField()
    item_picture = models.TextField(blank=True,null=True)
    category = models.CharField(max_length=10, blank=True, null=True)
    active = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

class Bids(models.Model):
    bid = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    winning_bid = models.BooleanField(null=True)

class WatchList(models.Model):
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user_watchlist")
    itemID = models.ForeignKey(AuctionListing, on_delete=models.DO_NOTHING, related_name="item_watchlist")
    item_active = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(blank=True, null=True)


class Comments(models.Model):
    comment = models.TextField(max_length=200)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)