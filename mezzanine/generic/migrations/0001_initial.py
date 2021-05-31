from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sites", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("django_comments", "__first__"),
        ("contenttypes", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AssignedKeyword",
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
                ("_order", models.IntegerField(null=True, verbose_name="Order")),
                ("object_pk", models.IntegerField()),
                (
                    "content_type",
                    models.ForeignKey(
                        to="contenttypes.ContentType", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={
                "ordering": ("_order",),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Keyword",
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
                ("title", models.CharField(max_length=500, verbose_name="Title")),
                (
                    "slug",
                    models.CharField(
                        help_text="Leave blank to have the URL auto-generated from the title.",
                        max_length=2000,
                        null=True,
                        verbose_name="URL",
                        blank=True,
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        editable=False, to="sites.Site", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={
                "verbose_name": "Keyword",
                "verbose_name_plural": "Keywords",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Rating",
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
                ("value", models.IntegerField(verbose_name="Value")),
                (
                    "rating_date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Rating date", null=True
                    ),
                ),
                ("object_pk", models.IntegerField()),
                (
                    "content_type",
                    models.ForeignKey(
                        to="contenttypes.ContentType", on_delete=models.CASCADE
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        related_name="ratings",
                        verbose_name="Rater",
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "verbose_name": "Rating",
                "verbose_name_plural": "Ratings",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ThreadedComment",
            fields=[
                (
                    "comment_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="django_comments.Comment",
                        on_delete=models.CASCADE,
                    ),
                ),
                ("rating_count", models.IntegerField(default=0, editable=False)),
                ("rating_sum", models.IntegerField(default=0, editable=False)),
                ("rating_average", models.FloatField(default=0, editable=False)),
                (
                    "by_author",
                    models.BooleanField(
                        default=False, verbose_name="By the blog author"
                    ),
                ),
                (
                    "replied_to",
                    models.ForeignKey(
                        related_name="comments",
                        editable=False,
                        to="generic.ThreadedComment",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "verbose_name": "Comment",
                "verbose_name_plural": "Comments",
            },
            bases=("django_comments.comment",),
        ),
        migrations.AddField(
            model_name="assignedkeyword",
            name="keyword",
            field=models.ForeignKey(
                related_name="assignments",
                verbose_name="Keyword",
                to="generic.Keyword",
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
    ]
