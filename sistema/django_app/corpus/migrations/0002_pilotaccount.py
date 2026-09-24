"""sistema/django_app/corpus/migrations/0002_pilotaccount.py: pilot accounts."""
import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("corpus", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PilotAccount",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("first_name", models.CharField(max_length=80)),
                ("last_name", models.CharField(max_length=80)),
                ("bar_number", models.CharField(blank=True, max_length=40)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                                 related_name="created_pilot_accounts",
                                                 to=settings.AUTH_USER_MODEL)),
                ("lawyer", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                                                related_name="pilot_account",
                                                to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
