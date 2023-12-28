import sqlite3
from ..constants import SQL


def insert_statement(table, values):
    params = ", ".join("?" for _ in range(len(values)))
    return f"{SQL.INSERT.value} {table} VALUES ({params})"


class SQLite:

    def __init__(self, db="../smarthome.db"):
        self.db = db
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
            self.conn.commit()
            self.conn.close()

    def _execute_query(self, success_message, query, parameters=None):
        with self.conn:
            cursor = self.conn.cursor()
            try:
                if parameters:
                    cursor.execute(query, parameters)
                else:
                    cursor.execute(query)
            except sqlite3.Error as e:
                return str(e), 409
            return success_message, 201

    def create_table(self, name, columns):
        self._check_conn()
        query = f"{SQL.CREATE.value} {name} ({columns})"
        return self._execute_query(f"Success! Table '{name}' has been created!", query)

    def insert(self, name, values):
        self._check_conn()
        query = insert_statement(name, values)
        return self._execute_query(f"Success! Data inserted into table '{name}'!", query, values)

    def delete_all(self, name):
        self._check_conn()
        query = f"{SQL.DELETE.value} {name}"
        return self._execute_query(f"Success! Table {name}'s data has been deleted.", query)

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
            return result, 200

    def get_all(self, name):
        return self._select(name, lambda cursor: cursor.fetchall())

    def get_one(self, name):
        return self._select(name, lambda cursor: cursor.fetchone())

    def table_exists(self, table_name):
        """
        Check if a table exists in the database.

        Args:
            table_name (str): The name of the table.

        Returns:
            bool: True if the table exists, False otherwise.
        """
        with self.conn:
            cursor = self.conn.cursor()

            # Check if the table exists in sqlite_master
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            result = cursor.fetchone()

            # Return True if the table exists, False otherwise
            return result is not None
