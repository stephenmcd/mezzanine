from __future__ import unicode_literals
from future.builtins import int, zip

from functools import reduce
from operator import ior, iand
from string import punctuation

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Manager, Q, CharField, TextField, get_models
from django.db.models.manager import ManagerDescriptor
from django.db.models.query import QuerySet
from django.contrib.sites.managers import CurrentSiteManager as DjangoCSM
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.utils.models import get_model
from mezzanine.utils.sites import current_site_id
from mezzanine.utils.urls import home_slug


class PublishedManager(Manager):
    """
    Provides filter for restricting items returned by status and
    publish date when the given user is not a staff member.
    """

    def published(self, for_user=None):
        """
        For non-staff users, return items with a published status and
        whose publish and expiry dates fall before and after the
        current date when specified.
        """
        from mezzanine.core.models import CONTENT_STATUS_PUBLISHED
        if for_user is not None and for_user.is_staff:
            return self.all()
        return self.filter(
            Q(publish_date__lte=now()) | Q(publish_date__isnull=True),
            Q(expiry_date__gte=now()) | Q(expiry_date__isnull=True),
            Q(status=CONTENT_STATUS_PUBLISHED))

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


def search_fields_to_dict(fields):
    """
    In ``SearchableQuerySet`` and ``SearchableManager``, search fields
    can either be a sequence, or a dict of fields mapped to weights.
    This function converts sequences to a dict mapped to even weights,
    so that we're consistently dealing with a dict of fields mapped to
    weights, eg: ("title", "content") -> {"title": 1, "content": 1}
    """
    if not fields:
        return {}
    try:
        int(list(dict(fields).values())[0])
    except (TypeError, ValueError):
        fields = dict(zip(fields, [1] * len(fields)))
    return fields


class SearchableQuerySet(QuerySet):
    """
    QuerySet providing main search functionality for
    ``SearchableManager``.
    """

    def __init__(self, *args, **kwargs):
        self._search_ordered = False
        self._search_terms = set()
        self._search_fields = kwargs.pop("search_fields", {})
        super(SearchableQuerySet, self).__init__(*args, **kwargs)

    def search(self, query, search_fields=None):
        """
        Build a queryset matching words in the given search query,
        treating quoted terms as exact phrases and taking into
        account + and - symbols as modifiers controlling which terms
        to require and exclude.
        """

        #### DETERMINE FIELDS TO SEARCH ###

        # Use search_fields arg if given, otherwise use search_fields
        # initially configured by the manager class.
        if search_fields:
            self._search_fields = search_fields_to_dict(search_fields)
        if not self._search_fields:
            return self.none()

        #### BUILD LIST OF TERMS TO SEARCH FOR ###

        # Remove extra spaces, put modifiers inside quoted terms.
        terms = " ".join(query.split()).replace("+ ", "+")     \
                                       .replace('+"', '"+')    \
                                       .replace("- ", "-")     \
                                       .replace('-"', '"-')    \
                                       .split('"')
        # Strip punctuation other than modifiers from terms and create
        # terms list, first from quoted terms and then remaining words.
        terms = [("" if t[0:1] not in "+-" else t[0:1]) + t.strip(punctuation)
            for t in terms[1::2] + "".join(terms[::2]).split()]
        # Remove stop words from terms that aren't quoted or use
        # modifiers, since words with these are an explicit part of
        # the search query. If doing so ends up with an empty term
        # list, then keep the stop words.
        terms_no_stopwords = [t for t in terms if t.lower() not in
            settings.STOP_WORDS]
        get_positive_terms = lambda terms: [t.lower().strip(punctuation)
            for t in terms if t[0:1] != "-"]
        positive_terms = get_positive_terms(terms_no_stopwords)
        if positive_terms:
            terms = terms_no_stopwords
        else:
            positive_terms = get_positive_terms(terms)
        # Append positive terms (those without the negative modifier)
        # to the internal list for sorting when results are iterated.
        if not positive_terms:
            return self.none()
        else:
            self._search_terms.update(positive_terms)

        #### BUILD QUERYSET FILTER ###

        # Create the queryset combining each set of terms.
        excluded = [reduce(iand, [~Q(**{"%s__icontains" % f: t[1:]}) for f in
            self._search_fields.keys()]) for t in terms if t[0:1] == "-"]
        required = [reduce(ior, [Q(**{"%s__icontains" % f: t[1:]}) for f in
            self._search_fields.keys()]) for t in terms if t[0:1] == "+"]
        optional = [reduce(ior, [Q(**{"%s__icontains" % f: t}) for f in
            self._search_fields.keys()]) for t in terms if t[0:1] not in "+-"]
        queryset = self
        if excluded:
            queryset = queryset.filter(reduce(iand, excluded))
        if required:
            queryset = queryset.filter(reduce(iand, required))
        # Optional terms aren't relevant to the filter if there are
        # terms that are explicitly required.
        elif optional:
            queryset = queryset.filter(reduce(ior, optional))
        return queryset.distinct()

    def _clone(self, *args, **kwargs):
        """
        Ensure attributes are copied to subsequent queries.
        """
        for attr in ("_search_terms", "_search_fields", "_search_ordered"):
            kwargs[attr] = getattr(self, attr)
        return super(SearchableQuerySet, self)._clone(*args, **kwargs)

    def order_by(self, *field_names):
        """
        Mark the filter as being ordered if search has occurred.
        """
        if not self._search_ordered:
            self._search_ordered = len(self._search_terms) > 0
        return super(SearchableQuerySet, self).order_by(*field_names)

    def iterator(self):
        """
        If search has occurred and no ordering has occurred, decorate
        each result with the number of search terms so that it can be
        sorted by the number of occurrence of terms.

        In the case of search fields that span model relationships, we
        cannot accurately match occurrences without some very
        complicated traversal code, which we won't attempt. So in this
        case, namely when there are no matches for a result (count=0),
        and search fields contain relationships (double underscores),
        we assume one match for one of the fields, and use the average
        weight of all search fields with relationships.
        """
        results = super(SearchableQuerySet, self).iterator()
        if self._search_terms and not self._search_ordered:
            results = list(results)
            for i, result in enumerate(results):
                count = 0
                related_weights = []
                for (field, weight) in self._search_fields.items():
                    if "__" in field:
                        related_weights.append(weight)
                    for term in self._search_terms:
                        field_value = getattr(result, field, None)
                        if field_value:
                            count += field_value.lower().count(term) * weight
                if not count and related_weights:
                    count = int(sum(related_weights) / len(related_weights))
                results[i].result_count = count
            return iter(results)
        return results


