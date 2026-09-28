from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from supplynode.utils.config import DATABASE_URL


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)