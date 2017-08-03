from __future__ import unicode_literals
from future.builtins import range

from mezzanine.conf import settings
from mezzanine.core.managers import DisplayableManager
from mezzanine.utils.urls import home_slug
from mezzanine.utils.deprecation import is_authenticated


class PageManager(DisplayableManager):

    def published(self, for_user=None, include_login_required=False):
        """
        Override ``DisplayableManager.published`` to exclude
        pages with ``login_required`` set to ``True``. if the
        user is unauthenticated and the setting
        ``PAGES_PUBLISHED_INCLUDE_LOGIN_REQUIRED`` is ``False``.

        The extra ``include_login_required`` arg allows callers to
        override the ``PAGES_PUBLISHED_INCLUDE_LOGIN_REQUIRED``
        behaviour in special cases where they want to deal with the
        ``login_required`` field manually, such as the case in
        ``PageMiddleware``.
        """
        published = super(PageManager, self).published(for_user=for_user)
        unauthenticated = for_user and not is_authenticated(for_user)
        if (unauthenticated and not include_login_required and
                not settings.PAGES_PUBLISHED_INCLUDE_LOGIN_REQUIRED):
            published = published.exclude(login_required=True)
        return published

    def with_ascendants_for_slug(self, slug, **kwargs):
        """
        Given a slug, returns a list of pages from ascendants to
        descendants, that form the parent/child page relationships
        for that slug. The main concern is to do this in a single
        database query rather than querying the database for parents
        of a given page.

        Primarily used in ``PageMiddleware`` to provide the current
        page, which in the case of non-page views, won't match the
        slug exactly, but will likely match a page that has been
        created for linking to the entry point for the app, eg the
        blog page when viewing blog posts.

        Also used within ``Page.get_ascendants``, which gets called
        in the ``pages.views`` view, for building a list of possible
        templates that can be used for the page.

        If a valid chain of pages is found, we also assign the pages
        to the ``page._ascendants`` attr of the main/first/deepest
        page, so that when its ``get_ascendants`` method is called,
        the ascendants chain can be re-used without querying the
        database again. This occurs at least once, given the second
        use-case described above.
        """

        if slug == "/":
            slugs = [home_slug()]
        else:
            # Create a list of slugs within this slug,
            # eg: ['about', 'about/team', 'about/team/mike']
            parts = slug.split("/")
            slugs = ["/".join(parts[:i]) for i in range(1, len(parts) + 1)]

        # Find the deepest page that matches one of our slugs.
        # Sorting by "-slug" should ensure that the pages are in
        # descendant -> ascendant order.
        pages_for_user = self.published(**kwargs)
        pages = list(pages_for_user.filter(slug__in=slugs).order_by("-slug"))
        if not pages:
            return []

        # Check to see if the other pages retrieved form a valid path
        # in the page tree, i.e. pages[0].parent == pages[1],
        # pages[1].parent == pages[2], and so on. If they do, assign
        # the ascendants to the main/first/deepest page, so that it
        # can be re-used on calls to its get_ascendants method.
        pages[0]._ascendants = []
        for i, page in enumerate(pages):
            try:
                parent = pages[i + 1]
            except IndexError:
                # IndexError indicates that this is the last page in
                # the list, so it should have no parent.
                if page.parent_id:
                    break  # Invalid parent
            else:
                if page.parent_id != parent.id:
                    break  # Invalid parent
        else:
            # Valid parents
            pages[0]._ascendants = pages[1:]
        return pages
