from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication, exceptions


class UrlTokenAuthentication(TokenAuthentication):

    def authenticate(self, request):
        token = None
        if 'token' in request.GET:
            token = request.GET['token']
            return self.authenticate_credentials(token)
        else:
            return (None, None)
