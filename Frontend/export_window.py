import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os, tempfile

try:
    import win32print
except ImportError:
    win32print = None


class ExportWindow(ctk.CTkToplevel):
    def __init__(self, master, rows):
        super().__init__(master)
        self.transient(master)
        self.grab_set()
        self.focus_force()
        self.title("Exportieren / Drucken")
        self.geometry("500x400")
        self.rows = rows

        ctk.CTkLabel(self, text="Dateiname:").pack(anchor="w", padx=10, pady=(10, 0))
        self.filename_entry = ctk.CTkEntry(self, width=400)
        self.filename_entry.insert(0, "kundenliste.pdf")
        self.filename_entry.pack(padx=10, pady=5)

        ctk.CTkLabel(self, text="Drucker:").pack(anchor="w", padx=10, pady=(10, 0))
        printers = ["Als PDF speichern"]
        if win32print:
            flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
            printers += [p[2] for p in win32print.EnumPrinters(flags)]
        self.printer_var = tk.StringVar(value=printers[0])
        self.printer_menu = ctk.CTkOptionMenu(self, values=printers, variable=self.printer_var)
        self.printer_menu.pack(padx=10, pady=5)

        ctk.CTkLabel(self, text="Vorschau:").pack(anchor="w", padx=10, pady=(10, 0))
        self.preview_box = ctk.CTkTextbox(self, height=150, width=460)
        self.preview_box.pack(padx=10, pady=5)
        self.show_preview()

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=15, fill="x")
        ctk.CTkButton(btn_frame, text="Abbrechen", command=self.destroy).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Drucken", command=self.print_or_save).pack(side="right", padx=5)

    def show_preview(self):
        self.preview_box.delete("1.0", "end")
        for row in self.rows[:10]:
            self.preview_box.insert("end", f"ID: {row[0]} | Name: {row[1]} | Email: {row[2]}\n")

    def print_or_save(self):
        filename = self.filename_entry.get().strip()
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        if self.printer_var.get() == "Als PDF speichern":
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Dateien", "*.pdf")],
                initialfile=filename
            )
            if not file_path:
                return
        else:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            file_path = tmp.name
            tmp.close()

        self.generate_pdf(file_path)

        if self.printer_var.get() == "Als PDF speichern":
            messagebox.showinfo("Export", f"PDF gespeichert unter:\n{file_path}")
        else:
            try:
                if win32print:
                    os.startfile(file_path, "print")
                else:
                    messagebox.showwarning("Hinweis", "Direktdruck nur unter Windows verfügbar.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Drucken fehlgeschlagen:\n{e}")

    def generate_pdf(self, path):
        c = canvas.Canvas(path, pagesize=A4)
        width, height = A4
        y = height - 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Kundenliste")
        y -= 30
        c.setFont("Helvetica", 12)
        for row in self.rows:
            c.drawString(50, y, f"ID: {row[0]} | Name: {row[1]} | Email: {row[2]}")
            y -= 20
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 12)
        c.save()