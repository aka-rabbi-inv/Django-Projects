from django.contrib import admin
from .models import AuctionListing, Comments, Bids

# Register your models here.
admin.site.register(AuctionListing)
admin.site.register(Comments)
admin.site.register(Bids)
