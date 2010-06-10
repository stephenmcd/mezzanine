
from datetime import datetime

from django.db.models import Manager

from mezzanine.settings import CONTENT_STATUS_PUBLISHED


class PublishedManager(Manager):
    """
    Provides filter for restricting items returned by status and publish date 
    when the given user is not a staff member.
    """
    
    def published(self, for_user=None):
        if for_user is not None and for_user.is_staff:
            return self.all()
        return self.filter(status=CONTENT_STATUS_PUBLISHED, 
            publish_date__lte=datetime.now())
