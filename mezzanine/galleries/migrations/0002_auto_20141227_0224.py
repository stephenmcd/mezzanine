from django.db import migrations, models

import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ("galleries", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="galleryimage",
            name="_order",
            field=mezzanine.core.fields.OrderField(null=True, verbose_name="Order"),
            preserve_default=True,
        ),
    ]
