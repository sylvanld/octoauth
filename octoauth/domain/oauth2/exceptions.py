class Oauth2Exception(Exception):
    ...


class AuthenticationError(Oauth2Exception):
    ...


class ScopesNotGrantedError(Oauth2Exception):
    ...
