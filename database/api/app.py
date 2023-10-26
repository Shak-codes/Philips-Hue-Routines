from flask import Flask, json, request
from flask_caching import Cache
from datetime import datetime
import sqlite3
import threading

# Inject data
# instance.execute("INSERT INTO day VALUES (20, 456, 200, 13)")

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 86400
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)


@cache.memoize(86400)
def set_light_on(light, color):
    now = datetime.now()
    return {
        "date": now.strftime('%Y:%m:%d'),
        "dow": now.strftime("%A"),
        "start_time": now,
        "color": color
    }


@app.route("/create-table", methods=['POST'])
def create_table():
    body = request.json
    columns = body['columns']
    table_columns = ""
    for key in columns:
        try:
            assert (columns[key] in ['integer', 'text'])
        except:
            response = app.response_class(
                response=f"Table column '{key}' can only be of type 'text' or 'integer'. '{columns[key]}' is not allowed.",
                status=409,
                mimetype='application.json'
            )
            return response
        else:
            table_columns += f"{key} {columns[key]},\n"
    table_columns = table_columns[:-2]
    try:
        connection = sqlite3.connect('../smarthome.db')
        instance = connection.cursor()
        instance.execute(
            f"""CREATE TABLE {body['table_name']} (
                {table_columns}
            )
        """
        )
    except:
        response = app.response_class(
            response=f"Table '{body['table_name']}' already exists.",
            status=409,
            mimetype='application.json'
        )
        return response
    else:
        response = app.response_class(
            response=f"Success! Table '{body['table_name']}' has been created!",
            status=201,
            mimetype='application.json'
        )
        return response
    finally:
        connection.close()


@app.route("/lights/<id>/power-on", methods=['POST'])
def power_on(id):
    assert id == request.view_args['id']
    body = request.json
    color = body['color']
    set_light_on(id, color)
    response = app.response_class(
        response=f"Success! Lamp {id} turned on at {set_light_on(id, color)['start_time']} with color: {color}",
        status=201,
        mimetype='application.json'
    )
    return response


@app.route("/lights/<id>/power-off", methods=['POST'])
def power_off(id):
    assert id == request.view_args['id']
    now = datetime.now()
    color = request.args.get('color')
    data = set_light_on(id, color)
    difference = now - data['start_time']
    difference = difference.total_seconds()
    if difference == 0:
        cache.delete_memoized(set_light_on, id)
        response = app.response_class(
            response=f"Failed! Lamp {id} with color({color}) does not exist or was never on in the first place.",
            status=409,
            mimetype='application.json'
        )
        return response
    cache.delete_memoized(set_light_on, id, color)
    connection = sqlite3.connect('../smarthome.db')
    instance = connection.cursor()
    instance.execute(
        f"INSERT INTO lights VALUES (?, ?, ?, ?, ?, ?)",
        (id, data['date'], data['dow'], data['start_time'].strftime('%H:%M:%S'), now.strftime('%H:%M:%S'), color))
    connection.commit()
    response = app.response_class(
        response=f"Success! The lamp was turned on at {data['start_time'].strftime('%H:%M:%S')} and turned off at {now.strftime('%H:%M:%S')}."
        f"The lamp was on for {round(divmod(difference, 60)[0])} minutes and {round(divmod(difference, 60)[1])} seconds.",
        status=201,
        mimetype='application.json'
    )
    connection.close()
    return response


@app.route("/lights", methods=['GET'])
def get_light_data():
    connection = sqlite3.connect('../smarthome.db')
    instance = connection.cursor()
    instance.execute("SELECT * FROM lights")
    response = app.response_class(
        response=f"{instance.fetchall()}",
        status=200,
        mimetype='application.json'
    )
    connection.close()
    return response
