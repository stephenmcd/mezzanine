from inspect import getmro

from django import VERSION


if VERSION < (1, 6):

    def renamed_get_queryset(cls):
        """
        On classes and their bases with ``get_queryset`` defines
        ``get_query_set`` to preserve compatibility with Django 1.5, on
        those with ``get_query_set`` defines ``get_queryset``, so calls
        to the latter one can be always used.

        Compare with ``django.utils.deprecation.RenameMethodsBase``.
        """
        for base in getmro(cls):
            old_method = base.__dict__.get("get_query_set")
            new_method = base.__dict__.get("get_queryset")
            if not old_method and new_method:
                setattr(base, "get_query_set", new_method)
            elif not new_method and old_method:
                setattr(base, "get_queryset", old_method)
        return cls

else:

    def renamed_get_queryset(cls):
        return cls
