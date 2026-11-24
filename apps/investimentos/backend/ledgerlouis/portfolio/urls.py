from django.urls import path, re_path

from . import views

urlpatterns = [
    path("profile", views.profile),
    path("portfolio", views.portfolio),
    path("holdings/<str:ticker>", views.holding),
    path("proposals", views.proposals),
    path("proposals/<int:pk>", views.proposal_detail),
    path("proposal-items/<int:pk>/decision", views.decision),
    path("alerts", views.alerts),
    path("alerts/<int:pk>/seen", views.alert_seen),
    path("scoreboard", views.scoreboard),
    path("pending-changes", views.pending_changes),
    re_path(r"^pending-changes/(?P<pk>\d+)/(?P<verb>apply|reject)$", views.decide_change),
]
