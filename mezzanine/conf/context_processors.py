

def settings(request):
    """
    Add the settings object to the template context.
    """
    from mezzanine.conf import settings
    settings.use_editable()
    settings_dict = dict([(k, getattr(settings, k))
                          for k in settings.TEMPLATE_ACCESSIBLE_SETTINGS])
    #don't load analytics for admin users
    settings_dict['GOOGLE_ANALYTICS_ID']=((settings.GOOGLE_ANALYTICS_ADMIN or
                                           not request.user.is_staff) and
                                          settings_dict.get('GOOGLE_ANALYTICS_ID'))
    return {"settings": type("Settings", (), settings_dict)}
