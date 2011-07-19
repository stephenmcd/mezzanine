
import os.path

from django.conf import settings
from django.utils.translation import ugettext as _

from mezzanine.conf import register_setting


register_setting(
    name="ADMIN_MENU_ORDER",
    description=_("Controls the ordering and grouping of the admin menu."),
    editable=False,
    default=(
        (_("Content"), ("pages.Page", "blog.BlogPost",
           "generic.ThreadedComment", (_("Media Library"), "fb_browse"),)),
        (_("Site"), ("sites.Site", "redirects.Redirect", "conf.Setting")),
        (_("Users"), ("auth.User", "auth.Group",)),
    ),
)

register_setting(
    name="ADMIN_REMOVAL",
    description=_("Unregister these models from the admin."),
    editable=False,
    default=(),
)

register_setting(
    name="BLOG_BITLY_USER",
    label=_("bit.ly username"),
    description=_("Username for bit.ly URL shortening service."),
    editable=True,
    default="",
)

register_setting(
    name="BLOG_BITLY_KEY",
    label=_("bit.ly key"),
    description=_("Key for bit.ly URL shortening service."),
    editable=True,
    default="",
)

register_setting(
    name="BLOG_POST_PER_PAGE",
    label=_("Blog posts per page"),
    description=_("Number of blog posts to show on a blog listing page."),
    editable=True,
    default=5,
)

register_setting(
    name="BLOG_POST_MAX_PAGING_LINKS",
    label=_("Max blog paging links"),
    description=_("Max number of paging links to show on a blog listing page."),
    editable=True,
    default=10,
)

register_setting(
    name="BLOG_SLUG",
    description=_("Slug of the page object for the blog."),
    editable=False,
    default="blog",
)

register_setting(
    name="COMMENTS_DISQUS_SHORTNAME",
    label=_("Disqus shortname"),
    description=_("Shortname for the http://disqus.com comments service."),
    editable=True,
    default="",
)

register_setting(
    name="COMMENTS_DISQUS_API_PUBLIC_KEY",
    label=_("Disqus public key"),
    description=_("Public key for Disqus developer API"),
    editable=True,
    default="",
)

register_setting(
    name="COMMENTS_DISQUS_API_SECRET_KEY",
    label=_("Disqus secret key"),
    description=_("Secret key for Disqus developer API"),
    editable=True,
    default="",
)

register_setting(
    name="COMMENTS_DEFAULT_APPROVED",
    label=_("Auto-approve comments"),
    description=_("If ``True``, built-in comments are approved by default."),
    editable=True,
    default=True,
)

register_setting(
    name="COMMENTS_NUM_LATEST",
    label=_("Admin comments"),
    description=_("Number of latest comments to show in the admin dashboard."),
    editable=True,
    default=5,
)

register_setting(
    name="COMMENTS_UNAPPROVED_VISIBLE",
    label=_("Show unapproved comments"),
    description=_("If ``True``, comments that have ``is_public`` unchecked "
        "will still be displayed, but replaced with a ``waiting to be "
        "approved`` message."),
    editable=True,
    default=True,
)

register_setting(
    name="COMMENTS_REMOVED_VISIBLE",
    label=_("Show removed comments"),
    description=_("If ``True``, comments that have ``removed`` checked "
        "will still be displayed, but replaced with a ``removed`` message."),
    editable=True,
    default=True,
)

register_setting(
    name="CONTENT_MEDIA_PATH",
    description=_("Absolute path to Mezzanine's internal media files."),
    editable=False,
    default=os.path.join(os.path.dirname(__file__), "..", "core", "media"),
)

register_setting(
    name="CONTENT_MEDIA_URL",
    description=_("URL prefix for serving Mezzanine's internal media files."),
    editable=False,
    default="/content_media/",
)

if "mezzanine.blog" in settings.INSTALLED_APPS:
    dashboard_tags = (
        ("blog_tags.quick_blog", "mezzanine_tags.app_list"),
        ("comment_tags.recent_comments",),
        ("mezzanine_tags.recent_actions",),
    )
else:
    dashboard_tags = (
        ("mezzanine_tags.app_list",),
        ("mezzanine_tags.recent_actions",),
        (),
    )

register_setting(
    name="DASHBOARD_TAGS",
    description=_("A three item sequence, each containing a sequence of "
        "template tags used to render the admin dashboard."),
    editable=False,
    default=dashboard_tags,
)

register_setting(
    name="DEVICE_DEFAULT",
    description=_("Device specific template sub-directory to use as the "
        "default device."),
    editable=False,
    default="",
)

