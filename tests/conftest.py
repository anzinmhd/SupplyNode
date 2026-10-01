import pytest
from sqlalchemy.orm import sessionmaker

from supplynode.utils.config import TEST_DATABASE_URL
from supplynode.utils.db import create_db_engine


@pytest.fixture
def test_session():
    engine = create_db_engine(TEST_DATABASE_URL)
    TestSessionLocal = sessionmaker(bind=engine)

    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()