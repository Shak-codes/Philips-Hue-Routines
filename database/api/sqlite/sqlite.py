import sqlite3
from ..constants import SQL


def insert_statement(table, values):
    params = ", ".join("?" for _ in range(len(values)))
    return f"{SQL.INSERT.value} {table} VALUES ({params})"


class SQLite:
    db = "../smarthome.db"

    def __init__(self):
        self.conn = None

    def __enter__(self):
        self._check_conn()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._close_conn()

    def _check_conn(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db)

    def _close_conn(self):
        if self.conn is not None:
            self.conn.close()

    def _execute_query(self, query, parameters=None):
        with self.conn:
            cursor = self.conn.cursor()
            try:
                if parameters:
                    cursor.execute(query, parameters)
                else:
                    cursor.execute(query)
            except sqlite3.Error as e:
                return str(e), 409
            return None, 201

    def create_table(self, name, columns):
        self._check_conn()
        query = f"{SQL.CREATE.value} {name} ({columns})"
        result, status = self._execute_query(query)
        return result or f"Success! Table '{name}' has been created!", status

    def insert(self, name, values):
        self._check_conn()
        query = insert_statement(name, values)
        result, status = self._execute_query(query, values)
        return result or f"Success! Data inserted into table '{name}'!", status

    def delete_all(self, name):
        self._check_conn()
        query = f"{SQL.DELETE.value} {name}"
        result, status = self._execute_query(query)
        return result or f"Success! Table {name}'s data has been deleted.", status

    def _select(self, name, fetch_method):
        self._check_conn()
        query = f"{SQL.SELECT_ALL.value} {name}"
        with self.conn:
            cursor = self.conn.cursor()
            try:
                cursor.execute(query)
                result = fetch_method(cursor)
            except sqlite3.Error:
                return f"Table '{name}' does not exist. Cannot get data.", 409
            return f"{result}", 200

    def get_all(self, name):
        return self._select(name, lambda cursor: cursor.fetchall())

    def get_one(self, name):
        return self._select(name, lambda cursor: cursor.fetchone())
