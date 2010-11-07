

from django.core.mail import EmailMessage
from django.shortcuts import redirect

from mezzanine.conf import settings
from mezzanine.forms.forms import FormForForm
from mezzanine.forms.models import Form
from mezzanine.pages.page_processors import processor_for


def format_value(value):
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
        entry = form.save()
        fields = ["%s: %s" % (v.label, format_value(form.cleaned_data[k]))
            for (k, v) in form.fields.items()]
        subject = page.form.email_subject
        if not subject:
            subject = "%s - %s" % (page.form.title, entry.entry_time)
        body = "\n".join(fields)
        if page.form.email_message:
            body = "%s\n\n%s" % (page.form.email_message, body)
        email_from = page.form.email_from or settings.DEFAULT_FROM_EMAIL
        email_to = form.email_to()
        if email_to and page.form.send_email:
            msg = EmailMessage(subject, body, email_from, [email_to])
            msg.send()
        email_from = email_to or email_from  # Send from the email entered.
        email_copies = [e.strip() for e in page.form.email_copies.split(",")
            if e.strip()]
        if email_copies:
            msg = EmailMessage(subject, body, email_from, email_copies)
            for f in form.files.values():
                f.seek(0)
                msg.attach(f.name, f.read())
            msg.send()
        return redirect(page.get_absolute_url() + "?sent=1")
    return {"form": form}
