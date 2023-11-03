from datetime import datetime
from constants import DB_URL, Tables, SQL, PHUE
import requests
import json
import sqlite3

from lights.tokens import tokens


class Light:
    tokens = tokens.Tokens()
    HEADERS = {"Content-Type": "application/json"}

    def __init__(self, id: int):
        self.id = id
        if self.tokens.get_access_token():
            HEADERS = {
                "Authorization": f"Bearer {self.tokens.get_access_token()}"}
            print(self.HEADERS)
            response = requests.get(
                f"{PHUE.LIGHTS_URL.value}/{id}", headers=HEADERS)
            response = json.loads(response.text)
            self.name = response['name']
            self.state = response['state']['on']
            self.brightness = response['state']['bri']
            self.x = response['state']['xy'][0]
            self.y = response['state']['xy'][1]
            print("Lights have been initialized!")
        else:
            print("Light cannot be initialized. Please generate an access token!")

    def pull_light_data(self):
        HEADERS = {"Authorization": f"Bearer {self.tokens.get_access_token()}"}
        print(HEADERS)
        response = json.loads(requests.get(
            f"{PHUE.LIGHTS_URL.value}/{self.id}", headers=HEADERS).text)
        print(response)
        self.name = response['name']
        self.state = response['state']['on']
        self.brightness = response['state']['bri']
        self.x = response['state']['xy'][0]
        self.y = response['state']['xy'][1]
        print("Light data has been pulled!")

    def store_light_data(self):
        connection = sqlite3.connect(DB_URL)
        instance = connection.cursor()
        instance.execute(
            f"{SQL.INSERT.value} {Tables.LIGHT.value} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (self.id, self.name, self.turn_on_date, self.turn_on_dow, self.turn_on_time,
                self.turn_off_date, self.turn_off_dow, self.turn_off_time, self.brightness,
                self.x, self.y))
        # TODO: ACCOUNT FOR LIGHT BEING TURNED ON, PROGRAM CRASHING, THEN TURNING LIGHT OFF
        connection.commit()
        connection.close()

    def set_light_on(self, now):
        self.turn_on_date = now.strftime('%Y-%m-%d')
        self.turn_on_dow = now.strftime('%A')
        self.turn_on_time = now.strftime('%H:%M:%S')
        self.turn_on_info = now
        return f"Light {self.id} has been turned on!", 200

    def set_light_off(self, now):
        self.turn_off_date = now.strftime('%Y-%m-%d')
        self.turn_off_dow = now.strftime('%A')
        self.turn_off_time = now.strftime('%H:%M:%S')
        self.turn_off_info = now
        self.store_light_data()
        return f"Light {self.id} has been turned off!", 200

    def set_light(self, state: str):
        if not self.tokens.get_access_token():
            return "Light cannot be turned on. Please generate the tokens.", 403
        assert state != self.state
        raw = '{"on": true}' if state == "on" else '{"on": false}'
        self.HEADERS['Authorization'] = f"Bearer {self.tokens.get_access_token()}"
        requests.put(
            f"{PHUE.LIGHTS_URL.value}/{self.id}/state",
            headers=self.HEADERS,
            data=raw
        )
        self.state = state
        return self.set_light_on(datetime.now()) if self.state == "on" else\
            self.set_light_off(datetime.now())

    def get_light_data(self):
        if not self.tokens.get_access_token():
            return "Cannot get light data. Please generate an access token!", 403
        return {
            "id": self.id,
            "name": self.name,
            "state": self.state,
            "brightness": self.brightness,
            "x": self.x,
            "y": self.y
        }, 200
