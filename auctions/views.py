from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max

from .models import User, AuctionListing, WatchList, Bids, Comments

user = User.objects.none()

def maximum_bid(item):
    
    max_bid = Bids.objects.filter(itemID=item).aggregate(Max("bid"))
    if not max_bid["bid__max"]:
        return item.starting_bid
    elif max_bid["bid__max"] > item.starting_bid:
        return max_bid["bid__max"]

def index(request):
    global user
    items = AuctionListing.objects.filter(active=1)
    category_names = items.values_list("category", flat=True)
    
    return render(request, "auctions/index.html", {
        'items':items,
        'categories':list(dict.fromkeys(category_names)),
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

def show_item(request, item_id, message=""):
    user_id = request.user.id
    user = User.objects.get(id=user_id)
    item = AuctionListing.objects.get(id=item_id)
        
    current_price = maximum_bid(item)
    try:
        watchlist_item = WatchList.objects.get(owner=user, itemID=item)
        if watchlist_item.item_active:
            watchlist_image="auctions/eye_close.svg"
        else:
            watchlist_image="auctions/eye.svg"
    except Exception as e:
        watchlist_image="auctions/eye.svg" 
    try:
        bid = Bids.objects.get(bid=current_price)
        created_at = bid.created_at
        created_by = bid.owner
        if bid.winning_bid and bid.owner == user:
            win_message = "You have won this bid!"
        else:
            win_message = ""        
    except Exception as e:
        win_message = "" 
        created_at = item.created_at
        created_by = item.owner
        
    comments = Comments.objects.filter(listing=item)
    
    return render(request, "auctions/item_page.html", {
        'item':item,
        'message':message,
        'price':current_price,
        'winner':win_message,
        'comments':comments,
        'watchlist_image':watchlist_image,
        'created':created_at,
        'owner':created_by,
    })
    

def add_show_watchlist(request):
    user_id = request.user.id
    user = User.objects.get(id=user_id)
    if request.method == "POST":
        
        item_id = request.POST.get("item_id")
        item_active = True
        
        try:
            watchlist_item = WatchList.objects.get(owner=user, itemID=AuctionListing.objects.get(id=item_id))
            watchlist_item.item_active = not watchlist_item.item_active
            watchlist_item.save()

        except Exception:
            WatchList.objects.create(owner=user, itemID=AuctionListing.objects.get(id=item_id), item_active=item_active)
        
        return HttpResponseRedirect( reverse("item_page", kwargs={"item_id":item_id}) )

    watchlist_items = WatchList.objects.filter(owner=user)
    listings = AuctionListing.objects.filter( pk__in=watchlist_items.values_list('itemID') )

    return render(request, "auctions/watchlist.html", {
        "items": zip(listings, watchlist_items),
    })
    

def close_or_open(request):
    user_id = request.user.id
    user = User.objects.get(id=user_id)
    item_id = request.POST.get("item_id")
    item = AuctionListing.objects.get(id=item_id)
    current_price = maximum_bid(item)
    try:
        bid = Bids.objects.get(bid=current_price)
        if item.active and bid.owner is not user:
            
            bid.winning_bid = 1
            bid.save()
            winner = bid.owner
    except Exception as e:
        pass
        
    item.active = not item.active
    item.save()
    return HttpResponseRedirect( reverse("item_page", kwargs={"item_id":item_id}) )

def place_bid(request):
    user_id = request.user.id
    user = User.objects.get(id=user_id)
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        item = AuctionListing.objects.get(id=item_id) 
        bid_amount = request.POST.get("bid")
        current_price = maximum_bid(item)
        if float(bid_amount) < item.starting_bid:
            return HttpResponseRedirect( reverse("item_with_message", kwargs={"item_id":item_id, "message":"Bid cannot be less than starting bid!"}) )
        
        elif float(bid_amount) <= current_price:
            return HttpResponseRedirect( reverse("item_with_message", kwargs={"item_id":item_id, "message":"Your bid has to be greater than the current price!"}) )
        
        elif float(bid_amount) > current_price and float(bid_amount) > item.starting_bid:
            Bids.objects.create(owner=user, itemID=item, bid=float(bid_amount))
            return HttpResponseRedirect( reverse("item_with_message", kwargs={"item_id":item_id, "message":"Your bid has been placed."}) )        
        
def add_comment(request):
    user_id = request.user.id
    user = User.objects.get(id=user_id)
    item_id = request.POST.get("item_id")
    item = AuctionListing.objects.get(id=item_id) 
    comment = request.POST.get("comment")
    Comments.objects.create(owner=user, listing=item, comment=comment)
    return HttpResponseRedirect( reverse("item_page", kwargs={"item_id":item_id}) )

def show_category(request, type):
    items = AuctionListing.objects.filter(active=1, category=type)
    
    return render(request, "auctions/index.html", {
        'items':items,
        })