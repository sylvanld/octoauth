"""
Defines functions to send emails (that can be used as event handlers)
"""
from octoauth.architecture.mailing import EmailBuilder, EmailTemplateFactory
from octoauth.domain.accounts.dtos import AccountSummaryDTO

email_templates_factory = EmailTemplateFactory("octoauth/domain/accounts/mail_templates")


def send_welcome_email(account: AccountSummaryDTO):
    (
        EmailBuilder(email_templates_factory)
        .set_subject("Welcome on Sortify!")
        .set_body_from_template("welcome.html", username=account.username)
        .send(account.email)
    )


def send_account_deleted_email(account: AccountSummaryDTO):
    (
        EmailBuilder(email_templates_factory)
        .set_subject("Your Sortify account has been deleted.")
        .set_body_from_template("account-deleted.html", username=account.username)
        .send(account.email)
    )
