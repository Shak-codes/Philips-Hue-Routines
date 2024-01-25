from datetime import datetime
import requests
import json
from ...sqlite.sqlite import SQLite
from ...constants import PHUE, Tables


def valid_access_token(generated_at: datetime, validity_duration_seconds: int = 600000) -> bool:
    current_time = datetime.now()
    token_age = current_time - generated_at

    if token_age.total_seconds() > validity_duration_seconds:
        return False

    return True


class Tokens:
    TABLE_NAME = Tables.TOKENS.value

    def __init__(self) -> None:
        self.generated_at = None
        self.access_token = None
        self.refresh_token = None

        self.pull_tokens()

    def _set_tokens(self, generated_at, access_token, refresh_token):
        self.generated_at = generated_at
        self.access_token = access_token
        self.refresh_token = refresh_token

    def pull_tokens(self) -> None:
        with SQLite() as db:
            result, _ = db.get_one(self.TABLE_NAME)
            if result:
                self._set_tokens(*result)

    def _refresh_access_token(self) -> (str, int):
        data = {"refresh_token": self.refresh_token}
        response = requests.post(
            PHUE.REFRESH_ACCESS_TOKEN_URL.value,
            auth=PHUE.AUTH.value,
            headers=PHUE.REFRESH_ACCESS_TOKEN_AUTH.value,
            data=data
        )
        if response.status_code >= 400:
            return "Something went wrong refreshing the access token!", response.status_code

        response_json = json.loads(response.text)
        self._set_tokens(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            response_json['access_token'],
            response_json['refresh_token']
        )

        with SQLite() as db:
            db.delete_all(self.TABLE_NAME)
            db.insert(self.TABLE_NAME, (self.generated_at,
                      self.access_token, self.refresh_token))

        return self.access_token, 200

    def get_access_token(self) -> (str, int):
        if self.generated_at is None:
            return "Access Token cannot be obtained. Please generate the tokens!", 409

        if valid_access_token(datetime.strptime(self.generated_at, "%Y-%m-%d %H:%M:%S.%f")):
            return self.access_token, 200

        return self._refresh_access_token()
