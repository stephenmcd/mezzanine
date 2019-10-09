.. THIS DOCUMENT IS AUTO GENERATED VIA conf.py

.. _ACCOUNTS_APPROVAL_EMAILS:

``ACCOUNTS_APPROVAL_EMAILS``
----------------------------

A comma separated list of email addresses that will receive an email notification each time a new account is created that requires approval.

Default: ``''``

.. _ACCOUNTS_APPROVAL_REQUIRED:

``ACCOUNTS_APPROVAL_REQUIRED``
------------------------------

If ``True``, when users create an account, they will not be enabled by default and a staff member will need to activate their account in the admin interface.

Default: ``False``

.. _ACCOUNTS_MIN_PASSWORD_LENGTH:

``ACCOUNTS_MIN_PASSWORD_LENGTH``
--------------------------------

Minimum length for passwords

Default: ``6``

.. _ACCOUNTS_NO_USERNAME:

``ACCOUNTS_NO_USERNAME``
------------------------

If ``True``, the username field will be excluded from sign up and account update forms.

Default: ``False``

.. _ACCOUNTS_PROFILE_FORM_CLASS:

``ACCOUNTS_PROFILE_FORM_CLASS``
-------------------------------

Dotted package path and class name of profile form to use for users signing up and updating their profile, when ``mezzanine.accounts`` is installed.

Default: ``'mezzanine.accounts.forms.ProfileForm'``

.. _ACCOUNTS_PROFILE_FORM_EXCLUDE_FIELDS:

``ACCOUNTS_PROFILE_FORM_EXCLUDE_FIELDS``
----------------------------------------

List of fields to exclude from the profile form.

Default: ``()``

.. _ACCOUNTS_PROFILE_MODEL:

``ACCOUNTS_PROFILE_MODEL``
--------------------------

String in the form `app_label.model_name` for the model used for account profiles.

Default: ``None``

.. _ACCOUNTS_PROFILE_VIEWS_ENABLED:

``ACCOUNTS_PROFILE_VIEWS_ENABLED``
----------------------------------

If ``True``, users will have their own public profile pages.

Default: ``False``

.. _ACCOUNTS_VERIFICATION_REQUIRED:

``ACCOUNTS_VERIFICATION_REQUIRED``
----------------------------------

If ``True``, when users create an account, they will be sent an email with a verification link, which they must click to enable their account.

Default: ``False``

.. _ADD_PAGE_ORDER:

``ADD_PAGE_ORDER``
------------------

A sequence of ``Page`` subclasses in the format ``app_label.model_name``, that controls the ordering of items in the select drop-down for adding new pages within the admin page tree interface.

Default: ``('pages.RichTextPage',)``

.. _ADMIN_MENU_COLLAPSED:

``ADMIN_MENU_COLLAPSED``
------------------------

Controls whether or not the left-hand admin menu is collapsed by default.

Default: ``False``

.. _ADMIN_MENU_ORDER:

``ADMIN_MENU_ORDER``
--------------------

Controls the ordering and grouping of the admin menu.

Default: ``(('Content', ('pages.Page', 'blog.BlogPost', 'generic.ThreadedComment', ('Media Library', 'media-library'))), ('Site', ('sites.Site', 'redirects.Redirect', 'conf.Setting')), ('Users', ('auth.User', 'auth.Group')))``

.. _ADMIN_REMOVAL:

``ADMIN_REMOVAL``
-----------------

A sequence of Python dotted paths to models (eg: ``['mezzanine.blog.models.BlogPost',]``) that should be removed from the admin.

Default: ``()``

.. _ADMIN_THUMB_SIZE:

``ADMIN_THUMB_SIZE``
--------------------

Size of thumbnail previews for image fields in the admin interface.

Default: ``'24x24'``

.. _AKISMET_API_KEY:

``AKISMET_API_KEY``
-------------------

Key for `http://akismet.com <http://akismet.com>`_ spam filtering service. Used for filtering comments and forms.

Default: ``''``

.. _BITLY_ACCESS_TOKEN:

``BITLY_ACCESS_TOKEN``
----------------------

Access token for `http://bit.ly <http://bit.ly>`_ URL shortening service.

Default: ``''``

.. _BLOG_POST_PER_PAGE:

``BLOG_POST_PER_PAGE``
----------------------

Number of blog posts shown on a blog listing page.

Default: ``5``

.. _BLOG_RSS_LIMIT:

