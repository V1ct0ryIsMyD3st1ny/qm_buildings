from typing import List, Optional
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from geoalchemy2.types import Geometry


class Base(DeclarativeBase):
    pass


class LookupBuilding(Base):
    __tablename__ = "lookup_buildings"
    hauskey: Mapped[int] = mapped_column(primary_key=True)
    strasse: Mapped[str]
    house_nr: Mapped[Optional[str]]
    gangfolge: Mapped[Optional[int]]
    zgb: Mapped[str] = mapped_column(String(7))
    depot: Mapped[int]
    zgb_nr: Mapped[int]
    geom: Mapped[str] = mapped_column(Geometry(geometry_type="POINT", srid=2056))

    search_buildings: Mapped[List["SearchBuilding"]] = relationship(back_populates="lookup_building")

    def __repr__(self) -> str:
        return f"Building(hauskey={self.hauskey}, gangfolge={self.gangfolge})"
    

class SearchBuilding(Base):
    __tablename__ = "search_buildings"

    hauskey: Mapped[int] = mapped_column(primary_key=True)
    street: Mapped[str]
    house_number: Mapped[str]
    geom: Mapped[str] = mapped_column(Geometry(geometry_type="POINT", srid=2056))
    lookup_hauskey: Mapped[Optional[List[int]]] = mapped_column(ForeignKey("lookup_buildings.hauskey"))

    lookup_building: Mapped["LookupBuilding"] = relationship(back_populates="search_buildings")

    def __repr__(self) -> str:
        return f"Building(hauskey={self.hauskey})"
    
    
