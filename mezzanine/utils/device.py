from __future__ import unicode_literals


def device_from_request(request):
    """
    Determine's the device name from the request by first looking for an
    overridding cookie, and if not found then matching the user agent.
    Used at both the template level for choosing the template to load and
    also at the cache level as a cache key prefix.
    """
    from mezzanine.conf import settings
    try:
        # If a device was set via cookie, match available devices.
        for (device, _) in settings.DEVICE_USER_AGENTS:
            if device == request.COOKIES["mezzanine-device"]:
                return device
    except KeyError:
        # If a device wasn't set via cookie, match user agent.
        try:
            user_agent = request.META["HTTP_USER_AGENT"].lower()
        except KeyError:
            pass
        else:
            try:
                user_agent = user_agent.decode("utf-8")
                for (device, ua_strings) in settings.DEVICE_USER_AGENTS:
                    for ua_string in ua_strings:
                        if ua_string.lower() in user_agent:
                            return device
            except (AttributeError, UnicodeDecodeError, UnicodeEncodeError):
                pass
    return ""


def templates_for_device(request, templates):
    """
    Given a template name (or list of them), returns the template names
    as a list, with each name prefixed with the device directory
    inserted before it's associate default in the list.
    """
    from mezzanine.conf import settings
    if not isinstance(templates, (list, tuple)):
        templates = [templates]
    device = device_from_request(request)
    device_templates = []
    for template in templates:
        if device:
            device_templates.append("%s/%s" % (device, template))
        if settings.DEVICE_DEFAULT and settings.DEVICE_DEFAULT != device:
            default = "%s/%s" % (settings.DEVICE_DEFAULT, template)
            device_templates.append(default)
        device_templates.append(template)
    return device_templates
