"""sistema/django_app/corpus/apps.py: application registration."""
from django.apps import AppConfig


class CorpusConfig(AppConfig):
    """Register the isolated application without side effects."""
    name = "corpus"
