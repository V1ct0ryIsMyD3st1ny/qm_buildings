import pytest
import qm_buildings.file_loader as fl
from unittest.mock import Mock


@pytest.fixture
def csv_file(tmp_path):
    file = tmp_path / "dummy.csv"
    file.write_text("col2;col1;col3\ndata2;data1;data3")
    return file


def test_load_file(monkeypatch, csv_file):
    
    mock_askopenfilename = Mock()
    mock_askretrycancel = Mock()
    
    monkeypatch.setattr(fl.fd, "askopenfilename", lambda *args, **kwargs: mock_askopenfilename())
    monkeypatch.setattr(fl.mb, "askretrycancel", lambda *args, **kwargs: mock_askretrycancel())
    
    #Test no file selected + no retry -> KeyboardInterrupt
    mock_askopenfilename.side_effect = [""]
    mock_askretrycancel.side_effect = [False]
    with pytest.RaisesExc(KeyboardInterrupt):
        fl.load_file("")
        
    #Test file selected + retry + right file -> return filepath
    mock_askopenfilename.side_effect = ["", csv_file]
    mock_askretrycancel.side_effect = [True]
    assert fl.load_file("") == csv_file
    
    
def test_save_file(monkeypatch, csv_file):
    
    mock_asksaveasfilename = Mock()
    mock_askretrycancel = Mock()
    
    monkeypatch.setattr(fl.fd, "asksaveasfilename", lambda *args, **kwargs: mock_asksaveasfilename())
    monkeypatch.setattr(fl.mb, "askretrycancel", lambda *args, **kwargs: mock_askretrycancel())
    
    #Test no file selected + no retry -> KeyboardInterrupt
    mock_asksaveasfilename.side_effect = [""]
    mock_askretrycancel.side_effect = [False]
    with pytest.RaisesExc(KeyboardInterrupt):
        fl.save_file("")
        
    #Test file selected + retry + right file -> return filepath
    mock_asksaveasfilename.side_effect = ["", csv_file]
    mock_askretrycancel.side_effect = [True]
    assert fl.save_file("") == csv_file