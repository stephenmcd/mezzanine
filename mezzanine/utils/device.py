

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
            user_agent = request.META["HTTP_USER_AGENT"]
        except KeyError:
            pass
        else:
            for (device, ua_strings) in settings.DEVICE_USER_AGENTS:
                for ua_string in ua_strings:
                    if ua_string in user_agent:
                        return device
    return ""
