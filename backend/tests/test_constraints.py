from .conftest import status_records
from datetime import datetime, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from app.db import User, Application, AppEvent


def get_valid_user_kwargs(db_session):
    return {
        "google_sub": "j4s0n-wu-12345",
        "refresh_token": "refr3sh_m3",
    }


def get_valid_app_kwargs(db_session):
    user = User(google_sub="j4s0n-wu-12345", refresh_token="refr3sh_m3")
    db_session.add(user)
    db_session.flush()

    return {
        "user_id": user.id,
        "company_name": "GitHub",
        "job_title": "Site Unreliability Engineer",
        "status": status_records[0].status,
        "updated_at": datetime.now(timezone.utc),
        "applied_at": datetime.now(timezone.utc),
    }


def get_valid_app_event_kwargs(db_session):
    user = User(google_sub="j4s0n-wu-12345", refresh_token="refr3sh_m3")
    db_session.add(user)
    db_session.flush()

    app = Application(
        user_id=user.id,
        company_name="GitHub",
        job_title="Site Unreliability Engineer",
        status=status_records[0].status,
        updated_at=datetime.now(timezone.utc),
        applied_at=datetime.now(timezone.utc),
    )
    db_session.add(app)
    db_session.flush()

    return {
        "application_id": app.id,
        "gmail_message_id": "message_id_12345",
        "inferred_status": status_records[0].status,
        "received_at": datetime.now(timezone.utc),
    }


# parameterized "rejects null" test (FKs, statuses, google_sub, gmail_message_id)
@pytest.mark.parametrize(
    "model, valid_kwargs, missing_field",
    [
        (User, get_valid_user_kwargs, "google_sub"),
        (AppEvent, get_valid_app_event_kwargs, "gmail_message_id"),
        (Application, get_valid_app_kwargs, "status"),
        (AppEvent, get_valid_app_event_kwargs, "inferred_status"),
        (Application, get_valid_app_kwargs, "user_id"),
        (AppEvent, get_valid_app_event_kwargs, "application_id"),
    ],
)
def test_required_field_rejects_null(db_session, model, valid_kwargs, missing_field):
    kwargs = valid_kwargs(db_session)
    kwargs[missing_field] = None

    db_session.add(model(**kwargs))
    with pytest.raises(IntegrityError):
        db_session.flush()


# CHECK enum
def test_status_is_valid_enum(db_session):
    bad_status_enum = "I_dont_exist"

    user = User(google_sub="j4s0n-wu-12345", refresh_token="refr3sh_m3")
    db_session.add(user)
    db_session.flush()

    app = Application(
        user_id=user.id,
        company_name="Anthropic",
        job_title="Member of Bubble Blowing Staff",
        status=bad_status_enum,
        updated_at=datetime.now(timezone.utc),
        applied_at=datetime.now(timezone.utc),
    )
    db_session.add(app)

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_inferred_status_is_valid_enum(db_session):
    bad_status_enum = "I_dont_exist"

    user = User(google_sub="j4s0n-wu-12345", refresh_token="refr3sh_m3")
    db_session.add(user)
    db_session.flush()

    app = Application(
        user_id=user.id,
        company_name="Anthropic",
        job_title="Member of Bubble Blowing Staff",
        status=status_records[0].status,
        updated_at=datetime.now(timezone.utc),
        applied_at=datetime.now(timezone.utc),
    )
    db_session.add(app)
    db_session.flush()

    appEvent = AppEvent(
        application_id=app.id,
        gmail_message_id="from_sam_4ltman-123",
        inferred_status=bad_status_enum,
        received_at=datetime.now(timezone.utc),
    )
    db_session.add(appEvent)

    with pytest.raises(IntegrityError):
        db_session.flush()


# test unique (google_sub)
def test_google_sub_rejects_dup(db_session):
    user1 = User(google_sub="j4s0n-wu-12345", refresh_token="refr3sh_m3")
    user2 = User(google_sub="j4s0n-wu-12345", refresh_token="refr3sh_y0u")

    db_session.add(user1)
    db_session.flush()

    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.flush()


# test unique (gmail_message_id)
def test_gmail_message_id_rejects_dup(db_session):
    user = User(google_sub="j4s0n-wu-12345", refresh_token="refr3sh_m3")
    db_session.add(user)
    db_session.flush()

    app = Application(
        user_id=user.id,
        company_name="Google",
        job_title="CEO",
        status=status_records[0].status,
        updated_at=datetime.now(timezone.utc),
        applied_at=datetime.now(timezone.utc),
    )
    db_session.add(app)
    db_session.flush()

    appEvent = AppEvent(
        application_id=app.id,
        gmail_message_id="h3llo-w0rld-12345",
        inferred_status=status_records[0].status,
        received_at=datetime.now(timezone.utc),
    )
    db_session.add(appEvent)
    db_session.flush()

    dupAppEvent = AppEvent(
        application_id=app.id,
        gmail_message_id="h3llo-w0rld-12345",
        inferred_status=status_records[0].status,
        received_at=datetime.now(timezone.utc),
    )
    db_session.add(dupAppEvent)
    with pytest.raises(IntegrityError):
        db_session.flush()


# test FK integrity (applications.user_id)
def test_app_user_id_integrity(db_session):
    db_session.add(
        Application(
            user_id=67,
            company_name="Snoogle",
            job_title="Senior Shoe-sniffer",
            status=status_records[0].status,
            updated_at=datetime.now(timezone.utc),
            applied_at=(datetime.now(timezone.utc)),
        )
    )

    with pytest.raises(IntegrityError):
        db_session.flush()


# test FK integrity (application_events.application_id)
def test_app_event_app_id_integrity(db_session):
    db_session.add(
        AppEvent(
            application_id=21,
            gmail_message_id="h3llo-w0rld-12345",
            inferred_status=status_records[0].status,
            received_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
        )
    )

    with pytest.raises(IntegrityError):
        db_session.flush()
