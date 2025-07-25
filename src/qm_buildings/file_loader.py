from tkinter import filedialog as fd, messagebox as mb
import pandas as pd
import qm_buildings.settings as settings
from typing import NamedTuple
from functools import partial


def building_columns(building_type: str) -> list[str]:
    """Return the required columns according to the building_type

    Args:
        building_type ({'lookup', 'search'}): The type of buildings to return the required columns of

    Raises:
        ValueError: bulding_type was neither 'lookup' nor 'search'

    Returns:
        list[str]: The required columns.
    """    
    
    #Check that building_type is either "lookup" or "search"
    if "lookup" in building_type.lower():
        expected_columns = settings.LOOKUP_COLUMNS
    elif "search" in building_type.lower():
        expected_columns = settings.SEARCH_COLUMNS
    else:
        raise ValueError("building_type must be either lookup or search")
    return expected_columns


def missing_columns(df: pd.DataFrame, expected_columns: list[str]) -> list[str]:
    """Return list of elements in expected_columns but not in dataframe."""
    missing = [col for col in expected_columns if col not in df.columns]
    return missing
    

def validate_file_columns(filepath: str, expected_columns: list[str]) -> tuple[bool, str]:
    """Validate if the file contains all expected_columns

    Args:
        filepath (str): A csv-File
        expected_columns (list[str]): A list of columns to test if contained in the file.

    Returns:
        tuple[bool, str]: Returns True if all columns were found. If not also returns an error message.
    """    
    df = pd.read_csv(filepath, sep=";", encoding='utf-8', nrows=10, header=0)
    missing = missing_columns(df, expected_columns)
    if not missing:
        return True, ""
    msg = f"Spalte(n) {', '.join(missing)} fehlen"
    return False, msg


def load_files(validator: callable) -> str:
    """Let user select a csv-file and validate it using the validator.

    Args:
        validator (callable): Function to validate the file.

    Raises:
        KeyboardInterrupt: If no file is selected and user cancels retry
        KeyboardInterrupt: If the file did not pass validation and user cancels retry

    Returns:
        str: filepath of the selected file
    """    

    #User should only select a csv-file
    options = {
        'title': 'Wähle eine Datei aus',
        'filetypes': (("CSV-Datei","*.csv"),),
        'initialdir': settings.BASE_DIR,
        'defaultextension': ".csv"
    }
    
    while True:
        filepath = fd.askopenfilename(**options)
        if filepath:
            valid, message = validator(filepath)
            if not valid:
                retry = mb.askretrycancel(
                    title='Import fehlgeschlagen',
                    message=message
                )
                if not retry:
                    raise KeyboardInterrupt("Nutzer hat den Import abgebrochen")
            else:
                return filepath
        else:
            retry = mb.askretrycancel(
                title='Keine Datei ausgwählt',
                message="Willst du es nochmal versuchen"
            )
            if not retry:
                raise KeyboardInterrupt("Nutzer hat den Import abgebrochen.")