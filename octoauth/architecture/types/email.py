import re

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")


def validate_email(email_string: str):
    if not isinstance(email_string, str):
        raise TypeError("Email must be a string")

    match = EMAIL_PATTERN.match(email_string)
    if match is None:
        raise TypeError("Invalid email format")

    return email_string


class Email(str):
    """
    Defines a new type that can be used in a pydantic schema to validate email strings.
    """

    @classmethod
    def __get_validators__(cls):
        yield validate_email

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            example="toto@example.com",
        )
