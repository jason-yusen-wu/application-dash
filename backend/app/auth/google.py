"""Google OAuth2 + Gmail readonly credential handling.

Boilerplate/plumbing only, per worklog.md's scope split: no handling here
for a denied consent screen, an expired/revoked refresh_token, or any
other failure path — those are being built separately.
"""

from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2 import id_token as google_id_token
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.db import User, get_db

router = APIRouter(prefix="/auth/google", tags=["auth"])

# Readonly is the only scope this app needs — it never sends or modifies mail.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "openid"]

# Must exactly match a redirect URI registered on the OAuth client in the
# Google Cloud console, or the token exchange in /callback will be rejected.
REDIRECT_URI = f"{settings.backend_base_url}/auth/google/callback"


def _build_flow() -> Flow:
    """Builds the OAuth2 flow object used by both /login (to generate the
    consent-screen URL) and /callback (to exchange the returned code)."""
    return Flow.from_client_config(
        {
            "web": {
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )


@router.get("/login")
def login():
    flow = _build_flow()

    # access_type="offline" is what makes Google issue a refresh_token at
    # all — without it you only ever get a short-lived access token back.
    # prompt="consent" forces the consent screen even for a user who has
    # already granted access before, which forces Google to issue a *new*
    # refresh_token on every login. Google's default behavior is to only
    # issue one on a user's very first authorization ever, which would
    # otherwise mean /callback sometimes has no refresh_token to store.
    # Trade-off: the user sees the consent screen on every login, not just
    # the first — acceptable here to keep the callback's storage logic
    # simple (see the User.refresh_token discussion in db_schema.md).
    authorization_url, _state = flow.authorization_url(
        access_type="offline",
        prompt="consent",  # change this, the user shouldn't need to consent every log-in
        include_granted_scopes="true",
    )
    # TODO: use `_state` for CSRF (how?)
    return RedirectResponse(authorization_url)


@router.get("/callback")
def callback(code: str, db: Session = Depends(get_db)):
    # Note: Google redirects here with `error=` instead of `code` if the
    # user denies consent — requiring `code` means FastAPI's own request
    # validation rejects that case with a 422 rather than this function
    # trying to proceed without one. Handling that gracefully is left to you.
    flow = _build_flow()

    # Exchanges the one-time authorization code for real tokens.
    flow.fetch_token(code=code)
    credentials = flow.credentials

    # id_token is a signed JWT identifying the Google account. Verifying it
    # (rather than trusting it unchecked) confirms Google actually issued it
    # for our client_id, and gives us `sub` — the stable account identifier
    # users are keyed on (see db_schema.md for why not email).
    claims = google_id_token.verify_oauth2_token(
        credentials.id_token, GoogleAuthRequest(), settings.google_client_id
    )
    google_sub = claims["sub"]

    user = db.query(User).filter(User.google_sub == google_sub).one_or_none()
    if user is None:
        user = User(google_sub=google_sub, refresh_token=credentials.refresh_token)
        db.add(user)
    else:
        user.refresh_token = credentials.refresh_token
    db.commit()

    return {"user_id": user.id}


def build_credentials(user: User) -> Credentials:
    """Reconstructs usable Credentials from a stored refresh_token. There's
    no cached access token to start from — the first API call made with
    these credentials will use the refresh_token to obtain one."""
    return Credentials(
        token=None,
        refresh_token=user.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=SCOPES,
    )


def build_gmail_service(user: User):
    """Returns an authenticated, readonly Gmail API client for this user."""
    return build("gmail", "v1", credentials=build_credentials(user))