register_setting(
    name="DEVICE_USER_AGENTS",
    description=_("Mapping of device specific template sub-directory names to "
        "the sequence of strings that may be found in their user agents."),
    editable=False,
    default=(
        ("mobile", ("2.0 MMP", "240x320", "400X240", "AvantGo", "BlackBerry",
            "Blazer", "Cellphone", "Danger", "DoCoMo", "Elaine/3.0",
            "EudoraWeb", "Googlebot-Mobile", "hiptop", "IEMobile",
            "KYOCERA/WX310K", "LG/U990", "MIDP-2.", "MMEF20", "MOT-V",
            "NetFront", "Newt", "Nintendo Wii", "Nitro", "Nokia",
            "Opera Mini", "Palm", "PlayStation Portable", "portalmmm",
            "Proxinet", "ProxiNet", "SHARP-TQ-GX10", "SHG-i900",
            "Small", "SonyEricsson", "Symbian OS", "SymbianOS",
            "TS21i-10", "UP.Browser", "UP.Link", "webOS", "Windows CE",
            "WinWAP", "YahooSeeker/M1A1-R2D2", "iPhone", "iPod", "Android",
            "BlackBerry9530", "LG-TU915 Obigo", "LGE VX", "webOS",
            "Nokia5800",)
        ),
    ),
)

register_setting(
    name="FORMS_FIELD_MAX_LENGTH",
    description=_("Max length allowed for field values in the forms app."),
    editable=False,
    default=2000,
)

register_setting(
    name="FORMS_LABEL_MAX_LENGTH",
    description=_("Max length allowed for field labels in the forms app."),
    editable=False,
    default=200,
)

register_setting(
    name="FORMS_USE_HTML5",
    description=_("If ``True``, website forms created by the forms app will "
        "use HTML5 features."),
    editable=False,
    default=False,
)

register_setting(
    name="FORMS_CSV_DELIMITER",
    description=_("Char to use as a field delimiter when exporting form "
        "responses as CSV."),
    editable=False,
    default=",",
)

register_setting(
    name="FORMS_UPLOAD_ROOT",
    description=_("Absolute path for storing file uploads for the forms app."),
    editable=False,
    default="",
)

register_setting(
    name="GOOGLE_ANALYTICS_ID",
    label=_("Google Analytics ID"),
    editable=True,
    description=_("Google Analytics ID (http://www.google.com/analytics/)"),
    default="",
)

register_setting(
    name="RICHTEXT_WIDGET_CLASS",
    description=_("Dotted package path and class name of the widget to use "
        "for the ``RichTextField``."),
    editable=False,
    default="mezzanine.core.forms.TinyMceWidget",
)

register_setting(
    name="RICHTEXT_FILTER",
    description=_("Dotted path to the function to call on a ``RichTextField`` "
        "value before it is rendered to the template."),
    editable=False,
    default=None,
)

register_setting(
    name="TAG_CLOUD_SIZES",
    label=_("Tag Cloud Sizes"),
    description=_("Number of different sizes for tags when shown as a cloud."),
    editable=True,
    default=4,
)

register_setting(
    name="THEME",
    description=_("Package name of theme app to use."),
    editable=False,
    default="",
)

register_setting(
    name="PAGES_MENU_SHOW_ALL",
    description=_("If ``True``, the pages menu will show all levels of "
        "navigation, otherwise child pages are only shown when viewing the "
        "parent page."),
    editable=False,
    default=True,
)

register_setting(
    name="RATINGS_MIN",
    description=_("Min value for a rating."),
    editable=False,
    default=1,
)

register_setting(
    name="RATINGS_MAX",
    description=_("Max value for a rating."),
    editable=False,
    default=5,
)

register_setting(
    name="SEARCH_PER_PAGE",
    label=_("Search results per page"),
    description=_("Number of results to show in the search results page."),
    editable=True,
    default=10,
)

register_setting(
    name="SEARCH_MAX_PAGING_LINKS",
    label=_("Max search paging links"),
    description=_("Max number of paging links for the search results page."),
    editable=True,
    default=10,
)

register_setting(
    name="SITE_TITLE",
    label=_("Site Title"),
    description=_("Title that will display at the top of the site, and be "
        "appended to the content of the HTML title tags on every page."),
    editable=True,
    default="Mezzanine",
)

register_setting(
    name="SITE_TAGLINE",
    label=_("Tagline"),
    description=_("A tag line that will appear at the top of all pages."),
    editable=True,
    default=_("An open source content management platform."),
)

