from copy import deepcopy
from csv import writer
from datetime import datetime
from io import BytesIO, StringIO
from mimetypes import guess_type
from os.path import join

from django.contrib import admin
from django.contrib.messages import info
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import re_path
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from mezzanine.conf import settings
from mezzanine.core.admin import TabularDynamicInlineAdmin
from mezzanine.core.forms import DynamicInlineAdminForm
from mezzanine.forms.forms import EntriesForm
from mezzanine.forms.models import Field, FieldEntry, Form, FormEntry
from mezzanine.pages.admin import PageAdmin
from mezzanine.utils.static import static_lazy as static
from mezzanine.utils.urls import admin_url, slugify

fs = FileSystemStorage(location=settings.FORMS_UPLOAD_ROOT)

# Copy the fieldsets for PageAdmin and add the extra fields for FormAdmin.
form_fieldsets = deepcopy(PageAdmin.fieldsets)
form_fieldsets[0][1]["fields"][3:0] = ["content", "button_text", "response"]
form_fieldsets = list(form_fieldsets)
form_fieldsets.insert(
    1,
    (
        _("Email"),
        {
            "fields": (
                "send_email",
                "email_from",
                "email_copies",
                "email_subject",
                "email_message",
            )
        },
    ),
)

inline_field_excludes = []
if not settings.FORMS_USE_HTML5:
    inline_field_excludes += ["placeholder_text"]


class FieldAdminInlineForm(DynamicInlineAdminForm):
    def __init__(self, *args, **kwargs):
        """
        Ensure the label and help_text fields are rendered as text inputs
        instead of text areas.
        """
        super().__init__(*args, **kwargs)
        for name in self.fields:
            # We just want to swap some textareas for inputs here, but
            # there are some extra considerations for modeltranslation:
            #   1) Form field names are suffixed with language,
            #      eg help_text_en, so we check for the name as a prefix.
            #   2) At this point, modeltranslation has also monkey-patched
            #      on necessary CSS classes to the widget, so retain those.
            if name.startswith("label") or name.startswith("help_text"):
                css_class = self.fields[name].widget.attrs.get("class", None)
                self.fields[name].widget = admin.widgets.AdminTextInputWidget()
                if css_class:
                    self.fields[name].widget.attrs["class"] = css_class

    class Meta:
        model = Field
        exclude = inline_field_excludes


class FieldAdmin(TabularDynamicInlineAdmin):
    """
    Admin class for the form field. Inherits from TabularDynamicInlineAdmin to
    add dynamic "Add another" link and drag/drop ordering.
    """

    model = Field
    form = FieldAdminInlineForm


class FormAdmin(PageAdmin):
    """
    Admin class for the Form model. Includes the urls & views for exporting
    form entries as CSV and downloading files uploaded via the forms app.
    """

    class Media:
        css = {"all": (static("mezzanine/css/admin/form.css"),)}

    inlines = (FieldAdmin,)
    list_display = (
        "title",
        "status",
        "email_copies",
    )
    list_display_links = ("title",)
    list_editable = ("status", "email_copies")
    list_filter = ("status",)
    search_fields = ("title", "content", "response", "email_from", "email_copies")
    fieldsets = form_fieldsets

    def get_urls(self):
        """
        Add the entries view to urls.
        """
        urls = super().get_urls()
        extra_urls = [
            re_path(
                r"^(?P<form_id>\d+)/entries/$",
                self.admin_site.admin_view(self.entries_view),
                name="form_entries",
            ),
            re_path(
                r"^file/(?P<field_entry_id>\d+)/$",
                self.admin_site.admin_view(self.file_view),
                name="form_file",
            ),
        ]
        return extra_urls + urls

    def entries_view(self, request, form_id):
        """
        Displays the form entries in a HTML table with option to
        export as CSV file.
        """
        if request.POST.get("back"):
            change_url = admin_url(Form, "change", form_id)
            return HttpResponseRedirect(change_url)
        form = get_object_or_404(Form, id=form_id)
        entries_form = EntriesForm(form, request, request.POST or None)
        delete_entries_perm = "%s.delete_formentry" % FormEntry._meta.app_label
        can_delete_entries = request.user.has_perm(delete_entries_perm)
        submitted = entries_form.is_valid()
        if submitted:
            if request.POST.get("export"):
                response = HttpResponse(content_type="text/csv")
                timestamp = slugify(datetime.now().ctime())
                fname = f"{form.slug}-{timestamp}.csv"
                header = "attachment; filename=%s" % fname
                response["Content-Disposition"] = header
                queue = StringIO()
                delimiter = settings.FORMS_CSV_DELIMITER
                try:
                    csv = writer(queue, delimiter=delimiter)
                    writerow = csv.writerow
                except TypeError:
                    queue = BytesIO()
                    delimiter = bytes(delimiter, encoding="utf-8")
                    csv = writer(queue, delimiter=delimiter)
                    writerow = lambda row: csv.writerow(
                        [c.encode("utf-8") if hasattr(c, "encode") else c for c in row]
                    )
                writerow(entries_form.columns())
                for row in entries_form.rows(csv=True):
                    writerow(row)
                data = queue.getvalue()
                response.write(data)
                return response
            elif request.POST.get("delete") and can_delete_entries:
                selected = request.POST.getlist("selected")
                if selected:
                    entries = FormEntry.objects.filter(id__in=selected)
                    count = entries.count()
                    if count > 0:
                        entries.delete()
                        message = ngettext(
                            "1 entry deleted", "%(count)s entries deleted", count
                        )
                        info(request, message % {"count": count})
        template = "admin/forms/entries.html"
        context = {
            "title": _("View Entries"),
            "entries_form": entries_form,
            "opts": self.model._meta,
            "original": form,
            "can_delete_entries": can_delete_entries,
            "submitted": submitted,
        }
        return render(request, template, context)

    def file_view(self, request, field_entry_id):
        """
        Output the file for the requested field entry.
        """
        field_entry = get_object_or_404(FieldEntry, id=field_entry_id)
        path = join(fs.location, field_entry.value)
        response = HttpResponse(content_type=guess_type(path)[0])
        with open(path, "r+b") as f:
            response["Content-Disposition"] = "attachment; filename=%s" % f.name
            response.write(f.read())
        return response


admin.site.register(Form, FormAdmin)
