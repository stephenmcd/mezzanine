from __future__ import unicode_literals
from future.builtins import int, range, str

from datetime import date, datetime
from os.path import join, split
from uuid import uuid4

from django import forms
from django.forms.extras import SelectDateWidget
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.template import Template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.timezone import now

from mezzanine.conf import settings
from mezzanine.forms import fields
from mezzanine.forms.models import FormEntry, FieldEntry
from mezzanine.utils.email import split_addresses as split_choices


fs = FileSystemStorage(location=settings.FORMS_UPLOAD_ROOT)

##############################
# Each type of export filter #
##############################

# Text matches
FILTER_CHOICE_CONTAINS = "1"
FILTER_CHOICE_DOESNT_CONTAIN = "2"

# Exact matches
FILTER_CHOICE_EQUALS = "3"
FILTER_CHOICE_DOESNT_EQUAL = "4"

# Greater/less than
FILTER_CHOICE_BETWEEN = "5"

# Multiple values
FILTER_CHOICE_CONTAINS_ANY = "6"
FILTER_CHOICE_CONTAINS_ALL = "7"
FILTER_CHOICE_DOESNT_CONTAIN_ANY = "8"
FILTER_CHOICE_DOESNT_CONTAIN_ALL = "9"

##########################
# Export filters grouped #
##########################

# Text fields
TEXT_FILTER_CHOICES = (
    ("", _("Nothing")),
    (FILTER_CHOICE_CONTAINS, _("Contains")),
    (FILTER_CHOICE_DOESNT_CONTAIN, _("Doesn't contain")),
    (FILTER_CHOICE_EQUALS, _("Equals")),
    (FILTER_CHOICE_DOESNT_EQUAL, _("Doesn't equal")),
)

# Choices with single value entries
CHOICE_FILTER_CHOICES = (
    ("", _("Nothing")),
    (FILTER_CHOICE_CONTAINS_ANY, _("Equals any")),
    (FILTER_CHOICE_DOESNT_CONTAIN_ANY, _("Doesn't equal any")),
)

# Choices with multiple value entries
MULTIPLE_FILTER_CHOICES = (
    ("", _("Nothing")),
    (FILTER_CHOICE_CONTAINS_ANY, _("Contains any")),
    (FILTER_CHOICE_CONTAINS_ALL, _("Contains all")),
    (FILTER_CHOICE_DOESNT_CONTAIN_ANY, _("Doesn't contain any")),
    (FILTER_CHOICE_DOESNT_CONTAIN_ALL, _("Doesn't contain all")),
)

# Dates
DATE_FILTER_CHOICES = (
    ("", _("Nothing")),
    (FILTER_CHOICE_BETWEEN, _("Is between")),
)

# The filter function for each filter type
FILTER_FUNCS = {
    FILTER_CHOICE_CONTAINS:
        lambda val, field: val.lower() in field.lower(),
    FILTER_CHOICE_DOESNT_CONTAIN:
        lambda val, field: val.lower() not in field.lower(),
    FILTER_CHOICE_EQUALS:
        lambda val, field: val.lower() == field.lower(),
    FILTER_CHOICE_DOESNT_EQUAL:
        lambda val, field: val.lower() != field.lower(),
    FILTER_CHOICE_BETWEEN:
        lambda val_from, val_to, field: (
            (not val_from or val_from <= field) and
            (not val_to or val_to >= field)
        ),
    FILTER_CHOICE_CONTAINS_ANY:
        lambda val, field: set(val) & set(split_choices(field)),
    FILTER_CHOICE_CONTAINS_ALL:
        lambda val, field: set(val) == set(split_choices(field)),
    FILTER_CHOICE_DOESNT_CONTAIN_ANY:
        lambda val, field: not set(val) & set(split_choices(field)),
    FILTER_CHOICE_DOESNT_CONTAIN_ALL:
        lambda val, field: set(val) != set(split_choices(field)),
}

# Export form fields for each filter type grouping
text_filter_field = forms.ChoiceField(label=" ", required=False,
                                      choices=TEXT_FILTER_CHOICES)
