import customtkinter as ctk
from tkinter import messagebox
from datetime import date
from Utils.validierung import is_valid_email, is_valid_phone, parse_de_date, fmt_de_date
from Frontend.widgets.tooltip import Tooltip
from Frontend.constants import labels, label_to_attr

class CustomerForm(ctk.CTkToplevel):
    def __init__(self, parent, manager, config, customer=None, on_save=None):
        super().__init__(parent)
        self.manager = manager
        self.config = config
        self.customer = customer
        self.on_save = on_save
        self.title("Kunde bearbeiten" if customer else "Neuen Kunden hinzufügen")
        self.geometry("500x650")
        self.attributes("-topmost", True)
        self.focus_force()
        main_frame = ctk.CTkFrame(self, corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.entries_local = {}
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
                self.entries_local[label] = entry
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
            self.entries_local[label] = entry
            def on_focus_out(e, label=label, entry=entry):
                val = entry.get()
                try:
                    entry.configure(border_color=None)
                except Exception:
                    pass
                if label == "Email" and not is_valid_email(val):
                    entry.configure(border_color="#ef4444")
                elif label == "Telefon" and not is_valid_phone(val):
                    entry.configure(border_color="#ef4444")
                elif label in ("Geburtstag", "Datum"):
                    if val.strip() and not parse_de_date(val):
                        entry.configure(border_color="#ef4444")
            entry.bind("<FocusOut>", on_focus_out)
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=len(labels), column=0, columnspan=2, pady=20)
        btn_save = ctk.CTkButton(button_frame, text="Speichern", width=120, command=self.save_customer)
        btn_save.pack(side="left", padx=10)
        btn_cancel = ctk.CTkButton(button_frame, text="Abbrechen", width=120, command=self.destroy)
        btn_cancel.pack(side="right", padx=10)

    def save_customer(self):
        errors = []
        data = {}
        for label in labels:
            if label == "ID":
                continue
            attr = label_to_attr[label]
            raw = self.entries_local[label].get().strip()
            try:
                self.entries_local[label].configure(border_color=None)
            except Exception:
                pass
            if label in ("Datum", "Vorname", "Name") and not raw:
                errors.append(f"{label} darf nicht leer sein.")
                self.entries_local[label].configure(border_color="#ef4444")
                continue
            if label == "Email":
                if not is_valid_email(raw):
                    errors.append("Bitte eine gültige Email angeben.")
                    self.entries_local[label].configure(border_color="#ef4444")
                data[attr] = raw
            elif label == "Telefon":
                if not is_valid_phone(raw):
                    errors.append("Telefonnummer ist ungültig (z. B. +49 123 4567).")
                    self.entries_local[label].configure(border_color="#ef4444")
                data[attr] = raw
            elif label in ("Geburtstag", "Datum"):
                if raw:
                    d = parse_de_date(raw)
                    if not d:
                        errors.append(f"{label}: bitte als TT.MM.JJJJ angeben.")
                        self.entries_local[label].configure(border_color="#ef4444")
                    else:
                        data[attr] = d.isoformat()
                else:
                    data[attr] = ""
            else:
                data[attr] = raw
        if errors:
            first_error = errors[0]
            messagebox.showerror("Validierung", first_error, parent=self)
            for label in labels:
                if label == "ID":
                    continue
                entry = self.entries_local[label]
                if entry.cget("border_color") == "#ef4444":
                    entry.focus_set()
                    break
            return
        if self.customer:
            self.manager.update_customer(self.customer.id, **data)
        else:
            self.manager.add_customer(**data)
        if self.on_save:
            self.on_save()
        self.destroy()
