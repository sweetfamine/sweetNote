import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from typing import Optional
from datetime import date

from Manager.customer_manager import CustomerManager
from Domain.customer import Customer
from Frontend.widgets.tooltip import Tooltip
from Utils.validierung import (is_valid_email, is_valid_phone, parse_de_date, fmt_de_date)
from Utils.config import Config

config = Config()
ctk.set_appearance_mode(config.get("appearance_mode", "light"))
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("sweetNote - Kundenverwaltung")
root.geometry("1900x600")

db_path = config.get("db_path", "data/customers.db")
manager = CustomerManager(db_path=db_path)

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

sort_column: Optional[str] = None
sort_reverse: bool = False

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

def _sort_key_for_value(col: str, raw_value: str):
    v = (raw_value or "").strip()
    if v == "":
        return (1, None)
    if col == "ID":
        try:
            return (0, int(v))
        except Exception:
            return (0, v.lower())
    if col in ("Datum", "Geburtstag"):
        d = parse_de_date(v)
        if d:
            return (0, d.toordinal())
        return (0, v.lower())
    return (0, v.lower())

def sort_treeview(col: Optional[str], reverse: bool):
    if col is None:
        return
    items = list(tree.get_children(""))

    def item_key(iid):
        cell = tree.set(iid, col)
        return _sort_key_for_value(col, cell)

    items.sort(key=item_key, reverse=reverse)
    for idx, iid in enumerate(items):
        tree.move(iid, "", idx)

def on_heading_click(col: str):
    global sort_column, sort_reverse
    if sort_column == col:
        sort_reverse = not sort_reverse
    else:
        sort_column = col
        sort_reverse = False
    sort_treeview(sort_column, sort_reverse)
    _update_heading_arrows()

def _update_heading_arrows():
    for c in columns:
        if sort_column == c:
            arrow = " ▼" if sort_reverse else " ▲"
        else:
            arrow = ""
        tree.heading(c, text=c + arrow, command=lambda col=c: on_heading_click(col))

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
    if sort_column:
        sort_treeview(sort_column, sort_reverse)
    _update_heading_arrows()

def btn_search_click(event=None):
    query = entry_search.get()
    results = manager.search_customers(query)
    update_table(results)

def btn_delete_click():
    selected_item = tree.selection()
    if not selected_item:
        return
    kunde_id = int(tree.item(selected_item[0])["values"][0])
    if not messagebox.askyesno("Löschen bestätigen", f"Kunde #{kunde_id} wirklich löschen?"):
        return
    manager.delete_customer_by_id(kunde_id)
    update_table()

def btn_add_click():
    open_customer_window(None)

def btn_edit_click():
    selected_item = tree.selection()
    if not selected_item:
        return
    kunde_id = int(tree.item(selected_item[0])["values"][0])
    kunde = manager.get_customer_by_id(kunde_id)
    if kunde:
        open_customer_window(kunde)

def open_settings_window():
    win = ctk.CTkToplevel(root)
    win.title("Einstellungen")
    win.geometry("460x260")
    win.attributes("-topmost", True)
    win.focus_force()
    win.grab_set()

    wrapper = ctk.CTkFrame(win, corner_radius=10)
    wrapper.pack(fill="both", expand=True, padx=16, pady=16)

    ctk.CTkLabel(wrapper, text="Theme").grid(row=0, column=0, sticky="w", padx=6, pady=(6,4))
    appearance_var = ctk.StringVar(value=str(config.get("appearance_mode", "light")).capitalize())
    appearance = ctk.CTkOptionMenu(wrapper, values=["Light", "Dark", "System"], variable=appearance_var, width=180)
    appearance.grid(row=0, column=1, sticky="w", padx=6, pady=(6,4))

    ctk.CTkLabel(wrapper, text="Prefill 'Datum' on new").grid(row=1, column=0, sticky="w", padx=6, pady=4)
    prefill_var = ctk.BooleanVar(value=bool(config.get("prefill_date_on_new", True)))
    prefill = ctk.CTkSwitch(wrapper, text="", variable=prefill_var)
    prefill.grid(row=1, column=1, sticky="w", padx=6, pady=4)

    ctk.CTkLabel(wrapper, text="Database path").grid(row=2, column=0, sticky="w", padx=6, pady=4)
    db_var = ctk.StringVar(value=config.get("db_path", "data/customers.db"))
    db_entry = ctk.CTkEntry(wrapper, textvariable=db_var, width=260)
    db_entry.grid(row=2, column=1, sticky="w", padx=(6,0), pady=4)

    def browse_db():
        path = filedialog.askopenfilename(
            title="Select SQLite database",
            filetypes=[("SQLite DB", "*.db *.sqlite"), ("All files", "*.*")]
        )
        if path:
            db_var.set(path)

    browse_btn = ctk.CTkButton(wrapper, text="Browse…", width=90, command=browse_db)
    browse_btn.grid(row=2, column=2, sticky="w", padx=6, pady=4)

    info = ctk.CTkLabel(wrapper, text=f"Config file: {config.file_path}", text_color="#6b7280")
    info.grid(row=4, column=0, columnspan=3, sticky="w", padx=6, pady=(16,8))

    btns = ctk.CTkFrame(wrapper)
    btns.grid(row=5, column=0, columnspan=3, sticky="e", padx=6, pady=(8,0))

    def apply_and_close():
        config.set("appearance_mode", appearance_var.get().lower())
        config.set("prefill_date_on_new", bool(prefill_var.get()))
        config.set("db_path", db_var.get())
        try:
            config.save()
        except Exception as e:
            messagebox.showerror("Save error", f"Failed to save config:\n{e}", parent=win)
            return
        try:
            ctk.set_appearance_mode(config.get("appearance_mode", "light"))
        except Exception:
            pass
        new_db_path = config.get("db_path", "data/customers.db")
        try:
            global manager
            manager.close()
            manager = CustomerManager(db_path=new_db_path)
            update_table()
        except Exception as e:
            messagebox.showerror("DB wechseln", f"Datenbank konnte nicht geöffnet werden:\n{e}", parent=win)
            return
        win.destroy()

    save_btn = ctk.CTkButton(btns, text="Save", width=110, command=apply_and_close)
    save_btn.pack(side="right", padx=(6,0))
    cancel_btn = ctk.CTkButton(btns, text="Cancel", width=110, command=win.destroy)
    cancel_btn.pack(side="right", padx=6)

    wrapper.grid_columnconfigure(1, weight=1)

