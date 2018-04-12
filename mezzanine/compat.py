import django


_django_ver = django.VERSION

is_dj2 = (_django_ver[0] == 2)

if is_dj2:
    from django.forms.widgets import SelectDateWidget
    from django.urls import (resolve, reverse, NoReverseMatch,
                             get_script_prefix)

else:
    from django.forms.extras.widgets import SelectDateWidget  #noqa
    from django.core.urlresolvers import (resolve, reverse, NoReverseMatch, #noqa
                                          get_script_prefix)


def get_rel_to(self):
    if is_dj2:
        return self.remote_field
    else:
        return self.rel.to


def get_js_catalog():
    if is_dj2:
        from django.views.i18n import JavaScriptCatalog
        return JavaScriptCatalog.as_view()
    else:
        from django.views.i18n import javascript_catalog
        return javascript_catalog
