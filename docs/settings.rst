.. THIS DOCUMENT IS AUTO GENERATED VIA conf.py

``MEZZANINE_ADMIN_REMOVAL``
---------------------------

Default: ``()``

Unregister these models installed by default (occurs in urlconf).

``MEZZANINE_BLOG_TITLE``
------------------------

Default: ``"The Mezzanine Blog"``

Blog feed settings.

``MEZZANINE_BLOG_DESCRIPTION``
------------------------------

Default: ``"The Mezzanine Blog"``


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