``BLOG_RSS_LIMIT``
------------------

Number of most recent blog posts shown in the RSS feed. Set to ``None`` to display all blog posts in the RSS feed.

Default: ``20``

.. _BLOG_SLUG:

``BLOG_SLUG``
-------------

Slug of the page object for the blog.

Default: ``'blog'``

.. _BLOG_URLS_DATE_FORMAT:

``BLOG_URLS_DATE_FORMAT``
-------------------------

A string containing the value ``year``, ``month``, or ``day``, which controls the granularity of the date portion in the URL for each blog post. Eg: ``year`` will define URLs in the format /blog/yyyy/slug/, while ``day`` will define URLs with the format /blog/yyyy/mm/dd/slug/. An empty string means the URLs will only use the slug, and not contain any portion of the date at all.

Default: ``''``

.. _BLOG_USE_FEATURED_IMAGE:

``BLOG_USE_FEATURED_IMAGE``
---------------------------

Enable featured images in blog posts

Default: ``False``

.. _CACHE_SET_DELAY_SECONDS:

``CACHE_SET_DELAY_SECONDS``
---------------------------

Mezzanine's caching uses a technique know as mint caching. This is where the requested expiry for a cache entry is stored with the cache entry in cache, and the real expiry used has the ``CACHE_SET_DELAY`` added to it. Then on a cache get, the store expiry is checked, and if it has passed, the cache entry is set again, and no entry is returned. This tries to ensure that cache misses never occur, and if many clients were to get a cache miss at once, only one would actually need to re-generated the cache entry.

Default: ``30``

.. _COMMENTS_ACCOUNT_REQUIRED:

``COMMENTS_ACCOUNT_REQUIRED``
-----------------------------

If ``True``, users must log in to comment.

Default: ``False``

.. _COMMENTS_DEFAULT_APPROVED:

``COMMENTS_DEFAULT_APPROVED``
-----------------------------

If ``True``, built-in comments are approved by default.

Default: ``True``

.. _COMMENTS_DISQUS_API_PUBLIC_KEY:

``COMMENTS_DISQUS_API_PUBLIC_KEY``
----------------------------------

Public key for `http://disqus.com <http://disqus.com>`_ developer API

Default: ``''``

.. _COMMENTS_DISQUS_API_SECRET_KEY:

``COMMENTS_DISQUS_API_SECRET_KEY``
----------------------------------

Secret key for `http://disqus.com <http://disqus.com>`_ developer API

Default: ``''``

.. _COMMENTS_DISQUS_SHORTNAME:

``COMMENTS_DISQUS_SHORTNAME``
-----------------------------

Shortname for the `http://disqus.com <http://disqus.com>`_ comments service.

Default: ``''``

.. _COMMENTS_NOTIFICATION_EMAILS:

``COMMENTS_NOTIFICATION_EMAILS``
--------------------------------

A comma separated list of email addresses that will receive an email notification each time a new comment is posted on the site.

Default: ``''``

.. _COMMENTS_NUM_LATEST:

``COMMENTS_NUM_LATEST``
-----------------------

Number of latest comments shown in the admin dashboard.

Default: ``5``

.. _COMMENTS_REMOVED_VISIBLE:

``COMMENTS_REMOVED_VISIBLE``
----------------------------

If ``True``, comments that have ``removed`` checked will still be displayed, but replaced with a ``removed`` message.

Default: ``True``

.. _COMMENTS_UNAPPROVED_VISIBLE:

``COMMENTS_UNAPPROVED_VISIBLE``
-------------------------------

If ``True``, comments that have ``is_public`` unchecked will still be displayed, but replaced with a ``waiting to be approved`` message.

Default: ``True``

.. _COMMENTS_USE_RATINGS:

``COMMENTS_USE_RATINGS``
------------------------

If ``True``, comments can be rated.

Default: ``True``

.. _COMMENT_FILTER:

``COMMENT_FILTER``
------------------

Dotted path to the function to call on a comment's value before it is rendered to the template.

Default: ``None``

.. _COMMENT_FORM_CLASS:

``COMMENT_FORM_CLASS``
----------------------

The form class to use for adding new comments.

Default: ``'mezzanine.generic.forms.ThreadedCommentForm'``

.. _DASHBOARD_TAGS:

``DASHBOARD_TAGS``
------------------

A three item sequence, each containing a sequence of template tags used to render the admin dashboard.

