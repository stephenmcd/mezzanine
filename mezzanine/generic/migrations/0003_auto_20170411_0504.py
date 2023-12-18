from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("generic", "0002_auto_20141227_0224"),
    ]

    operations = [
        migrations.AlterField(
            model_name="keyword",
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