choice_filter_field = forms.ChoiceField(label=" ", required=False,
                                        choices=CHOICE_FILTER_CHOICES)
multiple_filter_field = forms.ChoiceField(label=" ", required=False,
                                          choices=MULTIPLE_FILTER_CHOICES)
date_filter_field = forms.ChoiceField(label=" ", required=False,
                                      choices=DATE_FILTER_CHOICES)


class FormForForm(forms.ModelForm):
    """
    Form with a set of fields dynamically assigned, directly based on the
    given ``forms.models.Form`` instance.
    """

    class Meta:
        model = FormEntry
        exclude = ("form", "entry_time")

    def __init__(self, form, context, *args, **kwargs):
        """
        Dynamically add each of the form fields for the given form model
        instance and its related field model instances.
        """
        self.form = form
        self.form_fields = form.fields.visible()
        initial = kwargs.pop("initial", {})
        # If a FormEntry instance is given to edit, populate initial
        # with its field values.
        field_entries = {}
        if kwargs.get("instance"):
            for field_entry in kwargs["instance"].fields.all():
                field_entries[field_entry.field_id] = field_entry.value
        super(FormForForm, self).__init__(*args, **kwargs)
        # Create the form fields.
        for field in self.form_fields:
            field_key = "field_%s" % field.id
            field_class = fields.CLASSES[field.field_type]
            field_widget = fields.WIDGETS.get(field.field_type)
            field_args = {"label": field.label, "required": field.required,
                          "help_text": field.help_text}
            if field.required and not field.help_text:
                field_args["help_text"] = _("required")
            arg_names = field_class.__init__.__code__.co_varnames
            if "max_length" in arg_names:
                field_args["max_length"] = settings.FORMS_FIELD_MAX_LENGTH
            if "choices" in arg_names:
                choices = list(field.get_choices())
                if (field.field_type == fields.SELECT and
                        field.default not in [c[0] for c in choices]):
                    choices.insert(0, ("", field.placeholder_text))
                field_args["choices"] = choices
            if field_widget is not None:
                field_args["widget"] = field_widget
            #
            #   Initial value for field, in order of preference:
            #
            # - If a form model instance is given (eg we're editing a
            #   form response), then use the instance's value for the
            #   field.
            # - If the developer has provided an explicit "initial"
            #   dict, use it.
            # - The default value for the field instance as given in
            #   the admin.
            #
            initial_val = None
            try:
                initial_val = field_entries[field.id]
            except KeyError:
                try:
                    initial_val = initial[field_key]
                except KeyError:
                    initial_val = Template(field.default).render(context)
            if initial_val:
                if field.is_a(*fields.MULTIPLE):
                    initial_val = split_choices(initial_val)
                elif field.field_type == fields.CHECKBOX:
                    initial_val = initial_val != "False"
                self.initial[field_key] = initial_val
            self.fields[field_key] = field_class(**field_args)

            if field.field_type == fields.DOB:
                _now = datetime.now()
                years = list(range(_now.year, _now.year - 120, -1))
                self.fields[field_key].widget.years = years

            # Add identifying type attr to the field for styling.
            setattr(self.fields[field_key], "type",
                    field_class.__name__.lower())
            if (field.required and settings.FORMS_USE_HTML5 and
                field.field_type != fields.CHECKBOX_MULTIPLE):
                self.fields[field_key].widget.attrs["required"] = ""
            if field.placeholder_text and not field.default:
                text = field.placeholder_text
                self.fields[field_key].widget.attrs["placeholder"] = text

    def save(self, **kwargs):
        """
        Create a ``FormEntry`` instance and related ``FieldEntry``
        instances for each form field.
        """
        entry = super(FormForForm, self).save(commit=False)
        entry.form = self.form
        entry.entry_time = now()
        entry.save()
        entry_fields = entry.fields.values_list("field_id", flat=True)
        new_entry_fields = []
        for field in self.form_fields:
            field_key = "field_%s" % field.id
            value = self.cleaned_data[field_key]
            if value and self.fields[field_key].widget.needs_multipart_form:
                value = fs.save(join("forms", str(uuid4()), value.name), value)
            if isinstance(value, list):
                value = ", ".join([v.strip() for v in value])
            if field.id in entry_fields:
                field_entry = entry.fields.get(field_id=field.id)
                field_entry.value = value
                field_entry.save()
            else:
                new = {"entry": entry, "field_id": field.id, "value": value}
                new_entry_fields.append(FieldEntry(**new))
        if new_entry_fields:
            FieldEntry.objects.bulk_create(new_entry_fields)
        return entry

    def email_to(self):
        """
        Return the value entered for the first field of type
        ``forms.fields.EMAIL``.
        """
        for field in self.form_fields:
            if field.is_a(fields.EMAIL):
                return self.cleaned_data["field_%s" % field.id]
        return None


