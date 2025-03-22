from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(User)
admin.site.register(Bids)
admin.site.register(Titles)
admin.site.register(Descriptions)
admin.site.register(AuctionCategories)
admin.site.register(Urls)
admin.site.register(Comments)
admin.site.register(AuctionsListing)
admin.site.register(Watchlist)