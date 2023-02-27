from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from .config import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    numOfPass = Column(Integer)
    numberPlate = Column(String)
    plateImg = Column(String)

class Driver(Base):
    __tablename__ = "driver5"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    license_img = Column(String)    # url of image location
    expiry_date = Column(String)
    finger_id = Column(Integer)