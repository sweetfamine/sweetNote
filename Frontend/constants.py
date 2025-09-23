labels = [
    "ID", "Datum", "Name", "Vorname", "Geburtstag", "Adresse",
    "Telefon", "Email", "Versicherung", "Hausarzt", "Vorbehandlung", "Grund"
]

required_fields = {"Datum", "Vorname", "Name"}

label_to_attr = {
    "ID": "id",
    "Datum": "date",
    "Name": "lastName",
    "Vorname": "firstName",
    "Geburtstag": "birthDate",
    "Adresse": "address",
    "Telefon": "telephoneNumber",
    "Email": "email",
    "Versicherung": "insurance",
    "Hausarzt": "doctor",
    "Vorbehandlung": "pretreatment",
    "Grund": "reason"
}