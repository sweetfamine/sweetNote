CREATE_CUSTOMER_TABLE = """
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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

INSERT_CUSTOMER = """
INSERT INTO customers (date, lastName, firstName, birthDate, address,
                       telephoneNumber, email, insurance, doctor, pretreatment, reason)
VALUES (:date, :lastName, :firstName, :birthDate, :address,
        :telephoneNumber, :email, :insurance, :doctor, :pretreatment, :reason)
"""

UPDATE_CUSTOMER = """
UPDATE customers
SET date=:date, lastName=:lastName, firstName=:firstName, birthDate=:birthDate,
    address=:address, telephoneNumber=:telephoneNumber, email=:email,
    insurance=:insurance, doctor=:doctor, pretreatment=:pretreatment, reason=:reason
WHERE id=:id
"""

DELETE_CUSTOMER = "DELETE FROM customers WHERE id=:id"

SELECT_ALL_CUSTOMERS = "SELECT * FROM customers"

SELECT_CUSTOMER_BY_ID = "SELECT * FROM customers WHERE id=:id"

SEARCH_CUSTOMERS = """
SELECT * FROM customers
WHERE LOWER(firstName) LIKE :query
   OR LOWER(lastName)  LIKE :query
   OR LOWER(email)     LIKE :query
   OR LOWER(telephoneNumber) LIKE :query
"""
DELETE_ALL_CUSTOMERS = "DELETE FROM customers;"