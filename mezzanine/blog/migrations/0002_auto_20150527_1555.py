from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blogpost",
            name="publish_date",
            field=models.DateTimeField(
                help_text="With Published chosen, won't be shown until this time",
                null=True,
                verbose_name="Published from",
                db_index=True,
                blank=True,
            ),
        ),
    ]
