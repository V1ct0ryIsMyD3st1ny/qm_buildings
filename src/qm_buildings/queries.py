from sqlalchemy import insert, delete
from sqlalchemy.orm import Session
from qm_buildings.models import Base
import pandas as pd


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
