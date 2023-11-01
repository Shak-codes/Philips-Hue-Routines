from datetime import datetime
from constants import PHUE_LIGHTS_URL
from constants import DB_URL
import requests
import json
import sqlite3

from tokens import Tokens


class Light:
    tokens = Tokens()
    HEADERS = {"Content-Type": "application/json"}

    def __init__(self, id: int):
        self.id = id
        if self.tokens.get_access_token():
            HEADERS = {
                "Authorization": f"Bearer {self.tokens.get_access_token()}"}
            print(self.HEADERS)
            response = requests.get(
                f"{PHUE_LIGHTS_URL}/{id}", headers=HEADERS)
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
            f"{PHUE_LIGHTS_URL}/{self.id}", headers=HEADERS).text)
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
            f"INSERT INTO lights VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
        print(f"Light {self.id} has been turned on!")

    def set_light_off(self, now):
        self.turn_off_date = now.strftime('%Y-%m-%d')
        self.turn_off_dow = now.strftime('%A')
        self.turn_off_time = now.strftime('%H:%M:%S')
        self.turn_off_info = now
        self.store_light_data()
        print(f"Light {self.id} has been turned off!")

    def set_light(self, state: str):
        if self.tokens.get_access_token():
            assert state != self.state
            raw = '{"on": true}' if state == "on" else '{"on": false}'
            self.HEADERS['Authorization'] = f"Bearer {self.tokens.get_access_token()}"
            requests.put(
                f"{PHUE_LIGHTS_URL}/{self.id}/state",
                headers=self.HEADERS,
                data=raw
            )
            self.state = state
            if self.state == "on":
                self.set_light_on(datetime.now())
            else:
                self.set_light_off(datetime.now())
        else:
            print("Light cannot be set. Please generate an access token!")

    def get_light_data(self):
        if self.tokens.get_access_token():
            return {
                "id": self.id,
                "name": self.name,
                "state": self.state,
                "brightness": self.brightness,
                "x": self.x,
                "y": self.y
            }
        return "Cannot get light data. Please generate an access token!"
