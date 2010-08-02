
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.template import RequestContext
from django.shortcuts import get_object_or_404, redirect, render_to_response

from forms_builder.forms.forms import FormForForm
from forms_builder.forms.models import Form


def form_detail(request, slug, template="forms/form_detail.html"):
    """
    Display a built form and handle submission.
    """    
    published = Form.objects.published(for_user=request.user)
    form = get_object_or_404(published, slug=slug)
    form_for_form = FormForForm(form, request.POST or None, request.FILES or None)
    if request.method == "POST":
        if form_for_form.is_valid():
            entry = form_for_form.save()
            fields = ["%s: %s" % (v.label, form_for_form.cleaned_data[k]) 
                for (k, v) in form_for_form.fields.items()]
            subject = "%s - %s" % (form.title, entry.entry_time)
            body = "\n".join(fields)
            email_from = form.email_from or settings.DEFAULT_FROM_EMAIL
            email_to = form_for_form.email_to()
            if email_to and form.send_email:
                msg = EmailMessage(subject, body, email_from, [email_to])
                msg.send()
            email_from = email_to or email_from # Send from the email entered.
            email_copies = [e.strip() for e in form.email_copies.split(",") 
                if e.strip()]
            if email_copies:
                msg = EmailMessage(subject, body, email_from, email_copies)
                for f in form_for_form.files.values():
                    f.seek(0)
                    msg.attach(f.name, f.read())
                msg.send()
            return redirect(reverse("form_sent", kwargs={"slug": form.slug}))
    context = {"form": form, "form_for_form": form_for_form}
    return render_to_response(template, context, RequestContext(request))

def form_sent(request, slug, template="forms/form_sent.html"):
    """
    Show the response message.
    """
    published = Form.objects.published(for_user=request.user)
    form = get_object_or_404(published, slug=slug)
    context = {"form": form}
    return render_to_response(template, context, RequestContext(request))
