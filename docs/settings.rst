.. THIS DOCUMENT IS AUTO GENERATED VIA conf.py

``MEZZANINE_ADMIN_REMOVAL``
---------------------------

Default: ``()``

Unregister these models installed by default (occurs in urlconf).

``MEZZANINE_ADMIN_MENU_ORDER``
------------------------------

Default: ``((<django.utils.functional.__proxy__ object at 0x981df4c>, ('pages.Page', 'blog.BlogPost', 'blog.Comment')), (<django.utils.functional.__proxy__ object at 0x981dfcc>, ('auth.User', 'auth.Group', 'sites.Site', 'redirects.Redirect')))``

Controls the ordering and grouping of the admin menu.

``MEZZANINE_BLOG_BITLY_USER``
-----------------------------

Default: ``None``

Credentials for bit.ly URL shortening service.

``MEZZANINE_BLOG_BITLY_KEY``
----------------------------

Default: ``None``


``MEZZANINE_BLOG_POST_PER_PAGE``
--------------------------------

Default: ``5``

Number of blog posts to show on a blog listing page.

``MEZZANINE_BLOG_POST_MAX_PAGING_LINKS``
----------------------------------------

Default: ``10``

Maximum number of paging links to show on a blog listing page.

``MEZZANINE_BLOG_SLUG``
-----------------------

Default: ``"blog"``

Slug of the page object for the blog.

``MEZZANINE_COMMENTS_DISQUS_SHORTNAME``
---------------------------------------

Default: ``None``

