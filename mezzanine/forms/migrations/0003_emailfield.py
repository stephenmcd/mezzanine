from django.db import migrations, models

import mezzanine.pages.managers


class Migration(migrations.Migration):

    dependencies = [
        ("forms", "0002_auto_20141227_0224"),
    ]

    operations = [
        migrations.AlterField(
            model_name="form",
            name="email_from",
            field=models.EmailField(
                help_text="The address the email will be sent from",
                max_length=254,
                verbose_name="From address",
                blank=True,
            ),
        ),
    ]
