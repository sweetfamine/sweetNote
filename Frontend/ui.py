import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import customtkinter as ctk
from tkinter import ttk, messagebox
from Manager.customer_manager import CustomerManager
from Domain.customer import Customer
from Frontend.widgets.tooltip import Tooltip
from Utils.validierung import (is_valid_email, is_valid_phone, parse_de_date, fmt_de_date)
from datetime import date

# --- Appearance settings ---
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("sweetNote - Kundenverwaltung")
root.geometry("1900x600")

manager = CustomerManager()

# --- Labels and attribute mapping ---
labels = [
    "ID", "Datum", "Name", "Vorname", "Geburtstag", "Adresse",
    "Telefon", "Email", "Versicherung", "Hausarzt", "Vorbehandlung", "Grund"
]

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

# --- Helper for UI feedback ---
def mark_invalid(entry):
    try:
        entry.configure(border_color="#ef4444")
    except Exception:
        pass

def clear_invalid(entry):
    try:
        entry.configure(border_color=None)
    except Exception:
        pass

# --- Update table with customer data ---
def update_table(customers=None):
    for row in tree.get_children():
        tree.delete(row)
    data = customers if customers is not None else manager.get_all_customers()
    for customer in data:
        def fmt(col):
            val = getattr(customer, label_to_attr[col])
            if col in ("Geburtstag", "Datum") and isinstance(val, str):
                return fmt_de_date(val)
            return val
        tree.insert("", "end", values=[fmt(col) for col in columns])

# --- Search functionality ---
def btn_search_click(event=None):
    query = entry_search.get()
    results = manager.search_customers(query)
    update_table(results)

# --- Delete functionality ---
def btn_delete_click():
    selected_item = tree.selection()
    if selected_item:
        kunde_id = int(tree.item(selected_item[0])["values"][0])
        manager.delete_customer_by_id(kunde_id)
        update_table()

# --- Add new customer window ---
def btn_add_click():
    open_customer_window(None)

# --- Edit existing customer window ---
def btn_edit_click():
    selected_item = tree.selection()
    if not selected_item:
        return
    kunde_id = int(tree.item(selected_item[0])["values"][0])
    kunde = manager.get_customer_by_id(kunde_id)
    if kunde:
        open_customer_window(kunde)

