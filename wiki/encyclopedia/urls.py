from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    url(
        r'^wiki/(?P<entry>[a-zA-Z0-9_\- ]+)$',
        views.entry_page,
        name="entry_page"
    ),
        url(
        r'^search/',
        views.search_page,
        name="search_page"
    ),
       url(
        r"^create/",
        views.new_page,
        name="new_page"
    ),
       url(
           r'^edit/(?P<id>[a-zA-Z0-9_\- ]+)$',
           views.edit_page,
           name='edit_page'
       ),
        url(
           r'^edit/',
           views.post_edit_page,
           name='post_edit_page'
       ),        
        url(
           r'^random/',
           views.random_page,
           name='random_page'
       ),
]
