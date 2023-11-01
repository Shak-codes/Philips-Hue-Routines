from requests.auth import HTTPBasicAuth
from credentials import CLIENT_ID, CLIENT_SECRET, USERNAME

# Philips Hue
PHUE_AUTH = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
PHUE_REFRESH_ACCESS_TOKEN_AUTH = {
    "Content-Type": "application/x-www-form-urlencoded"
}
PHUE_REFRESH_ACCESS_TOKEN_URL = "https://api.meethue.com/oauth2/refresh?grant_type=refresh_token"
PHUE_LIGHTS_URL = f"https://api.meethue.com/bridge/{USERNAME}/lights"

# Database
DB_URL = "../smarthome.db"
