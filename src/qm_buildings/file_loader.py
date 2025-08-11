from tkinter import filedialog as fd, messagebox as mb
import qm_buildings.settings as settings
import tkinter as tk
from tkinter import ttk

  

def load_file(title: str) -> str:
    """Let user select a csv-file.

    Raises:
        KeyboardInterrupt: No file was selected and user cancels retry.

    Returns:
        str: filepath of the selected file.
    """    
    #User should only select a csv-file
    options = {
        'title': title,
        'filetypes': (("CSV-Datei","*.csv"),),
        'initialdir': settings.BASE_DIR,
        'defaultextension': ".csv"
    }
    #Loop until file is selected.
    while True:
        filepath = fd.askopenfilename(**options)
        if filepath:
            return filepath
        #If no file selected ask for retry.
        else:
            retry = mb.askretrycancel(
                title='Keine Datei ausgewählt',
                message="Willst du es nochmal versuchen"
            )
            if not retry:
                raise KeyboardInterrupt("Nutzer hat den Import abgebrochen.")
            
            
def download_file(title: str) -> str:
    
    options = {
        'title': title,
        'filetypes': (("CSV-Datei","*.csv"),),
        'initialdir': settings.BASE_DIR,
        'defaultextension': ".csv"
    }
     #Loop until file is selected.
    while True:
        filepath = fd.asksaveasfilename(**options)
        if filepath:
            return filepath
        #If no file selected ask for retry.
        else:
            retry = mb.askretrycancel(
                title='Keine Datei ausgewählt',
                message="Willst du es nochmal versuchen"
            )
            if not retry:
                raise KeyboardInterrupt("Nutzer hat den Import abgebrochen.")
       

def launch_mapping_window(match_columns: list[str], select_columns: list[str]) -> dict:
    """Let user match columns by selecting columns in select_columns.

    Args:
        match__columns (list[str]): List of columns to match.
        select_columns (list[str]): List of columns to select.

    Returns:
        dict: Dictionnary with key in select_columns and corresponding match_column.
    """    

    root = tk.Tk()
    root.title("Match columns")

    tk.Label(root, text="SQL Column", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10, pady=5)
    tk.Label(root, text="Table Column", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=10, pady=5)

    #Store the pairs (selected_column: match_column) in mapping
    mapping = {}
    #Store comboboxes for each match_column
    comboboxes = {}

    #Replace the "geom" column with x and y coordinate for matching.
    match_columns += ["x coordinate", "y coordinate"]
    match_columns.remove("geom")
    
    #List all match_columns as rows with comboboxes holding selected_columns as values.
    for i, match_col in enumerate(match_columns):
        tk.Label(root, text=match_col).grid(row=i+1, column=0, padx=10, pady=5, sticky="w")

        cb = ttk.Combobox(root, values=select_columns, state="readonly", width=30)
        cb.grid(row=i+1, column=1, padx=10, pady=5)
        comboboxes[match_col] = cb

    #Successively add non-null values as long as selected_column is not already in mapping. Otherwise start loop again.
    def on_submit():
        mapping.clear()
        for _, match_col in enumerate(match_columns):
            selected = comboboxes[match_col].get()
            #match_col has no match.
            if not selected:
                mb.showerror(title="Wrong input", message=f"Zeile {match_col} nicht ausgefüllt.")
                break
            #selected_col was already selected.
            elif selected in mapping.keys():
                mb.showerror(title="Wrong input", message=f"{selected} was selected multiple times.")
                break
            #all values are not null and do not occur twice.
            else:
                mapping[selected] = match_col
        else:
            root.destroy()

    submit_btn = ttk.Button(root, text="Submit Mapping", command=on_submit)
    submit_btn.grid(row=len(match_columns)+1, column=0, columnspan=4, pady=10)

    root.mainloop()
    return mapping