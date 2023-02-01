import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from core.settings import (
    SMTP_EMAIL_HOST,
    SMTP_EMAIL_PORT,
    SMTP_EMAIL_USER,
    SMTP_EMAIL_PASSWORD,
    EMAIL_RECIPIENTS
)


def send_email_with_attachments(parsed_link: str, paths: list[str]) -> None:
    """
        Sends an email with files.
        Args:
            parsed_link: Parsed link to specify it in message text
            paths: List of strings. Every string is an absolute path of a file to attach
        Raises:
            - AssertionError: Invalid `paths` argument
    """

    assert isinstance(paths, list), '`paths` parameter must be a list instance'

    message = MIMEMultipart()
    message['To'] = ', '.join(EMAIL_RECIPIENTS)
    message['From'] = f'Parser <{SMTP_EMAIL_USER}>'
    message['Subject'] = 'Информация о работе парсера.'
    message.attach(
        MIMEText(f'Парсер успешно отработал по ссылке {parsed_link}')
    )

    for path in paths:
        with open(path, 'rb') as f:
            message_part = MIMEApplication(
                f.read(),
                name=os.path.basename(f.name)
            )
            message_part['Content-Disposition'] = f'attachment; filename={os.path.basename(f.name)}'

        message.attach(message_part)

    with smtplib.SMTP_SSL(host=SMTP_EMAIL_HOST, port=SMTP_EMAIL_PORT) as smtp:
        smtp.login(
            user=SMTP_EMAIL_USER,
            password=SMTP_EMAIL_PASSWORD
        )
        smtp.send_message(
            msg=message,
            from_addr=SMTP_EMAIL_USER,
            to_addrs=EMAIL_RECIPIENTS
        )
