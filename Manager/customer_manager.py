import os
import sqlite3
from Domain.customer import Customer
from Data.Mssql import sql_commands as sql

class CustomerManager:
    def __init__(self, db_path: str):
        self.db_path = os.path.abspath(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode = WAL;")
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self._create_table()

    def _create_table(self):
        self.conn.execute(sql.CREATE_CUSTOMER_TABLE)
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(lastName, firstName);")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);")
        self.conn.commit()

    def add_customer(self, **data):
        data.pop("id", None)
        cur = self.conn.execute(sql.INSERT_CUSTOMER, data)
        self.conn.commit()
        new_id = cur.lastrowid
        return self.get_customer_by_id(new_id)

    def update_customer(self, id, **data):
        data["id"] = id
        self.conn.execute(sql.UPDATE_CUSTOMER, data)
        self.conn.commit()
        return self.get_customer_by_id(id)

    def delete_customer_by_id(self, id):
        self.conn.execute(sql.DELETE_CUSTOMER, {"id": id})
        self.conn.commit()

    def get_all_customers(self):
        cursor = self.conn.execute(sql.SELECT_ALL_CUSTOMERS)
        return [Customer(**row) for row in map(dict, cursor.fetchall())]

    def get_customer_by_id(self, id):
        cursor = self.conn.execute(sql.SELECT_CUSTOMER_BY_ID, {"id": id})
        row = cursor.fetchone()
        return Customer(**dict(row)) if row else None

    def search_customers(self, query):
        query = f"%{(query or '').lower()}%"
        cursor = self.conn.execute(sql.SEARCH_CUSTOMERS, {"query": query})
        return [Customer(**row) for row in map(dict, cursor.fetchall())]

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass