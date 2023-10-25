from flask import Flask, json, request
import sqlite3

# Setup


# Create table
# instance.execute(
#     """CREATE TABLE day (
#         avg_temp integer,
#         lamp_runtime integer,
#         heater_runtime integer,
#         fan_runtime integer
# )
# """)

# Inject data
# instance.execute("INSERT INTO day VALUES (20, 456, 200, 13)")

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/create-table", methods=['POST'])
def create_table():
    connection = sqlite3.connect('../smarthome.db')
    instance = connection.cursor()
    body = request.json
    try:
        instance.execute(
            f"""CREATE TABLE {body['table_name']} (
            avg_temp integer,
            lamp_runtime integer,
            heater_runtime integer,
            fan_runtime integer
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
