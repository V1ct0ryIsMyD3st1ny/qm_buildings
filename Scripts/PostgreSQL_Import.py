from typing import List
from sqlalchemy import create_engine
from sqlalchemy import insert, delete
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from geoalchemy2.types import Geometry
from geoalchemy2.shape import WKTElement
import pandas as pd
import os


class Base(DeclarativeBase):
    pass


class LookupBuilding(Base):
    __tablename__ = "lookup_buildings"

    hauskey: Mapped[int] = mapped_column(primary_key=True)
    location: Mapped[str] = mapped_column(Geometry(geometry_type="POINT", srid=2056))

    search_buildings: Mapped[List["SearchBuilding"]] = relationship(back_populates="lookup_building")


    def __repr__(self) -> str:
        return f"Building(hauskey={self.hauskey})"
    

class SearchBuilding(Base):
    __tablename__ = "search_buildings"

    hauskey: Mapped[int] = mapped_column(primary_key=True)
    location: Mapped[str] = mapped_column(Geometry(geometry_type="POINT", srid=2056))
    lookup_hauskey: Mapped[int] = mapped_column(ForeignKey("lookup_buildings.hauskey"))

    lookup_building: Mapped["LookupBuilding"] = relationship(back_populates="search_buildings")


    def __repr__(self) -> str:
        return f"Building(hauskey={self.hauskey})"
    

pwd = os.environ.get("POSTGRES_PWD")
engine = create_engine("postgresql+psycopg2://postgres:"+pwd+"@localhost:5432/Datenmanagement")
Session = sessionmaker(engine)

def setup_tables(engine):

    Base.metadata.create_all(engine)

def populate_lookup_buildingsSession(Session):

    filename = r'C:\Users\QPAuser\OneDrive - Quickmail AG\Python Scripts\Test\Gebäudedaten_Quickmail.csv'

    df = pd.read_csv(filename, sep=";", header=0, encoding='utf-8', low_memory=False)
    df = df[['Hauskey','Geo-X Gebäude', 'Geo-Y Gebäude']]
    df.rename(columns={'Hauskey': 'hauskey'}, inplace=True)
    df['Geo-X Gebäude'] = df['Geo-X Gebäude'] + 2000000
    df['Geo-Y Gebäude'] = df['Geo-Y Gebäude'] + 1000000

    df['location'] = df.apply(
        lambda row: WKTElement(f"POINT({row['Geo-X Gebäude']} {row['Geo-Y Gebäude']})", srid=2056),
        axis=1
    )

    df = df[['hauskey', 'location']]

    records = df.to_dict(orient='records')

    with Session.begin() as session:
        session.execute(delete(LookupBuilding))
        session.execute(insert(LookupBuilding), records)

    print('QM Import successful')

def populate_buildings_post(Session):

    filename = r'C:\Users\QPAuser\OneDrive - Quickmail AG\Python Scripts\Test\Postdaten_bereinigt.csv'

    df = pd.read_csv(filename, sep=";", header=0, encoding='utf-8', low_memory=False)
    df = df[['HAUSKEY','KOORD_X_LV95', 'KOORD_Y_LV95']]
    df.rename(columns={'HAUSKEY': 'hauskey'}, inplace=True)

    df['location'] = df.apply(
        lambda row: WKTElement(f"POINT({row['KOORD_Y_LV95']} {row['KOORD_X_LV95']})", srid=2056),
        axis=1
    )

    df = df[['hauskey', 'location']]

    records = df.to_dict(orient='records')

    with Session.begin() as session:
        session.execute(insert(PostBuilding), records)

    print('Post Import successful')

# setup_tables(engine)
# populate_buildings_qm(Session)
# populate_buildings_post(Session)

from Scripts import CONFIG_PATH