Default: ``(('blog_tags.quick_blog', 'mezzanine_tags.app_list'), ('comment_tags.recent_comments',), ('mezzanine_tags.recent_actions',))``

.. _EMAIL_FAIL_SILENTLY:

``EMAIL_FAIL_SILENTLY``
-----------------------

If ``True``, failures to send email will happen silently, otherwise an exception is raised. Defaults to ``settings.DEBUG``.

Default: ``False``

.. _EXTRA_MODEL_FIELDS:

``EXTRA_MODEL_FIELDS``
----------------------

A sequence of fields that will be injected into Mezzanine's (or any library's) models. Each item in the sequence is a four item sequence. The first two items are the dotted path to the model and its field name to be added, and the dotted path to the field class to use for the field. The third and fourth items are a sequence of positional args and a dictionary of keyword args, to use when creating the field instance. When specifying the field class, the path ``django.models.db.`` can be omitted for regular Django model fields.

Default: ``()``

.. _FORMS_CSV_DELIMITER:

``FORMS_CSV_DELIMITER``
-----------------------

Char to use as a field delimiter when exporting form responses as CSV.

Default: ``','``

.. _FORMS_EXTRA_FIELDS:

``FORMS_EXTRA_FIELDS``
----------------------

Extra field types for the forms app. Should contain a sequence of three-item sequences, each containing the ID, dotted import path for the field class, and field name, for each custom field type. The ID is simply a numeric constant for the field, but cannot be a value already used, so choose a high number such as 100 or greater to avoid conflicts.

Default: ``()``

.. _FORMS_EXTRA_WIDGETS:

``FORMS_EXTRA_WIDGETS``
-----------------------

Extra field widgets for the forms app. Should contain a sequence of two-item sequences, each containing an existing ID for a form field, and a dotted import path for the widget class.

Default: ``()``

.. _FORMS_FIELD_MAX_LENGTH:

``FORMS_FIELD_MAX_LENGTH``
--------------------------

Max length allowed for field values in the forms app.

Default: ``2000``

.. _FORMS_UPLOAD_ROOT:

``FORMS_UPLOAD_ROOT``
---------------------

Absolute path for storing file uploads for the forms app.

Default: ``''``

.. _FORMS_USE_HTML5:

``FORMS_USE_HTML5``
-------------------

If ``True``, website forms will use HTML5 features.

Default: ``False``

.. _GOOGLE_ANALYTICS_ID:

``GOOGLE_ANALYTICS_ID``
-----------------------

Google Analytics ID (`http://www.google.com/analytics/ <http://www.google.com/analytics/>`_)

Default: ``''``

.. _HOST_THEMES:

``HOST_THEMES``
---------------

A sequence mapping host names to themes, allowing different templates to be served per HTTP host. Each item in the sequence is a two item sequence, containing a host such as ``othersite.example.com``, and the name of an importable Python package for the theme. If the host is matched for a request, the templates directory inside the theme package will be first searched when loading templates.

Default: ``()``

.. _INLINE_EDITING_ENABLED:

``INLINE_EDITING_ENABLED``
--------------------------

If ``True``, front-end inline editing will be enabled.

Default: ``True``

.. _JQUERY_FILENAME:

``JQUERY_FILENAME``
-------------------

Name of the jQuery file found in mezzanine/core/static/mezzanine/js/

Default: ``'jquery-1.8.3.min.js'``

.. _JQUERY_UI_FILENAME:

``JQUERY_UI_FILENAME``
----------------------

Name of the jQuery UI file found in mezzanine/core/static/mezzanine/js/

Default: ``'jquery-ui-1.8.24.min.js'``

.. _MAX_PAGING_LINKS:

``MAX_PAGING_LINKS``
--------------------

Max number of paging links to display when paginating.

Default: ``10``

.. _MEDIA_LIBRARY_PER_SITE:

``MEDIA_LIBRARY_PER_SITE``
--------------------------

If ``True``, each site will use its own directory within the filebrowser media library.

Default: ``False``

.. _NEVERCACHE_KEY:

``NEVERCACHE_KEY``
------------------

Unique random string like ``SECRET_KEY``, but used for two-phased cache responses. Like ``SECRET_KEY``, should be automatically generated by the ``mezzanine-project`` command.

Default: ``''``

.. _OWNABLE_MODELS_ALL_EDITABLE:

``OWNABLE_MODELS_ALL_EDITABLE``
-------------------------------

