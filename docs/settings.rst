.. THIS DOCUMENT IS AUTO GENERATED VIA conf.py

``ACCOUNTS_MIN_PASSWORD_LENGTH``
--------------------------------

Minimum length for passwords

Default: ``6``

``ACCOUNTS_PROFILE_FORM_EXCLUDE_FIELDS``
----------------------------------------

List of fields to exclude from the profile form.

Default: ``()``

``ACCOUNTS_VERIFICATION_REQUIRED``
----------------------------------

If ``True``, when users create an account, they will be sent an email with a verification link, which they must click to enable their account.

Default: ``False``

``ADMIN_MENU_ORDER``
--------------------

Controls the ordering and grouping of the admin menu.

Default: ``((u'Content', ('pages.Page', 'blog.BlogPost', 'generic.ThreadedComment', (u'Media Library', 'fb_browse'))), (u'Site', ('sites.Site', 'redirects.Redirect', 'conf.Setting')), (u'Users', ('auth.User', 'auth.Group')))``

``ADMIN_REMOVAL``
-----------------

Unregister these models from the admin.

Default: ``()``

``AKISMET_API_KEY``
-------------------

Key for `http://akismet.com <http://akismet.com>`_ spam filtering service. Used for filtering comments and forms.

Default: ``''``

``BLOG_BITLY_KEY``
------------------

Key for `http://bit.ly <http://bit.ly>`_ URL shortening service.

Default: ``''``

``BLOG_BITLY_USER``
-------------------

Username for `http://bit.ly <http://bit.ly>`_ URL shortening service.

Default: ``''``

``BLOG_POST_PER_PAGE``
----------------------

Number of blog posts shown on a blog listing page.

Default: ``5``

``BLOG_SLUG``
-------------

Slug of the page object for the blog.

Default: ``'blog'``

``BLOG_URLS_USE_DATE``
----------------------

If ``True``, URLs for blog post include the month and year. Eg: /blog/yyyy/mm/slug/

Default: ``False``

``BLOG_USE_FEATURED_IMAGE``
---------------------------

Enable featured images in blog posts

Default: ``False``

``COMMENTS_ACCOUNT_REQUIRED``
-----------------------------

If ``True``, users must log in to comment.

Default: ``False``

``COMMENTS_DEFAULT_APPROVED``
-----------------------------

If ``True``, built-in comments are approved by default.

Default: ``True``

``COMMENTS_DISQUS_API_PUBLIC_KEY``
----------------------------------

Public key for `http://disqus.com <http://disqus.com>`_ developer API

Default: ``''``

``COMMENTS_DISQUS_API_SECRET_KEY``
----------------------------------

Secret key for `http://disqus.com <http://disqus.com>`_ developer API

Default: ``''``

``COMMENTS_DISQUS_SHORTNAME``
-----------------------------

Shortname for the `http://disqus.com <http://disqus.com>`_ comments service.

Default: ``''``

``COMMENTS_NUM_LATEST``
-----------------------

Number of latest comments shown in the admin dashboard.

Default: ``5``

``COMMENTS_REMOVED_VISIBLE``
----------------------------

If ``True``, comments that have ``removed`` checked will still be displayed, but replaced with a ``removed`` message.

Default: ``True``

``COMMENTS_UNAPPROVED_VISIBLE``
-------------------------------

If ``True``, comments that have ``is_public`` unchecked will still be displayed, but replaced with a ``waiting to be approved`` message.

Default: ``True``

``DASHBOARD_TAGS``
------------------

A three item sequence, each containing a sequence of template tags used to render the admin dashboard.

Default: ``(('blog_tags.quick_blog', 'mezzanine_tags.app_list'), ('comment_tags.recent_comments',), ('mezzanine_tags.recent_actions',))``

``DEVICE_DEFAULT``
------------------

Device specific template sub-directory to use as the default device.

Default: ``''``

``DEVICE_USER_AGENTS``
----------------------

Mapping of device specific template sub-directory names to the sequence of strings that may be found in their user agents.

