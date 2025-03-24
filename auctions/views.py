from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import (
    AuctionCategories,
    Bids,
    Comments,
    Descriptions,
    Titles,
    Urls,
    User,
    AuctionsListing,
    Watchlist,
)
from .forms import CreateListingForm, NewBiddingForm, NewCommentForm
from django.utils import timezone


def get_auction_listing(**kwargs):
    return {
        "auctions": AuctionsListing.objects.filter(
            status=AuctionsListing.Status.ACTIVE, **kwargs
        ).order_by("created_at")
    }


def get_auction_context(listing_id, user):
    auction = get_object_or_404(AuctionsListing, id=listing_id)
    is_watchlist = False
    if user.is_authenticated:
        is_watchlist = Watchlist.objects.filter(
            auctionlisting=listing_id, user=user
        ).exists()
    bid_count = auction.bids.count()
    latest_bid = auction.bids.last()
    is_bidder_user = latest_bid.created_by == user if latest_bid else False
    return {
        "auction": auction,
        "bid_count": bid_count,
        "is_bidder_user": is_bidder_user,
        "bid_form": NewBiddingForm(),
        "comment_form": NewCommentForm(),
        "all_comments": auction.comments.filter(parent_comment__isnull=True),
        "is_watchlist": is_watchlist,
    }


def is_valid_bid(bid_value, latest_bid):
    return latest_bid and bid_value > latest_bid.value


def index(request):
    listings = get_auction_listing()
    listings["title"] = "Active Listings"
    return render(request, "auctions/index.html", listings)


@login_required
def watchlist(request):
    listings = get_auction_listing(user_watchlist__user=request.user)
    listings["title"] = f"{request.user.username.capitalize()}'s Watchlist"

    return render(request, "auctions/index.html", listings)


def new_bid(request, listing_id):
    if request.method == "POST":
        bid_form = NewBiddingForm(request.POST)

        if bid_form.is_valid():
            listing = get_object_or_404(AuctionsListing, id=listing_id)
            bid_value = bid_form.cleaned_data["new_bid"]
            latest_bid = listing.bids.last()

            if not is_valid_bid(bid_value, latest_bid):
                context = get_auction_context(listing_id, request.user)
                context["bid_form"] = bid_form
                context["error_message"] = (
                    "Your bid must be higher than the current bid."
                )
                return render(
                    request,
                    "auctions/listings.html",
                    context,
                )

            Bids.objects.create(
                value=bid_value, created_by=request.user, listing=listing
            )

    return redirect("listings", listing_id=listing_id)


def new_comment(request, listing_id, parent_comment=None):
    if request.method == "POST":
        comment_form = NewCommentForm(request.POST)

        if comment_form.is_valid():
            listing = get_object_or_404(AuctionsListing, id=listing_id)
            parent = (
                get_object_or_404(Comments, id=parent_comment)
                if parent_comment
                else None
            )
            Comments.objects.create(
                user_comment=comment_form.cleaned_data["comment"],
                listing=listing,
                parent_comment=parent,
            )
    return redirect("listings", listing_id=listing_id)


def listings(request, listing_id):
    context = get_auction_context(listing_id, request.user)
    return render(
        request,
        "auctions/listings.html",
        context,
    )


def login_view(request):
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
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def add_listing(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            user = request.user
            url_instance, _ = Urls.objects.get_or_create(
                url=form.cleaned_data["image_url"]
            )
            title_instance, _ = Titles.objects.get_or_create(
                title=form.cleaned_data["title"]
            )
            description_instance, _ = Descriptions.objects.get_or_create(
                description=form.cleaned_data["description"]
            )

            listing = AuctionsListing(
                created_by=user,
                category=(
                    form.cleaned_data["category"]
                    if form.cleaned_data["category"]
                    else None
                ),
                url=url_instance,
                title=title_instance,
                description=description_instance,
                status=AuctionsListing.Status.ACTIVE,
            )
            listing.save()
            Bids.objects.create(
                value=form.cleaned_data["starting_bid"], listing=listing, created_by=user
            )
            return redirect("index")
    else:
        return render(
            request, "auctions/add_listing.html", {"form": CreateListingForm()}
        )


def search_by_category(request):
    categories = AuctionCategories.objects.all()
    return render(request, "auctions/categories.html", {"categories": categories})


def go_to_category(request, category_id):
    listings = get_auction_listing(category__category=category_id)
    listings["title"] = category_id
    return render(request, "auctions/index.html", listings)


@login_required
def toggle_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionsListing, id=listing_id)
    watchlist_entry, created = Watchlist.objects.get_or_create(
        user=request.user, auctionlisting=listing
    )
    if not created:
        watchlist_entry.delete()
    return redirect("listings", listing_id=listing_id)
