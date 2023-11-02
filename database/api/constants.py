from enum import Enum
from requests.auth import HTTPBasicAuth
from credentials import CLIENT_ID, CLIENT_SECRET, USERNAME

# Enums


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
PHUE_AUTH = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
PHUE_REFRESH_ACCESS_TOKEN_AUTH = {
    "Content-Type": "application/x-www-form-urlencoded"
}
PHUE_REFRESH_ACCESS_TOKEN_URL = "https://api.meethue.com/oauth2/refresh?grant_type=refresh_token"
PHUE_LIGHTS_URL = f"https://api.meethue.com/bridge/{USERNAME}/lights"

# Database
DB_URL = "../smarthome.db"
