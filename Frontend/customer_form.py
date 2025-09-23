import customtkinter as ctk
from tkinter import messagebox
from datetime import date
from functools import partial

from Utils.validierung import is_valid_email, is_valid_phone, parse_de_date, fmt_de_date
from Frontend.widgets.tooltip import Tooltip
from Frontend.constants import labels, label_to_attr, required_fields


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
        self._default_border = ctk.ThemeManager.theme["CTkEntry"]["border_color"]

        main_frame = ctk.CTkFrame(self, corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.entries_local = {}

        for i, label in enumerate(labels):
            label_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            label_frame.grid(row=i, column=0, padx=10, pady=8, sticky="e")

            ctk.CTkLabel(label_frame, text=label, anchor="e").pack(side="left")
            if label in required_fields:
                ctk.CTkLabel(label_frame, text="*", text_color="red").pack(side="left")

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
                Tooltip(entry, "Die ID wird nach dem Speichern automatisch vergeben" if not customer else "ID des Kunden")
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
                val = entry.get().strip()
                self._clear_invalid(entry)

                if label in ("Datum", "Vorname", "Name") and not val:
                    self._mark_invalid(entry)
                    return

                if label == "Email" and val and not is_valid_email(val):
                    self._mark_invalid(entry)
                elif label == "Telefon" and val and not is_valid_phone(val):
                    self._mark_invalid(entry)
                elif label in ("Geburtstag", "Datum") and val and not parse_de_date(val):
                    self._mark_invalid(entry)

            entry.bind("<FocusOut>", on_focus_out)
            entry.bind("<KeyRelease>", partial(self._validate_live, label, entry))

        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=len(labels), column=0, columnspan=2, pady=20)
        btn_save = ctk.CTkButton(button_frame, text="Speichern", width=120, command=self.save_customer)
        btn_save.pack(side="left", padx=10)
        btn_cancel = ctk.CTkButton(button_frame, text="Abbrechen", width=120, command=self.destroy)
        btn_cancel.pack(side="right", padx=10)

    def _mark_invalid(self, entry):
        try:
            entry.configure(border_color="#ef4444")
        except Exception:
            pass

    def _clear_invalid(self, entry):
        try:
            entry.configure(border_color=self._default_border)
        except Exception:
            pass

    def save_customer(self):
        errors = []
        data = {}
        for label in labels:
            if label == "ID":
                continue
            attr = label_to_attr[label]
            raw = self.entries_local[label].get().strip()
            self._clear_invalid(self.entries_local[label])

            if label in ("Datum", "Vorname", "Name") and not raw:
                errors.append(f"{label} darf nicht leer sein.")
                self._mark_invalid(self.entries_local[label])
                continue

            if label == "Email":
                if not is_valid_email(raw):
                    errors.append("Bitte eine gültige Email angeben.")
                    self._mark_invalid(self.entries_local[label])
                else:
                    data[attr] = raw

            elif label == "Telefon":
                if not is_valid_phone(raw):
                    errors.append("Telefonnummer ist ungültig (+49… oder 0…).")
                    self._mark_invalid(self.entries_local[label])
                else:
                    data[attr] = raw

            elif label in ("Geburtstag", "Datum"):
                if raw:
                    d = parse_de_date(raw)
                    if not d:
                        errors.append(f"{label}: bitte als TT.MM.JJJJ angeben.")
                        self._mark_invalid(self.entries_local[label])
                    else:
                        data[attr] = d.isoformat()
                else:
                    data[attr] = ""

            else:
                data[attr] = raw

        if errors:
            messagebox.showerror("Validierung", "\n".join(errors), parent=self)
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

    def _validate_live(self, label, entry, event=None):
        val = entry.get().strip()
        self._clear_invalid(entry)

        if label in ("Datum", "Vorname", "Name") and not val:
            self._mark_invalid(entry)
            return

        if label == "Email" and val and not is_valid_email(val):
            self._mark_invalid(entry)
        elif label == "Telefon" and val and not is_valid_phone(val):
            self._mark_invalid(entry)
        elif label in ("Geburtstag", "Datum") and val and not parse_de_date(val):
            self._mark_invalid(entry)

