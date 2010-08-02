
from csv import writer
from datetime import datetime
from mimetypes import guess_type
from os.path import join

from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import loader, Context
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from forms_builder.forms.models import Form, Field, FormEntry, FieldEntry
from forms_builder.forms.settings import UPLOAD_ROOT


fs = FileSystemStorage(location=UPLOAD_ROOT)

    
class FieldAdmin(admin.TabularInline):
    model = Field

class FormAdmin(admin.ModelAdmin):

    inlines = (FieldAdmin,)
    list_display = ("title", "status", "email_from", "email_copies", 
        "admin_link_export", "admin_link_view")
    list_display_links = ("title",)
    list_editable = ("status", "email_from", "email_copies")
    list_filter = ("status",)
    search_fields = ("title", "intro", "response", "email_from", 
        "email_copies")
    radio_fields = {"status": admin.HORIZONTAL}
    fieldsets = (
        (None, {"fields": ("title", "status", "intro", "response")}),
        (_("Email"), {"fields": ("send_email", "email_from", "email_copies")}),
    )

    def get_urls(self):
        """
        Add the export view to urls.
        """
        urls = super(FormAdmin, self).get_urls()
        extra_urls = patterns("", 
            url("^export/(?P<form_id>\d+)/$", 
                self.admin_site.admin_view(self.export_view), 
                name="form_export"),
            url("^file/(?P<field_entry_id>\d+)/$", 
                self.admin_site.admin_view(self.file_view), 
                name="form_file"),
        )
        return extra_urls + urls

    def export_view(self, request, form_id):
        """
        Output a CSV file to the browser containing the entries for the form. 
        """
        form = get_object_or_404(Form, id=form_id)
        response = HttpResponse(mimetype="text/csv")
        csvname = "%s-%s.csv" % (form.slug, slugify(datetime.now().ctime()))
        response["Content-Disposition"] = "attachment; filename=%s" % csvname
        csv = writer(response)
        # Write out the column names and store the index of each field 
        # against its ID for building each entry row. Also store the IDs of 
        # fields with a type of FileField for converting their field values 
        # into download URLs.
        columns = []
        field_indexes = {}
        file_field_ids = []
        for field in form.fields.all():
            columns.append(field.label.encode("utf-8"))
            field_indexes[field.id] = len(field_indexes)
            if field.field_type == "FileField":
                file_field_ids.append(field.id)
        entry_time_name = FormEntry._meta.get_field("entry_time").verbose_name
        columns.append(unicode(entry_time_name))
        csv.writerow(columns)
        # Loop through each field value order by entry, building up each  
        # entry as a row.
        current_entry = None
        current_row = None
        values = FieldEntry.objects.filter(entry__form=form
            ).order_by("-entry__id").select_related(depth=1)
        for field_entry in values:
            if field_entry.entry_id != current_entry:
                # New entry, write out the current row and start a new one.
                current_entry = field_entry.entry_id
                if current_row is not None:
                    csv.writerow(current_row)
                current_row = [""] * len(columns)
                current_row[-1] = field_entry.entry.entry_time
            value = field_entry.value.encode("utf-8")
            # Create download URL for file fields.
            if field_entry.field_id in file_field_ids:
                url = reverse("admin:form_file", args=(field_entry.id,))
                value = request.build_absolute_uri(url)
            # Only use values for fields that currently exist for the form.
            try:
                current_row[field_indexes[field_entry.field_id]] = value
            except KeyError:
                pass
        # Write out the final row.
        if current_row is not None:
            csv.writerow(current_row)
        return response        

    def file_view(self, request, field_entry_id):
        """
        Output the file for the requested field entry.
        """
        field_entry = get_object_or_404(FieldEntry, id=field_entry_id)
        path = join(fs.location, field_entry.value)
        response = HttpResponse(mimetype=guess_type(path)[0])
        f = open(path, "r+b")
        response["Content-Disposition"] = "attachment; filename=%s" % f.name
        response.write(f.read())
        f.close()
        return response

admin.site.register(Form, FormAdmin)

