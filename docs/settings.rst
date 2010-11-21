.. THIS DOCUMENT IS AUTO GENERATED VIA conf.py

``ADMIN_MENU_ORDER``
--------------------

Controls the ordering and grouping of the admin menu.

Default: ``((u'Content', ('pages.Page', 'blog.BlogPost', 'blog.Comment', (u'Media Library', 'fb_browse'))), (u'Site', ('sites.Site', 'redirects.Redirect', 'conf.Setting')), (u'Users', ('auth.User', 'auth.Group')))``

``ADMIN_REMOVAL``
-----------------

Unregister these models from the admin.

Default: ``()``

``BLOG_BITLY_KEY``
------------------

Key for bit.ly URL shortening service.

Default: ``''``

``BLOG_BITLY_USER``
-------------------

Username for bit.ly URL shortening service.

Default: ``''``

``BLOG_POST_MAX_PAGING_LINKS``
------------------------------

Max number of paging links to show on a blog listing page.

Default: ``10``

``BLOG_POST_PER_PAGE``
----------------------

Number of blog posts to show on a blog listing page.

Default: ``5``

``BLOG_SLUG``
-------------

Slug of the page object for the blog.

Default: ``'blog'``

``COMMENTS_DEFAULT_APPROVED``
-----------------------------

If ``True``, built-in comments are approved by default.

Default: ``True``

``COMMENTS_DISQUS_KEY``
-----------------------

API key for the http://disqus.com comments service.

Default: ``''``

``COMMENTS_DISQUS_SHORTNAME``
-----------------------------

Username for the http://disqus.com comments service.

Default: ``''``

``COMMENTS_NUM_LATEST``
-----------------------

Number of latest comments to show in the admin dashboard.

Default: ``5``

``COMMENTS_UNAPPROVED_VISIBLE``
-------------------------------

If ``True``, unapproved comments will have a placeholder visible on the site with a 'waiting for approval' or 'comment removed' message based on the workflow around the ``COMMENTS_DEFAULT_APPROVED`` setting - if ``True`` then the former message is used, if ``False`` then the latter.

Default: ``True``

``CONTENT_MEDIA_PATH``
----------------------

Absolute path to Mezzanine's internal media files.

Default: ``[dynamic]``

``CONTENT_MEDIA_URL``
---------------------

URL prefix for serving Mezzanine's internal media files.

Default: ``'/content_media/'``

``DASHBOARD_TAGS``
------------------

A three item sequence, each containing a sequence of template tags used to render the admin dashboard.

Default: ``(('blog_tags.quick_blog', 'mezzanine_tags.app_list'), ('blog_tags.recent_comments',), ('mezzanine_tags.recent_actions',))``

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

``GOOGLE_ANALYTICS_ID``
-----------------------

