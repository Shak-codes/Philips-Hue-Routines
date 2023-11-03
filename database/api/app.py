from flask import Flask, request
import json
from datetime import datetime
import sqlite3
import requests
from lights import light

from constants import DB_URL, Tables, Params, SQL, PHUE
from sqlite import sqlite


app = Flask(__name__)

Light1 = light.Light(1)
Light2 = light.Light(3)


@app.route("/listener")
def generate_refresh_token():
    code = request.args.get(Params.CODE.value)
    url = f"https://api.meethue.com/oauth2/token?code={code}&grant_type=authorization_code"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    response = json.loads(requests.post(url, auth=PHUE.AUTH.value).text)
    access_token = response[Params.ACCESS_TOKEN.value]
    refresh_token = response[Params.REFRESH_TOKEN.value]
    c = sqlite.SQLite()
    response, code = c.delete_all(Tables.TOKENS.value)
    if code == 409:
        c.close_conn()
        return response
    response, code = c.insert(
        Tables.TOKENS.value, (generated_at, access_token, refresh_token))
    if code == 409:
        c.close_conn()
        return response
    Light1.tokens.pull_tokens()
    Light2.tokens.pull_tokens()
    Light1.pull_light_data()
    Light2.pull_light_data()
    return "Success! Tokens have been generated!", 201


@app.route("/create-table", methods=['POST'])
def create_table():
    body = request.json
    columns = body[Params.COLUMNS.value]
    table_columns = ""
    for key in columns:
        try:
            assert (columns[key] in Tables.COLUMN_TYPES.value)
        except:
            message = f"Table column '{key}' can only be of type 'text', 'real' or 'integer'. '{columns[key]}' is not allowed."
            return message, 409
        else:
            table_columns += f"{key} {columns[key]},\n"
    table_columns = table_columns[:-2]
    c = sqlite.SQLite()
    response = c.create_table(body['table_name'], table_columns)
    c.close_conn()
    return response


@app.route("/lights/<id>/power-on", methods=['POST'])
def power_on(id):
    light = Light1 if int(id) == 1 else Light2
    response, code = light.set_light("on")
    if code == 403:
        return response, code
    response = f"Success! Lamp {id} turned on at {light.turn_on_time} with brightness {light.brightness} and xy: {light.x}, {light.y}"
    return response, 200


@app.route("/lights/<id>/power-off", methods=['POST'])
def power_off(id):
    assert id == request.view_args[Params.ID.value]
    light = Light1 if int(id) == 1 else Light2
    response, code = light.set_light("off")
    if code == 403:
        return response, code
    time_active = (light.turn_off_info - light.turn_on_info).total_seconds()
    message = f'''Success! The lamp was turned on at {light.turn_on_time} and turned off at {light.turn_off_time}.
    The lamp was on for {round(divmod(time_active, 60)[0])} minutes and {round(divmod(time_active, 60)[1])} seconds.'''
    return message, 201


@app.route("/db/<table>", methods=['GET'])
def get_dblight_data(table):
    assert table == request.view_args['table']
    c = sqlite.SQLite()
    response = c.get_all(table)
    c.close_conn()
    return response, 200


@app.route("/lights/state", methods=["GET"])
def curr_light_state():
    state = []
    state.append(Light1.get_light_data())
    state.append(Light2.get_light_data())
    return state
