from anthropic import Anthropic

from app.config import settings

client = Anthropic(api_key=settings.anthropic_api_key)


def classify_email(subject: str, body: str) -> dict:
    """Infer the company and application status from an email.

    Intentionally not implemented — prompt design, the structured
    output schema, and how results feed the status state machine are
    left to you.
    """
    raise NotImplementedError