# --- Customer window for add/edit ---
def open_customer_window(customer=None):

    # Create new add customer window
    win = ctk.CTkToplevel(root)
    win.title("Kunde bearbeiten" if customer else "Neuen Kunden hinzufügen")
    
    width, height = 500, 650
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    win.geometry(f"{width}x{height}+{x}+{y}")

    win.attributes("-topmost", True)
    win.focus_force()

    main_frame = ctk.CTkFrame(win, corner_radius=10)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    entries_local = {}

    # Create entry fields
    for i, label in enumerate(labels):
        tk_label = ctk.CTkLabel(main_frame, text=label, anchor="e", width=120)
        tk_label.grid(row=i, column=0, padx=10, pady=8, sticky="e")

        entry = ctk.CTkEntry(main_frame, width=250)
        entry.grid(row=i, column=1, padx=10, pady=8, sticky="we")

        # ID field (read-only)
        if label == "ID":
            if customer:
                entry.insert(0, str(customer.id))
            else:
                entry.insert(0, str(manager.preview_next_id()))

            entry.configure(state="disabled", takefocus=False)
            try:
                entry.configure(
                    fg_color=("#eeeeee", "#2a2a2a"),   # Background
                    text_color=("#6b7280", "#9ca3af"), # Text
                    border_color=("#d1d5db", "#3f3f46")
                )
            except Exception:
                pass

            # Tooltip
            Tooltip(entry, "Die ID wird automatisch vergeben")
            entries_local[label] = entry
            continue

        # normale Felder
        if customer:
            # existierender Kunde -> gespeicherte Werte anzeigen
            attr = label_to_attr[label]
            value = getattr(customer, attr)
            if label in ("Geburtstag", "Datum") and isinstance(value, str):
                value = fmt_de_date(value)
            entry.insert(0, value if value else "")
        else:
            # neuer Kunde -> Datum automatisch vorbelegen
            if label == "Datum":
                entry.insert(0, date.today().strftime("%d.%m.%Y"))

        entries_local[label] = entry

        # live validation on focus out
        def on_focus_out(e, label=label, entry=entry):
            val = entry.get()
            clear_invalid(entry)
            if label == "Email" and not is_valid_email(val):
                mark_invalid(entry)
            elif label == "Telefon" and not is_valid_phone(val):
                mark_invalid(entry)
            elif label in ("Geburtstag", "Datum"):
                if val.strip() and not parse_de_date(val):
                    mark_invalid(entry)

        entry.bind("<FocusOut>", on_focus_out)

    # Buttons frame
    button_frame = ctk.CTkFrame(main_frame)
    button_frame.grid(row=len(labels), column=0, columnspan=2, pady=20)

    # --- Save customer ---
    def save_customer():
        errors = []
        data = {}

        for label in labels:
            if label == "ID":
                continue
            attr = label_to_attr[label]
            raw = entries_local[label].get().strip()
            clear_invalid(entries_local[label])

            # Pflichtfelder
            if label in ("Datum", "Vorname", "Name") and not raw:
                errors.append(f"{label} darf nicht leer sein.")
                mark_invalid(entries_local[label])
                continue

            if label == "Email":
                if not is_valid_email(raw):
                    errors.append("Bitte eine gültige Email angeben.")
                    mark_invalid(entries_local[label])
                data[attr] = raw

            elif label == "Telefon":
                if not is_valid_phone(raw):
                    errors.append("Telefonnummer ist ungültig (z. B. +49 123 4567).")
                    mark_invalid(entries_local[label])
                data[attr] = raw

            elif label in ("Geburtstag", "Datum"):
                if raw:
                    d = parse_de_date(raw)
                    if not d:
                        errors.append(f"{label}: bitte als TT.MM.JJJJ angeben.")
                        mark_invalid(entries_local[label])
                    else:
                        data[attr] = d.isoformat()
                else:
                    data[attr] = ""
            else:
                data[attr] = raw

        if errors:
            messagebox.showerror("Validierung", "\n".join(sorted(set(errors))))
            return

        if customer:
            manager.update_customer(customer.id, **data)
        else:
            manager.add_customer(**data)

        update_table()
        win.destroy()

    btn_save = ctk.CTkButton(button_frame, text="Speichern", width=120, command=save_customer)
    btn_save.pack(side="left", padx=10)

    btn_cancel = ctk.CTkButton(button_frame, text="Abbrechen", width=120, command=win.destroy)
    btn_cancel.pack(side="right", padx=10)

# --- Layout main window ---

# Top frame: search
frame_top = ctk.CTkFrame(root)
frame_top.pack(fill="x", padx=10, pady=10)

entry_search = ctk.CTkEntry(frame_top)
entry_search.pack(side="left", fill="x", expand=True, padx=(0,5))
entry_search.bind("<Return>", btn_search_click)  # Trigger search on Enter

btn_search = ctk.CTkButton(frame_top, text="Suchen", width=100, command=btn_search_click)
btn_search.pack(side="left")

# Table frame
frame_table = ctk.CTkFrame(root)
frame_table.pack(fill="both", expand=True, padx=10, pady=(0,10))

columns = labels.copy()
tree = ttk.Treeview(frame_table, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120)
tree.pack(fill="both", expand=True, side="left")

scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

# Bottom buttons
frame_buttons = ctk.CTkFrame(root)
frame_buttons.pack(fill="x", padx=10, pady=(0,10), anchor="e")

btn_add = ctk.CTkButton(frame_buttons, text="Hinzufügen", width=120, command=btn_add_click)
btn_add.pack(side="left", padx=5)

btn_delete = ctk.CTkButton(frame_buttons, text="Löschen", width=120, command=btn_delete_click)
btn_delete.pack(side="left", padx=5)

btn_edit = ctk.CTkButton(frame_buttons, text="Bearbeiten", width=120, command=btn_edit_click)
btn_edit.pack(side="left", padx=5)

update_table()
root.mainloop()