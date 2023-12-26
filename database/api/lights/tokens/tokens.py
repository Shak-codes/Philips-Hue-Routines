import sqlite3
from datetime import datetime
import requests
import json

from sqlite import sqlite
from constants import PHUE, DB_URL, SQL, Tables


def valid_access_token(generated_at: datetime, validity_duration_seconds: int = 300) -> bool:
    current_time = datetime.now()
    token_age = current_time - generated_at

    if token_age.total_seconds() > validity_duration_seconds:
        print("Access Token is no longer valid")
        return False

    print("Access Token is still valid")
    return True


class Tokens:
    def __init__(self) -> None:
        self.pull_tokens()

    def set_tokens(self, generated_at, access_token, refresh_token):
        self.generated_at = generated_at
        self.access_token = access_token
        self.refresh_token = refresh_token

    def pull_tokens(self) -> None:
        c = sqlite.SQLite()
        response, code = c.get_one("TOKENS")
        c.close_conn()
        print(code)
        if code != 409:
            self.set_tokens(response[0], response[1], response[2])

    def refresh_access_token(self) -> None:
        data = {"refresh_token": self.refresh_token}
        response = requests.post(PHUE.REFRESH_ACCESS_TOKEN_URL.value,
                                 auth=PHUE.AUTH.value,
                                 headers=PHUE.REFRESH_ACCESS_TOKEN_AUTH.value,
                                 data=data)
        if response.status_code >= 400:
            return "Something went wrong refreshing the access token!", response.status_code
        response = json.loads(response.text)
        self.set_tokens(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                        response['access_token'],
                        response['refresh_token'])
        c = sqlite.SQLite()
        response, code = c.delete_all(Tables.TOKENS.value)
        if code != 409:
            response, code = c.insert(
                Tables.TOKENS.value, (self.generated_at, self.access_token, self.refresh_token))
        c.close_conn()
        return self.access_token, 200

    def get_access_token(self) -> (str, int):
        if not hasattr(self, 'generated_at'):
            return "Access Token cannot be obtained. Please generate the tokens!", 409
        if valid_access_token(datetime.strptime(self.generated_at, "%Y-%m-%d %H:%M:%S.%f"), datetime.now()):
            return self.access_token, 200
        return self.refresh_access_token(), 200
