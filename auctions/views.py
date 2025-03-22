from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Bids, Comments, Descriptions, Titles, Urls, User, AuctionsListing
from .forms import CreateListingForm, NewBiddingForm, NewCommentForm
from django.utils import timezone


def index(request):
    return render(
        request,
        "auctions/index.html",
        {
            "auctions": AuctionsListing.objects.filter(
                status=AuctionsListing.Status.ACTIVE
            ).order_by("created_at")
        },
    )


def new_bid(request, listing_id):
    if request.method == "POST":
        bid_form = NewBiddingForm(request.POST)
        
        if bid_form.is_valid():
            listing = get_object_or_404(AuctionsListing, id=listing_id)
            bid_value = bid_form.cleaned_data["new_bid"]
            latest_bid = listing.bids.last()

            if latest_bid and bid_value <= latest_bid.value:
                return render(
                    request,
                    "auctions/listings.html",
                    {
                        "auction": listing,
                        "bid_count": listing.bids.count(),
                        "is_bidder_user": latest_bid.created_by == request.user,
                        "bid_form": bid_form,
                        "comment_form": NewCommentForm(),
                        "all_comments": listing.comments.filter(parent_comment__isnull=True),
                        "error_message": "Your bid must be higher than the current bid."
                    },
                )

            Bids.objects.create(
                value=bid_value,
                created_by=request.user,
                listing=listing
            )

    return redirect('listings', listing_id=listing_id)


def new_comment(request, listing_id, parent_comment=None):
    if request.method == "POST":
        comment_form = NewCommentForm(request.POST)

        if comment_form.is_valid():
            listing = get_object_or_404(AuctionsListing, id=listing_id)
            parent = None  # Inicializa a variável parent com None
            if parent_comment:
                parent = get_object_or_404(Comments, id=parent_comment)
            Comments.objects.create(
                user_comment=comment_form.cleaned_data["comment"],
                listing=listing,
                parent_comment=parent,
            )
        else:
            print("formulario nao eh valido")
    return redirect('listings', listing_id=listing_id)


def listings(request, listing_id):
    if request.method == "POST":
        ...
    auction = get_object_or_404(
        AuctionsListing.objects.prefetch_related("bids", "comments"), id=listing_id
    )
    bid_count = auction.bids.count()
    latest_bid = auction.bids.last()
    is_bidder_user = latest_bid.created_by == request.user
    return render(
        request,
        "auctions/listings.html",
        {
            "auction": auction,
            "bid_count": bid_count,
            "is_bidder_user": is_bidder_user,
            "bid_form": NewBiddingForm(),
            "comment_form": NewCommentForm(),
            "all_comments": auction.comments.filter(parent_comment__isnull=True),
        },
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
            """comment_insance = create_fk_instance(
                Comments, form, "comment", "user_comment"
            )"""
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
                created_by=request.user,
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
                value=form.cleaned_data["starting_bid"], listing=listing
            )
            return redirect("index")
    else:
        return render(
            request, "auctions/add_listing.html", {"form": CreateListingForm()}
        )


def maintain_categories(request):
    return render(request, "auctions/categories.html")
