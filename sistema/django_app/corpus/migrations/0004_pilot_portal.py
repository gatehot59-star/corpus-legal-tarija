"""sistema/django_app/corpus/migrations/0004_pilot_portal.py: portal status and usage events."""
import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("corpus", "0003_employees_group"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="pilotaccount",
            name="status",
            field=models.CharField(default="activa", max_length=16),
        ),
        migrations.AddConstraint(
            model_name="pilotaccount",
            constraint=models.CheckConstraint(
                condition=models.Q(status__in=["activa", "eliminada"]),
                name="pilot_account_status"),
        ),
        migrations.CreateModel(
            name="PilotEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True,
                                        serialize=False)),
                ("at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("section", models.CharField(max_length=40)),
                ("detail", models.CharField(blank=True, max_length=240)),
                ("path", models.CharField(blank=True, max_length=240)),
                ("lawyer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                             related_name="pilot_events",
                                             to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
