import pytest
import pandas as pd
import qm_buildings.file_loader as fl
import qm_buildings.settings as settings
from unittest.mock import Mock

@pytest.fixture
def expected_columns():
    return ['col1', 'col2']

@pytest.fixture
def right_file(tmp_path):
    file = tmp_path / "right.csv"
    file.write_text("col2;col1;col3\ndata2;data1;data3")
    return file

@pytest.fixture
def partially_wrong_file(tmp_path):
    file = tmp_path / "partial.csv"
    file.write_text("col1;col3\ndata1;data3")
    return file

@pytest.fixture
def wrong_file(tmp_path):
    file = tmp_path / "wrong.csv"
    file.write_text("col3\ndata3")
    return file

def test_buildings_columns():
    assert fl.building_columns('*Lookup*') == settings.LOOKUP_COLUMNS
    assert fl.building_columns('*Search*') == settings.SEARCH_COLUMNS
    with pytest.RaisesExc(ValueError):
        fl.building_columns('random_string')
    

def test_missing_columns(expected_columns):
    right_data = {'col2': [1, 2], 'col1': [3, 4], 'col3': [5, 6]}
    partially_wrong_data = {'col1': [1, 2], 'col3': [3, 4]}
    wrong_data = {'col3': [1, 2]}
        
    assert fl.missing_columns(pd.DataFrame(data=right_data), expected_columns) == []
    assert fl.missing_columns(pd.DataFrame(data=partially_wrong_data), expected_columns) == ['col2']
    assert fl.missing_columns(pd.DataFrame(data=wrong_data), expected_columns) == ['col1', 'col2']


def test_validate_file_columns(right_file, partially_wrong_file, wrong_file, expected_columns):
    assert fl.validate_file_columns(right_file, expected_columns)[0] == True
    assert fl.validate_file_columns(partially_wrong_file, expected_columns)[0] == False
    assert fl.validate_file_columns(wrong_file, expected_columns)[0] == False
    
    
def test_load_files(monkeypatch):
    
    def validator(filepath):
        return [filepath == right_file, ""]
    
    mock_askopenfilename = Mock()
    mock_askretrycancel = Mock()
    
    monkeypatch.setattr(fl.fd, "askopenfilename", lambda *args, **kwargs: mock_askopenfilename())
    monkeypatch.setattr(fl.mb, "askretrycancel", lambda *args, **kwargs: mock_askretrycancel())
    
    #Test no file selected + no retry -> KeyboardInterrupt
    mock_askopenfilename.side_effect = [""]
    mock_askretrycancel.side_effect = [False]
    with pytest.RaisesExc(KeyboardInterrupt):
        fl.load_files(validator)
        
    #Test file selected + wrong file + no retry -> KeyboardInterrupt
    mock_askopenfilename.side_effect = [wrong_file]
    mock_askretrycancel.side_effect = [False]
    with pytest.RaisesExc(KeyboardInterrupt):
        fl.load_files(validator)
        
    #Test file selected + wrong file + retry + right file -> return filepath
    mock_askopenfilename.side_effect = [wrong_file, right_file]
    mock_askretrycancel.side_effect = [True]
    assert fl.load_files(validator) == right_file
    
    #Test file selected + wrong file + retry + no file selected + retry + right file -> return filepath
    mock_askopenfilename.side_effect = [wrong_file, "", right_file]
    mock_askretrycancel.side_effect = [True, True]
    assert fl.load_files(validator) == right_file