from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listings/<str:listing_id>", views.listings, name="listings"),
    path("listings/<str:listing_id>/comment", views.new_comment, name="insert_comments"),
    path("listings/<str:listing_id>/<str:parent_comment>/comment", views.new_comment, name="insert_comments"),
    path("listings/<str:listing_id>/new_bid", views.new_bid, name="new_bid"),
    path("add", views.add_listing, name="add"),
    path("categories", views.maintain_categories, name="categories")
]
