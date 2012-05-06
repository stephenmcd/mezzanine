
# Timezone support with fallback.
try:
    from django.utils.timezone import (now, get_default_timezone,
                                       make_aware as django_make_aware)
except ImportError:
    from datetime import datetime
    now = datetime.now
    make_aware = lambda v: v
else:
    make_aware = lambda v: django_make_aware(v, get_default_timezone())
