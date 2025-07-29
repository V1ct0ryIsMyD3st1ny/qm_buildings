from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


LOOKUP_COLUMNS = ["GebäudeID NEU", "Hauskey", "ZGB-PLZ", "Depot", "ZGB-Nr", "Geo-X Gebäude", "Geo-Y Gebäude"]
SEARCH_COLUMNS = ["HAUSKEY", "Street", "HouseNo", "KOORD_X_LV95", "KOORD_Y_LV95"]

lookup_mapper = {
    "Hauskey": "hauskey",
    "ZGB-PLZ": "zgb",
    "Depot": "depot",
    "ZGB-Nr": "nr",
    "Geo-X Gebäude": "geo_x",
    "Geo-Y Gebäude": "geo_y"
}

search_mapper = {
    "HAUSKEY": "hauskey",
    "Street": "street",
    "HouseNo": "house_number",
    "KOORD_X_LV95": "geo_x",
    "KOORD_Y_LV95": "geo_y"
}

SQL_SERVER = {"dialect": "psycopg2", "host": 5423, "database": "Datenmanagement"}