Models that subclass ``Ownable`` and use the ``OwnableAdmin`` have their admin change-list records filtered down to records owned by the current user. This setting contains a sequence of models in the format ``app_label.object_name``, that when subclassing ``Ownable``, will still show all records in the admin change-list interface, regardless of the current user.

Default: ``()``

.. _PAGES_PUBLISHED_INCLUDE_LOGIN_REQUIRED:

``PAGES_PUBLISHED_INCLUDE_LOGIN_REQUIRED``
------------------------------------------

If ``True``, pages with ``login_required`` checked will still be listed in menus and search results, for unauthenticated users. Regardless of this setting, when an unauthenticated user accesses a page with ``login_required`` checked, they'll be redirected to the login page.

Default: ``False``

.. _PAGE_MENU_TEMPLATES:

``PAGE_MENU_TEMPLATES``
-----------------------

A sequence of templates used by the ``page_menu`` template tag. Each item in the sequence is a three item sequence, containing a unique ID for the template, a label for the template, and the template path. These templates are then available for selection when editing which menus a page should appear in. Note that if a menu template is used that doesn't appear in this setting, all pages will appear in it.

Default: ``((1, 'Top navigation bar', 'pages/menus/dropdown.html'), (2, 'Left-hand tree', 'pages/menus/tree.html'), (3, 'Footer', 'pages/menus/footer.html'))``

.. _PAGE_MENU_TEMPLATES_DEFAULT:

``PAGE_MENU_TEMPLATES_DEFAULT``
-------------------------------

A sequence of IDs from the ``PAGE_MENU_TEMPLATES`` setting that defines the default menu templates selected when creating new pages. By default all menu templates are selected. Set this setting to an empty sequence to have no templates selected by default.

Default: ``None``

.. _RATINGS_ACCOUNT_REQUIRED:

``RATINGS_ACCOUNT_REQUIRED``
----------------------------

If ``True``, users must log in to rate content such as blog posts and comments.

Default: ``False``

.. _RATINGS_RANGE:

``RATINGS_RANGE``
-----------------

A sequence of integers that are valid ratings.

Default: ``[1, 2, 3, 4, 5]``

.. _RICHTEXT_ALLOWED_ATTRIBUTES:

``RICHTEXT_ALLOWED_ATTRIBUTES``
-------------------------------

List of HTML attributes that won't be stripped from ``RichTextField`` instances.

Default: ``('abbr', 'accept', 'accept-charset', 'accesskey', 'action', 'align', 'alt', 'axis', 'border', 'cellpadding', 'cellspacing', 'char', 'charoff', 'charset', 'checked', 'cite', 'class', 'clear', 'cols', 'colspan', 'color', 'compact', 'coords', 'datetime', 'dir', 'disabled', 'enctype', 'for', 'frame', 'headers', 'height', 'href', 'hreflang', 'hspace', 'id', 'ismap', 'label', 'lang', 'longdesc', 'maxlength', 'media', 'method', 'multiple', 'name', 'nohref', 'noshade', 'nowrap', 'prompt', 'readonly', 'rel', 'rev', 'rows', 'rowspan', 'rules', 'scope', 'selected', 'shape', 'size', 'span', 'src', 'start', 'style', 'summary', 'tabindex', 'target', 'title', 'type', 'usemap', 'valign', 'value', 'vspace', 'width', 'xml:lang')``

.. _RICHTEXT_ALLOWED_STYLES:

``RICHTEXT_ALLOWED_STYLES``
---------------------------

List of inline CSS styles that won't be stripped from ``RichTextField`` instances.

Default: ``('border', 'display', 'float', 'list-style-type', 'margin', 'margin-bottom', 'margin-left', 'margin-right', 'margin-top', 'padding-left', 'text-align', 'text-decoration', 'vertical-align')``

.. _RICHTEXT_ALLOWED_TAGS:

``RICHTEXT_ALLOWED_TAGS``
-------------------------

List of HTML tags that won't be stripped from ``RichTextField`` instances.

