import sys
from django.views.debug import technical_500_response
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class UserBasedExceptionMiddleware(MiddlewareMixin):
    # def process_exception(self, request, exception):
    #     return None

    def process_response(self, request, response):
        # if request.user.is_superuser or request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
        #     return technical_500_response(request, *sys.exc_info())
        return response