from django.conf import settings
from django.shortcuts import redirect

class TokenRefreshMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        new_access_token = request.META.get('NEW_ACCESS_TOKEN', None)
        if new_access_token:
            print('from middleware', new_access_token)
            response.set_cookie(
                key = settings.SIMPLE_JWT['AUTH_COOKIE'],
                value = new_access_token,
                secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )
        return response
    
class RedirectOn401Middleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 401:
            return redirect('home')
        return response