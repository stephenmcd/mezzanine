from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sites", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Setting",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=50)),
                ("value", models.CharField(max_length=2000)),
                (
                    "site",
                    models.ForeignKey(
                        editable=False, to="sites.Site", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={
                "verbose_name": "Setting",
                "verbose_name_plural": "Settings",
            },
            bases=(models.Model,),
        ),
    ]
