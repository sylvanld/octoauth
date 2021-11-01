from octoauth.architecture.query import QueryParserBuilder

from .database import Account

parse_accounts_query = (
    QueryParserBuilder().enable_equals_filtering_on(Account.username).enable_full_filtering_on(Account.email).build()
)
