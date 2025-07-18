from qm_buildings.settings import BASE_DIR, CONFIG_PATH
from configparser import ConfigParser
from tkinter import filedialog as fd, messagebox as mb
import pandas as pd



def expected_columns(section):
    config = ConfigParser()
    config.read(CONFIG_PATH, encoding='utf-8')

    if section not in config:
        raise ValueError(f"Section {section} not found in config.")
    
    cols = config[section]["expected_columns"]
    cols = [col.strip() for col in cols.split("\n") if col]
    return cols


def load_files(section):
    
    expected_col = expected_columns(section)

    while True:

        options = {
            'title': 'Wähle eine Datei aus',
            'filetypes': (("CSV-Datei","*.csv"),),
            'initialdir': BASE_DIR,
            'defaultextension': ".csv"
        }

        filepath = fd.askopenfilename(**options)

        if filepath:
            missing_columns = unmatched_columns(filepath, expected_col)
            if missing_columns:
                ans = mb.askretrycancel(
                    title='Spalte nicht gefunden',
                    message=f"Spalten {', '.join(expected_col)} fehlen"
                )
                if not ans:
                    return
            else:
                return filepath
        else:
            ans = mb.askretrycancel(title='Keine Datei ausgwählt', message="Willst du es nochmal versuchen")
            if not ans:
                return

            

def unmatched_columns(filepath, expected_columns):

    df = pd.read_csv(filepath, sep=";", encoding='utf-8', nrows=10, header=0)

    matches = [col for col in expected_columns if col not in df.columns]
    return matches