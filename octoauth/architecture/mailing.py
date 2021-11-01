import smtplib
import uuid
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Sequence, Union

from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.environment import Template

from octoauth.settings import SETTINGS


class EmailTemplateFactory:
    """
    Class used to load template from a directory
    """

    def __init__(self, templates_path: str):
        self.templating_environment = Environment(
            loader=FileSystemLoader(searchpath=templates_path, encoding="utf-8"),
            autoescape=select_autoescape(),
        )

    def get_template(self, template_name: str) -> Template:
        """
        Get mail template using jinja environment loader.
        Cache is already performed by the underlying library.
        """
        return self.templating_environment.get_template(template_name)


class EmailBuilder:
    def __init__(builder, templates_factory: EmailTemplateFactory = None):
        builder.email = MIMEMultipart()
        builder.templates_factory = templates_factory

    def set_subject(builder, subject: str):
        builder.email["Subject"] = subject
        return builder

    def set_body_from_template(builder, template_name: str, **context):
        if builder.templates_factory is None:
            raise NotImplementedError(
                "You must pass a TemplateFactory to this builder in order to set body from template"
            )

        mail_template = builder.templates_factory.get_template(template_name)
        mail_body = mail_template.render(embed_image=builder.attach_image, **context)
        builder.email.attach(MIMEText(mail_body, "html"))
        return builder

    def attach_image(builder, image_name: str):
        attachment_uid = str(uuid.uuid4())
        with open(image_name, "rb") as image_file:
            image = MIMEImage(image_file.read())
        image.add_header("Content-ID", attachment_uid)
        builder.email.attach(image)
        return attachment_uid

    def send(builder, recipient: Union[str, Sequence[str]]):
        builder.email["To"] = recipient if type(recipient) is str else ";".join(recipient)

        with smtplib.SMTP(SETTINGS.SMTP_HOST, SETTINGS.SMTP_PORT) as smtp_server:
            smtp_server.starttls()
            smtp_server.login(SETTINGS.SMTP_USERNAME, SETTINGS.SMTP_PASSWORD)
            smtp_server.sendmail(SETTINGS.SMTP_USERNAME, recipient, builder.email.as_string())
