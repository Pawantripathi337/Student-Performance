from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PredictionRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name="ID")),
                ("student_name", models.CharField(max_length=100)),
                ("age", models.PositiveSmallIntegerField()),
                ("sex", models.CharField(max_length=1)),
                ("studytime", models.PositiveSmallIntegerField()),
                ("failures", models.PositiveSmallIntegerField()),
                ("absences", models.PositiveSmallIntegerField()),
                ("g1", models.PositiveSmallIntegerField()),
                ("g2", models.PositiveSmallIntegerField()),
                ("schoolsup", models.CharField(max_length=3)),
                ("famsup", models.CharField(max_length=3)),
                ("activities", models.CharField(max_length=3)),
                ("internet", models.CharField(max_length=3)),
                ("freetime", models.PositiveSmallIntegerField()),
                ("goout", models.PositiveSmallIntegerField()),
                ("predicted_score", models.FloatField()),
                ("category", models.CharField(max_length=30)),
                ("risk_level", models.CharField(max_length=10)),
                ("pass_probability", models.FloatField(blank=True, null=True)),
                ("explanation", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
