from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from .config import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    numOfPass = Column(Integer)
    numberPlate = Column(String)
    plateImg = Column(String)
