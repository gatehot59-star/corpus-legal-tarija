"""sistema/django_app/corpus/migrations/0003_employees_group.py: employee role group."""
from django.db import migrations


def create_group(apps, schema_editor) -> None:
    """Create the employees group idempotently; memberships stay operator-assigned."""
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name="corpus-empleados")


def drop_group(apps, schema_editor) -> None:
    """Reverse removes only the group, never users or their memberships."""
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name="corpus-empleados").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("corpus", "0002_pilotaccount"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(create_group, drop_group),
    ]
