
import os.path

from django.utils.functional import lazy
from django.utils.translation import ugettext as _
from django.conf import settings


def setting(name="", editable=False, description="", default=None):
    """
    Settings that can be edited via the admin. Uses Django's ``lazy`` util 
    to allow setting to be lazily loaded from the ``Setting`` model. 
    """
    globals()[name] = {"description": description, "editable": editable, 
        "default": getattr(settings, "MEZZANINE_%s" % name, default)}
    

setting(
    name="ADMIN_MENU_ORDER",
    description="Controls the ordering and grouping of the admin menu.",
    editable=False,
    default=(
        (_("Content"), ("pages.Page", "blog.BlogPost", "blog.Comment",)),
        (_("Site"), ("sites.Site", "redirects.Redirect", "settings.Setting")),
        (_("Users"), ("auth.User", "auth.Group",)),
    ),
)

setting(
    name="ADMIN_REMOVAL",
    description="Unregister these models from the admin.",
    editable=False,
    default=(),
)

setting(
    name="BLOG_BITLY_USER",
    description="Username for bit.ly URL shortening service.",
    editable=True, 
    default="",
)

setting(
    name="BLOG_BITLY_KEY",
    description="Key for bit.ly URL shortening service.",
    editable=True, 
    default="",
)

setting(
    name="BLOG_POST_PER_PAGE", 
    description="Number of blog posts to show on a blog listing page.",
    editable=True,
    default=5,
)

setting(
    name="BLOG_POST_MAX_PAGING_LINKS", 
    description="Max number of paging links to show on a blog listing page.",
    editable=True, 
    default=10,
)

setting(
    name="BLOG_SLUG", 
    description="Slug of the page object for the blog.",
    editable=False,
    default="blog",
)

setting(
    name="COMMENTS_DISQUS_SHORTNAME", 
    description="Username for the http://disqus.com comments service.",
    editable=True, 
    default="",
)

setting(
    name="COMMENTS_DISQUS_KEY", 
    description="API key for the http://disqus.com comments service.",
    editable=True, 
    default="",
)

setting(
    name="COMMENTS_DEFAULT_APPROVED", 
    description="If True, the built-in comments are approved by default.",
    editable=True, 
    default=True,
)

setting(
    name="COMMENTS_NUM_LATEST", 
    description="Number of latest comments to show in the admin dashboard.",
    editable=True, 
    default=5,
)

setting(
    name="COMMENTS_UNAPPROVED_VISIBLE", 
    description="If True, unapproved comments will have a placeholder "
        "visible on the site with a 'waiting for approval' or "
        "'comment removed' message based on the workflow around the "
        "``MEZZANINE_COMMENTS_DEFAULT_APPROVED`` setting - if True then "
        "the former message is used, if False then the latter.",
    editable=True, 
    default=True,
)

setting(
    name="CONTENT_MEDIA_PATH", 
    description="Absolute path to Mezzanine's internal media files.",
    editable=False,
    default=os.path.join(os.path.dirname(__file__), "..", "core", "media"),
)

setting(
    name="CONTENT_MEDIA_URL", 
    description="URL prefix for serving Mezzanine's internal media files.",
    editable=False,
    default="/content_media/",
)

setting(
    name="DASHBOARD_TAGS", 
    description="A three item sequence, each containing a sequence of "
        "template tags used to render the admin dashboard.",
    editable=False,
    default=(
        ("blog_tags.quick_blog", "mezzanine_tags.app_list"),
        ("blog_tags.recent_comments",),
        ("mezzanine_tags.recent_actions",),
    ),
)

setting(
    name="FORMS_FIELD_MAX_LENGTH", 
    description="Max length allowed for field values in the forms app.",
    editable=False,
    default=2000,
)

setting(
    name="FORMS_LABEL_MAX_LENGTH",
    description="Max length allowed for field labels in the forms app.",
    editable=False,
    default=200,
)

setting(
    name="FORMS_UPLOAD_ROOT",
    description="Absolute path for storing file uploads to for the forms app.",
    editable=False,
    default="",
)

setting(
    name="GOOGLE_ANALYTICS_ID", 
    editable=True, 
    description="Google Analytics ID (http://www.google.com/analytics/)",
    default="",
)

setting(
    name="MOBILE_USER_AGENTS",
    description="Strings to search for in user agent when testing for a "
        "mobile device.",
    editable=False, 
    default=(
        "2.0 MMP", "240x320", "400X240", "AvantGo", "BlackBerry", 
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
        "Nokia5800",
    ),
)

setting(
    name="TAG_CLOUD_SIZES", 
    description="Number of different sizes for tags when shown as a cloud.",
    editable=True, 
    default=4,
)

setting(
    name="PAGES_MENU_SHOW_ALL", 
    description="If True, the pages menu will show all levels of navigation, "
        "otherwise child pages are only shown when viewing the parent page.",
    editable=False,
    default=True,
)

setting(
    name="SEARCH_PER_PAGE",
    description="Number of results to show in the search results page.",
    editable=True, 
    default=10,
)

setting(
    name="SEARCH_MAX_PAGING_LINKS", 
    description="Max number of page links to show in the search results page.",
    editable=True,
    default=10,
)

setting(
    name="STOP_WORDS", 
    description="List of words which will be stripped from search queries.",
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

setting(
    name="TINYMCE_URL", 
    description="URL prefix for serving Tiny MCE files.",
    editable=False,
    default="%s/tinymce" % settings.ADMIN_MEDIA_PREFIX,
)
