"""Fetching and parsing Gmail messages via the Gmail API.

Boilerplate/plumbing only, per worklog.md's scope split: no retry,
rate-limit, or malformed-payload handling here. Any
googleapiclient.errors.HttpError raised by an `.execute()` call below
propagates unmodified to the caller.
"""

import base64
from datetime import datetime, timezone


def _get_header(headers: list[dict], name: str) -> str | None:
    # Gmail headers arrive as a flat list of {"name": ..., "value": ...}
    # dicts rather than a mapping, so a lookup means a linear scan.
    for header in headers:
        if header["name"].lower() == name.lower():
            return header["value"]
    return None


def _decode_base64url(data: str) -> str:
    # Gmail encodes body content as URL-safe base64 without guaranteeing
    # padding, so it has to be restored before decoding.
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded).decode("utf-8", errors="replace")


def _extract_plain_text_body(payload: dict) -> str:
    # A message's body is either directly on this part (simple messages) or
    # nested arbitrarily deep in payload["parts"] (multipart messages) —
    # walk the tree for the first text/plain part.
    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data")
        if data:
            return _decode_base64url(data)

    for part in payload.get("parts", []):
        body = _extract_plain_text_body(part)
        if body:
            return body

    return ""


def _parse_message(message: dict) -> dict:
    headers = message["payload"]["headers"]

    # internalDate is Gmail's own record of when it received the message
    # (milliseconds since epoch, UTC) — used instead of parsing the
    # free-text Date header, which is client-supplied and not reliably
    # formatted.
    received_date = datetime.fromtimestamp(
        int(message["internalDate"]) / 1000, tz=timezone.utc
    )

    return {
        "gmail_message_id": message["id"],
        "subject": _get_header(headers, "Subject"),
        "sender": _get_header(headers, "From"),
        "snippet": message.get("snippet", ""),
        "body": _extract_plain_text_body(message["payload"]),
        "received_date": received_date,
    }


def fetch_emails(service, query: str, max_results: int) -> list[dict]:
    """Searches Gmail with `query` (Gmail search syntax, e.g.
    "newer_than:7d subject:application") and returns up to `max_results`
    parsed messages, handling pagination across list() calls.
    """
    message_refs = []
    page_token = None

    # messages().list() only returns {id, threadId} pairs — a separate
    # messages().get() call per message (below) is needed for real content.
    while len(message_refs) < max_results:
        response = (
            service.users()
            .messages()
            .list(
                userId="me",
                q=query,
                pageToken=page_token,
                maxResults=min(100, max_results - len(message_refs)),
            )
            .execute()
        )

        message_refs.extend(response.get("messages", []))
        page_token = response.get("nextPageToken")
        if not page_token:
            break

    emails = []
    for ref in message_refs[:max_results]:
        message = (
            service.users()
            .messages()
            .get(userId="me", id=ref["id"], format="full")
            .execute()
        )
        emails.append(_parse_message(message))

    return emails