class EntriesForm(forms.Form):
    """
    Form with a set of fields dynamically assigned that can be used to
    filter entries for the given ``forms.models.Form`` instance.
    """

    def __init__(self, form, request, *args, **kwargs):
        """
        Iterate through the fields of the ``forms.models.Form`` instance and
        create the form fields required to control including the field in
        the export (with a checkbox) or filtering the field which differs
        across field types. User a list of checkboxes when a fixed set of
        choices can be chosen from, a pair of date fields for date ranges,
        and for all other types provide a textbox for text search.
        """
        self.form = form
        self.request = request
        self.form_fields = form.fields.all()
        self.entry_time_name = str(FormEntry._meta.get_field(
            "entry_time").verbose_name)
        super(EntriesForm, self).__init__(*args, **kwargs)
        for field in self.form_fields:
            field_key = "field_%s" % field.id
            # Checkbox for including in export.
            self.fields["%s_export" % field_key] = forms.BooleanField(
                label=field.label, initial=True, required=False)
            if field.is_a(*fields.CHOICES):
                # A fixed set of choices to filter by.
                if field.is_a(fields.CHECKBOX):
                    choices = ((True, _("Checked")), (False, _("Not checked")))
                else:
                    choices = field.get_choices()
                contains_field = forms.MultipleChoiceField(label=" ",
                    choices=choices, widget=forms.CheckboxSelectMultiple(),
                    required=False)
                self.fields["%s_filter" % field_key] = choice_filter_field
                self.fields["%s_contains" % field_key] = contains_field
            elif field.is_a(*fields.MULTIPLE):
                # A fixed set of choices to filter by, with multiple
                # possible values in the entry field.
                contains_field = forms.MultipleChoiceField(label=" ",
                    choices=field.get_choices(),
                    widget=forms.CheckboxSelectMultiple(),
                    required=False)
                self.fields["%s_filter" % field_key] = multiple_filter_field
                self.fields["%s_contains" % field_key] = contains_field
            elif field.is_a(*fields.DATES):
                # A date range to filter by.
                self.fields["%s_filter" % field_key] = date_filter_field
                self.fields["%s_from" % field_key] = forms.DateField(
                    label=" ", widget=SelectDateWidget(), required=False)
                self.fields["%s_to" % field_key] = forms.DateField(
                    label=_("and"), widget=SelectDateWidget(), required=False)
            else:
                # Text box for search term to filter by.
                contains_field = forms.CharField(label=" ", required=False)
                self.fields["%s_filter" % field_key] = text_filter_field
                self.fields["%s_contains" % field_key] = contains_field
        # Add ``FormEntry.entry_time`` as a field.
        field_key = "field_0"
        self.fields["%s_export" % field_key] = forms.BooleanField(initial=True,
            label=FormEntry._meta.get_field("entry_time").verbose_name,
            required=False)
        self.fields["%s_filter" % field_key] = date_filter_field
        self.fields["%s_from" % field_key] = forms.DateField(
            label=" ", widget=SelectDateWidget(), required=False)
        self.fields["%s_to" % field_key] = forms.DateField(
            label=_("and"), widget=SelectDateWidget(), required=False)

    def __iter__(self):
        """
        Yield pairs of include checkbox / filters for each field.
        """
        for field_id in [f.id for f in self.form_fields] + [0]:
            prefix = "field_%s_" % field_id
            fields = [f for f in super(EntriesForm, self).__iter__()
                      if f.name.startswith(prefix)]
            yield fields[0], fields[1], fields[2:]

    def columns(self):
        """
        Returns the list of selected column names.
        """
        fields = [f.label for f in self.form_fields
                  if self.cleaned_data["field_%s_export" % f.id]]
        if self.cleaned_data["field_0_export"]:
            fields.append(self.entry_time_name)
        return fields

    def rows(self, csv=False):
        """
        Returns each row based on the selected criteria.
        """

        # Store the index of each field against its ID for building each
        # entry row with columns in the correct order. Also store the IDs of
        # fields with a type of FileField or Date-like for special handling of
        # their values.
        field_indexes = {}
        file_field_ids = []
        date_field_ids = []
        for field in self.form_fields:
            if self.cleaned_data["field_%s_export" % field.id]:
                field_indexes[field.id] = len(field_indexes)
                if field.is_a(fields.FILE):
                    file_field_ids.append(field.id)
                elif field.is_a(*fields.DATES):
                    date_field_ids.append(field.id)
        num_columns = len(field_indexes)
        include_entry_time = self.cleaned_data["field_0_export"]
        if include_entry_time:
            num_columns += 1

        # Get the field entries for the given form and filter by entry_time
        # if specified.
        field_entries = FieldEntry.objects.filter(entry__form=self.form
            ).order_by("-entry__id").select_related("entry")
        if self.cleaned_data["field_0_filter"] == FILTER_CHOICE_BETWEEN:
            time_from = self.cleaned_data["field_0_from"]
            time_to = self.cleaned_data["field_0_to"]
            if time_from and time_to:
                field_entries = field_entries.filter(
                    entry__entry_time__range=(time_from, time_to))

        # Loop through each field value ordered by entry, building up each
        # entry as a row. Use the ``valid_row`` flag for marking a row as
        # invalid if it fails one of the filtering criteria specified.
        current_entry = None
        current_row = None
        valid_row = True
        for field_entry in field_entries:
            if field_entry.entry_id != current_entry:
                # New entry, write out the current row and start a new one.
                if valid_row and current_row is not None:
                    if not csv:
                        current_row.insert(0, current_entry)
                    yield current_row
                current_entry = field_entry.entry_id
                current_row = [""] * num_columns
                valid_row = True
                if include_entry_time:
                    current_row[-1] = field_entry.entry.entry_time
            field_value = field_entry.value or ""
            # Check for filter.
            field_id = field_entry.field_id
            filter_type = self.cleaned_data.get("field_%s_filter" % field_id)
            filter_args = None
            if filter_type:
                if filter_type == FILTER_CHOICE_BETWEEN:
                    f, t = "field_%s_from" % field_id, "field_%s_to" % field_id
                    filter_args = [self.cleaned_data[f], self.cleaned_data[t]]
                else:
                    field_name = "field_%s_contains" % field_id
                    filter_args = self.cleaned_data[field_name]
                    if filter_args:
                        filter_args = [filter_args]
            if filter_args:
                # Convert dates before checking filter.
                if field_id in date_field_ids:
                    y, m, d = field_value.split(" ")[0].split("-")
                    dte = date(int(y), int(m), int(d))
                    filter_args.append(dte)
                else:
                    filter_args.append(field_value)
                filter_func = FILTER_FUNCS[filter_type]
                if not filter_func(*filter_args):
                    valid_row = False
            # Create download URL for file fields.
            if field_entry.value and field_id in file_field_ids:
                url = reverse("admin:form_file", args=(field_entry.id,))
                field_value = self.request.build_absolute_uri(url)
                if not csv:
                    parts = (field_value, split(field_entry.value)[1])
                    field_value = mark_safe("<a href=\"%s\">%s</a>" % parts)
            # Only use values for fields that were selected.
            try:
                current_row[field_indexes[field_id]] = field_value
            except KeyError:
                pass
        # Output the final row.
        if valid_row and current_row is not None:
            if not csv:
                current_row.insert(0, current_entry)
            yield current_row
