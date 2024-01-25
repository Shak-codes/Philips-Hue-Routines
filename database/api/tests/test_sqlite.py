import pytest
import os
from ..sqlite.sqlite import SQLite


@pytest.fixture(scope='session', autouse=True)
def sqlite_instance():
    with SQLite() as db:
        yield db
    project_root = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", ".."))
    db_path = os.path.join(project_root, "smarthome.db")
    os.remove(db_path)


def test_create_table_success(sqlite_instance):
    result, status_code = sqlite_instance.create_table(
        "test_table", "id integer, name text")
    assert status_code == 201
    assert "success" in result.lower()


def test_create_table_failure(sqlite_instance):
    # Assuming the table "test_table" already exists
    result, status_code = sqlite_instance.create_table(
        "test_table", "id integer, name text")
    assert status_code == 409
    assert "already exists" in result.lower()


def test_insert_success(sqlite_instance):
    result, status_code = sqlite_instance.insert(
        "test_table", (1, "test_name"))
    result, status_code = sqlite_instance.insert(
        "test_table", (2, "test_name2"))
    assert status_code == 201
    assert "success" in result.lower()


def test_insert_failure_nonexistant_table(sqlite_instance):
    result, status_code = sqlite_instance.insert(
        "test_table2", (1, "test_name"))
    assert status_code == 409
    assert "no such table" in result.lower()


def test_insert_failure_not_enough_params(sqlite_instance):
    result, status_code = sqlite_instance.insert(
        "test_table", [1])
    assert status_code == 409
    assert "has 2 columns" in result.lower()


def test_insert_failure_too_many_params(sqlite_instance):
    result, status_code = sqlite_instance.insert(
        "test_table", (1, "test_name", "test_name"))
    assert status_code == 409
    assert "has 2 columns" in result.lower()


def test_get_all_success(sqlite_instance):
    result, status_code = sqlite_instance.get_all("test_table")
    assert status_code == 200
    assert "[(1, 'test_name'), (2, 'test_name2')]" in result.lower()


def test_get_all_failure(sqlite_instance):
    result, status_code = sqlite_instance.get_all("test_table2")
    assert status_code == 409
    assert "does not exist" in result.lower()


def test_get_one_success(sqlite_instance):
    result, status_code = sqlite_instance.get_one("test_table")
    assert status_code == 200
    assert "(1, 'test_name')" in result.lower()


def test_get_one_failure(sqlite_instance):
    result, status_code = sqlite_instance.get_one("test_table2")
    assert status_code == 409
    assert "does not exist" in result.lower()


def test_delete_all_success(sqlite_instance):
    result, status_code = sqlite_instance.delete_all(
        "test_table")
    assert status_code == 201
    assert "success" in result.lower()


def test_delete_all_failure_nonexistant_table(sqlite_instance):
    result, status_code = sqlite_instance.delete_all(
        "test_table2")
    assert status_code == 409
    assert "no such table" in result.lower()


def test_table_exists_true(sqlite_instance):
    assert sqlite_instance.table_exists(
        "test_table") == True


def test_table_exists_false(sqlite_instance):
    assert sqlite_instance.table_exists(
        "test_table2") == False
