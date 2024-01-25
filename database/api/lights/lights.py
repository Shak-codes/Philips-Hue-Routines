from datetime import datetime
import requests
import json
from ..sqlite.sqlite import SQLite
from .tokens.tokens import Tokens
from ..constants import Tables, PHUE


class Lights:
    HEADERS = {"Content-Type": "application/json"}
    tokens = Tokens()

    def __init__(self, light_id: int):
        self.id = light_id
        self.pull_light_data()

    def pull_light_data(self):
        access_token, code = self.tokens.get_access_token()

        if code == 200:
            self.HEADERS["Authorization"] = f"Bearer {access_token}"
            response = json.loads(requests.get(
                f"{PHUE.LIGHTS_URL.value}/{self.id}", headers=self.HEADERS).text)

            self.name = response['name']
            self.on = response['state']['on']
            self.brightness = response['state']['bri']
            self.x = response['state']['xy'][0]
            self.y = response['state']['xy'][1]

            print("Light data has been pulled!")

    def store_light_data(self):
        values = (self.id, self.name, self.turn_on_date, self.turn_on_dow, self.turn_on_time,
                  self.turn_off_date, self.turn_off_dow, self.turn_off_time, self.brightness,
                  self.x, self.y)
        with SQLite() as db:
            response, code = db.insert(Tables.LIGHT.value, values)
            return response, code

    def set_light_on(self, now):
        print("SET_LIGHT_ON")
        self.turn_on_date = now.strftime('%Y-%m-%d')
        self.turn_on_dow = now.strftime('%A')
        self.turn_on_time = now.strftime('%H:%M:%S')
        self.on = True

        return f"Light {self.id} has been turned on at {self.turn_on_time}!", 200

    def set_light_off(self, now):
        print("SET_LIGHT_OFF")
        self.turn_off_date = now.strftime('%Y-%m-%d')
        self.turn_off_dow = now.strftime('%A')
        self.turn_off_time = now.strftime('%H:%M:%S')
        self.on = False

        return self.store_light_data()

    def set_light(self):
        response, code = self.tokens.get_access_token()
        if code != 200:
            return response, code
        raw = '{"on": true}' if not self.on else '{"on": false}'
        self.HEADERS['Authorization'] = f"Bearer {response}"
        response = requests.put(
            f"{PHUE.LIGHTS_URL.value}/{self.id}/state",
            headers=self.HEADERS,
            data=raw
        )
        if response.status_code >= 400:
            return "API call to modify the light state has failed.", 409
        now = datetime.now()
        return self.set_light_on(now) if not self.on else self.set_light_off(now)

    def get_light_data(self):
        if not self.tokens.get_access_token()[1] == 200:
            return "Cannot get light data. Please generate an access token!", 403

        return {
            "id": self.id,
            "name": self.name,
            "on": self.on,
            "brightness": self.brightness,
            "x": self.x,
            "y": self.y
        }, 200
