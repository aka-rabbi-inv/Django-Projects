from django.urls import path
from . import models
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("category/<type>", views.show_category, name="show_category"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create_listing"),
    path("item_page/<int:item_id>", views.show_item, name="item_page"),
    path("item_page/<int:item_id>/<message>", views.show_item, name="item_with_message"),
    path("add_show_watchlist", views.add_show_watchlist, name="add_show_watchlist"),
    path("status", views.close_or_open, name="close_open_listing"),
    path("place_bid", views.place_bid, name="place_bid"),
    path("add_comment", views.add_comment, name="add_comment"),
]
