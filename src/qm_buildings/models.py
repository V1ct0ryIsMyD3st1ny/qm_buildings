from typing import List, Optional
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from geoalchemy2.types import Geometry


class Base(DeclarativeBase):
    pass


class LookupBuilding(Base):
    __tablename__ = "lookup_buildings"
    hauskey: Mapped[int] = mapped_column(primary_key=True)
    street: Mapped[str]
    house_nr: Mapped[Optional[str]]
    gangfolge: Mapped[Optional[int]]
    zgb: Mapped[Optional[str]] = mapped_column(String(7))
    depot: Mapped[Optional[int]]
    zgb_nr: Mapped[Optional[int]]
    x_coord: Mapped[Optional[int]]
    y_coord: Mapped[Optional[int]]
    geom: Mapped[str] = mapped_column(Geometry(geometry_type="POINT", srid=2056))

    def __repr__(self) -> str:
        mapped_object = inspect(self)
        info = ", ".join(
            f"{col.key}: {getattr(self, col.key)}"
            for col in mapped_object.attrs if col.key not in ["geom", "search_buildings"]
        )        
        return f"LookupBuilding({info})"
     

class SearchBuilding(Base):
    __tablename__ = "search_buildings"

    hauskey: Mapped[int] = mapped_column(primary_key=True)
    plz4: Mapped[int]
    city: Mapped[str]
    plz6: Mapped[int]
    street: Mapped[str]
    house_nr: Mapped[Optional[str]]
    x_coord: Mapped[Optional[int]]
    y_coord: Mapped[Optional[int]]
    geom: Mapped[str] = mapped_column(Geometry(geometry_type="POINT", srid=2056))

    def __repr__(self) -> str:
        mapped_object = inspect(self)
        info = ", ".join(
            f"{col.key}: {getattr(self, col.key)}"
            for col in mapped_object.attrs if col.key not in ["geom", "lookup_building"]
        )
        return f"SearchBuilding({info})"
    