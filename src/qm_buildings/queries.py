from sqlalchemy import insert, delete, select, exists, true, join
from sqlalchemy.orm import Session, aliased
from sqlalchemy.inspection import inspect
from qm_buildings.models import Base
from qm_buildings.utils import execution_time
import pandas as pd


@execution_time
def import_table(df: pd.DataFrame, Table: type[Base], session: Session) -> None:
    """Import the the contents of the Dataframe to Table.

    Args:
        df (pd.DataFrame): Dataframe containg columns matching the columns of Table
        Table (type[Base]): Mapped class derived from Base.
        session (Session): Session connecting to Table.
    """    
    records = df.to_dict(orient='records')
    session.execute(delete(Table))
    session.execute(insert(Table), records)
    print(f'Import of {Table.__table__.name} successful.')


@execution_time
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


def mapped_instances_to_dict[MappedClass: Base](instances: list[MappedClass]) -> pd.DataFrame:
    records = [
        {k: v for k, v in vars(obj).items()
        if k not in ('geom', '_sa_instance_state')}
        for obj in instances
    ]
    return pd.DataFrame(records)

