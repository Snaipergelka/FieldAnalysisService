from sqlalchemy import JSON, Column, Integer, String

from .database_config import Base


class Fields(Base):
    __tablename__ = "field_data"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    geo_json = Column(JSON)
    ndvi = Column(String, default=None)
    status = Column(String)
