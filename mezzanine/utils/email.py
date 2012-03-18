
from django.core.mail import EmailMultiAlternatives
from django.template import loader, Context


def send_mail_template(subject, template, addr_from, addr_to, context=None,
                       attachments=None, fail_silently=False):
    """
    Send email rendering text and html versions for the specified template name
    using the context dictionary passed in.
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
