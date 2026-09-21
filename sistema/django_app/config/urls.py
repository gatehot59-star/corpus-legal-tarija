"""sistema/django_app/config/urls.py: no legacy routes or admin exposure."""
from django.urls import include, path

urlpatterns = [path("corpus/", include("corpus.urls"))]