class SearchableManager(Manager):
    """
    Manager providing a chainable queryset.
    Adapted from http://www.djangosnippets.org/snippets/562/
    search method supports spanning across models that subclass the
    model being used to search.
    """

    def __init__(self, *args, **kwargs):
        self._search_fields = kwargs.pop("search_fields", {})
        super(SearchableManager, self).__init__(*args, **kwargs)

    def get_search_fields(self):
        """
        Returns the search field names mapped to weights as a dict.
        Used in ``get_query_set`` below to tell ``SearchableQuerySet``
        which search fields to use. Also used by ``DisplayableAdmin``
        to populate Django admin's ``search_fields`` attribute.

        Search fields can be populated via
        ``SearchableManager.__init__``, which then get stored in
        ``SearchableManager._search_fields``, which serves as an
        approach for defining an explicit set of fields to be used.

        Alternatively and more commonly, ``search_fields`` can be
        defined on models themselves. In this case, we look at the
        model and all its base classes, and build up the search
        fields from all of those, so the search fields are implicitly
        built up from the inheritence chain.

        Finally if no search fields have been defined at all, we
        fall back to any fields that are ``CharField`` or ``TextField``
        instances.
        """
        search_fields = self._search_fields.copy()
        if not search_fields:
            for cls in reversed(self.model.__mro__):
                super_fields = getattr(cls, "search_fields", {})
                search_fields.update(search_fields_to_dict(super_fields))
        if not search_fields:
            search_fields = []
            for f in self.model._meta.fields:
                if isinstance(f, (CharField, TextField)):
                    search_fields.append(f.name)
            search_fields = search_fields_to_dict(search_fields)
        return search_fields

    def get_query_set(self):
        search_fields = self.get_search_fields()
        return SearchableQuerySet(self.model, search_fields=search_fields)

    def contribute_to_class(self, model, name):
        """
        Django 1.5 explicitly prevents managers being accessed from
        abstract classes, which is behaviour the search API has relied
        on for years. Here we reinstate it.
        """
        super(SearchableManager, self).contribute_to_class(model, name)
        setattr(model, name, ManagerDescriptor(self))

    def search(self, *args, **kwargs):
        """
        Proxy to queryset's search method for the manager's model and
        any models that subclass from this manager's model if the
        model is abstract.
        """
        if not settings.SEARCH_MODEL_CHOICES:
            # No choices defined - build a list of leaf models (those
            # without subclasses) that inherit from Displayable.
            models = [m for m in get_models() if issubclass(m, self.model)]
            parents = reduce(ior, [m._meta.get_parent_list() for m in models])
            models = [m for m in models if m not in parents]
        elif getattr(self.model._meta, "abstract", False):
            # When we're combining model subclasses for an abstract
            # model (eg Displayable), we only want to use models that
            # are represented by the ``SEARCH_MODEL_CHOICES`` setting.
            # Now this setting won't contain an exact list of models
            # we should use, since it can define superclass models such
            # as ``Page``, so we check the parent class list of each
            # model when determining whether a model falls within the
            # ``SEARCH_MODEL_CHOICES`` setting.
            search_choices = set()
            models = set()
            parents = set()
            errors = []
            for name in settings.SEARCH_MODEL_CHOICES:
                try:
                    model = get_model(*name.split(".", 1))
                except LookupError:
                    errors.append(name)
                else:
                    search_choices.add(model)
            if errors:
                raise ImproperlyConfigured("Could not load the model(s) "
                        "%s defined in the 'SEARCH_MODEL_CHOICES' setting."
                        % ", ".join(errors))

            for model in get_models():
                # Model is actually a subclasses of what we're
                # searching (eg Displayabale)
                is_subclass = issubclass(model, self.model)
                # Model satisfies the search choices list - either
                # there are no search choices, model is directly in
                # search choices, or its parent is.
                this_parents = set(model._meta.get_parent_list())
                in_choices = not search_choices or model in search_choices
                in_choices = in_choices or this_parents & search_choices
                if is_subclass and (in_choices or not search_choices):
                    # Add to models we'll seach. Also maintain a parent
                    # set, used below for further refinement of models
                    # list to search.
                    models.add(model)
                    parents.update(this_parents)
            # Strip out any models that are superclasses of models,
            # specifically the Page model which will generally be the
            # superclass for all custom content types, since if we
            # query the Page model as well, we will get duplicate
            # results.
            models -= parents
        else:
            models = [self.model]
        all_results = []
        user = kwargs.pop("for_user", None)
        for model in models:
            try:
                queryset = model.objects.published(for_user=user)
            except AttributeError:
                queryset = model.objects.get_query_set()
            all_results.extend(queryset.search(*args, **kwargs))
        return sorted(all_results, key=lambda r: r.result_count, reverse=True)


