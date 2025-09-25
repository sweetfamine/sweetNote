import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os

class ImportWindow(ctk.CTkToplevel):
    def __init__(self, master, manager, config, on_done=None):
        super().__init__(master)
        self.title("Import (JSON)")
        self.geometry("400x280")

        self.transient(master)
        self.grab_set()
        self.focus_force()
        self.lift()

        self.manager = manager
        self.config = config
        self.on_done = on_done
        self.file_path = None

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # File selection
        ctk.CTkLabel(frame, text="JSON-Datei:").pack(anchor="w", pady=(0, 5))
        file_frame = ctk.CTkFrame(frame)
        file_frame.pack(fill="x", pady=(0, 15))
        self.file_entry = ctk.CTkEntry(file_frame)
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(file_frame, text="Auswählen", command=self.choose_file).pack(side="right")

        # Mode selection
        ctk.CTkLabel(frame, text="Import-Modus:").pack(anchor="w", pady=(0, 5))
        self.mode_var = tk.StringVar(value="Anhängen")
        self.mode_menu = ctk.CTkOptionMenu(frame, values=["Anhängen", "Bestehende ersetzen"], variable=self.mode_var)
        self.mode_menu.pack(fill="x", pady=(0, 15))

        # Buttons
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill="x", pady=10)
        ctk.CTkButton(btn_frame, text="Importieren", command=self.import_json).pack(side="left", expand=True, padx=10)
        ctk.CTkButton(btn_frame, text="Abbrechen", command=self.destroy).pack(side="left", expand=True, padx=10)

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Dateien", "*.json")])
        if path:
            self.file_path = path
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, path)

    def import_json(self):
        if not self.file_path or not os.path.exists(self.file_path):
            messagebox.showwarning("Fehler", "Bitte eine gültige JSON-Datei auswählen.")
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                customers = json.load(f)

            if not isinstance(customers, list):
                raise ValueError("Ungültiges JSON-Format.")

            if self.mode_var.get() == "Bestehende ersetzen":
                self.manager.delete_all_customers()

            for cust in customers:
                self.manager.add_customer(**cust)

            if self.on_done:
                self.on_done()

            messagebox.showinfo("Import", f"{len(customers)} Kunden importiert.")
            self.destroy()

        except Exception as e:
            messagebox.showerror("Fehler", f"Import fehlgeschlagen:\n{e}")
