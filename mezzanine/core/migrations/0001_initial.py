from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sites", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SitePermission",
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
                (
                    "sites",
                    models.ManyToManyField(
                        to="sites.Site", verbose_name="Sites", blank=True
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        related_name="sitepermissions",
                        verbose_name="Author",
                        to=settings.AUTH_USER_MODEL,
                        unique=True,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "verbose_name": "Site permission",
                "verbose_name_plural": "Site permissions",
            },
            bases=(models.Model,),
        ),
    ]
