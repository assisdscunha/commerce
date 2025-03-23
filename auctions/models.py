from decimal import Decimal
import uuid
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):
    pass


class Titles(models.Model):
    title = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.title


class Descriptions(models.Model):
    description = models.CharField(max_length=1000, primary_key=True)

    def __str__(self):
        return self.description


class AuctionCategories(models.Model):
    category = models.CharField(max_length=100, primary_key=True)

    class Meta:
        ordering = ["category"]

    def __str__(self):
        return self.category


class Urls(models.Model):
    url = models.URLField(primary_key=True, max_length=2000)

    def __str__(self):
        return self.url


class AuctionsListing(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "A", "Active"
        INACTIVE = "I", "Inactive"
        SOLD = "S", "Sold"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(
        User,
        models.SET_NULL,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        AuctionCategories,
        on_delete=models.RESTRICT,
        related_name="category_type",
        blank=True,
        null=True,
    )
    url = models.ForeignKey(
        Urls, on_delete=models.RESTRICT, blank=True, related_name="image"
    )
    title = models.ForeignKey(
        Titles, on_delete=models.RESTRICT, blank=False, related_name="titles"
    )
    description = models.ForeignKey(
        Descriptions,
        on_delete=models.RESTRICT,
        blank=False,
        related_name="descriptions",
    )
    status = models.CharField(max_length=1, default=Status.ACTIVE, choices=Status)

    class Meta:
        ordering = ["created_at"]


class Comments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_comment = models.CharField(max_length=500)
    parent_comment = models.ForeignKey(
        "self",
        max_length=500,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="responses",
    )
    listing = models.ForeignKey(AuctionsListing, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        models.SET_NULL,
        blank=True,
        null=True,
    )
    
    def get_all_comments(self):
        comments = [{"comment": self.user_comment, "id": self.id, "responses": []}]
        
        for response in self.responses.all():
            comments[0]["responses"].append({
                "comment": response.user_comment,
                "id": response.id,
                "responses": response.get_all_comments()
            })

        return comments

    def __str__(self):
        return self.user_comment
        
    class Meta:
        ordering = ["-created_at"]


class Bids(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    value = models.DecimalField(
        decimal_places=2, max_digits=7, validators=[MinValueValidator(Decimal("0.01"))]
    )
    listing = models.ForeignKey(
        AuctionsListing, on_delete=models.CASCADE, related_name="bids"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        get_latest_by = "created_at"
        ordering = ["created_at"]


class Watchlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        models.SET_NULL,
        blank=True,
        null=True,
    )
    auctionlisting = models.ForeignKey(
        AuctionsListing,
        models.CASCADE,
        related_name="user_watchlist"
    )
    created_at = models.DateTimeField(auto_now_add=True)