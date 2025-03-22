from decimal import Decimal
from django import forms
from .models import AuctionCategories


class BaseBidForm(forms.Form):
    bid = forms.DecimalField(
        decimal_places=2,
        max_digits=7,
        required=True,
        min_value=Decimal("0.01"),
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Enter bid"}
        ),
    )


class CreateListingForm(forms.Form):
    title = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter title"}
        ),
    )
    description = forms.CharField(
        max_length=1000,
        required=True,
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "Enter description"}
        ),
    )
    starting_bid = forms.DecimalField(
        decimal_places=2,
        max_digits=7,
        required=True,
        min_value=Decimal("0.01"),
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Enter bid"}
        ),
    )
    category = forms.ModelChoiceField(
        queryset=AuctionCategories.objects.all(),
        empty_label="Select Category",
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
    )
    image_url = forms.URLField(
        required=False,
        label="Image URL",
        widget=forms.URLInput(
            attrs={"class": "form-control", "placeholder": "Enter image URL"}
        ),
    )


class NewBiddingForm(BaseBidForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_bid"] = self.fields.pop("bid")
        self.fields["new_bid"].widget.attrs.update({"style": "width: 20%;"})


class NewCommentForm(forms.Form):
    comment = forms.CharField(
        max_length=500,
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "Leave a comment",
                "style": "width: 40%;",
                "rows": 3,
            }
        ),
    )