def open_customer_window(customer=None):
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
    for i, label in enumerate(labels):
        tk_label = ctk.CTkLabel(main_frame, text=label, anchor="e", width=120)
        tk_label.grid(row=i, column=0, padx=10, pady=8, sticky="e")
        entry = ctk.CTkEntry(main_frame, width=250)
        entry.grid(row=i, column=1, padx=10, pady=8, sticky="we")
        if label == "ID":
            entry.insert(0, str(customer.id) if customer else "—")
            entry.configure(state="disabled", takefocus=False)
            try:
                entry.configure(
                    fg_color=("#eeeeee", "#2a2a2a"),
                    text_color=("#6b7280", "#9ca3af"),
                    border_color=("#d1d5db", "#3f3f46")
                )
            except Exception:
                pass
            Tooltip(entry, "Die ID wird nach dem Speichern automatisch vergeben" if not customer else "Nicht änderbar")
            entries_local[label] = entry
            continue
        if customer:
            attr = label_to_attr[label]
            value = getattr(customer, attr)
            if label in ("Geburtstag", "Datum") and isinstance(value, str):
                value = fmt_de_date(value)
            entry.insert(0, value if value else "")
        else:
            if label == "Datum" and config.get("prefill_date_on_new", True):
                entry.insert(0, date.today().strftime("%d.%m.%Y"))
        entries_local[label] = entry

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

    button_frame = ctk.CTkFrame(main_frame)
    button_frame.grid(row=len(labels), column=0, columnspan=2, pady=20)

    def save_customer():
        errors = []
        data = {}
        for label in labels:
            if label == "ID":
                continue
            attr = label_to_attr[label]
            raw = entries_local[label].get().strip()
            clear_invalid(entries_local[label])
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
            first_error = errors[0]
            messagebox.showerror("Validierung", first_error, parent=win)
            for label in labels:
                if label == "ID":
                    continue
                entry = entries_local[label]
                if entry.cget("border_color") == "#ef4444":
                    entry.focus_set()
                    break
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

frame_top = ctk.CTkFrame(root)
frame_top.pack(fill="x", padx=10, pady=10)
entry_search = ctk.CTkEntry(frame_top)
entry_search.pack(side="left", fill="x", expand=True, padx=(0,5))
entry_search.bind("<Return>", btn_search_click)
btn_search = ctk.CTkButton(frame_top, text="Suchen", width=100, command=btn_search_click)
btn_search.pack(side="left", padx=(0,8))

frame_table = ctk.CTkFrame(root)
frame_table.pack(fill="both", expand=True, padx=10, pady=(0,10))
columns = labels.copy()
tree = ttk.Treeview(frame_table, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col, command=lambda c=col: on_heading_click(c))
    tree.column(col, width=120)
tree.pack(fill="both", expand=True, side="left")
scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

frame_buttons = ctk.CTkFrame(root)
frame_buttons.pack(fill="x", padx=10, pady=(0,10), anchor="e")
btn_add = ctk.CTkButton(frame_buttons, text="Hinzufügen", width=120, command=btn_add_click)
btn_add.pack(side="left", padx=5)
btn_delete = ctk.CTkButton(frame_buttons, text="Löschen", width=120, command=btn_delete_click)
btn_delete.pack(side="left", padx=5)
btn_edit = ctk.CTkButton(frame_buttons, text="Bearbeiten", width=120, command=btn_edit_click)
btn_edit.pack(side="left", padx=5)
btn_settings = ctk.CTkButton(frame_buttons, text="⚙ Einstellungen", width=140, command=open_settings_window)
btn_settings.pack(side="right", padx=5)

update_table()
sort_column = "ID"
sort_reverse = False
sort_treeview(sort_column, sort_reverse)
_update_heading_arrows()

def _on_close():
    try:
        manager.close()
    except Exception:
        pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", _on_close)
root.mainloop()