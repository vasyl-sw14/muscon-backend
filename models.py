from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    BLOB
)
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

BaseModel = declarative_base()
metadata = BaseModel.metadata
mysql_engine = create_engine("mysql+pymysql://root:1234432aat@localhost/muscon", encoding="utf-8", echo=True, future=True)
Session = sessionmaker(bind=mysql_engine)
session = Session()

class User(BaseModel):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(45),nullable=False, unique=True)
    email = Column(String(45),nullable=False)
    password = Column(String(60),nullable=False)
    city = Column(String(40),nullable=False)
    photo = Column(BLOB, nullable = True)