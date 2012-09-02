
from django.shortcuts import redirect

from mezzanine.conf import settings
from mezzanine.forms.forms import FormForForm
from mezzanine.forms.models import Form
from mezzanine.forms.signals import form_invalid, form_valid
from mezzanine.pages.page_processors import processor_for
from mezzanine.utils.email import send_mail_template
from mezzanine.utils.views import is_spam


def format_value(value):
    """
    Convert a list into a comma separated string, for displaying
    select multiple values in emails.
    """
    if isinstance(value, list):
        value = ", ".join([v.strip() for v in value])
    return value


@processor_for(Form)
def form_processor(request, page):
    """
    Display a built form and handle submission.
    """
    form = FormForForm(page.form, request.POST or None, request.FILES or None)
    if form.is_valid():
        url = page.get_absolute_url() + "?sent=1"
        if is_spam(request, form, url):
            return redirect(url)
        entry = form.save()
        subject = page.form.email_subject
        if not subject:
            subject = "%s - %s" % (page.form.title, entry.entry_time)
        fields = [(v.label, format_value(form.cleaned_data[k]))
                  for (k, v) in form.fields.items()]
        context = {
            "fields": fields,
            "message": page.form.email_message,
            "request": request,
        }
        email_from = page.form.email_from or settings.DEFAULT_FROM_EMAIL
        email_to = form.email_to()
        if email_to and page.form.send_email:
            send_mail_template(subject, "email/form_response", email_from,
                               email_to, context, fail_silently=settings.DEBUG)
        if not settings.FORMS_DISABLE_SEND_FROM_EMAIL_FIELD:
            # Send from the email entered,
            # unless FORMS_DISABLE_SEND_FROM_EMAIL_FIELD is True.
            email_from = email_to or email_from
        email_copies = page.form.email_copies.split(",")
        email_copies = [e.strip() for e in email_copies if e.strip()]
        if email_copies:
            attachments = []
            for f in form.files.values():
                f.seek(0)
                attachments.append((f.name, f.read()))
            send_mail_template(subject, "email/form_response", email_from,
                               email_copies, context, attachments=attachments,
                               fail_silently=settings.DEBUG)
        form_valid.send(sender=request, form=form, entry=entry)
        return redirect(url)
    form_invalid.send(sender=request, form=form)
    return {"form": form}