register_setting(
    name="STOP_WORDS",
    description=_("List of words which will be stripped from search queries."),
    editable=False,
    default=(
        "a", "about", "above", "above", "across", "after",
        "afterwards", "again", "against", "all", "almost", "alone",
        "along", "already", "also", "although", "always", "am",
        "among", "amongst", "amoungst", "amount", "an", "and",
        "another", "any", "anyhow", "anyone", "anything", "anyway",
        "anywhere", "are", "around", "as", "at", "back", "be",
        "became", "because", "become", "becomes", "becoming", "been",
        "before", "beforehand", "behind", "being", "below", "beside",
        "besides", "between", "beyond", "bill", "both", "bottom",
        "but", "by", "call", "can", "cannot", "cant", "co", "con",
        "could", "couldnt", "cry", "de", "describe", "detail", "do",
        "done", "down", "due", "during", "each", "eg", "eight",
        "either", "eleven", "else", "elsewhere", "empty", "enough",
        "etc", "even", "ever", "every", "everyone", "everything",
        "everywhere", "except", "few", "fifteen", "fify", "fill",
        "find", "fire", "first", "five", "for", "former", "formerly",
        "forty", "found", "four", "from", "front", "full", "further",
        "get", "give", "go", "had", "has", "hasnt", "have", "he",
        "hence", "her", "here", "hereafter", "hereby", "herein",
        "hereupon", "hers", "herself", "him", "himself", "his",
        "how", "however", "hundred", "ie", "if", "in", "inc",
        "indeed", "interest", "into", "is", "it", "its", "itself",
        "keep", "last", "latter", "latterly", "least", "less", "ltd",
        "made", "many", "may", "me", "meanwhile", "might", "mill",
        "mine", "more", "moreover", "most", "mostly", "move", "much",
        "must", "my", "myself", "name", "namely", "neither", "never",
        "nevertheless", "next", "nine", "no", "nobody", "none",
        "noone", "nor", "not", "nothing", "now", "nowhere", "of",
        "off", "often", "on", "once", "one", "only", "onto", "or",
        "other", "others", "otherwise", "our", "ours", "ourselves",
        "out", "over", "own", "part", "per", "perhaps", "please",
        "put", "rather", "re", "same", "see", "seem", "seemed",
        "seeming", "seems", "serious", "several", "she", "should",
        "show", "side", "since", "sincere", "six", "sixty", "so",
        "some", "somehow", "someone", "something", "sometime",
        "sometimes", "somewhere", "still", "such", "system", "take",
        "ten", "than", "that", "the", "their", "them", "themselves",
        "then", "thence", "there", "thereafter", "thereby",
        "therefore", "therein", "thereupon", "these", "they",
        "thickv", "thin", "third", "this", "those", "though",
        "three", "through", "throughout", "thru", "thus", "to",
        "together", "too", "top", "toward", "towards", "twelve",
        "twenty", "two", "un", "under", "until", "up", "upon", "us",
        "very", "via", "was", "we", "well", "were", "what", "whatever",
        "when", "whence", "whenever", "where", "whereafter", "whereas",
        "whereby", "wherein", "whereupon", "wherever", "whether",
        "which", "while", "whither", "who", "whoever", "whole", "whom",
        "whose", "why", "will", "with", "within", "without", "would",
        "yet", "you", "your", "yours", "yourself", "yourselves", "the",
    ),
)

register_setting(
    name="TEMPLATE_ACCESSIBLE_SETTINGS",
    description=_("Sequence of setting names available within templates."),
    editable=False,
    default=(
        "BLOG_BITLY_USER", "BLOG_BITLY_KEY",
        "COMMENTS_DISQUS_SHORTNAME", "COMMENTS_NUM_LATEST",
        "COMMENTS_DISQUS_API_PUBLIC_KEY", "COMMENTS_DISQUS_API_SECRET_KEY",
        "CONTENT_MEDIA_URL", "DEV_SERVER", "FORMS_USE_HTML5",
        "GRAPPELLI_INSTALLED", "GOOGLE_ANALYTICS_ID",
        "PAGES_MENU_SHOW_ALL", "SITE_TITLE", "SITE_TAGLINE",
        "RATINGS_MAX",
    ),
)

# The following settings are defined here for documentation purposes
# as this file is used to auto-generate the documentation for all
# available settings. They are Mezzanine specific, but their values
# are *always* overridden by the project's settings or local_settings
# modules, so the default values defined here will never be used.

register_setting(
    name="USE_SOUTH",
    description=_("If ``True``, the south application will be "
        "automatically added to the ``INSTALLED_APPS`` setting."),
    editable=False,
    default=True,
)
