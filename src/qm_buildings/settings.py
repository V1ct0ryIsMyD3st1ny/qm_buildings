from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

LOOKUP_COLUMNS = ["GebäudeID NEU", "Hauskey", "ZGB-PLZ", "Depot", "ZGB-Nr", "Geo-X Gebäude", "Geo-Y Gebäude"]
SEARCH_COLUMNS = ["HAUSKEY", "KOORD_X_LV95", "KOORD_Y_LV95"]

SQL_SERVER = {"dialect": "psycopg2", "host": 5423, "database": "Datenmanagement"}