Shortname when using the Disqus comments system (http://disqus.com).

``MEZZANINE_COMMENTS_DISQUS_KEY``
---------------------------------

Default: ``None``

Disqus user's API key for displaying recent comments in the admin dashboard.

``MEZZANINE_COMMENTS_DEFAULT_APPROVED``
---------------------------------------

Default: ``True``

If True, the built-in comments are approved by default.

``MEZZANINE_COMMENTS_NUM_LATEST``
---------------------------------

Default: ``5``

Number of latest comments to show in the admin dashboard.

``MEZZANINE_COMMENTS_UNAPPROVED_VISIBLE``
-----------------------------------------

Default: ``True``

If True, unapproved comments will have a placeholder visible on the site
with a "waiting for approval" or "comment removed" message based on the
workflow around the ``MEZZANINE_COMMENTS_DEFAULT_APPROVED`` setting - if
True then the former message is used, if False then the latter.

``MEZZANINE_GOOGLE_ANALYTICS_ID``
---------------------------------

Default: ``None``

ID for using Google Analytics (http://www.google.com/analytics/) referred to
as "Web Property ID"

``MEZZANINE_MOBILE_USER_AGENTS``
--------------------------------

Default: ``('2.0 MMP', '240x320', '400X240', 'AvantGo', 'BlackBerry', 'Blazer', 'Cellphone', 'Danger', 'DoCoMo', 'Elaine/3.0', 'EudoraWeb', 'Googlebot-Mobile', 'hiptop', 'IEMobile', 'KYOCERA/WX310K', 'LG/U990', 'MIDP-2.', 'MMEF20', 'MOT-V', 'NetFront', 'Newt', 'Nintendo Wii', 'Nitro', 'Nokia', 'Opera Mini', 'Palm', 'PlayStation Portable', 'portalmmm', 'Proxinet', 'ProxiNet', 'SHARP-TQ-GX10', 'SHG-i900', 'Small', 'SonyEricsson', 'Symbian OS', 'SymbianOS', 'TS21i-10', 'UP.Browser', 'UP.Link', 'webOS', 'Windows CE', 'WinWAP', 'YahooSeeker/M1A1-R2D2', 'iPhone', 'iPod', 'Android', 'BlackBerry9530', 'LG-TU915 Obigo', 'LGE VX', 'webOS', 'Nokia5800')``

Strings to check for in user agents when testing for a mobile device.

``MEZZANINE_TAG_CLOUD_SIZES``
-----------------------------

Default: ``4``

Number of different sizes given to tags when shown as a cloud.

``MEZZANINE_PAGES_MENU_SHOW_ALL``
---------------------------------

Default: ``True``

If True, the pages menu will show all levels of navigation by default,
otherwise child pages are only shown when viewing the parent page.

``MEZZANINE_SEARCH_PER_PAGE``
-----------------------------

Default: ``10``

Number of results to show in the search results page.

``MEZZANINE_SEARCH_MAX_PAGING_LINKS``
-------------------------------------

Default: ``10``

Maximum number of paging links to show in the search results page.

``MEZZANINE_STOP_WORDS``
------------------------

Default: ``('a', 'about', 'above', 'above', 'across', 'after', 'afterwards', 'again', 'against', 'all', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'am', 'among', 'amongst', 'amoungst', 'amount', 'an', 'and', 'another', 'any', 'anyhow', 'anyone', 'anything', 'anyway', 'anywhere', 'are', 'around', 'as', 'at', 'back', 'be', 'became', 'because', 'become', 'becomes', 'becoming', 'been', 'before', 'beforehand', 'behind', 'being', 'below', 'beside', 'besides', 'between', 'beyond', 'bill', 'both', 'bottom', 'but', 'by', 'call', 'can', 'cannot', 'cant', 'co', 'con', 'could', 'couldnt', 'cry', 'de', 'describe', 'detail', 'do', 'done', 'down', 'due', 'during', 'each', 'eg', 'eight', 'either', 'eleven', 'else', 'elsewhere', 'empty', 'enough', 'etc', 'even', 'ever', 'every', 'everyone', 'everything', 'everywhere', 'except', 'few', 'fifteen', 'fify', 'fill', 'find', 'fire', 'first', 'five', 'for', 'former', 'formerly', 'forty', 'found', 'four', 'from', 'front', 'full', 'further', 'get', 'give', 'go', 'had', 'has', 'hasnt', 'have', 'he', 'hence', 'her', 'here', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'however', 'hundred', 'ie', 'if', 'in', 'inc', 'indeed', 'interest', 'into', 'is', 'it', 'its', 'itself', 'keep', 'last', 'latter', 'latterly', 'least', 'less', 'ltd', 'made', 'many', 'may', 'me', 'meanwhile', 'might', 'mill', 'mine', 'more', 'moreover', 'most', 'mostly', 'move', 'much', 'must', 'my', 'myself', 'name', 'namely', 'neither', 'never', 'nevertheless', 'next', 'nine', 'no', 'nobody', 'none', 'noone', 'nor', 'not', 'nothing', 'now', 'nowhere', 'of', 'off', 'often', 'on', 'once', 'one', 'only', 'onto', 'or', 'other', 'others', 'otherwise', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'part', 'per', 'perhaps', 'please', 'put', 'rather', 're', 'same', 'see', 'seem', 'seemed', 'seeming', 'seems', 'serious', 'several', 'she', 'should', 'show', 'side', 'since', 'sincere', 'six', 'sixty', 'so', 'some', 'somehow', 'someone', 'something', 'sometime', 'sometimes', 'somewhere', 'still', 'such', 'system', 'take', 'ten', 'than', 'that', 'the', 'their', 'them', 'themselves', 'then', 'thence', 'there', 'thereafter', 'thereby', 'therefore', 'therein', 'thereupon', 'these', 'they', 'thickv', 'thin', 'third', 'this', 'those', 'though', 'three', 'through', 'throughout', 'thru', 'thus', 'to', 'together', 'too', 'top', 'toward', 'towards', 'twelve', 'twenty', 'two', 'un', 'under', 'until', 'up', 'upon', 'us', 'very', 'via', 'was', 'we', 'well', 'were', 'what', 'whatever', 'when', 'whence', 'whenever', 'where', 'whereafter', 'whereas', 'whereby', 'wherein', 'whereupon', 'wherever', 'whether', 'which', 'while', 'whither', 'who', 'whoever', 'whole', 'whom', 'whose', 'why', 'will', 'with', 'within', 'without', 'would', 'yet', 'you', 'your', 'yours', 'yourself', 'yourselves', 'the')``

List of words which will be stripped from search queries.