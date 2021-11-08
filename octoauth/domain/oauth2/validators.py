from .dtos import TokenRequestDTO


class TokenRequestValidator:
    """
    Helper class that provides methods to parse token requests and ensure it is complete.
    """

    @staticmethod
    def validate_authorization_code(request: TokenRequestDTO):
        """
        Ensure request contains all params required in authorizaton_code request.
        """
        print(request)
        # structural checks
        if request.code is None:
            raise ValueError("Missing mandatory body param for flow 'authorization_code': 'code'.")
        elif request.redirect_uri is None:
            raise ValueError("Missing mandatory body param for flow 'authorization_code': 'redirect_uri'.")
        elif request.client_secret is None and request.code_verifier is None:
            raise ValueError(
                "Missing PKCE body param for flow 'authorization_code' without 'client_secret': 'code_verifier'"
            )

    @staticmethod
    def validate_client_credentials(request: TokenRequestDTO):
        """
        Ensure request contains all params required in client_credentials request.
        """

    @staticmethod
    def validate_refresh_token(request: TokenRequestDTO):
        """
        Ensure request contains all params required in refresh_token request.
        """
