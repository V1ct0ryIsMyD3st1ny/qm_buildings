from tkinter import messagebox as mb
from typing import List, Optional, Callable
from sqlalchemy import create_engine
from sqlalchemy import insert, delete
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.engine import Engine
from geoalchemy2.types import Geometry
from geoalchemy2.shape import WKTElement
import qm_buildings.file_loader as fl
import qm_buildings.settings as settings
import pandas as pd
import os
import functools as func



class Base(DeclarativeBase):
    pass


class LookupBuilding(Base):
    __tablename__ = "lookup_buildings"

    hauskey: Mapped[int] = mapped_column(primary_key=True)
    zgb: Mapped[str]
    depot: Mapped[int]
    nr: Mapped[int]
    location: Mapped[str] = mapped_column(Geometry(geometry_type="POINT", srid=2056))

    search_buildings: Mapped[List["SearchBuilding"]] = relationship(back_populates="lookup_building")

    def __repr__(self) -> str:
        return f"Building(hauskey={self.hauskey})"
    

class SearchBuilding(Base):
    __tablename__ = "search_buildings"

    hauskey: Mapped[int] = mapped_column(primary_key=True)
    street: Mapped[str]
    house_number: Mapped[str]
    location: Mapped[str] = mapped_column(Geometry(geometry_type="POINT", srid=2056))
    lookup_hauskey: Mapped[Optional[List[int]]] = mapped_column(ForeignKey("lookup_buildings.hauskey"), nullable=True)

    lookup_building: Mapped["LookupBuilding"] = relationship(back_populates="search_buildings")

    def __repr__(self) -> str:
        return f"Building(hauskey={self.hauskey})"

def create_sessionmaker() -> sessionmaker:
    pwd = os.environ.get("POSTGRES_PWD")
    engine = create_engine("postgresql+psycopg2://postgres:"+pwd+"@localhost:5432/Datenmanagement")
    SessionLocal = sessionmaker(engine)
    return SessionLocal


def setup_tables() -> None:
    pwd = os.environ.get("POSTGRES_PWD")
    engine = create_engine("postgresql+psycopg2://postgres:"+pwd+"@localhost:5432/Datenmanagement")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    

def populate_lookup_buildings(session: Session) -> None:

    lookup_columns = settings.LOOKUP_COLUMNS
    x_coord, y_coord = lookup_columns[-2], lookup_columns[-1]
    
    #Open a file containing the lookup columns
    validator = func.partial(fl.validate_file_columns, expected_columns=lookup_columns)
    filename = fl.load_files(validator)

    df = pd.read_csv(filename, sep=";", header=0, encoding='utf-8', low_memory=False)
    df = df[lookup_columns]
    df[x_coord] = df[x_coord]
    df[y_coord] = df[y_coord]

    df['location'] = df.apply(
        lambda row: WKTElement(f"POINT({row[x_coord]} {row[y_coord]})", srid=2056),
        axis=1
    )

    df = df[lookup_columns[:-2] + ['location']]
    df.rename(columns=settings.lookup_mapper, inplace=True)

    records = df.to_dict(orient='records')
    
    session.execute(delete(LookupBuilding))
    session.execute(insert(LookupBuilding), records)
    print('QM Import successful')


def populate_search_buildings(session: Session) -> None:

    search_columns = settings.SEARCH_COLUMNS
    x_coord, y_coord = search_columns[-1], search_columns[-2]
    
    #Open a file containing the lookup columns
    validator = func.partial(fl.validate_file_columns, expected_columns=search_columns)
    filename = fl.load_files(validator)

    df = pd.read_csv(filename, sep=";", header=0, encoding='utf-8', low_memory=False)
    df = df[search_columns]

    df['location'] = df.apply(
        lambda row: WKTElement(f"POINT({row[x_coord]} {row[y_coord]})", srid=2056),
        axis=1
    )

    df = df[search_columns[:-2] + ['location']]
    df.rename(columns=settings.search_mapper, inplace=True)

    records = df.to_dict(orient='records')

    session.execute(delete(SearchBuilding))
    session.execute(insert(SearchBuilding), records)
    print('Post Import successful')



