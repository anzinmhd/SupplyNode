from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from supplynode.utils.config import DATABASE_URL


def create_db_engine(database_url: str):
    return create_engine(database_url)


engine = create_db_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)