Default: ``(('mobile', ('2.0 MMP', '240x320', '400X240', 'AvantGo', 'BlackBerry', 'Blazer', 'Cellphone', 'Danger', 'DoCoMo', 'Elaine/3.0', 'EudoraWeb', 'Googlebot-Mobile', 'hiptop', 'IEMobile', 'KYOCERA/WX310K', 'LG/U990', 'MIDP-2.', 'MMEF20', 'MOT-V', 'NetFront', 'Newt', 'Nintendo Wii', 'Nitro', 'Nokia', 'Opera Mini', 'Palm', 'PlayStation Portable', 'portalmmm', 'Proxinet', 'ProxiNet', 'SHARP-TQ-GX10', 'SHG-i900', 'Small', 'SonyEricsson', 'Symbian OS', 'SymbianOS', 'TS21i-10', 'UP.Browser', 'UP.Link', 'webOS', 'Windows CE', 'WinWAP', 'YahooSeeker/M1A1-R2D2', 'iPhone', 'iPod', 'Android', 'BlackBerry9530', 'LG-TU915 Obigo', 'LGE VX', 'webOS', 'Nokia5800')),)``

``EXTRA_MODEL_FIELDS``
----------------------

A sequence of fields that will be injected into Mezzanine's (or any library's) models. Each item in the sequence is a four item sequence. The first two items are the dotted path to the model and its field name to be added, and the dotted path to the field class to use for the field. The third and fourth items are a sequence of positional args and a dictionary of keyword args, to use when creating the field instance. When specifying the field class, the path ``django.models.db.`` can be omitted for regular Django model fields.

Default: ``()``

``FORMS_CSV_DELIMITER``
-----------------------

Char to use as a field delimiter when exporting form responses as CSV.

Default: ``','``

``FORMS_DISABLE_SEND_FROM_EMAIL_FIELD``
---------------------------------------

If ``True``, emails sent to extra recipients for form submissions won't be sent from an address taken from one of the form's email fields.

Default: ``False``

``FORMS_FIELD_MAX_LENGTH``
--------------------------

Max length allowed for field values in the forms app.

Default: ``2000``

``FORMS_LABEL_MAX_LENGTH``
--------------------------

Max length allowed for field labels in the forms app.

Default: ``200``

``FORMS_UPLOAD_ROOT``
---------------------

Absolute path for storing file uploads for the forms app.

Default: ``''``

``FORMS_USE_HTML5``
-------------------

If ``True``, website forms will use HTML5 features.

Default: ``False``

``GOOGLE_ANALYTICS_ID``
-----------------------

Google Analytics ID (`http://www.google.com/analytics/ <http://www.google.com/analytics/>`_)

Default: ``''``

``HOST_THEMES``
---------------

A sequence mapping host names to themes, allowing different templates to be served per HTTP hosts Each item in the sequence is a two item sequence, containing a host such as ``othersite.example.com``, and the name of an importable Python package for the theme. If the host is matched for a request, the templates directory inside the theme package will be first searched when loading templates.

Default: ``()``

``JQUERY_FILENAME``
-------------------

Name of the jQuery file found in mezzanine/core/static/mezzanine/js/

Default: ``'jquery-1.7.1.min.js'``

``MAX_PAGING_LINKS``
--------------------

Max number of paging links to display when paginating.

Default: ``10``

``PAGES_MENU_SHOW_ALL``
-----------------------

If ``True``, the pages menu will show all levels of navigation, otherwise child pages are only shown when viewing the parent page.

Default: ``True``

``RATINGS_MAX``
---------------

Max value for a rating.

Default: ``5``

``RATINGS_MIN``
---------------

Min value for a rating.

Default: ``1``

``RICHTEXT_ALLOWED_ATTRIBUTES``
-------------------------------

List of HTML attributes that won't be stripped from ``RichTextField`` instances.

Default: ``('abbr', 'accept', 'accept-charset', 'accesskey', 'action', 'align', 'alt', 'axis', 'border', 'cellpadding', 'cellspacing', 'char', 'charoff', 'charset', 'checked', 'cite', 'class', 'clear', 'cols', 'colspan', 'color', 'compact', 'coords', 'datetime', 'dir', 'disabled', 'enctype', 'for', 'frame', 'headers', 'height', 'href', 'hreflang', 'hspace', 'id', 'ismap', 'label', 'lang', 'longdesc', 'maxlength', 'media', 'method', 'multiple', 'name', 'nohref', 'noshade', 'nowrap', 'prompt', 'readonly', 'rel', 'rev', 'rows', 'rowspan', 'rules', 'scope', 'selected', 'shape', 'size', 'span', 'src', 'start', 'style', 'summary', 'tabindex', 'target', 'title', 'type', 'usemap', 'valign', 'value', 'vspace', 'width', 'xml:lang')``

