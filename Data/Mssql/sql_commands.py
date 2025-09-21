# Table creation
CREATE_CUSTOMER_TABLE = """
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    date TEXT,
    lastName TEXT,
    firstName TEXT,
    birthDate TEXT,
    address TEXT,
    telephoneNumber TEXT,
    email TEXT,
    insurance TEXT,
    doctor TEXT,
    pretreatment TEXT,
    reason TEXT
)
"""

# Insert a new customer
INSERT_CUSTOMER = """
INSERT INTO customers (id, date, lastName, firstName, birthDate, address,
                       telephoneNumber, email, insurance, doctor, pretreatment, reason)
VALUES (:id, :date, :lastName, :firstName, :birthDate, :address,
        :telephoneNumber, :email, :insurance, :doctor, :pretreatment, :reason)
"""

# Update an existing customer
UPDATE_CUSTOMER = """
UPDATE customers
SET date=:date, lastName=:lastName, firstName=:firstName, birthDate=:birthDate,
    address=:address, telephoneNumber=:telephoneNumber, email=:email,
    insurance=:insurance, doctor=:doctor, pretreatment=:pretreatment, reason=:reason
WHERE id=:id
"""

# Delete customer by ID
DELETE_CUSTOMER = "DELETE FROM customers WHERE id=:id"

# Select all customers
SELECT_ALL_CUSTOMERS = "SELECT * FROM customers"

# Select customer by ID
SELECT_CUSTOMER_BY_ID = "SELECT * FROM customers WHERE id=:id"

# Search customers
SEARCH_CUSTOMERS = """
SELECT * FROM customers
WHERE LOWER(firstName) LIKE :query OR LOWER(lastName) LIKE :query OR LOWER(email) LIKE :query
"""
