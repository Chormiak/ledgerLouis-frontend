from django.contrib import admin

from .models import Asset, FundamentalsSnapshot, MacroPoint, NewsFeed, NewsItem, Niche, Quote


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ["ticker", "name", "market", "sector", "cnpj", "active"]
    list_editable = ["cnpj", "active"]
    list_filter = ["market"]
    search_fields = ["ticker", "name"]


@admin.register(Niche)
class NicheAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "external"]
    list_editable = ["external"]
    prepopulated_fields = {"slug": ["name"]}
    filter_horizontal = ["assets"]


@admin.register(NewsFeed)
class NewsFeedAdmin(admin.ModelAdmin):
    list_display = ["name", "url", "category", "active", "fetched_at"]
    list_editable = ["category", "active"]


@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ["published_at", "source", "kind", "title"]
    list_filter = ["kind", "source"]


admin.site.register([Quote, FundamentalsSnapshot, MacroPoint])
