from flask import Flask, request, jsonify
import json
from datetime import datetime
import requests

from .constants import Tables, Params, PHUE, TABLE_COLUMNS
from .sqlite.sqlite import SQLite


app = Flask(__name__)


def startup():
    with SQLite() as db:
        if (not db.table_exists("LIGHTS") and not db.table_exists("TOKENS")):
            db.create_table(Tables.LIGHT.value,
                            TABLE_COLUMNS.LIGHTS.value)
            db.create_table(Tables.TOKENS.value,
                            TABLE_COLUMNS.TOKENS.value)


startup()


@app.route("/listener")
def generate_refresh_token():
    code = request.args.get(Params.CODE.value)
    url = f"https://api.meethue.com/oauth2/token?code={code}&grant_type=authorization_code"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    try:
        tokens = json.loads(requests.post(url, auth=PHUE.AUTH.value).text)
        access_token, refresh_token = tokens[Params.ACCESS_TOKEN.value], tokens[Params.REFRESH_TOKEN.value]
    except requests.RequestException as e:
        return f"Error fetching tokens: {str(e)}", 500

    with SQLite() as db:
        response, code = db.delete_all(Tables.TOKENS.value)
        if code == 409:
            return response, 409

        response, code = db.insert(
            Tables.TOKENS.value, (generated_at, access_token, refresh_token))
        if code == 409:
            return response, 409

    return jsonify(tokens), 201
