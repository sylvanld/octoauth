import pytest

from octoauth.domain.oauth2.dtos import TokenRequestDTO, TokenRequestWithAuthorizationCodeDTO
from octoauth.domain.oauth2.parsers import TokenRequestParser


class TestAuthorizationCodeParser:
    def test_parse_valid_request_without_pkce(self):
        """
        Ensure a valid request with authorization_code flow is parsed without errors.
        """
        request = TokenRequestParser.parse_authorization_code(
            TokenRequestDTO(
                client_id="sortify",
                client_secret="sortify-secret",
                code="f4ez84fez4f5ez4f8zf54ez4f5ez4fez5",
                redirect_uri="http://sortify.io/authorized",
            )
        )
        assert isinstance(request, TokenRequestWithAuthorizationCodeDTO)

    def test_parse_valid_request_with_pkce(self):
        """
        Ensure a valid request with authorization_code flow and PKCE is parsed without errors.
        """
        request = TokenRequestParser.parse_authorization_code(
            TokenRequestDTO(
                client_id="sortify",
                client_secret=None,
                code="f4ez84fez4f5ez4f8zf54ez4f5ez4fez5",
                redirect_uri="http://sortify.io/authorized",
                code_verifier="code-verifier",
            )
        )
        assert isinstance(request, TokenRequestWithAuthorizationCodeDTO)

    def test_exception_when_client_secret_and_code_verifier_missing(self):
        """
        Ensure request fails if no client_secret nor code_verifier is provided.
        This means that PKCE is mandatory for clients that can't use client_secret.
        """
        with pytest.raises(ValueError):
            TokenRequestParser.parse_authorization_code(
                TokenRequestDTO(
                    client_id="sortify",
                    client_secret=None,
                    code="f4ez84fez4f5ez4f8zf54ez4f5ez4fez5",
                    redirect_uri="http://sortify.io/authorized",
                )
            )

    def test_exception_when_code_missing(self):
        """
        Ensure an error is raised when code is missing in authorization_code flow.
        """
        with pytest.raises(ValueError):
            TokenRequestParser.parse_authorization_code(
                TokenRequestDTO(
                    client_id="sortify",
                    client_secret=None,
                    code=None,
                    redirect_uri="http://sortify.io/authorized",
                )
            )

    def test_exception_when_redirect_uri_missing(self):
        """
        Ensure an error is raised when redirect_uri is missing in authorization_code flow.
        """
        with pytest.raises(ValueError):
            TokenRequestParser.parse_authorization_code(
                TokenRequestDTO(
                    client_id="sortify",
                    client_secret=None,
                    code="f4ez84fez4f5ez4f8zf54ez4f5ez4fez5",
                    redirect_uri=None,
                )
            )
