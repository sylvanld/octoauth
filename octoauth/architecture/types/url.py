import re

URL_PATTERN = re.compile(
    r"^(?:http|ftp)s?://"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


def validate_url(url_string: str) -> str:
    if not isinstance(url_string, str):
        raise TypeError("Email must be a string")

    match = URL_PATTERN.match(url_string)
    if match is None:
        raise TypeError("Invalid email format")

    return url_string


class URL(str):
    """
    Defines a new type that can be used in a pydantic schema to validate URLs strings.
    """

    @classmethod
    def __get_validators__(cls):
        yield validate_url

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            example="https://cdn.icon-icons.com/icons2/2643/PNG/512/male_boy_person_people_avatar_icon_159358.png",
        )
