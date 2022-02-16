from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    BLOB,
    ForeignKey,
    DateTime,
    Enum,
    ARRAY
)
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from datetime import datetime

datetime.utcnow()

BaseModel = declarative_base()
metadata = BaseModel.metadata
mysql_engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres", encoding="utf-8", echo=True,
                             future=True)
Session = sessionmaker(bind=mysql_engine)
session = Session()


class User(BaseModel):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(45), nullable=False)  # unique=True
    email = Column(String(45), nullable=False)
    password = Column(String(160), nullable=False)
    city = Column(String(40), nullable=False)
    photo = Column(String(250), nullable=True)
    genre_id = Column(ARRAY(String(250)), nullable=False)
    artist_id = Column(ARRAY(String(250)), nullable=False)
    track_id = Column(ARRAY(String(250)), nullable=True)


class Friends(BaseModel):
    __tablename__ = "friends"

    user_id_1 = Column(Integer, ForeignKey('user.id'),
                       nullable=False, primary_key=True)
    user_id_2 = Column(Integer, ForeignKey('user.id'),
                       nullable=False, primary_key=True)
    status = Column(String, nullable=False, default='new')


class Wall(BaseModel):
    __tablename__ = "wall"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'),
                     nullable=False)  # 'user_id'
    genre_id = Column(Integer, ForeignKey('genre.id'),
                      nullable=False)  # 'genre_id'
    datetime = Column(DateTime, nullable=False, default=datetime.utcnow())
    text = Column(String(500), nullable=False)
    photo_wall = Column(String(250), nullable=True)


class Genre(BaseModel):
    __tablename__ = "genre"
    id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)


class Artist(BaseModel):
    __tablename__ = "artist"
    id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
