from __future__ import unicode_literals

import threading

from mezzanine.utils.deprecation import MiddlewareMixin


_thread_local = threading.local()


def current_request():
    """
    Retrieves the request from the current thread.
    """
    return getattr(_thread_local, "request", None)


class CurrentRequestMiddleware(MiddlewareMixin):
    """
    Stores the request in the current thread for global access.
    """

    def process_request(self, request):
        _thread_local.request = request

    # def process_response(self, request, response):
    #     try:
    #         return response
    #     finally:
    #         _thread_local.request = None
