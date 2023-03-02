from sqlalchemy import Boolean, Column, DateTime, Integer, String

from .config import Base

import datetime


class User(Base):
    __tablename__ = "users6"

    id = Column(Integer, primary_key=True, index=True)
    numOfPass = Column(Integer)
    numberPlate = Column(String)
    plateImg = Column(String)
    licenseImg = Column(String)    # url of image location
    expiry_date = Column(String)

    # url of image location
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)


class Driver(Base):
    __tablename__ = "driver5"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    license_img = Column(String)    # url of image location
    expiry_date = Column(String)
    finger_id = Column(Integer)
