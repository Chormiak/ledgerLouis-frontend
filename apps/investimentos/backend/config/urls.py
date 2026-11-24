from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from ledgerlouis.interfaces.chat import chat

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health", lambda request: JsonResponse({"status": "ok"})),
    path("api/chat", chat),
    path("api/", include("ledgerlouis.market.urls")),
    path("api/", include("ledgerlouis.portfolio.urls")),
]
