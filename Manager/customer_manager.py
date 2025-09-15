from Domain.customer import Customer

class CustomerManager:
    def __init__(self):
        self.customers = []
        self.free_ids = set()
        self.next_id = 1

    def _generate_id(self):
        # Generate a new ID, reuse freed IDs
        if self.free_ids:
            return self.free_ids.pop()
        else:
            id_ = self.next_id
            self.next_id += 1
            return id_
    
    def preview_next_id(self) -> int:
        # kleinste freie ID (falls vorhanden), sonst next_id
        return min(self.free_ids) if self.free_ids else self.next_id

    def save_customer(self, customer):
        # Save a new customer
        self.customers.append(customer)

    def add_customer(self, **data):
        # Automatically assign an ID
        id_ = self._generate_id()
        data["id"] = id_
        customer = Customer(**data)
        self.save_customer(customer)
        return customer

    def update_customer(self, id, **data):
        # Update existing customer by ID
        customer = self.get_customer_by_id(id)
        if customer:
            customer.update_details(**data)
        return customer

    def delete_customer_by_id(self, id):
        # Delete customer and free ID
        customer = self.get_customer_by_id(id)
        if customer:
            self.customers.remove(customer)
            self.free_ids.add(customer.id)

    def get_all_customers(self):
        return self.customers

    def get_customer_by_id(self, id):
        for c in self.customers:
            if c.id == id:
                return c
        return None

    def search_customers(self, query):
        query = query.lower()
        results = []
        for c in self.customers:
            # Search in firstName, lastName, email
            if query in c.firstName.lower() or query in c.lastName.lower() or query in c.email.lower():
                results.append(c)
        return results