from django.db import migrations, models

import mezzanine.core.fields
import mezzanine.pages.fields


class Migration(migrations.Migration):

    dependencies = [
        ("sites", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Page",
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
                (
                    "keywords_string",
                    models.CharField(max_length=500, editable=False, blank=True),
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
                    "_meta_title",
                    models.CharField(
                        help_text="Optional title to be used in the HTML title tag. If left blank, the main title field will be used.",
                        max_length=500,
                        null=True,
                        verbose_name="Title",
                        blank=True,
                    ),
                ),
                (
                    "description",
                    models.TextField(verbose_name="Description", blank=True),
                ),
                (
                    "gen_description",
                    models.BooleanField(
                        default=True,
                        help_text="If checked, the description will be automatically generated from content. Uncheck if you want to manually set a custom description.",
                        verbose_name="Generate description",
                    ),
                ),
                ("created", models.DateTimeField(null=True, editable=False)),
                ("updated", models.DateTimeField(null=True, editable=False)),
                (
                    "status",
                    models.IntegerField(
                        default=2,
                        help_text="With Draft chosen, will only be shown for admin users on the site.",
                        verbose_name="Status",
                        choices=[(1, "Draft"), (2, "Published")],
                    ),
                ),
                (
                    "publish_date",
                    models.DateTimeField(
                        help_text="With Published chosen, won't be shown until this time",
                        null=True,
                        verbose_name="Published from",
                        blank=True,
                    ),
                ),
                (
                    "expiry_date",
                    models.DateTimeField(
                        help_text="With Published chosen, won't be shown after this time",
                        null=True,
                        verbose_name="Expires on",
                        blank=True,
                    ),
                ),
                ("short_url", models.URLField(null=True, blank=True)),
                (
                    "in_sitemap",
                    models.BooleanField(default=True, verbose_name="Show in sitemap"),
                ),
                ("_order", models.IntegerField(null=True, verbose_name="Order")),
                (
                    "in_menus",
                    mezzanine.pages.fields.MenusField(
                        default=(1, 2, 3),
                        choices=[
                            (1, "Top navigation bar"),
                            (2, "Left-hand tree"),
                            (3, "Footer"),
                        ],
                        max_length=100,
                        blank=True,
                        null=True,
                        verbose_name="Show in menus",
                    ),
                ),
                (
                    "titles",
                    models.CharField(max_length=1000, null=True, editable=False),
                ),
                (
                    "content_model",
                    models.CharField(max_length=50, null=True, editable=False),
                ),
                (
                    "login_required",
                    models.BooleanField(
                        default=False,
                        help_text="If checked, only logged in users can view this page",
                        verbose_name="Login required",
                    ),
                ),
            ],
            options={
                "ordering": ("titles",),
                "verbose_name": "Page",
                "verbose_name_plural": "Pages",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Link",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="pages.Page",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "ordering": ("_order",),
                "verbose_name": "Link",
                "verbose_name_plural": "Links",
            },
            bases=("pages.page",),
        ),
        migrations.CreateModel(
            name="RichTextPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="pages.Page",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "content",
                    mezzanine.core.fields.RichTextField(verbose_name="Content"),
                ),
            ],
            options={
                "ordering": ("_order",),
                "verbose_name": "Rich text page",
                "verbose_name_plural": "Rich text pages",
            },
            bases=("pages.page", models.Model),
        ),
        migrations.AddField(
            model_name="page",
            name="parent",
            field=models.ForeignKey(
                related_name="children",
                blank=True,
                to="pages.Page",
                null=True,
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="page",
            name="site",
            field=models.ForeignKey(
                editable=False, to="sites.Site", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
    ]
