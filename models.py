from typing import Text
# import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    BLOB,
    ForeignKey,
    DateTime
)
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from datetime import datetime

datetime.utcnow()

BaseModel = declarative_base()
metadata = BaseModel.metadata
mysql_engine = create_engine("mysql+pymysql://root:Bonia9977@localhost/muscon", encoding="utf-8", echo=True,
                             future=True)
Session = sessionmaker(bind=mysql_engine)
session = Session()


class User(BaseModel):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(45), nullable=False, unique=True)
    email = Column(String(45), nullable=False)
    password = Column(String(60), nullable=False)
    city = Column(String(40), nullable=False)
    photo = Column(BLOB, nullable=True)


class Wall(BaseModel):
    __tablename__ = "wall"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('User.id'), nullable=False) # 'user_id'
    username = Column(String(45), ForeignKey('User.username'), nullable=False, unique=True) # 'username'
    photo = Column(BLOB, ForeignKey('photo'), nullable=True)
    genre_id = Column(Integer, ForeignKey('Genre.id'), nullable=False) # 'genre_id'
    datetime = Column(DateTime, nullable=False, default=datetime.utcnow())
    text = Column(String(500), nullable=False)
    photo_wall = Column(BLOB, nullable=True)


class Genre(BaseModel):
    __tablename__ = "genre"
    id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
