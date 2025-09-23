import customtkinter as ctk
from tkinter import filedialog, messagebox

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, manager, config, on_apply=None):
        super().__init__(parent)
        self.manager = manager
        self.config = config
        self.on_apply = on_apply
        self.title("Einstellungen")
        self.geometry("460x260")
        self.attributes("-topmost", True)
        self.focus_force()
        self.grab_set()
        
        wrapper = ctk.CTkFrame(self, corner_radius=10)
        wrapper.pack(fill="both", expand=True, padx=16, pady=16)
        ctk.CTkLabel(wrapper, text="Theme").grid(row=0, column=0, sticky="w", padx=6, pady=(6,4))
        self.appearance_var = ctk.StringVar(value=str(config.get("appearance_mode", "light")).capitalize())
        appearance = ctk.CTkOptionMenu(wrapper, values=["Light", "Dark", "System"], variable=self.appearance_var, width=180)
        appearance.grid(row=0, column=1, sticky="w", padx=6, pady=(6,4))
        ctk.CTkLabel(wrapper, text="Prefill 'Datum' on new").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.prefill_var = ctk.BooleanVar(value=bool(config.get("prefill_date_on_new", True)))
        prefill = ctk.CTkSwitch(wrapper, text="", variable=self.prefill_var)
        prefill.grid(row=1, column=1, sticky="w", padx=6, pady=4)
        ctk.CTkLabel(wrapper, text="Database path").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        self.db_var = ctk.StringVar(value=config.get("db_path", "data/customers.db"))
        db_entry = ctk.CTkEntry(wrapper, textvariable=self.db_var, width=260)
        db_entry.grid(row=2, column=1, sticky="w", padx=(6,0), pady=4)

        def browse_db():
            path = filedialog.askopenfilename(
                title="Select SQLite database",
                filetypes=[("SQLite DB", "*.db *.sqlite"), ("All files", "*.*")]
            )
            if path:
                self.db_var.set(path)
        browse_btn = ctk.CTkButton(wrapper, text="Browse…", width=90, command=browse_db)
        browse_btn.grid(row=2, column=2, sticky="w", padx=6, pady=4)
        info = ctk.CTkLabel(wrapper, text=f"Config file: {config.file_path}", text_color="#6b7280")
        info.grid(row=4, column=0, columnspan=3, sticky="w", padx=6, pady=(16,8))
        btns = ctk.CTkFrame(wrapper)
        btns.grid(row=5, column=0, columnspan=3, sticky="e", padx=6, pady=(8,0))
        save_btn = ctk.CTkButton(btns, text="Save", width=110, command=self.apply_and_close)
        save_btn.pack(side="right", padx=(6,0))
        cancel_btn = ctk.CTkButton(btns, text="Cancel", width=110, command=self.destroy)
        cancel_btn.pack(side="right", padx=6)
        wrapper.grid_columnconfigure(1, weight=1)

    def apply_and_close(self):
        self.config.set("appearance_mode", self.appearance_var.get().lower())
        self.config.set("prefill_date_on_new", bool(self.prefill_var.get()))
        self.config.set("db_path", self.db_var.get())
        try:
            self.config.save()
        except Exception as e:
            messagebox.showerror("Save error", f"Failed to save config:\n{e}", parent=self)
            return
        try:
            ctk.set_appearance_mode(self.config.get("appearance_mode", "light"))
        except Exception:
            pass
        if self.on_apply:
            self.on_apply()
        self.destroy()
