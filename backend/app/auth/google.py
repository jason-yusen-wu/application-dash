from fastapi import APIRouter

router = APIRouter(prefix="/auth/google", tags=["auth"])


@router.get("/login")
def login():
    """Kick off the Google OAuth2 flow requesting readonly Gmail access.

    Intentionally not implemented — the OAuth flow, token exchange, and
    encrypted refresh-token storage are left to you.
    """
    raise NotImplementedError


@router.get("/callback")
def callback(code: str | None = None):
    """Handle Google's OAuth2 redirect and exchange the code for tokens."""
    raise NotImplementedError
