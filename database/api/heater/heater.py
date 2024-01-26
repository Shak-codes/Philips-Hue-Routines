from ..credentials import GOVEE_API_KEY, HEATER_MAC_ADDRESS
from ..constants import HEATER_MODEL, GOVEE_API, Tables, TABLE_COLUMNS
from ..sqlite.sqlite import SQLite

from datetime import datetime
import requests


class Heater:
    HEADERS = {"Govee-API-Key": GOVEE_API_KEY}

    def __init__(self):
        with SQLite() as db:
            if not db.table_exists('HEATER') or not db.table_exists('HEATER_STATE'):
                db.create_table(Tables.HEATER.value,
                                TABLE_COLUMNS.HEATER.value)
                db.create_table(Tables.HEATER_STATE.value,
                                TABLE_COLUMNS.HEATER_STATE.value)

            result, _ = db.get_one(Tables.HEATER_STATE.value)
            if result:
                self.state = result
            else:
                self.state = "off"

    def manage(self, name, state):
        data = {"device": HEATER_MAC_ADDRESS, "model": HEATER_MODEL,
                "cmd": {"name": name, "value": state}}
        response = requests.put(f"{GOVEE_API}/appliance/devices/control",
                                headers=self.HEADERS, json=data)
        self.state = state
        now = datetime.now()
        self._turn_off(now) if state == "off" else self._turn_on(now)
        return "Success!", response.status_code

    def _turn_on(self, now):
        self.turn_on_date = now.strftime('%Y-%m-%d')
        self.turn_on_dow = now.strftime('%A')
        self.turn_on_time = now.strftime('%H:%M:%S')

    def _turn_off(self, now):
        self.turn_off_date = now.strftime('%Y-%m-%d')
        self.turn_off_dow = now.strftime('%A')
        self.turn_off_time = now.strftime('%H:%M:%S')
        self._store_heater_data()

    def _store_heater_data(self):
        values = (self.turn_on_date, self.turn_on_dow, self.turn_on_time,
                  self.turn_off_date, self.turn_off_dow, self.turn_off_time,
                  self.state)
        with SQLite() as db:
            response, code = db.insert(Tables.HEATER.value, values)
            return response, code

    def _store_last_heater_state(self, state):
        value = (state)
        with SQLite() as db:
            response, code = db.insert(Tables.HEATER_STATE.value, value)
            return response, code

    def get_heater_data(self):
        with SQLite() as db:
            return db.get_one(Tables.HEATER.value)
