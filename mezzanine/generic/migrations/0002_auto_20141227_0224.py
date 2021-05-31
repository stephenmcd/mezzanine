from django.db import migrations, models

import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ("generic", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assignedkeyword",
            name="_order",
            field=mezzanine.core.fields.OrderField(null=True, verbose_name="Order"),
            preserve_default=True,
        ),
    ]
