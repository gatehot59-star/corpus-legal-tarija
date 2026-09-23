"""sistema/django_app/corpus/migrations/0005_employeeaccount.py: employee accounts."""
import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("corpus", "0004_pilot_portal"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="EmployeeAccount",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True,
                                        serialize=False)),
                ("first_name", models.CharField(max_length=80)),
                ("last_name", models.CharField(blank=True, max_length=80)),
                ("status", models.CharField(default="activa", max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("created_by", models.ForeignKey(blank=True, null=True,
                                                 on_delete=django.db.models.deletion.PROTECT,
                                                 related_name="created_employee_accounts",
                                                 to=settings.AUTH_USER_MODEL)),
                ("employee", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                                                   related_name="employee_account",
                                                   to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name="employeeaccount",
            constraint=models.CheckConstraint(
                condition=models.Q(status__in=["activa", "eliminada"]),
                name="employee_account_status"),
        ),
    ]
