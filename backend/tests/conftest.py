import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base, AppStatus, status_enum_list

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://appdash:appdash@localhost:5432/appdash_test",
)


@pytest.fixture(scope="session")
def engine():
    return create_engine(TEST_DATABASE_URL)


@pytest.fixture(scope="session", autouse=True)
def create_schema(engine):
    """Creates every table on app.db.Base once for the whole test run.

    Add your own models' tables here implicitly just by importing them into
    app.db — anything registered on Base gets created automatically.
    """
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


status_records = [AppStatus(status=status) for status in status_enum_list]


@pytest.fixture
def db_session(engine):
    """A session bound to a connection-level transaction that's rolled back
    after the test, so nothing a test writes ever actually persists —
    tests stay isolated without truncating tables between runs.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    """ Add status enums as a lookup table """
    session.add_all(status_records)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
