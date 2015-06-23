from rest_framework.authentication import TokenAuthentication


class UrlTokenAuthentication(TokenAuthentication):

    def authenticate(self, request):
        token = None
        if 'token' in request.GET:
            token = request.GET['token']
            return self.authenticate_credentials(token)
        else:
            return (None, None)
