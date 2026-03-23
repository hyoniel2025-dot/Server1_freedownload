from sqlalchemy import Column, Integer, String
from database import Base

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    path = Column(String)
    size = Column(Integer)
    chunks = Column(String)
    compressed_parts = Column(String)
    link_id = Column(String, unique=True)