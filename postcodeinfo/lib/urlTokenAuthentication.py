from rest_framework.authentication import TokenAuthentication, exceptions


class UrlTokenAuthentication(TokenAuthentication):

    def authenticate(self, request):
        if 'token' not in request.GET:
            raise exceptions.AuthenticationFailed('Please supply a token')
        return self.authenticate_credentials(request.GET['token'])