``RICHTEXT_ALLOWED_TAGS``
-------------------------

List of HTML tags that won't be stripped from ``RichTextField`` instances.

Default: ``('a', 'abbr', 'acronym', 'address', 'area', 'b', 'bdo', 'big', 'blockquote', 'br', 'button', 'caption', 'center', 'cite', 'code', 'col', 'colgroup', 'dd', 'del', 'dfn', 'dir', 'div', 'dl', 'dt', 'em', 'fieldset', 'font', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'input', 'ins', 'kbd', 'label', 'legend', 'li', 'map', 'menu', 'ol', 'optgroup', 'option', 'p', 'pre', 'q', 's', 'samp', 'select', 'small', 'span', 'strike', 'strong', 'sub', 'sup', 'table', 'tbody', 'td', 'textarea', 'tfoot', 'th', 'thead', 'tr', 'tt', 'u', 'ul', 'var', 'wbr')``

``RICHTEXT_FILTER``
-------------------

Dotted path to the function to call on a ``RichTextField`` value before it is rendered to the template.

Default: ``None``

``RICHTEXT_FILTER_LEVEL``
-------------------------

*Do not change this setting unless you know what you're doing.*

When content is saved in a Rich Text (WYSIWYG) field, unsafe HTML tags and attributes are stripped from the content to protect against staff members intentionally adding code that could be used to cause problems, such as changing their account to a super-user with full access to the system.

This setting allows you to change the level of filtering that occurs. Setting it to low will allow certain extra tags to be permitted, such as those required for embedding video. While these tags are not the main candidates for users adding malicious code, they are still considered dangerous and could potentially be mis-used by a particularly technical user, and so are filtered out when the filtering level is set to high.

Setting the filtering level to no filtering, will disable all filtering, and allow any code to be entered by staff members, including script tags.

Choices: High: ``1``, Low (allows video, iframe, Flash, etc): ``2``, No filtering: ``3``


Default: ``1``

``RICHTEXT_WIDGET_CLASS``
-------------------------

Dotted package path and class name of the widget to use for the ``RichTextField``.

Default: ``'mezzanine.core.forms.TinyMceWidget'``

``SEARCH_PER_PAGE``
-------------------

Number of results shown in the search results page.

Default: ``10``

``SITE_TAGLINE``
----------------

A tag line that will appear at the top of all pages.

Default: ``u'An open source content management platform.'``

``SITE_TITLE``
--------------

Title that will display at the top of the site, and be appended to the content of the HTML title tags on every page.

Default: ``'Mezzanine'``

``SLUGIFY``
-----------

Dotted Python path to the callable for converting strings into URL slugs. Defaults to ``mezzanine.utils.urls.slugify_unicode`` which allows for non-ascii URLS. Change to ``django.template.defaultfilters.slugify`` to use Django's slugify function, or something of your own if required.

Default: ``'mezzanine.utils.urls.slugify_unicode'``

``SSL_ENABLED``
---------------

If ``True``, users will be automatically redirected to HTTPS for the URLs specified by the ``SSL_FORCE_URL_PREFIXES`` setting.

Default: ``False``

``SSL_FORCE_HOST``
------------------

Host name that the site should always be accessed via that matches the SSL certificate.

Default: ``''``

``SSL_FORCE_URL_PREFIXES``
--------------------------

Sequence of URL prefixes that will be forced to run over SSL when ``SSL_ENABLED`` is ``True``. i.e. ('/admin', '/example') would force all URLs beginning with /admin or /example to run over SSL.

Default: ``('/admin', '/account')``

``STOP_WORDS``
--------------

List of words which will be stripped from search queries.

