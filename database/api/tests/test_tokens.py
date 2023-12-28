import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from ..lights.tokens.tokens import Tokens
from ..sqlite.sqlite import SQLite


@pytest.fixture
def tokens_instance():
    # Fixture to create an instance of the Tokens class for testing
    return Tokens()


def test_set_tokens(tokens_instance):
    with SQLite() as db:
        data, _ = db.get_one("TOKENS")
        assert tokens_instance.generated_at == data[0]
        assert tokens_instance.access_token == data[1]
        assert tokens_instance.refresh_token == data[2]


def test_pull_tokens(tokens_instance):
    # Mocking the SQLite class and its methods
    with patch.object(SQLite, 'get_one', return_value=(('2023-01-01', 'token123', 'refresh123'), 200)):
        # Calling the method to be tested
        tokens_instance.pull_tokens()

        assert (tokens_instance.generated_at == '2023-01-01')
        assert (tokens_instance.access_token == 'token123')
        assert (tokens_instance.refresh_token == 'refresh123')


def test_get_access_token(tokens_instance):
    # Case 1: No generated_at (tokens not obtained)
    tokens_instance.generated_at = None
    result = tokens_instance.get_access_token()
    assert result == (
        "Access Token cannot be obtained. Please generate the tokens!", 409)

    # Case 2: Valid access token
    tokens_instance.generated_at = (
        datetime.now() - timedelta(seconds=240)).strftime("%Y-%m-%d %H:%M:%S.%f")
    tokens_instance.access_token = "test_access_token"
    result = tokens_instance.get_access_token()
    assert result == (tokens_instance.access_token, 200)

    # Case 3: Expired access token
    tokens_instance.generated_at = (
        datetime.now() - timedelta(seconds=700000)).strftime("%Y-%m-%d %H:%M:%S.%f")
    tokens_instance._refresh_access_token = MagicMock(
        return_value=("new_access_token", 200))
    result = tokens_instance.get_access_token()
    assert result == ("new_access_token", 200)


def test_refresh_access_token(tokens_instance):
    # Mock the requests.post method to simulate a successful response
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = '{"access_token": "new_access_token", "refresh_token": "new_refresh_token"}'

        result = tokens_instance._refresh_access_token()

    # Verify the expected calls
    mock_post.assert_called_once()

    # Verify the result
    assert result == ("new_access_token", 200)


def test_get_access_token(tokens_instance):
    # Case 1: No generated_at (tokens not obtained)
    tokens_instance.generated_at = None
    result = tokens_instance.get_access_token()
    assert result == (
        "Access Token cannot be obtained. Please generate the tokens!", 409)

    # Case 2: Valid access token
    tokens_instance.generated_at = (
        datetime.now() - timedelta(seconds=240)).strftime("%Y-%m-%d %H:%M:%S.%f")
    tokens_instance.access_token = "test_access_token"
    result = tokens_instance.get_access_token()
    assert result == (tokens_instance.access_token, 200)

    # Case 3: Expired access token
    tokens_instance.generated_at = (
        datetime.now() - timedelta(seconds=700000)).strftime("%Y-%m-%d %H:%M:%S.%f")
    tokens_instance._refresh_access_token = MagicMock(
        return_value=("new_access_token", 200))
    result = tokens_instance.get_access_token()
    assert result == ("new_access_token", 200)
