from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listings/<str:listing_id>", views.listings, name="listings"),
    path("listings/<str:listing_id>/comment", views.new_comment, name="insert_comments"),
    path("listings/<str:listing_id>/<str:parent_comment>/comment", views.new_comment, name="insert_comments"),
    path("listings/<str:listing_id>/new_bid", views.new_bid, name="new_bid"),
    path("toggle_watchlist/<str:listing_id>", views.toggle_watchlist, name="toggle_watchlist"),
    path("add", views.add_listing, name="add"),
    path("categories", views.search_by_category, name="categories"),
    path("goto/<str:category_id>", views.go_to_category, name="filter_category"),
    path("close_auction/<str:listing_id>", views.close_auction, name="close_auction"),
    path("cancel_auction/<str:listing_id>", views.cancel_auction, name="cancel_auction"),
]