Default: ``('a', 'abbr', 'acronym', 'address', 'area', 'article', 'aside', 'b', 'bdo', 'big', 'blockquote', 'br', 'button', 'caption', 'center', 'cite', 'code', 'col', 'colgroup', 'dd', 'del', 'dfn', 'dir', 'div', 'dl', 'dt', 'em', 'fieldset', 'figure', 'font', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'hr', 'i', 'img', 'input', 'ins', 'kbd', 'label', 'legend', 'li', 'map', 'men', 'nav', 'ol', 'optgroup', 'option', 'p', 'pre', 'q', 's', 'samp', 'section', 'select', 'small', 'span', 'strike', 'strong', 'sub', 'sup', 'table', 'tbody', 'td', 'textarea', 'tfoot', 'th', 'thead', 'tr', 'tt', '', 'ul', 'var', 'wbr')``

.. _RICHTEXT_FILTERS:

``RICHTEXT_FILTERS``
--------------------

List of dotted paths to functions, called in order, on a ``RichTextField`` value before it is rendered to the template.

Default: ``('mezzanine.utils.html.thumbnails',)``

.. _RICHTEXT_FILTER_LEVEL:

``RICHTEXT_FILTER_LEVEL``
-------------------------

*Do not change this setting unless you know what you're doing.*

When content is saved in a Rich Text (WYSIWYG) field, unsafe HTML tags and attributes are stripped from the content to protect against staff members intentionally adding code that could be used to cause problems, such as changing their account to a super-user with full access to the system.

This setting allows you to change the level of filtering that occurs. Setting it to low will allow certain extra tags to be permitted, such as those required for embedding video. While these tags are not the main candidates for users adding malicious code, they are still considered dangerous and could potentially be mis-used by a particularly technical user, and so are filtered out when the filtering level is set to high.

Setting the filtering level to no filtering, will disable all filtering, and allow any code to be entered by staff members, including script tags.

Choices: High: ``1``, Low (allows video, iframe, Flash, etc): ``2``, No filtering: ``3``


Default: ``1``

.. _RICHTEXT_WIDGET_CLASS:

``RICHTEXT_WIDGET_CLASS``
-------------------------

Dotted package path and class name of the widget to use for the ``RichTextField``.

Default: ``'mezzanine.core.forms.TinyMceWidget'``

.. _SEARCH_AGE_SCALE_FACTOR:

``SEARCH_AGE_SCALE_FACTOR``
---------------------------

The amount of emphasis to put on age when ranking search results. A higher number gives more emphasis to age, ranking newer results higher with less regard to their ordinary score. Setting this to zero disables weighing search results by age.

Default: ``1.5``

.. _SEARCH_MODEL_CHOICES:

``SEARCH_MODEL_CHOICES``
------------------------

Sequence of models that will be provided by default as choices in the search form. Each model should be in the format ``app_label.model_name``. Only models that subclass ``mezzanine.core.models.Displayable`` should be used.

Default: ``('pages.Page', 'blog.BlogPost')``

.. _SEARCH_PER_PAGE:

``SEARCH_PER_PAGE``
-------------------

Number of results shown in the search results page.

Default: ``10``

.. _SITE_PREFIX:

``SITE_PREFIX``
---------------

A URL prefix for mounting all of Mezzanine's urlpatterns under. When using this, you'll also need to manually apply it to your project's root ``urls.py`` module. The root ``urls.py`` module provided by Mezzanine's ``mezzanine-project`` command contains an example of this towards its end.

Default: ``''``

.. _SITE_TAGLINE:

``SITE_TAGLINE``
----------------

A tag line that will appear at the top of all pages.

Default: ``'An open source content management platform.'``

.. _SITE_TITLE:

``SITE_TITLE``
--------------

Title that will display at the top of the site, and be appended to the content of the HTML title tags on every page.

Default: ``'Mezzanine'``

.. _SLUGIFY:

``SLUGIFY``
-----------

Dotted Python path to the callable for converting strings into URL slugs. Defaults to ``mezzanine.utils.urls.slugify_unicode`` which allows for non-ascii URLs. Change to ``django.template.defaultfilters.slugify`` to use Django's slugify function, or something of your own if required.

Default: ``'mezzanine.utils.urls.slugify_unicode'``

.. _SPAM_FILTERS:

``SPAM_FILTERS``
----------------

Sequence of dotted Python paths to callable functions used for checking posted content (such as forms or comments) is spam. Each function should accept three arguments: the request object, the form object, and the URL that was posted from. Defaults to ``mezzanine.utils.views.is_spam_akismet`` which will use the `http://akismet.com <http://akismet.com>`_ spam filtering service when the ``AKISMET_API_KEY`` setting is configured.

Default: ``('mezzanine.utils.views.is_spam_akismet',)``