Google Analytics ID (http://www.google.com/analytics/)

Default: ``''``

``MOBILE_USER_AGENTS``
----------------------

Strings to search user agent for when testing for a mobile device.

Default: ``('2.0 MMP', '240x320', '400X240', 'AvantGo', 'BlackBerry', 'Blazer', 'Cellphone', 'Danger', 'DoCoMo', 'Elaine/3.0', 'EudoraWeb', 'Googlebot-Mobile', 'hiptop', 'IEMobile', 'KYOCERA/WX310K', 'LG/U990', 'MIDP-2.', 'MMEF20', 'MOT-V', 'NetFront', 'Newt', 'Nintendo Wii', 'Nitro', 'Nokia', 'Opera Mini', 'Palm', 'PlayStation Portable', 'portalmmm', 'Proxinet', 'ProxiNet', 'SHARP-TQ-GX10', 'SHG-i900', 'Small', 'SonyEricsson', 'Symbian OS', 'SymbianOS', 'TS21i-10', 'UP.Browser', 'UP.Link', 'webOS', 'Windows CE', 'WinWAP', 'YahooSeeker/M1A1-R2D2', 'iPhone', 'iPod', 'Android', 'BlackBerry9530', 'LG-TU915 Obigo', 'LGE VX', 'webOS', 'Nokia5800')``

``PAGES_MENU_SHOW_ALL``
-----------------------

If ``True``, the pages menu will show all levels of navigation, otherwise child pages are only shown when viewing the parent page.

Default: ``True``

``SEARCH_MAX_PAGING_LINKS``
---------------------------

Max number of paging links for the search results page.

Default: ``10``

``SEARCH_PER_PAGE``
-------------------

Number of results to show in the search results page.

Default: ``10``

``STOP_WORDS``
--------------

List of words which will be stripped from search queries.

Default: ``('a', 'about', 'above', 'above', 'across', 'after', 'afterwards', 'again', 'against', 'all', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'am', 'among', 'amongst', 'amoungst', 'amount', 'an', 'and', 'another', 'any', 'anyhow', 'anyone', 'anything', 'anyway', 'anywhere', 'are', 'around', 'as', 'at', 'back', 'be', 'became', 'because', 'become', 'becomes', 'becoming', 'been', 'before', 'beforehand', 'behind', 'being', 'below', 'beside', 'besides', 'between', 'beyond', 'bill', 'both', 'bottom', 'but', 'by', 'call', 'can', 'cannot', 'cant', 'co', 'con', 'could', 'couldnt', 'cry', 'de', 'describe', 'detail', 'do', 'done', 'down', 'due', 'during', 'each', 'eg', 'eight', 'either', 'eleven', 'else', 'elsewhere', 'empty', 'enough', 'etc', 'even', 'ever', 'every', 'everyone', 'everything', 'everywhere', 'except', 'few', 'fifteen', 'fify', 'fill', 'find', 'fire', 'first', 'five', 'for', 'former', 'formerly', 'forty', 'found', 'four', 'from', 'front', 'full', 'further', 'get', 'give', 'go', 'had', 'has', 'hasnt', 'have', 'he', 'hence', 'her', 'here', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'however', 'hundred', 'ie', 'if', 'in', 'inc', 'indeed', 'interest', 'into', 'is', 'it', 'its', 'itself', 'keep', 'last', 'latter', 'latterly', 'least', 'less', 'ltd', 'made', 'many', 'may', 'me', 'meanwhile', 'might', 'mill', 'mine', 'more', 'moreover', 'most', 'mostly', 'move', 'much', 'must', 'my', 'myself', 'name', 'namely', 'neither', 'never', 'nevertheless', 'next', 'nine', 'no', 'nobody', 'none', 'noone', 'nor', 'not', 'nothing', 'now', 'nowhere', 'of', 'off', 'often', 'on', 'once', 'one', 'only', 'onto', 'or', 'other', 'others', 'otherwise', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'part', 'per', 'perhaps', 'please', 'put', 'rather', 're', 'same', 'see', 'seem', 'seemed', 'seeming', 'seems', 'serious', 'several', 'she', 'should', 'show', 'side', 'since', 'sincere', 'six', 'sixty', 'so', 'some', 'somehow', 'someone', 'something', 'sometime', 'sometimes', 'somewhere', 'still', 'such', 'system', 'take', 'ten', 'than', 'that', 'the', 'their', 'them', 'themselves', 'then', 'thence', 'there', 'thereafter', 'thereby', 'therefore', 'therein', 'thereupon', 'these', 'they', 'thickv', 'thin', 'third', 'this', 'those', 'though', 'three', 'through', 'throughout', 'thru', 'thus', 'to', 'together', 'too', 'top', 'toward', 'towards', 'twelve', 'twenty', 'two', 'un', 'under', 'until', 'up', 'upon', 'us', 'very', 'via', 'was', 'we', 'well', 'were', 'what', 'whatever', 'when', 'whence', 'whenever', 'where', 'whereafter', 'whereas', 'whereby', 'wherein', 'whereupon', 'wherever', 'whether', 'which', 'while', 'whither', 'who', 'whoever', 'whole', 'whom', 'whose', 'why', 'will', 'with', 'within', 'without', 'would', 'yet', 'you', 'your', 'yours', 'yourself', 'yourselves', 'the')``

``TAG_CLOUD_SIZES``
-------------------

Number of different sizes for tags when shown as a cloud.

Default: ``4``

``THEME``
---------

Package name of theme app to use.

Default: ``''``

``TINYMCE_URL``
---------------

URL prefix for serving Tiny MCE files.

Default: ``'/media/admin/tinymce'``