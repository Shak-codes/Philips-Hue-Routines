import pytest
from unittest.mock import patch, MagicMock
from ..lights.lights import Lights
from ..lights.tokens.tokens import Tokens
from ..sqlite.sqlite import SQLite
from datetime import datetime
from ..constants import PHUE


@pytest.fixture
def light_instance():
    with patch('requests.get') as mock_get:

        mock_get.return_value = MagicMock(
            text='{"name": "Test Light", "state": {"on": false, "bri": 50, "xy": [0.5, 0.5]}}')

        return Lights(1)


def test_init_sets_attributes_correctly(light_instance):
    assert light_instance.id == 1
    assert light_instance.name == "Test Light"
    assert light_instance.on == False
    assert light_instance.brightness == 50
    assert light_instance.x == 0.5
    assert light_instance.y == 0.5


def test_pull_light_data(light_instance):
    with patch('requests.get') as mock_get:
        mock_get.return_value = MagicMock(
            text='{"name": "Updated Light", "state": {"on": true, "bri": 75, "xy": [0.6, 0.7]}}')

        light_instance.pull_light_data()

    assert light_instance.name == "Updated Light"
    assert light_instance.on == True
    assert light_instance.brightness == 75
    assert light_instance.x == 0.6
    assert light_instance.y == 0.7


def test_store_light_data(light_instance):
    light_instance.turn_on_date = '2023-01-01'
    light_instance.turn_on_dow = 'Sunday'
    light_instance.turn_on_time = '12:00:00'
    light_instance.turn_off_date = '2023-01-01'
    light_instance.turn_off_dow = 'Sunday'
    light_instance.turn_off_time = '12:05:00'

    with patch.object(SQLite, 'insert', return_value=("Success! Data inserted into table 'LIGHT'", 201)):
        response, code = light_instance.store_light_data()

    assert response == "Success! Data inserted into table 'LIGHT'"
    assert code == 201


def test_set_light_on(light_instance):
    now = datetime(2023, 1, 1, 12, 0, 0)
    response, code = light_instance.set_light_on(now)

    assert response == f"Light 1 has been turned on at 12:00:00!"
    assert code == 200
    assert light_instance.turn_on_date == '2023-01-01'
    assert light_instance.turn_on_dow == 'Sunday'
    assert light_instance.turn_on_time == '12:00:00'
    assert light_instance.on == True


def test_set_light_off(light_instance):
    now = datetime(2023, 1, 1, 12, 0, 0)
    response, code = light_instance.set_light_on(now)
    response, code = light_instance.set_light_off(now)

    assert response == f"Success! Data inserted into table 'LIGHTS'!"
    assert code == 201
    assert light_instance.turn_off_date == '2023-01-01'
    assert light_instance.turn_off_dow == 'Sunday'
    assert light_instance.turn_off_time == '12:00:00'
    assert light_instance.on == False


def test_set_light_success(light_instance):
    # Mock the Tokens class
    with patch.object(Tokens, 'get_access_token', return_value=("fake_token", 200)):
        # Mock the requests.put method
        with patch('requests.put') as mock_put:
            mock_put.return_value.status_code = 200

            # Call the set_light method
            _, code = light_instance.set_light()

            assert code == 200
            assert light_instance.on == True

            mock_put.assert_called_once_with(
                f"{PHUE.LIGHTS_URL.value}/1/state",
                headers={"Content-Type": "application/json",
                         "Authorization": "Bearer fake_token"},
                data='{"on": true}'
            )


def test_set_light_failure(light_instance):
    # Mock the Tokens class
    with patch.object(Tokens, 'get_access_token', return_value=("fake_token", 200)):
        # Mock the requests.put method
        with patch('requests.put') as mock_put:
            mock_put.return_value.status_code = 400

            response, code = light_instance.set_light()

            assert response == "API call to modify the light state has failed."
            assert code == 409


def test_get_light_data(light_instance):
    with patch.object(Tokens, 'get_access_token', return_value=("fake_token", 200)):
        data, code = light_instance.get_light_data()

        assert data == {
            "id": light_instance.id,
            "name": "Test Light",
            "on": False,
            "brightness": 50,
            "x": 0.5,
            "y": 0.5
        }
        assert code == 200
