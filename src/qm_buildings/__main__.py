import qm_buildings.file_loader as fl
import qm_buildings.queries as queries
import qm_buildings.models as models
import qm_buildings.engine_setup as setup
import qm_buildings.utils as utils
import qm_buildings.settings as settings
import pandas as pd
import numpy as np
from sqlalchemy import inspect

engine = setup.local_engine()

#setup.setup_tables(models.Base, engine)
Session = setup.create_sessionmaker(engine)

for Table in (models.LookupBuilding, models.SearchBuilding):
    break
    mapped_object = inspect(Table)
    table_columns = [col.key for col in mapped_object.columns if col.key != "lookup_hauskey"]

    filepath = fl.load_file()
    df = pd.read_csv(filepath, sep=";", header=0, encoding='utf-8', nrows=10, low_memory=False)

    csv_columns = df.columns.values.tolist()
    mapper = fl.launch_mapping_window(table_columns, csv_columns)
    csv_columns = mapper.keys()

    df = pd.read_csv(filepath, sep=";", header=0, encoding='utf-8', low_memory=False)
    df = df.replace(np.nan, None)
    df.rename(columns=mapper, inplace=True)
    df = utils.add_geometry(df, "x coordinate", "y coordinate")

    with Session.begin() as session:
        queries.import_table(df, Table, session)
        
with Session.begin() as session:
    buildings = queries.assign_closest_lookup(models.SearchBuilding, models.LookupBuilding, session)
    first_row = [building[0] for building in buildings]
    second_row = [building[1] for building in buildings]
    df1 = queries.mapped_instances_to_dict(first_row)
    df2 = queries.mapped_instances_to_dict(second_row)
    df = df1.join(df2, lsuffix='_first_row', rsuffix='_second_row')
    df.to_csv(settings.BASE_DIR.parent / 'Export.csv', sep=";", header=True, index=False, encoding='utf-8')