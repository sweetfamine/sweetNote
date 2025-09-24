import customtkinter as ctk
import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from Utils.validierung import parse_de_date, fmt_de_date
from Frontend.customer_form import CustomerForm
from Frontend.settings_window import SettingsWindow
from Frontend.constants import labels, label_to_attr

class MainWindow(ctk.CTk):
    def __init__(self, manager, config):
        super().__init__()
        self.manager = manager
        self.config = config
        self.sort_column: Optional[str] = None
        self.sort_reverse: bool = False
        self.title("sweetNote - Kundenverwaltung")
        self.geometry("1900x600")

        logo_path = os.path.join(os.path.dirname(__file__), "assets", "sweetNote_Icon128.ico")
        if os.path.exists(logo_path):
            try:
                self.iconbitmap(logo_path)
            except Exception as e:
                print("Logo konnte nicht geladen werden:", e)

        self._build_ui()
        self.update_table()
        self.sort_column = "ID"
        self.sort_reverse = False
        self.sort_treeview(self.sort_column, self.sort_reverse)
        self._update_heading_arrows()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        try:
            self.manager.close()
        except Exception:
            pass
        self.destroy()

    def _build_ui(self):
        frame_top = ctk.CTkFrame(self)
        frame_top.pack(fill="x", padx=10, pady=10)
        self.entry_search = ctk.CTkEntry(frame_top)
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0,5))
        self.entry_search.bind("<Return>", self.btn_search_click)
        btn_search = ctk.CTkButton(frame_top, text="Suchen", width=100, command=self.btn_search_click)
        btn_search.pack(side="left", padx=(0,8))
        frame_table = ctk.CTkFrame(self)
        frame_table.pack(fill="both", expand=True, padx=10, pady=(0,10))
        self.columns = labels.copy()
        self.tree = ttk.Treeview(frame_table, columns=self.columns, show="headings")

        for col in self.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.on_heading_click(c))
            self.tree.column(col, width=120)
            
        self.tree.pack(fill="both", expand=True, side="left")
        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        frame_buttons = ctk.CTkFrame(self)
        frame_buttons.pack(fill="x", padx=10, pady=(0,10), anchor="e")
        btn_add = ctk.CTkButton(frame_buttons, text="Hinzufügen", width=120, command=self.btn_add_click)
        btn_add.pack(side="left", padx=5)
        btn_delete = ctk.CTkButton(frame_buttons, text="Löschen", width=120, command=self.btn_delete_click)
        btn_delete.pack(side="left", padx=5)
        btn_edit = ctk.CTkButton(frame_buttons, text="Bearbeiten", width=120, command=self.btn_edit_click)
        btn_edit.pack(side="left", padx=5)
        btn_settings = ctk.CTkButton(frame_buttons, text="⚙ Einstellungen", width=140, command=self.open_settings_window)
        btn_settings.pack(side="right", padx=5)

    def _sort_key_for_value(self, col: str, raw_value: str):
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

    def sort_treeview(self, col: Optional[str], reverse: bool):
        if col is None:
            return
        items = list(self.tree.get_children(""))
        def item_key(iid):
            cell = self.tree.set(iid, col)
            return self._sort_key_for_value(col, cell)
        items.sort(key=item_key, reverse=reverse)
        for idx, iid in enumerate(items):
            self.tree.move(iid, "", idx)

    def on_heading_click(self, col: str):
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False
        self.sort_treeview(self.sort_column, self.sort_reverse)
        self._update_heading_arrows()

    def _update_heading_arrows(self):
        for c in self.columns:
            if self.sort_column == c:
                arrow = " ▼" if self.sort_reverse else " ▲"
            else:
                arrow = ""
            self.tree.heading(c, text=c + arrow, command=lambda col=c: self.on_heading_click(col))

    def update_table(self, customers=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        data = customers if customers is not None else self.manager.get_all_customers()
        for customer in data:
            def fmt(col):
                val = getattr(customer, label_to_attr[col])
                if col in ("Geburtstag", "Datum") and isinstance(val, str):
                    return fmt_de_date(val)
                return val
            self.tree.insert("", "end", values=[fmt(col) for col in self.columns])
        if self.sort_column:
            self.sort_treeview(self.sort_column, self.sort_reverse)
        self._update_heading_arrows()

    def btn_search_click(self, event=None):
        query = self.entry_search.get()
        results = self.manager.search_customers(query)
        self.update_table(results)

    def btn_delete_click(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        kunde_id = int(self.tree.item(selected_item[0])["values"][0])
        if not messagebox.askyesno("Löschen bestätigen", f"Kunde #{kunde_id} wirklich löschen?"):
            return
        self.manager.delete_customer_by_id(kunde_id)
        self.update_table()

    def btn_add_click(self):
        CustomerForm(self, self.manager, self.config, on_save=self.update_table)

    def btn_edit_click(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        kunde_id = int(self.tree.item(selected_item[0])["values"][0])
        kunde = self.manager.get_customer_by_id(kunde_id)
        if kunde:
            CustomerForm(self, self.manager, self.config, customer=kunde, on_save=self.update_table)

    def open_settings_window(self):
        SettingsWindow(self, self.manager, self.config, on_apply=self.update_table)
