from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.urls import reverse
from django.utils.http import int_to_base36

from mezzanine.conf import settings
from mezzanine.conf.context_processors import settings as context_settings
from mezzanine.utils.urls import admin_url, next_url


def split_addresses(email_string_list):
    """
    Converts a string containing comma separated email addresses
    into a list of email addresses.
    """
    return [f for f in [s.strip() for s in email_string_list.split(",")] if f]


def subject_template(template, context):
    """
    Loads and renders an email subject template, returning the
    subject string.
    """
    subject = loader.get_template(template).render(context)
    return " ".join(subject.splitlines()).strip()


def send_mail_template(
    subject,
    template,
    addr_from,
    addr_to,
    context=None,
    attachments=None,
    fail_silently=None,
    addr_bcc=None,
    headers=None,
):
    """
    Send email rendering text and html versions for the specified
    template name using the context dictionary passed in.
    """
    if context is None:
        context = {}
    if attachments is None:
        attachments = []
    if fail_silently is None:
        fail_silently = settings.EMAIL_FAIL_SILENTLY
    # Add template accessible settings from Mezzanine to the context
    # (normally added by a context processor for HTTP requests).
    context.update(context_settings())
    # Allow for a single address to be passed in.
    # Python 3 strings have an __iter__ method, so the following hack
    # doesn't work: if not hasattr(addr_to, "__iter__"):
    if isinstance(addr_to, str) or isinstance(addr_to, bytes):
        addr_to = [addr_to]
    if addr_bcc is not None and (
        isinstance(addr_bcc, str) or isinstance(addr_bcc, bytes)
    ):
        addr_bcc = [addr_bcc]
    # Loads a template passing in vars as context.
    render = lambda type: loader.get_template(f"{template}.{type}").render(context)
    # Create and send email.
    msg = EmailMultiAlternatives(
        subject, render("txt"), addr_from, addr_to, addr_bcc, headers=headers
    )
    msg.attach_alternative(render("html"), "text/html")
    for attachment in attachments:
        msg.attach(*attachment)
    msg.send(fail_silently=fail_silently)


def send_verification_mail(request, user, verification_type):
    """
    Sends an email with a verification link to users when
    ``ACCOUNTS_VERIFICATION_REQUIRED`` is ```True`` and they're signing
    up, or when they reset a lost password.
    The ``verification_type`` arg is both the name of the urlpattern for
    the verification link, as well as the names of the email templates
    to use.
    """
    verify_url = (
        reverse(
            verification_type,
            kwargs={
                "uidb36": int_to_base36(user.id),
                "token": default_token_generator.make_token(user),
            },
        )
        + "?next="
        + (next_url(request) or "/")
    )
    context = {
        "request": request,
        "user": user,
        "verify_url": verify_url,
    }
    subject_template_name = "email/%s_subject.txt" % verification_type
    subject = subject_template(subject_template_name, context)
    send_mail_template(
        subject,
        "email/%s" % verification_type,
        settings.DEFAULT_FROM_EMAIL,
        user.email,
        context=context,
    )


def send_approve_mail(request, user):
    """
    Sends an email to staff in listed in the setting
    ``ACCOUNTS_APPROVAL_EMAILS``, when a new user signs up and the
    ``ACCOUNTS_APPROVAL_REQUIRED`` setting is ``True``.
    """
    approval_emails = split_addresses(settings.ACCOUNTS_APPROVAL_EMAILS)
    if not approval_emails:
        return
    context = {
        "request": request,
        "user": user,
        "change_url": admin_url(user.__class__, "change", user.id),
    }
    subject = subject_template("email/account_approve_subject.txt", context)
    send_mail_template(
        subject,
        "email/account_approve",
        settings.DEFAULT_FROM_EMAIL,
        approval_emails,
        context=context,
    )


def send_approved_mail(request, user):
    """
    Sends an email to a user once their ``is_active`` status goes from
    ``False`` to ``True`` when the ``ACCOUNTS_APPROVAL_REQUIRED``
    setting is ``True``.
    """
    context = {"request": request, "user": user}
    subject = subject_template("email/account_approved_subject.txt", context)
    send_mail_template(
        subject,
        "email/account_approved",
        settings.DEFAULT_FROM_EMAIL,
        user.email,
        context=context,
    )
