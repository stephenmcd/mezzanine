from django.db import migrations, models

import mezzanine.core.fields
from mezzanine.forms.fields import NAMES


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="Field",
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
                ("label", models.CharField(max_length=200, verbose_name="Label")),
                ("field_type", models.IntegerField(verbose_name="Type", choices=NAMES)),
                (
                    "required",
                    models.BooleanField(default=True, verbose_name="Required"),
                ),
                ("visible", models.BooleanField(default=True, verbose_name="Visible")),
                (
                    "choices",
                    models.CharField(
                        help_text="Comma separated options where applicable. If an option itself contains commas, surround the option with `backticks`.",
                        max_length=1000,
                        verbose_name="Choices",
                        blank=True,
                    ),
                ),
                (
                    "default",
                    models.CharField(
                        max_length=2000, verbose_name="Default value", blank=True
                    ),
                ),
                (
                    "placeholder_text",
                    models.CharField(
                        verbose_name="Placeholder Text",
                        max_length=100,
                        editable=False,
                        blank=True,
                    ),
                ),
                (
                    "help_text",
                    models.CharField(
                        max_length=100, verbose_name="Help text", blank=True
                    ),
                ),
            ],
            options={
                "ordering": ("_order",),
                "verbose_name": "Field",
                "verbose_name_plural": "Fields",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="FieldEntry",
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
                ("field_id", models.IntegerField()),
                ("value", models.CharField(max_length=2000, null=True)),
            ],
            options={
                "verbose_name": "Form field entry",
                "verbose_name_plural": "Form field entries",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Form",
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
                (
                    "button_text",
                    models.CharField(
                        default="Submit", max_length=50, verbose_name="Button text"
                    ),
                ),
                (
                    "response",
                    mezzanine.core.fields.RichTextField(verbose_name="Response"),
                ),
                (
                    "send_email",
                    models.BooleanField(
                        default=True,
                        help_text="To send an email to the email address supplied in the form upon submission, check this box.",
                        verbose_name="Send email to user",
                    ),
                ),
                (
                    "email_from",
                    models.EmailField(
                        help_text="The address the email will be sent from",
                        max_length=75,
                        verbose_name="From address",
                        blank=True,
                    ),
                ),
                (
                    "email_copies",
                    models.CharField(
                        help_text="Provide a comma separated list of email addresses to be notified upon form submission. Leave blank to disable notifications.",
                        max_length=200,
                        verbose_name="Send email to others",
                        blank=True,
                    ),
                ),
                (
                    "email_subject",
                    models.CharField(
                        max_length=200, verbose_name="Subject", blank=True
                    ),
                ),
                (
                    "email_message",
                    models.TextField(
                        help_text="Emails sent based on the above options will contain each of the form fields entered. You can also enter a message here that will be included in the email.",
                        verbose_name="Message",
                        blank=True,
                    ),
                ),
            ],
            options={
                "ordering": ("_order",),
                "verbose_name": "Form",
                "verbose_name_plural": "Forms",
            },
            bases=("pages.page", models.Model),
        ),
        migrations.CreateModel(
            name="FormEntry",
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
                ("entry_time", models.DateTimeField(verbose_name="Date/time")),
                (
                    "form",
                    models.ForeignKey(
                        related_name="entries",
                        to="forms.Form",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "verbose_name": "Form entry",
                "verbose_name_plural": "Form entries",
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="fieldentry",
            name="entry",
            field=models.ForeignKey(
                related_name="fields", to="forms.FormEntry", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="field",
            name="form",
            field=models.ForeignKey(
                related_name="fields", to="forms.Form", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
    ]