.. _SSL_ENABLED:

``SSL_ENABLED``
---------------

If ``True``, users will be automatically redirected to HTTPS for the URLs specified by the ``SSL_FORCE_URL_PREFIXES`` setting.

Default: ``False``

.. _SSL_FORCED_PREFIXES_ONLY:

``SSL_FORCED_PREFIXES_ONLY``
----------------------------

If ``True``, only URLs specified by the ``SSL_FORCE_URL_PREFIXES`` setting will be accessible over SSL, and all other URLs will be redirected back to HTTP if accessed over HTTPS.

Default: ``True``

.. _SSL_FORCE_HOST:

``SSL_FORCE_HOST``
------------------

Host name that the site should always be accessed via that matches the SSL certificate.

Default: ``''``

.. _SSL_FORCE_URL_PREFIXES:

``SSL_FORCE_URL_PREFIXES``
--------------------------

Sequence of URL prefixes that will be forced to run over SSL when ``SSL_ENABLED`` is ``True``. i.e. ('/admin', '/example') would force all URLs beginning with /admin or /example to run over SSL.

Default: ``('/admin', '/account')``

.. _STOP_WORDS:

``STOP_WORDS``
--------------

List of words which will be stripped from search queries.

Default: ``('a', 'about', 'above', 'above', 'across', 'after', 'afterwards', 'again', 'against', 'all', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'am', 'among', 'amongst', 'amoungst', 'amount', 'an', 'and', 'another', 'any', 'anyhow', 'anyone', 'anything', 'anyway', 'anywhere', 'are', 'around', 'as', 'at', 'back', 'be', 'became', 'because', 'become', 'becomes', 'becoming', 'been', 'before', 'beforehand', 'behind', 'being', 'below', 'beside', 'besides', 'between', 'beyond', 'bill', 'both', 'bottom', 'but', 'by', 'call', 'can', 'cannot', 'cant', 'co', 'con', 'could', 'couldnt', 'cry', 'de', 'describe', 'detail', 'do', 'done', 'down', 'due', 'during', 'each', 'eg', 'eight', 'either', 'eleven', 'else', 'elsewhere', 'empty', 'enough', 'etc', 'even', 'ever', 'every', 'everyone', 'everything', 'everywhere', 'except', 'few', 'fifteen', 'fifty', 'fill', 'find', 'fire', 'first', 'five', 'for', 'former', 'formerly', 'forty', 'found', 'four', 'from', 'front', 'full', 'further', 'get', 'give', 'go', 'had', 'has', 'hasnt', 'have', 'he', 'hence', 'her', 'here', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'however', 'hundred', 'ie', 'if', 'in', 'inc', 'indeed', 'interest', 'into', 'is', 'it', 'its', 'itself', 'keep', 'last', 'latter', 'latterly', 'least', 'less', 'ltd', 'made', 'many', 'may', 'me', 'meanwhile', 'might', 'mill', 'mine', 'more', 'moreover', 'most', 'mostly', 'move', 'much', 'must', 'my', 'myself', 'name', 'namely', 'neither', 'never', 'nevertheless', 'next', 'nine', 'no', 'nobody', 'none', 'noone', 'nor', 'not', 'nothing', 'now', 'nowhere', 'of', 'off', 'often', 'on', 'once', 'one', 'only', 'onto', 'or', 'other', 'others', 'otherwise', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'part', 'per', 'perhaps', 'please', 'put', 'rather', 're', 'same', 'see', 'seem', 'seemed', 'seeming', 'seems', 'serious', 'several', 'she', 'should', 'show', 'side', 'since', 'sincere', 'six', 'sixty', 'so', 'some', 'somehow', 'someone', 'something', 'sometime', 'sometimes', 'somewhere', 'still', 'such', 'system', 'take', 'ten', 'than', 'that', 'the', 'their', 'them', 'themselves', 'then', 'thence', 'there', 'thereafter', 'thereby', 'therefore', 'therein', 'thereupon', 'these', 'they', 'thickv', 'thin', 'third', 'this', 'those', 'though', 'three', 'through', 'throughout', 'thr', 'thus', 'to', 'together', 'too', 'top', 'toward', 'towards', 'twelve', 'twenty', 'two', 'un', 'under', 'until', 'up', 'upon', 'us', 'very', 'via', 'was', 'we', 'well', 'were', 'what', 'whatever', 'when', 'whence', 'whenever', 'where', 'whereafter', 'whereas', 'whereby', 'wherein', 'whereupon', 'wherever', 'whether', 'which', 'while', 'whither', 'who', 'whoever', 'whole', 'whom', 'whose', 'why', 'will', 'with', 'within', 'without', 'would', 'yet', 'you', 'your', 'yours', 'yourself', 'yourselves', 'the')``

