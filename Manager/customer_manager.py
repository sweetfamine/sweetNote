import sqlite3
from Domain.customer import Customer
from Data.Mssql import sql_commands as sql

DB_PATH = "data/customers.db"

class CustomerManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        self.conn.execute(sql.CREATE_CUSTOMER_TABLE)
        self.conn.commit()

    def _generate_id(self):
        cursor = self.conn.execute("SELECT MAX(id) FROM customers")
        max_id = cursor.fetchone()[0]
        return (max_id or 0) + 1

    def add_customer(self, **data):
        if "id" not in data or data["id"] is None:
            data["id"] = self._generate_id()
        self.conn.execute(sql.INSERT_CUSTOMER, data)
        self.conn.commit()
        return self.get_customer_by_id(data["id"])

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
        query = f"%{query.lower()}%"
        cursor = self.conn.execute(sql.SEARCH_CUSTOMERS, {"query": query})
        return [Customer(**row) for row in map(dict, cursor.fetchall())]

    def preview_next_id(self):
        cursor = self.conn.execute("SELECT MAX(id) FROM customers")
        max_id = cursor.fetchone()[0]
        return (max_id or 0) + 1
