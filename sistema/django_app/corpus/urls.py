"""sistema/django_app/corpus/urls.py: explicit private application routes."""
from django.urls import path
from . import views

urlpatterns = [
    path("", views.workspace, name="workspace"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("theme/", views.theme_view, name="theme"),
    path("reset/", views.reset_request, name="reset"),
    path("reset/<str:uid>/<str:token>/", views.reset_confirm, name="reset-confirm"),
    path("read/", views.read_view, name="read"),
    path("download/", views.download_view, name="download_text"),
    path("save/", views.save_view, name="save"),
    path("feedback/", views.feedback_view, name="feedback"),
    path("piloto/", views.pilot_view, name="pilot"),
    path("live/", views.health, {"kind": "live"}),
    path("ready/", views.health, {"kind": "ready"}),
    path("health/", views.health, {"kind": "health"}),
]
