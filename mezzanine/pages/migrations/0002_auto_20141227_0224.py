from django.db import migrations, models

import mezzanine.core.fields
import mezzanine.pages.fields


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="page",
            name="_order",
            field=mezzanine.core.fields.OrderField(null=True, verbose_name="Order"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="page",
            name="in_menus",
            field=mezzanine.pages.fields.MenusField(
                max_length=100, null=True, verbose_name="Show in menus", blank=True
            ),
            preserve_default=True,
        ),
    ]
