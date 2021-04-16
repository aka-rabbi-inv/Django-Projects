from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class AuctionListing(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="member")
    title =  models.TextField(max_length=25)
    description =  models.TextField()
    starting_bid =  models.FloatField()
    item_picture = models.TextField(blank=True,null=True)
    category = models.CharField(max_length=10, blank=True, null=True)
    active = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

class Bids(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="member_bid")
    itemID = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="item_bid")
    bid = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    winning_bid = models.BooleanField(null=True)
    
    class Meta:
        verbose_name_plural = "Bids"

class WatchList(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_watchlist")
    itemID = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="item_watchlist")
    item_active = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(blank=True, null=True)


class Comments(models.Model):
    comment = models.TextField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Comments"