from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("forms", "0005_auto_20151026_1600"),
    ]

    operations = [
        migrations.AlterField(
            model_name="field",
            name="help_text",
            field=models.TextField(blank=True, verbose_name="Help text"),
        ),
        migrations.AlterField(
            model_name="field",
            name="label",
            field=models.TextField(verbose_name="Label"),
        ),
    ]
