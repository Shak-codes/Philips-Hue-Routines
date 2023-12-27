from enum import Enum
from requests.auth import HTTPBasicAuth
from .credentials import CLIENT_ID, CLIENT_SECRET, USERNAME

# Enums


class TABLE_COLUMNS(Enum):
    LIGHTS = """id INTEGER,
                name TEXT,
                turn_on_date TEXT,
                turn_on_dow TEXT,
                turn_on_time TEXT,
                turn_off_date TEXT,
                turn_off_dow TEXT,
                turn_off_time TEXT,
                brightness INTEGER,
                x REAL,
                y REAL"""
    TOKENS = """generated_at TEXT,
                access_token TEXT,
                refresh_token TEXT"""


class Tables(Enum):
    TOKENS = "TOKENS"
    LAMP = "LAMPS"
    LIGHT = "LIGHTS"
    HEATER = "HEATER"
    COLUMN_TYPES = ["integer", "text", "real"]


class SQL(Enum):
    CREATE = "CREATE TABLE"
    INSERT = "INSERT INTO"
    DELETE = "DELETE FROM"
    SELECT_ALL = "SELECT * FROM"


class Params(Enum):
    ID = "id"
    CODE = "code"
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    COLUMNS = "columns"


# Philips Hue
class PHUE(Enum):
    AUTH = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    REFRESH_ACCESS_TOKEN_AUTH = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    REFRESH_ACCESS_TOKEN_URL = "https://api.meethue.com/oauth2/refresh?grant_type=refresh_token"
    LIGHTS_URL = f"https://api.meethue.com/bridge/{USERNAME}/lights"


# Database
DB_URL = "../smarthome.db"