class CurrentSiteManager(DjangoCSM):
    """
    Extends Django's site manager to first look up site by ID stored in
    the request, the session, then domain for the current request
    (accessible via threadlocals in ``mezzanine.core.request``), the
    environment variable ``MEZZANINE_SITE_ID`` (which can be used by
    management commands with the ``--site`` arg, finally falling back
    to ``settings.SITE_ID`` if none of those match a site.
    """

    def __init__(self, field_name=None, *args, **kwargs):
        super(DjangoCSM, self).__init__(*args, **kwargs)
        self.__field_name = field_name
        self.__is_validated = False

    def get_query_set(self):
        if not self.__is_validated:
            try:
                # Django <= 1.6
                self._validate_field_name()
            except AttributeError:
                # Django >= 1.7: will populate "self.__field_name".
                self._get_field_name()
        lookup = {self.__field_name + "__id__exact": current_site_id()}
        return super(DjangoCSM, self).get_query_set().filter(**lookup)


class DisplayableManager(CurrentSiteManager, PublishedManager,
                         SearchableManager):
    """
    Manually combines ``CurrentSiteManager``, ``PublishedManager``
    and ``SearchableManager`` for the ``Displayable`` model.

    """

    def url_map(self, for_user=None, **kwargs):
        """
        Returns a dictionary of urls mapped to Displayable subclass
        instances, including a fake homepage instance if none exists.
        Used in ``mezzanine.core.sitemaps``.
        """
        home = self.model(title=_("Home"))
        setattr(home, "get_absolute_url", home_slug)
        items = {home.get_absolute_url(): home}
        for model in get_models():
            if issubclass(model, self.model):
                for item in (model.objects.published(for_user=for_user)
                                  .filter(**kwargs)
                                  .exclude(slug__startswith="http://")
                                  .exclude(slug__startswith="https://")):
                    items[item.get_absolute_url()] = item
        return items
