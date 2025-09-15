class Customer:
    def __init__(self, id, date="", lastName="", firstName="", birthDate="",
                 address="", telephoneNumber="", email="", insurance="",
                 doctor="", pretreatment="", reason=""):
        self.id = id
        self.date = date
        self.lastName = lastName
        self.firstName = firstName
        self.birthDate = birthDate
        self.address = address
        self.telephoneNumber = telephoneNumber
        self.email = email
        self.insurance = insurance
        self.doctor = doctor
        self.pretreatment = pretreatment
        self.reason = reason

    def update_details(self, **kwargs):
        # Update customer details except ID
        for key, value in kwargs.items():
            if key != "id" and hasattr(self, key):
                setattr(self, key, value)