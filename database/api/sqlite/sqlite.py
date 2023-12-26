import sqlite3
from constants import SQL


def insert_statement(table, values):
    params = "(".join(["?, " for i in range(1, len(values))], "?)")
    return f"{SQL.INSERT.value} {table} VALUES {params}"


class SQLite:
    db = "../smarthome.db"
    conn = None

    def check_conn(self) -> None:
        if self.conn is None:
            self.conn = sqlite3.connect(self.db)

    def close_conn(self) -> None:
        if self.conn is not None:
            self.conn.close()

    def create_table(self, name, columns) -> (str, int):
        self.check_conn()
        c = self.conn.cursor()
        try:
            c.execute(
                f"""{SQL.CREATE.value} {name} (
                    {columns}
                )"""
            )
            self.conn.commit()
        except:
            return f"Table '{name}' already exists.", 409
        else:
            return f"Success! Table '{name}' has been created!", 201

    def insert(self, name, values) -> (str, int):
        self.check_conn()
        c = self.conn.cursor()
        try:
            c.execute(
                f"{insert_statement(name, values)}",
                values
            )
            self.conn.commit()
        except:
            return f"Table '{name}' does not exist. Cannot insert data.", 409
        else:
            return f"Success! Data inserted into table '{name}'!", 201

    def delete_all(self, name) -> (str, int):
        self.check_conn()
        c = self.conn.cursor()
        try:
            c.execute(f"{SQL.DELETE.value} {name}")
            self.conn.commit()
        except:
            return f"Table '{name}' does not exist. Cannot delete a non-existing table's data.", 409
        else:
            return f"Success! Table {name}'s data has been deleted.", 201

    def get_all(self, name) -> (str, int):
        self.check_conn()
        c = self.conn.cursor()
        try:
            c.execute(f"{SQL.SELECT_ALL.value} {name}")
        except:
            return f"Table '{name}' does not exist. Cannot get data.", 409
        else:
            return f"{c.fetchall()}", 200

    def get_one(self, name) -> (str, int):
        self.check_conn()
        c = self.conn.cursor()
        try:
            c.execute(f"{SQL.SELECT_ALL.value} {name}")
        except:
            return f"Table '{name}' does not exist. Cannot get data.", 409
        else:
            return f"{c.fetchone()}", 200
