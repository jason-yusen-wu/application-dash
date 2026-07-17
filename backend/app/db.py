from typing import Optional
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    create_engine,
    Text,
    BigInteger,
    DateTime,
    UniqueConstraint,
    CheckConstraint,
    ForeignKey,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    type_annotation_map = {datetime: DateTime(timezone=True)}


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    google_sub: Mapped[str] = mapped_column(String(255))
    refresh_token: Mapped[str] = mapped_column(Text)
    last_history_id: Mapped[Optional[int]] = mapped_column(BigInteger)

    __table_args__ = (UniqueConstraint("google_sub"),)


status_enum_list = ["submitted", "OA", "interview", "offer", "rejected"]
status_enum_list_string = ", ".join([f"'{enum}'" for enum in status_enum_list])


class AppStatus(Base):
    __tablename__ = "application_status"

    status: Mapped[str] = mapped_column(String(255), primary_key=True)
    __table_args__ = (
        CheckConstraint(f"status IN ({status_enum_list_string})", "ck_status_valid"),
    )


class Applications(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    company_name: Mapped[str] = mapped_column(String(255))
    job_title: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(
        String(255), ForeignKey("application_status.status")
    )
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    # implicit DateTime type with timezone=True (see Base)
    updated_at: Mapped[datetime] = mapped_column()
    applied_at: Mapped[datetime] = mapped_column()


class AppEvents(Base):
    __tablename__ = "application_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"))
    gmail_message_id: Mapped[str] = mapped_column(String(255))
    inferred_status: Mapped[str] = mapped_column(
        String(255), ForeignKey("application_status.status")
    )
    # implicit DateTime type with timezone=True (see Base)
    received_at: Mapped[datetime] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (UniqueConstraint("gmail_message_id"),)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