.. _TAG_CLOUD_SIZES:

``TAG_CLOUD_SIZES``
-------------------

Number of different sizes for tags when shown as a cloud.

Default: ``4``

.. _TEMPLATE_ACCESSIBLE_SETTINGS:

``TEMPLATE_ACCESSIBLE_SETTINGS``
--------------------------------

Sequence of setting names available within templates.

Default: ``('ACCOUNTS_APPROVAL_REQUIRED', 'ACCOUNTS_VERIFICATION_REQUIRED', 'ADMIN_MENU_COLLAPSED', 'BITLY_ACCESS_TOKEN', 'BLOG_USE_FEATURED_IMAGE', 'COMMENTS_DISQUS_SHORTNAME', 'COMMENTS_NUM_LATEST', 'COMMENTS_DISQUS_API_PUBLIC_KEY', 'COMMENTS_DISQUS_API_SECRET_KEY', 'COMMENTS_USE_RATINGS', 'DEV_SERVER', 'FORMS_USE_HTML5', 'GRAPPELLI_INSTALLED', 'GOOGLE_ANALYTICS_ID', 'JQUERY_FILENAME', 'JQUERY_UI_FILENAME', 'LOGIN_URL', 'LOGOUT_URL', 'SITE_TITLE', 'SITE_TAGLINE', 'USE_L10N', 'USE_MODELTRANSLATION')``

.. _THUMBNAILS_DIR_NAME:

``THUMBNAILS_DIR_NAME``
-----------------------

Directory name to store thumbnails in, that will be created relative to the original image's directory.

Default: ``'.thumbnails'``

.. _TINYMCE_SETUP_JS:

``TINYMCE_SETUP_JS``
--------------------

URL for the JavaScript file (relative to ``STATIC_URL``) that handles configuring TinyMCE when the default ``RICHTEXT_WIDGET_CLASS`` is used.

Default: ``'mezzanine/js/tinymce_setup.js'``

.. _TWITTER_ACCESS_TOKEN_KEY:

``TWITTER_ACCESS_TOKEN_KEY``
----------------------------



Default: ``''``

.. _TWITTER_ACCESS_TOKEN_SECRET:

``TWITTER_ACCESS_TOKEN_SECRET``
-------------------------------



Default: ``''``

.. _TWITTER_CONSUMER_KEY:

``TWITTER_CONSUMER_KEY``
------------------------



Default: ``''``

.. _TWITTER_CONSUMER_SECRET:

``TWITTER_CONSUMER_SECRET``
---------------------------



Default: ``''``

.. _TWITTER_DEFAULT_NUM_TWEETS:

``TWITTER_DEFAULT_NUM_TWEETS``
------------------------------

Number of tweets to display in the default Twitter feed.

Default: ``3``

.. _TWITTER_DEFAULT_QUERY:

``TWITTER_DEFAULT_QUERY``
-------------------------

Twitter query to use for the default query type. 

*Note:* Once you change this from the default, you'll need to configure each of the oAuth consumer/access key/secret settings. Please refer to `http://dev.twitter.com <http://dev.twitter.com>`_ for more information on creating an application and acquiring these settings.

Default: ``'from:stephen_mcd mezzanine'``

.. _TWITTER_DEFAULT_QUERY_TYPE:

``TWITTER_DEFAULT_QUERY_TYPE``
------------------------------

Type of query that will be used to retrieve tweets for the default Twitter feed.

Choices: User: ``user``, List: ``list``, Search: ``search``


Default: ``'search'``

.. _UPLOAD_TO_HANDLERS:

``UPLOAD_TO_HANDLERS``
----------------------

Dict mapping file field names in the format ``app_label.model_name.field_name`` to the Python dotted path to function names that will be used for the file field's ``upload_to`` argument.

Default: ``{}``

.. _USE_MODELTRANSLATION:

``USE_MODELTRANSLATION``
------------------------

If ``True``, the django-modeltranslation application will be automatically added to the ``INSTALLED_APPS`` setting.

Default: ``False``