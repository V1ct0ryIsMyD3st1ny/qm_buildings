import pytest
import os
import pandas as pd
from qm_buildings import queries as queries
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import create_engine, select
from geoalchemy2.types import Geometry
from geoalchemy2.shape import WKTElement


@pytest.fixture(scope='session')
def Base():
    class base(DeclarativeBase):
        pass
    return base
    

@pytest.fixture(scope='session')
def LookupTable(Base):
    class LookupTable(Base):
        __tablename__ = "lookup_table"
        hauskey: Mapped[int] = mapped_column(primary_key=True)
        geom: Mapped[str] = mapped_column(Geometry(geometry_type="POINT", srid=2056))
    return LookupTable


@pytest.fixture(scope='session')
def SearchTable(Base):
    class SearchTable(Base):
        __tablename__ = "search_table"
        hauskey: Mapped[int] = mapped_column(primary_key=True)
        geom: Mapped[str] = mapped_column(Geometry(geometry_type="POINT", srid=2056))
    return SearchTable


@pytest.fixture(scope='session')
def engine(Base, LookupTable, SearchTable):
    user = os.environ.get("POSTGRES_USER")
    pwd = os.environ.get("POSTGRES_PWD")
    engine = create_engine(f"postgresql+psycopg://{user}:{pwd}@localhost:5432/test_db")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()
    
    
@pytest.fixture(scope='session')
def connection(engine):
    conn = engine.connect()
    yield conn
    conn.close()
    
    
@pytest.fixture
def db_session(connection):
    trans = connection.begin()    
    session = Session(bind=connection)
    yield session
    session.close()
    trans.rollback()
    
    
def test_import_table(LookupTable, db_session):
    geom1 = WKTElement("POINT(2600423 1199520)", srid=2056)
    geom2 = WKTElement("POINT(2600521 1199503)", srid=2056)
    df = pd.DataFrame({'hauskey': [1,2], 'geom': [geom1, geom2]})
    queries.import_table(df, LookupTable, db_session)
    stmt = select(LookupTable)
    result = db_session.scalars(stmt).first()
    assert result.hauskey == 1
    
    
def test_assing_closest_lookup(SearchTable, LookupTable, db_session):
    search1 = SearchTable(hauskey=1, geom=WKTElement("POINT(2600423 1199520)", srid=2056))
    search2 = SearchTable(hauskey=2, geom=WKTElement("POINT(2600521 1199503)", srid=2056))
    db_session.add(search1)
    db_session.add(search2)
    lookup1 = LookupTable(hauskey=1, geom=WKTElement("POINT(2600423 1199520)", srid=2056))
    lookup2 = LookupTable(hauskey=4, geom=WKTElement("POINT(2600521 1199503)", srid=2056))
    db_session.add(lookup1)
    db_session.add(lookup2)
    db_session.commit()
    result = queries.assign_closest_lookup(SearchTable, LookupTable, db_session)
    assert len(result) == 1
    search, lookup = result[0]
    assert [search.hauskey, lookup.hauskey] == [2, 4]
    
    
def test_mapped_instances_to_dataframe(LookupTable):
    lookup1 = LookupTable(hauskey=1, geom=WKTElement("POINT(2600423 1199520)", srid=2056))
    lookup2 = LookupTable(hauskey=4, geom=WKTElement("POINT(2600521 1199503)", srid=2056))
    
    df = queries.mapped_instances_to_dataframe([lookup1, lookup2])
    assert list(df) == ['hauskey']
    assert df['hauskey'].to_list() == [1, 4]