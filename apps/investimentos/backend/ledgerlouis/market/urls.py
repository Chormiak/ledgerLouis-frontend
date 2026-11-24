from django.urls import path

from . import sync_trigger, views

urlpatterns = [
    path("assets", views.assets),
    path("assets/<str:ticker>", views.asset_detail),
    path("macro", views.macro),
    path("groups", views.groups),
    path("groups/<str:kind>/<slug:slug>", views.group_detail),
    path("news/<str:category>", views.category_news),
    path("screen-context", views.screen_context),
    path("screen-commands", views.screen_commands),
    path("sparklines", views.sparklines),
    path("sync-trigger", sync_trigger.trigger),
]
