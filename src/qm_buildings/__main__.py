import qm_buildings.file_loader as fl
import qm_buildings.queries as queries
import qm_buildings.models as models
import qm_buildings.engine_setup as setup
import qm_buildings.utils as utils
import qm_buildings.settings as settings
import pandas as pd
import numpy as np
import tkinter as tk
import threading
from tkinter import ttk
from sqlalchemy import inspect

engine = setup.local_engine()

setup.setup_tables(models.Base, engine)
SessionLocal = setup.create_sessionmaker(engine)

root = tk.Tk()
root.title("QM Buildings")

tk.Label(root, text="Import Search Buildings", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10, pady=5)
tk.Label(root, text="Import Lookup Buildings", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=10, pady=5)
tk.Label(root, text="Export closest Buildings", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=10, pady=5)

def import_search():
    with SessionLocal.begin() as session:
        queries.import_to_mapped_class(models.SearchBuilding, session)
        
def import_lookup():
    with SessionLocal.begin() as session:
        queries.import_to_mapped_class(models.LookupBuilding, session)
        
def export_closest():
    with SessionLocal.begin() as session:
        df = queries.export_closest_lookup(models.SearchBuilding, models.LookupBuilding, session)
    save_filepath = fl.save_file('Wo soll die Datei gespeichert werden?')
    df.to_csv(save_filepath, sep=";", header=True, index=False, encoding='utf-8')
    print(f"Saved under {save_filepath}")

 
search_import_btn = ttk.Button(root, text="Import", command=lambda: threading.Thread(target=import_search, daemon=True).start())
search_import_btn.grid(row=1, column=0, columnspan=1, pady=5)
lookup_import_btn = ttk.Button(root, text="Import", command=lambda: threading.Thread(target=import_lookup, daemon=True).start())
lookup_import_btn.grid(row=1, column=1, columnspan=1, pady=5)
export_btn = ttk.Button(root, text="Export", command=lambda: threading.Thread(target=export_closest, daemon=True).start())
export_btn.grid(row=1, column=2, columnspan=1, pady=5)

root.mainloop()
