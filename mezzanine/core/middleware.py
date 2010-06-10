
MOBILE_USERAGENTS = ("2.0 MMP","240x320","400X240","AvantGo","BlackBerry",
    "Blazer","Cellphone","Danger","DoCoMo","Elaine/3.0","EudoraWeb",
    "Googlebot-Mobile","hiptop","IEMobile","KYOCERA/WX310K","LG/U990",
    "MIDP-2.","MMEF20","MOT-V","NetFront","Newt","Nintendo Wii","Nitro",
    "Nokia","Opera Mini","Palm","PlayStation Portable","portalmmm","Proxinet",
    "ProxiNet","SHARP-TQ-GX10","SHG-i900","Small","SonyEricsson","Symbian OS",
    "SymbianOS","TS21i-10","UP.Browser","UP.Link","webOS","Windows CE",
    "WinWAP","YahooSeeker/M1A1-R2D2","iPhone","iPod","Android",
    "BlackBerry9530","LG-TU915 Obigo","LGE VX","webOS","Nokia5800")

class MobileTemplate(object):
    """
    If a mobile user agent is detected, inspect the default args for the view 
    func, and if a template name is found assume it is the template arg and 
    attempt to load a mobile template based on the original template name.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        if any(ua for ua in MOBILE_USERAGENTS if ua in 
            request.META["HTTP_USER_AGENT"]):
            template = view_kwargs.get("template")
            if template is None:
                for default in view_func.func_defaults:
                    if str(default).endswith(".html"):
                        template = default
            if template is not None:
                template = template.rsplit(".html", 1)[0] + ".mobile.html"
                try:
                    get_template(template)
                except TemplateDoesNotExist:
                    pass
                else:
                    view_kwargs["template"] = template
                    return view_func(request, *view_args, **view_kwargs)
        return None
