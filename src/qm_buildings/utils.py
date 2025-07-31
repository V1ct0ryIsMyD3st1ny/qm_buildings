import pandas as pd
from geoalchemy2.shape import WKTElement


def add_geometry(df: pd.DataFrame, x_col: str, y_col: str, srid: int=2056) -> pd.DataFrame:
    """Add a column 'geom' to the dataframe of geometry type.

    Args:
        df (pd.DataFrame): The Dataframe to add geometry.
        x_col (str): The label of the x-coordinate.
        y_col (str): The label of the y-coordinate.
        srid (int, optional): The srid the coordinates are based of. Defaults to 2056.

    Returns:
        pd.DataFrame: Copy of the dataframe with the added column 'geom' in place of coordinate columns.
    """    
    df = df.copy()
    df['geom'] = df.apply(
        lambda row: WKTElement(f"POINT({row[x_col]} {row[y_col]})", srid=srid),
        axis=1
    )
    used_columns = [col for col in df.columns if col not in (x_col, y_col)]
    df = df[used_columns]
    return df