import sqlite3
from datetime import datetime
import requests
import json

from constants import PHUE_AUTH, PHUE_REFRESH_ACCESS_TOKEN_AUTH, PHUE_REFRESH_ACCESS_TOKEN_URL, DB_URL, SQL, Tables


def valid_access_token(generated_at, now) -> bool:
    now = datetime.now()
    if (now - generated_at).total_seconds() > 300:
        print("Access Token is no longer valid")
        return False
    print("Access Token is still valid")
    return True


class Tokens:
    def __init__(self) -> None:
        connection = sqlite3.connect('../smarthome.db')
        instance = connection.cursor()
        try:
            instance.execute(f"{SQL.SELECT_ALL.value} {Tables.TOKENS.value}")
            entry = instance.fetchone()
            self.generated_at = entry[0]
            self.access_token = entry[1]
            self.refresh_token = entry[2]
            print("Tokens have been set in Class initialization!")
        except:
            print("Tokens cannot be obtained. Please generate the tokens!")
        finally:
            connection.close()

    def pull_tokens(self) -> None:
        connection = sqlite3.connect('../smarthome.db')
        instance = connection.cursor()
        instance.execute(f"{SQL.SELECT_ALL.value} {Tables.TOKENS.value}")
        entry = instance.fetchone()
        self.generated_at = entry[0]
        self.access_token = entry[1]
        self.refresh_token = entry[2]
        connection.close()
        print("Tokens have been pulled!")

    def refresh_access_token(self) -> None:
        data = {"refresh_token": self.refresh_token}
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        response = requests.post(PHUE_REFRESH_ACCESS_TOKEN_URL,
                                 auth=PHUE_AUTH,
                                 headers=PHUE_REFRESH_ACCESS_TOKEN_AUTH,
                                 data=data)
        response = json.loads(response.text)
        self.generated_at = generated_at
        self.access_token = response['access_token']
        self.refresh_token = response['refresh_token']
        connection = sqlite3.connect(DB_URL)
        instance = connection.cursor()
        instance.execute('DELETE FROM TOKENS',)
        instance.execute(
            f"INSERT INTO TOKENS VALUES (?, ?, ?)",
            (self.generated_at, self.access_token, self.refresh_token)
        )
        connection.commit()
        connection.close()
        print("Tokens have been refreshed successfully!")

    def get_access_token(self) -> str | bool:
        if not hasattr(self, 'generated_at'):
            print("Access Token cannot be obtained. Please generate the tokens!")
            return False
        if valid_access_token(datetime.strptime(self.generated_at, "%Y-%m-%d %H:%M:%S.%f"), datetime.now()):
            return self.access_token
        self.refresh_access_token()
        return self.access_token
