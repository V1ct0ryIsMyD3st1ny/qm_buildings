from sqlalchemy import insert, delete, select, exists, true, join
from sqlalchemy.orm import Session, aliased
from sqlalchemy.inspection import inspect
from geoalchemy2.types import Geometry
from qm_buildings.models import Base
from qm_buildings.utils import execution_time, add_geometry
import pandas as pd
import numpy as np
import tkinter.messagebox as mb
import qm_buildings.file_loader as fl


def df_to_mapped_class(df: pd.DataFrame, Table: type[Base], session: Session) -> None:
    """Import the the contents of the Dataframe to Table.

    Args:
        df (pd.DataFrame): Dataframe containg columns matching the columns of Table
        Table (type[Base]): Mapped class derived from Base.
        session (Session): Session connecting to Table.
    """   
    print(f'Starting import of {Table.__table__.name}') 
    records = df.to_dict(orient='records')
    session.execute(delete(Table))
    session.execute(insert(Table), records)
    print(f'Import of {Table.__table__.name} successful.')


def assign_closest_lookup[MappedObject: Base](SearchTable: type[MappedObject], LookupTable: type[MappedObject], session: Session) -> list[tuple[MappedObject, MappedObject]]:
    """For each building in SearchTable match the closest building in LookupTable.

    Args:
        SearchTable (type[MappedObject]): Buildings to find closest building.
        LookupTable (type[MappedObject]): Buildings to lookup in.
    
    Returns:
        list[tuple[MappedObject, MappedObject]]: List of pairs of buldings in SearchTable with closest buliding in LookupTable
        
    Type Variables:
        MappedObject: A SQLAlchemy ORM mapped class type bound to Base containing the building data.
    """    
    # Get the primary keys of the tables.
    lookup_key = inspect(LookupTable).primary_key[0]
    search_key = inspect(SearchTable).primary_key[0]
    filtered_search = session.query(SearchTable).where(~exists().where(search_key == lookup_key)).subquery()
    FilteredSearch = aliased(SearchTable, filtered_search)
    nearest_building = (
        select(LookupTable)
        .order_by(FilteredSearch.geom.op('<->')(LookupTable.geom))
        .limit(1)
        .lateral()
    )
    NearestBuilding = aliased(LookupTable, nearest_building)
    stmt = (
        select(FilteredSearch, NearestBuilding)
        .select_from(join(FilteredSearch, NearestBuilding, true()))
    )
    result = session.execute(stmt).all()
    return result


def mapped_instances_to_dataframe[MappedClass: Base](instances: list[MappedClass]) -> pd.DataFrame:
    records = [
        {k: v for k, v in vars(obj).items()
        if k not in ('geom', '_sa_instance_state')}
        for obj in instances
    ]
    return pd.DataFrame(records)


@execution_time
def import_to_mapped_class(Table: type[Base], session: Session) -> None:
    filepath = fl.load_file(f'Choose a file to import into {Table.__tablename__}')
    df = pd.read_csv(filepath, sep=";", header=0, encoding='utf-8', nrows=10, low_memory=False)
    
    mapped_class = inspect(Table)
    table_columns = [col.key for col in mapped_class.columns if col.key != 'geom']
    csv_columns = df.columns.values.tolist()
    mapper = fl.launch_mapping_window(table_columns, csv_columns)
    if mapper == {}:
        raise KeyboardInterrupt("x-Button pressed")
    df = pd.read_csv(filepath, sep=";", header=0, encoding='utf-8', low_memory=False)
    df = df.replace(np.nan, None)
    df.rename(columns=mapper, inplace=True)
    df = add_geometry(df, "x_coord", "y_coord")
    df_to_mapped_class(df, Table, session)
    
    
@execution_time
def export_closest_lookup[MappedObject: Base](SearchTable: type[MappedObject], LookupTable: type[MappedObject], session: Session) -> pd.DataFrame:
    result = assign_closest_lookup(SearchTable, LookupTable, session)
    search_instances = [row[0] for row in result]
    lookup_instances = [row[1] for row in result]
    df_search = mapped_instances_to_dataframe(search_instances)
    df_lookup = mapped_instances_to_dataframe(lookup_instances)
    df = df_search.join(df_lookup, lsuffix='_search', rsuffix='_lookup')
    return df