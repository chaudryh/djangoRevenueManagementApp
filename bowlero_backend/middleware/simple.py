from django.utils.deprecation import MiddlewareMixin


class simpleMiddleware(MiddlewareMixin):

    def process_request(self, request):
        return None

    # def process_response(self, request, response):
    #     return response
