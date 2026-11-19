"""Data referensi awal: varietas microgreens yang umum di platform."""

from django.db import migrations

VARIETIES = [
    ("sawi-putih", "Sawi Putih"),
    ("daun-katuk", "Daun Katuk"),
    ("brokoli", "Brokoli"),
    ("selada", "Selada"),
]


def seed_varieties(apps, schema_editor):
    Variety = apps.get_model("products", "Variety")
    for slug, name in VARIETIES:
        Variety.objects.get_or_create(slug=slug, defaults={"name": name})


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_varieties, migrations.RunPython.noop),
    ]
