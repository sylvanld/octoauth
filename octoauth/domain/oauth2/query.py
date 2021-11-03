from octoauth.architecture.query import QueryParserBuilder
from octoauth.domain.oauth2.database import Application

parse_application_query = (
    QueryParserBuilder()
    .enable_contains_filtering_on(Application.name)
    .enable_contains_filtering_on(Application.description)
    .build()
)
