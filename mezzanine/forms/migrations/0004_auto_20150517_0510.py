from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("forms", "0003_emailfield"),
    ]

    operations = [
        migrations.AlterField(
            model_name="form",
            name="button_text",
            field=models.CharField(
                max_length=50, verbose_name="Button text", blank=True
            ),
        ),
    ]
