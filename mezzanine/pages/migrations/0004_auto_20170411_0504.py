from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0003_auto_20150527_1555"),
    ]

    operations = [
        migrations.AlterField(
            model_name="page",
            name="slug",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Leave blank to have the URL auto-generated from the title.",
                max_length=2000,
                verbose_name="URL",
            ),
            preserve_default=False,
        ),
    ]
