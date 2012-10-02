
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.template import loader, Context
from django.utils.http import int_to_base36

from mezzanine.conf import settings


def send_mail_template(subject, template, addr_from, addr_to, context=None,
                       attachments=None, fail_silently=False):
    """
    Send email rendering text and html versions for the specified
    template name using the context dictionary passed in.
    """
    if context is None:
        context = {}
    if attachments is None:
        attachments = []
    # Allow for a single address to be passed in.
    if not hasattr(addr_to, "__iter__"):
        addr_to = [addr_to]
    # Loads a template passing in vars as context.
    render = lambda type: loader.get_template("%s.%s" %
                          (template, type)).render(Context(context))
    # Create and send email.
    msg = EmailMultiAlternatives(subject, render("txt"), addr_from, addr_to)
    msg.attach_alternative(render("html"), "text/html")
    for attachment in attachments:
        msg.attach(*attachment)
    msg.send(fail_silently=fail_silently)


def send_verification_mail(request, user, verification_type):
    """
    Sends an email with a verification link to users when
    ``ACCOUNTS_VERIFICATION_REQUIRED`` is ```True`` and they're signing
    up, or when they retrieve a lost password.
    The ``verification_type`` arg is both the name of the urlpattern for
    the verification link, as well as the names of the email templates
    to use.
    """
    verify_url = reverse(verification_type, kwargs={
        "uidb36": int_to_base36(user.id),
        "token": default_token_generator.make_token(user),
    }) + "?next=" + request.GET.get("next", "/")
    context = {
        "request": request,
        "user": user,
        "verify_url": verify_url,
    }
    subject_template = "email/%s_subject.txt" % verification_type
    subject = loader.get_template(subject_template).render(Context(context))
    send_mail_template("".join(subject.splitlines()),
                       "email/%s" % verification_type,
                       settings.DEFAULT_FROM_EMAIL, user.email,
                       context=context, fail_silently=settings.DEBUG)
