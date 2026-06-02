from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Click(Base):
    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(String, nullable=False, index=True)
    source = Column(String, nullable=False)
    affiliate_network = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


# To create tables: Base.metadata.create_all(bind=engine)
