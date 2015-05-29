from rest_framework.authentication import TokenAuthentication, exceptions


class UrlTokenAuthentication(TokenAuthentication):

    def authenticate(self, request):
        token = request.GET.get('token', '')
        if not token:
            raise exceptions.AuthenticationFailed('Please supply a token')
        return self.authenticate_credentials(token)
