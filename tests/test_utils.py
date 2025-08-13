import pytest
import qm_buildings.utils as utils
import pandas as pd
from geoalchemy2.elements import WKTElement


def test_create_mapping():
    match_columns = ['col1','col2']
    
    valid_selection = {'col1': 'val1', 'col2': 'val2'}
    missing_selection = {'col1': 'val1', 'col2': ''}
    duplicate_selection = {'col1': 'val1', 'col2': 'val1'}
    
    # Assert valid selection returns a dict
    assert utils.create_mapping(match_columns, valid_selection) == {'val1': 'col1', 'val2': 'col2'}
    # Assert missing selection raises missing error
    with pytest.raises(ValueError, match="Row col2 is empty."):
        utils.create_mapping(match_columns, missing_selection)
    # Assert duplicate selection raises duplicate error
    with pytest.raises(ValueError, match="val1 was selected multiple times."):
        utils.create_mapping(match_columns, duplicate_selection)
        
        
def test_add_geometry():
    df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
    df = utils.add_geometry(df, "x", "y", 31492)
    
    # Assert that geometry column was created
    assert "geom" in list(df)
    # Assert "geom" contains the correct WKTElement
    element = df['geom'].iloc[0]
    assert type(element) == WKTElement
    assert element.srid == 31492
    assert element.data == "POINT(1 3)"