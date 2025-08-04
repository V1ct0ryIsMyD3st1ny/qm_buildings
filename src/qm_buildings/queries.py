from sqlalchemy import insert, delete, select
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from qm_buildings.models import Base
import pandas as pd
from sqlalchemy.engine import CursorResult


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
    

def remove_existing_id(SearchTable: type[Base], LookupTable: type[Base], session: Session) -> CursorResult:
    """Remove objects of SearchTable with primary key contained in LookupTable

    Args:
        SearchTable (type[Base]): The table to remove keys of.
        LookupTable (type[Base]): The table to look for keys in.
        session (Session): Session with instances of SearchTable and LookupTable

    Returns:
        CursorResult: Cursor pointing at removed objects.
    """
    #Get the primary keys of the tables.
    lookup_key = inspect(LookupTable).primary_key[0]
    search_id = inspect(SearchTable).primary_key[0]
    #Create a list of all keys in LookupTable.
    stmt = select(lookup_key)
    lookup_keys = session.execute(stmt).scalars().all()
    #Delete all row in SearchTable with key in LookupTable.
    stmt = delete(SearchTable).where(search_id.in_(lookup_keys))
    result = session.execute(stmt)
    return result
