from flask import Flask, request, jsonify
import json
from datetime import datetime
import sqlite3
import requests
from light import Light

from constants import PHUE_AUTH, DB_URL, Tables, Params, SQL

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 86400
}

app = Flask(__name__)
app.config.from_mapping(config)

Light1 = Light(1)
Light2 = Light(3)


def get_response(response: str, status=200, mimetype='application.json'):
    response = app.response_class(
        response=response,
        status=status,
        mimetype=mimetype
    )
    return response


@app.route("/listener")
def generate_refresh_token():
    code = request.args.get(Params.CODE.value)
    url = f"https://api.meethue.com/oauth2/token?code={code}&grant_type=authorization_code"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    response = json.loads(requests.post(url, auth=PHUE_AUTH).text)
    access_token = response[Params.ACCESS_TOKEN.value]
    refresh_token = response[Params.REFRESH_TOKEN.value]
    connection = sqlite3.connect(DB_URL)
    instance = connection.cursor()
    instance.execute(f"{SQL.DELETE.value} {Tables.TOKENS.value}",)
    instance.execute(
        f"{SQL.INSERT.value} {Tables.TOKENS.value} VALUES (?, ?, ?)",
        (generated_at, access_token, refresh_token)
    )
    connection.commit()
    connection.close()

    Light1.tokens.pull_tokens()
    Light2.tokens.pull_tokens()
    Light1.pull_light_data()
    Light2.pull_light_data()
    return response


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
            return get_response(message, status=409)
        else:
            table_columns += f"{key} {columns[key]},\n"
    table_columns = table_columns[:-2]
    try:
        connection = sqlite3.connect('../smarthome.db')
        instance = connection.cursor()
        instance.execute(
            f"""{SQL.CREATE.value} {body['table_name']} (
                {table_columns}
            )
        """
        )
    except:
        message = f"Table '{body['table_name']}' already exists."
        return get_response(message, 409)
    else:
        message = f"Success! Table '{body['table_name']}' has been created!"
        return get_response(message, 201)
    finally:
        connection.close()


@app.route("/lights/<id>/power-on", methods=['POST'])
def power_on(id):
    light = Light1 if int(id) == 1 else Light2
    light.set_light("on")
    message = f"Success! Lamp {id} turned on at {light.turn_on_time} with brightness {light.brightness} and xy: {light.x}, {light.y}"
    return get_response(message, 201)


@app.route("/lights/<id>/power-off", methods=['POST'])
def power_off(id):
    assert id == request.view_args[Params.ID.value]
    print("ID IS VALID")
    light = Light1 if int(id) == 1 else Light2
    print(f"Attempting to turn off light {id}")
    light.set_light("off")
    time_active = (light.turn_off_info - light.turn_on_info).total_seconds()
    message = f'''Success! The lamp was turned on at {light.turn_on_time} and turned off at {light.turn_off_time}.
    The lamp was on for {round(divmod(time_active, 60)[0])} minutes and {round(divmod(time_active, 60)[1])} seconds.'''
    return get_response(message, 201)


@app.route("/db/lights", methods=['GET'])
def get_dblight_data():
    connection = sqlite3.connect('../smarthome.db')
    instance = connection.cursor()
    instance.execute(f"{SQL.SELECT_ALL.value} {Tables.LIGHT.value}")
    message = f"{instance.fetchall()}"
    connection.close()
    return get_response(message, 200)


@app.route("/lights/state", methods=["GET"])
def curr_light_state():
    state = []
    state.append(Light1.get_light_data())
    state.append(Light2.get_light_data())
    return jsonify(state)
