from __future__ import unicode_literals

import time
import pytz
import datetime


def get_best_local_timezone():
    """
    Compares local timezone offset to pytz's timezone db, to determine
    a matching timezone name to use when TIME_ZONE is not set.
    """
    if time.daylight:
        local_offset = time.altzone
        localtz = time.tzname[1]
    else:
        local_offset = time.timezone
        localtz = time.tzname[0]
    local_offset = datetime.timedelta(seconds=-local_offset)
    for name in pytz.all_timezones:
        timezone = pytz.timezone(name)
        if not hasattr(timezone, '_tzinfos'):
            continue
        for utcoffset, daylight, tzname in timezone._tzinfos:
            if utcoffset == local_offset and tzname == localtz:
                return name
