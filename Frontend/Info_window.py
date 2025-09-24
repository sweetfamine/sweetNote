import customtkinter as ctk
import webbrowser
import urllib.parse
from tkinter import font as tkfont

class AboutWindow(ctk.CTkToplevel):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config_obj = config

        self.title("Information")
        self.geometry("480x320")
        self.attributes("-topmost", True)
        self.focus_force()
        self.grab_set()

        wrapper = ctk.CTkFrame(self, corner_radius=12)
        wrapper.pack(fill="both", expand=True, padx=18, pady=18)

        title = ctk.CTkLabel(wrapper, text="sweetNote", font=("Arial", 24, "bold"))
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,10))

        subtitle = ctk.CTkLabel(wrapper, text="Kundenverwaltung", text_color="#6b7280")
        subtitle.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0,14))

        sep = ctk.CTkFrame(wrapper, height=2, fg_color=("#e5e7eb", "#2a2a2a"))
        sep.grid(row=2, column=0, columnspan=2, sticky="we", pady=(0,14))
        wrapper.grid_columnconfigure(1, weight=1)

        version = str(self.config_obj.get("app_version", "?"))
        build = str(self.config_obj.get("build_date", "?"))
        phone = str(self.config_obj.get("support_phone", "") or "")
        site = str(self.config_obj.get("support_website", "") or "")
        email = str(self.config_obj.get("support_email", "") or "")

        self._row(wrapper, 3, "Version", version)
        self._row(wrapper, 4, "Build-Datum", build)

        r = 5
        if phone.strip():
            self._row(wrapper, r, "Support Telefon", phone)
            r += 1

        if email.strip():
            self._link_row(wrapper, r, "Support E-Mail", email, self._open_email)
            r += 1

        if site.strip():
            self._link_row(wrapper, r, "Website", site, self._open_site)
            r += 1

        spacer = ctk.CTkLabel(wrapper, text="")
        spacer.grid(row=r, column=0, columnspan=2, pady=(12,0))

    def _row(self, parent, row, label_text, value_text):
        ctk.CTkLabel(parent, text=label_text).grid(row=row, column=0, sticky="w", padx=(0,12), pady=6)
        ctk.CTkLabel(parent, text=value_text).grid(row=row, column=1, sticky="w", pady=6)

    def _link_row(self, parent, row, label_text, link_text, handler):
        ctk.CTkLabel(parent, text=label_text).grid(row=row, column=0, sticky="w", padx=(0,12), pady=6)
        link = ctk.CTkLabel(parent, text=link_text, text_color="#2563eb", font=("Arial", 13, "underline"))
        link.grid(row=row, column=1, sticky="w", pady=6)
        try:
            link.configure(cursor="hand2")
        except Exception:
            pass
        link.bind("<Button-1>", lambda e, v=link_text: handler(v))

    def _open_site(self, url):
        if url:
            webbrowser.open(url)

    def _open_email(self, addr):
        if not addr:
            return
        subject = urllib.parse.quote("Support | sweetNote")
        webbrowser.open(f"mailto:{addr}?subject={subject}")