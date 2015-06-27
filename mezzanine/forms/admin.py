from __future__ import unicode_literals
from future.builtins import open, bytes

from copy import deepcopy
from io import BytesIO, StringIO
from csv import writer
from datetime import datetime
from mimetypes import guess_type
from os.path import join

from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.messages import info
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ungettext, ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.core.admin import TabularDynamicInlineAdmin
from mezzanine.forms.forms import EntriesForm
from mezzanine.forms.models import Form, Field, FormEntry, FieldEntry
from mezzanine.pages.admin import PageAdmin
from mezzanine.utils.urls import admin_url, slugify


fs = FileSystemStorage(location=settings.FORMS_UPLOAD_ROOT)

# Copy the fieldsets for PageAdmin and add the extra fields for FormAdmin.
form_fieldsets = deepcopy(PageAdmin.fieldsets)
form_fieldsets[0][1]["fields"][3:0] = ["content", "button_text", "response"]
form_fieldsets = list(form_fieldsets)
form_fieldsets.insert(1, (_("Email"), {"fields": ("send_email", "email_from",
    "email_copies", "email_subject", "email_message")}))


class FieldAdmin(TabularDynamicInlineAdmin):
    """
    Admin class for the form field. Inherits from TabularDynamicInlineAdmin to
    add dynamic "Add another" link and drag/drop ordering.
    """
    model = Field


class FormAdmin(PageAdmin):
    """
    Admin class for the Form model. Includes the urls & views for exporting
    form entries as CSV and downloading files uploaded via the forms app.
    """

    class Media:
        css = {"all": ("mezzanine/css/admin/form.css",)}

    inlines = (FieldAdmin,)
    list_display = ("title", "status", "email_copies",)
    list_display_links = ("title",)
    list_editable = ("status", "email_copies")
    list_filter = ("status",)
    search_fields = ("title", "content", "response", "email_from",
                     "email_copies")
    fieldsets = form_fieldsets

    def get_urls(self):
        """
        Add the entries view to urls.
        """
        urls = super(FormAdmin, self).get_urls()
        extra_urls = patterns("",
            url("^(?P<form_id>\d+)/entries/$",
                self.admin_site.admin_view(self.entries_view),
                name="form_entries"),
            url("^file/(?P<field_entry_id>\d+)/$",
                self.admin_site.admin_view(self.file_view),
                name="form_file"),
        )
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
                fname = "%s-%s.csv" % (form.slug, timestamp)
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
                    writerow = lambda row: csv.writerow([c.encode("utf-8")
                        if hasattr(c, "encode") else c for c in row])
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
                        message = ungettext("1 entry deleted",
                                            "%(count)s entries deleted", count)
                        info(request, message % {"count": count})
        template = "admin/forms/entries.html"
        context = {"title": _("View Entries"), "entries_form": entries_form,
                   "opts": self.model._meta, "original": form,
                   "can_delete_entries": can_delete_entries,
                   "submitted": submitted}
        return render_to_response(template, context, RequestContext(request))

    def file_view(self, request, field_entry_id):
        """
        Output the file for the requested field entry.
        """
        field_entry = get_object_or_404(FieldEntry, id=field_entry_id)
        path = join(fs.location, field_entry.value)
        response = HttpResponse(content_type=guess_type(path)[0])
        f = open(path, "r+b")
        response["Content-Disposition"] = "attachment; filename=%s" % f.name
        response.write(f.read())
        f.close()
        return response

admin.site.register(Form, FormAdmin)
