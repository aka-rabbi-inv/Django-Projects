from django.urls import path
from . import models
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create_listing"),
    path("item_page/<int:item_id>", views.show_item, name="item_page"),
    path("add_watchlist", views.add_to_watchlist, name="add_watchlist"),
    path("watchlist", views.show_watchlist, name="watchlist"),
]
