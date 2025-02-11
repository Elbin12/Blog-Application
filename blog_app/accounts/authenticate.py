from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken




class CustomAuthentication(JWTAuthentication):
    def authenticate(self, request):
        print('jjiijji')
        header = self.get_header(request)

        if header is None:
            print('jiii')
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
            print(raw_token, type(raw_token))
        else:
            raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
        
        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except Exception as e:
            print(e, 'e')
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token is None:
                    raise AuthenticationFailed('Authentication credentials were not provided.')
            try:
                print('hi')
                print('vall')
                new_access_token = str  (RefreshToken(refresh_token).access_token)
                print(new_access_token, 'new')
                validated_token = self.get_validated_token(new_access_token)
                print('kk')
                request.META['NEW_ACCESS_TOKEN'] = new_access_token
                request.user = self.get_user(validated_token)
                print('kl')
                return self.get_user(validated_token), validated_token
            except Exception as e:
                print('eee', e)
                raise AuthenticationFailed('Token refresh failed.')