Default: ``('a', 'about', 'above', 'above', 'across', 'after', 'afterwards', 'again', 'against', 'all', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'am', 'among', 'amongst', 'amoungst', 'amount', 'an', 'and', 'another', 'any', 'anyhow', 'anyone', 'anything', 'anyway', 'anywhere', 'are', 'around', 'as', 'at', 'back', 'be', 'became', 'because', 'become', 'becomes', 'becoming', 'been', 'before', 'beforehand', 'behind', 'being', 'below', 'beside', 'besides', 'between', 'beyond', 'bill', 'both', 'bottom', 'but', 'by', 'call', 'can', 'cannot', 'cant', 'co', 'con', 'could', 'couldnt', 'cry', 'de', 'describe', 'detail', 'do', 'done', 'down', 'due', 'during', 'each', 'eg', 'eight', 'either', 'eleven', 'else', 'elsewhere', 'empty', 'enough', 'etc', 'even', 'ever', 'every', 'everyone', 'everything', 'everywhere', 'except', 'few', 'fifteen', 'fify', 'fill', 'find', 'fire', 'first', 'five', 'for', 'former', 'formerly', 'forty', 'found', 'four', 'from', 'front', 'full', 'further', 'get', 'give', 'go', 'had', 'has', 'hasnt', 'have', 'he', 'hence', 'her', 'here', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'however', 'hundred', 'ie', 'if', 'in', 'inc', 'indeed', 'interest', 'into', 'is', 'it', 'its', 'itself', 'keep', 'last', 'latter', 'latterly', 'least', 'less', 'ltd', 'made', 'many', 'may', 'me', 'meanwhile', 'might', 'mill', 'mine', 'more', 'moreover', 'most', 'mostly', 'move', 'much', 'must', 'my', 'myself', 'name', 'namely', 'neither', 'never', 'nevertheless', 'next', 'nine', 'no', 'nobody', 'none', 'noone', 'nor', 'not', 'nothing', 'now', 'nowhere', 'of', 'off', 'often', 'on', 'once', 'one', 'only', 'onto', 'or', 'other', 'others', 'otherwise', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'part', 'per', 'perhaps', 'please', 'put', 'rather', 're', 'same', 'see', 'seem', 'seemed', 'seeming', 'seems', 'serious', 'several', 'she', 'should', 'show', 'side', 'since', 'sincere', 'six', 'sixty', 'so', 'some', 'somehow', 'someone', 'something', 'sometime', 'sometimes', 'somewhere', 'still', 'such', 'system', 'take', 'ten', 'than', 'that', 'the', 'their', 'them', 'themselves', 'then', 'thence', 'there', 'thereafter', 'thereby', 'therefore', 'therein', 'thereupon', 'these', 'they', 'thickv', 'thin', 'third', 'this', 'those', 'though', 'three', 'through', 'throughout', 'thru', 'thus', 'to', 'together', 'too', 'top', 'toward', 'towards', 'twelve', 'twenty', 'two', 'un', 'under', 'until', 'up', 'upon', 'us', 'very', 'via', 'was', 'we', 'well', 'were', 'what', 'whatever', 'when', 'whence', 'whenever', 'where', 'whereafter', 'whereas', 'whereby', 'wherein', 'whereupon', 'wherever', 'whether', 'which', 'while', 'whither', 'who', 'whoever', 'whole', 'whom', 'whose', 'why', 'will', 'with', 'within', 'without', 'would', 'yet', 'you', 'your', 'yours', 'yourself', 'yourselves', 'the')``

``TAG_CLOUD_SIZES``
-------------------

Number of different sizes for tags when shown as a cloud.

Default: ``4``

``TEMPLATE_ACCESSIBLE_SETTINGS``
--------------------------------

Sequence of setting names available within templates.

Default: ``('ACCOUNTS_VERIFICATION_REQUIRED', 'ADMIN_MEDIA_PREFIX', 'BLOG_BITLY_USER', 'BLOG_BITLY_KEY', 'COMMENTS_DISQUS_SHORTNAME', 'COMMENTS_NUM_LATEST', 'COMMENTS_DISQUS_API_PUBLIC_KEY', 'COMMENTS_DISQUS_API_SECRET_KEY', 'DEV_SERVER', 'FORMS_USE_HTML5', 'GRAPPELLI_INSTALLED', 'GOOGLE_ANALYTICS_ID', 'JQUERY_FILENAME', 'LOGIN_URL', 'LOGOUT_URL', 'PAGES_MENU_SHOW_ALL', 'SITE_TITLE', 'SITE_TAGLINE', 'RATINGS_MAX')``

``THUMBNAILS_DIR_NAME``
-----------------------

Directory name to store thumbnails in, that will be created relative to the original image's directory.

Default: ``'.thumbnails'``

``TINYMCE_SETUP_JS``
--------------------

URL for the JavaScript file (relative to ``STATIC_URL``) that handles configuring TinyMCE when the default ``RICHTEXT_WIDGET_CLASS`` is used.

Default: ``'mezzanine/js/tinymce_setup.js'``

``USE_SOUTH``
-------------

If ``True``, the south application will be automatically added to the ``INSTALLED_APPS`` setting.

Default: ``True``