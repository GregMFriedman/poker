# Generated by Django 5.1.2 on 2024-10-18 19:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hand_ranker", "0002_hand_hand_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="hand",
            name="hand_type",
            field=models.IntegerField(
                choices=[
                    (9, "Straight Flush"),
                    (8, "Quads"),
                    (7, "Full House"),
                    (6, "Flush"),
                    (5, "Staight"),
                    (4, "Trips"),
                    (3, "Two Pair"),
                    (2, "Pair"),
                    (1, "High Card"),
                ],
                db_index=True,
            ),
        ),
        migrations.AlterField(
            model_name="hand",
            name="rank",
            field=models.PositiveIntegerField(db_index=True),
        ),
    ]
