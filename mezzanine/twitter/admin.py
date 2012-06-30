# admin interface for mezzanine twitter app including topics

from django.contrib import admin

from mezzanine.twitter.models import Query, Tweet, Topic


class QueryAdmin(admin.ModelAdmin):
    """
    Admin class for twitter queries.
    """
    pass


class TopicAdmin(admin.ModelAdmin):
    """
    Admin class for twitter topics.
    """
    pass


admin.site.register(Query, QueryAdmin)
admin.site.register(Topic, TopicAdmin)
