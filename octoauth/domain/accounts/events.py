"""
Defines events that happens on accounts, and bind listener to these events
"""
from octoauth.architecture.patterns import EventBus
from octoauth.domain.accounts.mailing import send_account_deleted_email, send_welcome_email
from octoauth.settings import SETTINGS

# define kinds of events that can happens on accounts

ACCOUNT_CREATED = "account:created"
ACCOUNT_UPDATED = "account:updated"
ACCOUNT_DELETED = "account:deleted"

# event bus listener can subscribe to be notified on account event

event_bus = EventBus()

if SETTINGS.MAILING_ENABLED:
    event_bus.subscribe(ACCOUNT_CREATED, send_welcome_email)
    event_bus.subscribe(ACCOUNT_DELETED, send_account_deleted_email)
