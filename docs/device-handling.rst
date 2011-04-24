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
to user agent strings is defined in the setting ``DEVICE_USER_AGENTS``::

    DEVICE_USER_AGENTS = (
        ("mobile", ("Android", "BlackBerry", "iPhone")),
        ("desktop", ("Windows", "Macintosh", "Linux")),
    )

Give the above example value for ``DEVICE_USER_AGENTS``, suppose a view or
template referenced the template ``blog/index.html``. If an iPhone made
the request to the website, the template ``mobile/blog/index.html`` would
be searched for, and if a Windows OS made the request then the template
``desktop/blog/index.html`` would be searched for.

.. note::

    If the device specific templates don't exist or a user agent isn't
    matched to any of the device specific strings, then the original
    template name (``blog/index.html`` in the above example) will be used
    as per usual with Django. This means that supporting device specific
    templates is entirely optional.

You can also specify which device should be treated as the default by
defining the setting ``DEFAULT_DEVICE``. For example to ensure templates
for the ``mobile`` device group are used even when no matching user agent
is found, simply define the following in your project's ``settings``
module::

    DEFAULT_DEVICE = "mobile"

Mobile Theme
============

As described in the :doc:`themes` section, a Mezzanine theme is simply a
Django reusable app with templates that can be installed into a project
using the ``install_theme`` management command. Mezzanine includes the
package ``mezzanine.mobile`` which contains a full set of default templates
and assests for creating a mobile version of your site. To install the
``mezzanine.mobile`` templates and assets directly into your project
simply run the following command in your project directory::

    $ python manage.py install_theme mezzanine.mobile

Implementation Considerations
=============================

Using the ``DEVICE_USER_AGENTS`` setting, Mezzanine simply prefixes
any referenced template path with the device specific sub-directory name
if a user agent matches one of the strings specified for the device. For
example if a user agent matches the ``mobile`` device set of templates,
a reference to ``blog/index.html`` will be changed to call
``select_template(["mobile/blog/index.html", "blog/index.html"])`` under
the hood.

To achieve this, a request's user agent string (via the template context)
must be accessible at the time a template name is passed to
Django's template loading system. Mezzanine therefore provides its own
implementation of the following Django functions which are all context
aware and should be used in place of their Django counterparts when
developing custom functionality for a Mezzanine based project or
application.

==================================================  =============================================
Django                                              Mezzanine
==================================================  =============================================
``django.shortcuts.render_to_response``             ``mezzanine.utils.views.render_to_response``
``django.template.Library().inclusion_tag``         ``mezzanine.template.Library().inclusion_tag``
``django.template.loader.get_template``             ``mezzanine.template.loader.get_template``
``django.template.loader.select_template``          ``mezzanine.template.loader.select_template``
``django.views.generic.simple.direct_to_template``  ``mezzanine.core.views.direct_to_template``
==================================================  =============================================

Mezzanine also provides replacements for the ``extends`` and ``include``
template tags however this is implemented transparently with no changes
required to your code.
