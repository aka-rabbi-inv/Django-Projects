from typing import ValuesView
from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path("", views.all_post, name="all_posts"),
    path("index", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    url(
        r"create/post", views.new_post, name="create"
    ),
    url(
        r"^profile/(?P<profile_id>[a-zA-Z0-9_]+)$", views.profile_view, name="profile"
    ),
    url(
        r"profile/follow/(?P<profile_id>[a-zA-Z0-9_]+)$", views.follow_user, name='follow'
    ),
    url(
        r"posts/filter/(?P<profile_id>[a-zA-Z0-9_]+)$", views.filtered_posts, name='filtered_posts'
    ),
    url(
        r"like/(?P<post_id>[0-9]+)$", views.like_post, name='like'
    ),
    url(
        r"is_liked/(?P<post_id>[0-9]+)$", views.is_liked, name="is_liked"
    ),
    url(
        r'pages', views.get_pages, name='pages'
    ),
    path("edit", views.edit_post, name="edit"),
]
