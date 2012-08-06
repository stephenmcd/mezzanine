"""
Default settings for the ``mezzanine.pages`` app. Each of these can be
overridden in your project's settings module, just like regular
Django settings. The ``editable`` argument for each controls whether
the setting is editable via Django's admin.

Thought should be given to how a setting is actually used before
making it editable, as it may be inappropriate - for example settings
that are only read during startup shouldn't be editable, since changing
them would require an application reload.
"""

from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import register_setting


register_setting(
    name="PAGE_MENU_TEMPLATES",
    description=_("A sequence of templates used by the ``page_menu`` "
        "template tag. Each item in the sequence is a three item sequence, "
        "containing a unique ID for the template, a label for the template, "
        "and the template path. These templates are then available for "
        "selection when editing which menus a page should appear in. Note "
        "that if a menu template is used that doesn't appear in this "
        "setting, all pages will appear in it."),
    editable=False,
    default=(
        (1, _("Top navigation bar"), "pages/menus/dropdown.html"),
        (2, _("Left-hand tree"), "pages/menus/tree.html"),
        (3, _("Footer"), "pages/menus/footer.html"),
    ),
)

register_setting(
    name="PAGE_MENU_TEMPLATES_DEFAULT",
    description=_("A sequence of IDs from the ``PAGE_MENU_TEMPLATES`` "
        "setting that defines the default menu templates selected when "
        "creating new pages. By default all menu templates are selected. "
        "Set this setting to an empty sequence to have no templates "
        "selected by default."),
    editable=False,
    default=None,
)

register_setting(
    name="PAGES_MENU_SHOW_ALL",
    description=_("If ``True``, the left-hand tree template for the pages "
        "menu will show all levels of navigation, otherwise child pages "
        "are only shown when viewing the parent page."),
    editable=False,
    default=True,
)

register_setting(
    name="PAGES_PUBLISHED_INCLUDE_LOGIN_REQUIRED",
    description=_("If ``True``, pages with ``login_required`` checked will "
        "still be listed in menus and search results, for unauthenticated "
        "users. Regardless of this setting, when an unauthenticated user "
        "accesses a page with ``login_required`` checked, they'll be "
        "redirected to the login page."),
    editable=False,
    default=False,
)
