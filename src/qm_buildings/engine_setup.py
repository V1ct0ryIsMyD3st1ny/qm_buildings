from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
import os





def local_engine() -> Engine:
    pwd = os.environ.get("POSTGRES_PWD")
    engine = create_engine("postgresql+psycopg2://postgres:"+pwd+"@localhost:5432/Datenmanagement")
    return engine


def create_sessionmaker(engine: Engine) -> sessionmaker:
    SessionLocal = sessionmaker(engine)
    return SessionLocal


def setup_tables(Base: type[DeclarativeBase], engine: Engine) -> None:
    pwd = os.environ.get("POSTGRES_PWD")
    engine = create_engine("postgresql+psycopg2://postgres:"+pwd+"@localhost:5432/Datenmanagement")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
