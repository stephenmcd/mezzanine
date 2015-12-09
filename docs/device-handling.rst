===============
Device Handling
===============

Mezzanine comes with the ability to use different sets of templates
depending on the device being used to access the website. For example one
set of templates may be used for desktop browsers with a corresponding set
of templates being used for mobile phones.

Devices are grouped into types with each type being named after the
sub-directory containing its specific set of templates. Each device is then
defined by a list of strings that could be found in the user agent that
matches the particular device. This mapping of device sub-directory names
to user agent strings is defined in the setting :ref:`DEVICE_USER_AGENTS-LABEL`::

    DEVICE_USER_AGENTS = (
        ("mobile", ("Android", "BlackBerry", "iPhone")),
        ("desktop", ("Windows", "Macintosh", "Linux")),
    )

Given the above example value for :ref:`DEVICE_USER_AGENTS-LABEL` suppose a
view or template referenced the template ``blog/index.html``. If an iPhone
made the request to the website, the template ``mobile/blog/index.html``
would be searched for, and if a Windows OS made the request then the template
``desktop/blog/index.html`` would be searched for.

.. note::

    If the device specific templates don't exist or a user agent isn't
    matched to any of the device specific strings, then the original
    template name (``blog/index.html`` in the above example) will be used
    as per usual with Django. This means that supporting device specific
    templates is entirely optional.

You can also specify which device should be treated as the default by
defining the setting :ref:`DEVICE_DEFAULT-LABEL`. For example to ensure templates
for the ``mobile`` device group are used even when no matching user agent
is found, simply define the following in your project's ``settings``
module::

    DEVICE_DEFAULT = "mobile"

Mobile Theme
============

Mezzanine includes the app :mod:`mezzanine.mobile` which contains a full
set of default templates and assets for creating a mobile version of
your site. Simply add :mod:`mezzanine.mobile` to your ``INSTALLED_APPS``
setting to use it.

Implementation Considerations
=============================

Using the :ref:`DEVICE_USER_AGENTS-LABEL` setting, Mezzanine simply prefixes
any referenced template path with the device specific sub-directory name
if a user agent matches one of the strings specified for the device. For
example if a user agent matches the ``mobile`` device set of templates,
a reference to ``blog/index.html`` will be changed to the list
``["mobile/blog/index.html", "blog/index.html"]`` under the hood.

To achieve this, the middleware
:class:`mezzanine.core.middleware.TemplateForDeviceMiddleware` catches Django
``TemplateResponse`` responses, and changes the template list prior to
the response being rendered. As such, any views you implement should
return ``TemplateResponse`` objects. The table below lists Mezzanine
versions of Django features that can be used to ensure a
``TemplateResponse`` is returned.

==================================================  ==================================================
Django                                              Mezzanine
==================================================  ==================================================
``django.shortcuts.render``                         :func:`mezzanine.utils.views.render`
``django.template.Library().inclusion_tag``         :meth:`mezzanine.template.Library().inclusion_tag`
``django.views.generic.simple.direct_to_template``  :func:`mezzanine.core.views.direct_to_template`
==================================================  ==================================================
