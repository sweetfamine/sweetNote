import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas as rl_canvas
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import tempfile, os, datetime

try:
    import win32print
except ImportError:
    win32print = None


class PrintWindow(ctk.CTkToplevel):
    def __init__(self, master, columns, rows):
        super().__init__(master)
        self.title("Print / PDF Export")
        self.geometry("1650x800")

        logo_path = os.path.join(os.path.dirname(__file__), "assets", "sweetNote_Icon128.png")
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                photo = ImageTk.PhotoImage(img)
                self.iconphoto(False, photo)
            except Exception as e:
                print("Logo konnte nicht geladen werden:", e)

        self.transient(master)
        self.grab_set()
        self.focus_force()
        self.lift()

        self.columns = columns
        self.rows = rows

        self.grid_columnconfigure(0, weight=0, minsize=250)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==== options (left) ====
        options_frame = ctk.CTkFrame(self)
        options_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)

        ctk.CTkLabel(options_frame, text="Filename:").pack(anchor="w", padx=5, pady=(10, 0))
        self.filename_entry = ctk.CTkEntry(options_frame, width=200)
        self.filename_entry.insert(0, "kundenliste.pdf")
        self.filename_entry.pack(anchor="w", padx=5, pady=5)

        printers = ["Save as PDF"]
        if win32print:
            flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
            printers += [p[2] for p in win32print.EnumPrinters(flags)]
        self.printer_var = tk.StringVar(value=printers[0])
        ctk.CTkLabel(options_frame, text="Drucker:").pack(anchor="w", padx=5, pady=(10, 0))
        self.printer_menu = ctk.CTkOptionMenu(options_frame, values=printers, variable=self.printer_var)
        self.printer_menu.pack(anchor="w", padx=5, pady=5)

        btn_frame = ctk.CTkFrame(options_frame)
        btn_frame.pack(pady=20, fill="x")
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Print", command=self.print_or_save).pack(side="right", padx=5)

        # ==== preview (right) ====
        preview_frame = ctk.CTkFrame(self)
        preview_frame.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)

        self.canvas = tk.Canvas(preview_frame, bg="grey")
        self.scroll_y = tk.Scrollbar(preview_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_x = tk.Scrollbar(preview_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        self.scroll_y.pack(side="right", fill="y")
        self.scroll_x.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.preview_images = []
        self.preview_path = self.generate_temp_pdf()
        self.show_preview(self.preview_path)

    def generate_temp_pdf(self):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        path = tmp.name
        tmp.close()
        self.generate_pdf(path)
        return path

    def _footer(self, canv: rl_canvas.Canvas, doc):
        page_num = canv.getPageNumber()
        text = f"Page {page_num} | Generated {datetime.date.today().strftime('%d.%m.%Y')}"
        canv.setFont("Helvetica", 8)
        canv.setFillColor(colors.grey)
        canv.drawRightString(landscape(A4)[0] - 10, 20, text)

    def _header(self, canv: rl_canvas.Canvas, doc):
        pass

    def generate_pdf(self, path):
        styles = getSampleStyleSheet()

        header_style = ParagraphStyle(
            "header",
            parent=styles["Normal"],
            alignment=0,
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=9
        )
        body_style = ParagraphStyle(
            "body",
            parent=styles["Normal"],
            alignment=0,
            fontName="Helvetica",
            fontSize=8,
            leading=9
        )
        title_style = ParagraphStyle(
            "title",
            parent=styles["Normal"],
            alignment=1,
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=16,
            spaceAfter=12
        )

        elements = [Paragraph("sweetNote – Patientenverwaltung", title_style)]

        header_row = [
            Paragraph(str(c).replace(" ", "<br/>"), header_style)
            for c in self.columns
        ]

        data = [header_row]
        for row in self.rows:
            data.append([Paragraph(str(c), body_style) for c in row])

        # Calculate column widths
        total_width = landscape(A4)[0] - 20
        id_width = 40
        date_width = 60
        geb_width = 60
        other_cols = len(self.columns) - 3
        col_widths = []
        for col in self.columns:
            if col.lower() == "id":
                col_widths.append(id_width)
            elif col.lower() in ("date", "datum"):
                col_widths.append(date_width)
            elif col.lower().startswith("geb"):
                col_widths.append(geb_width)
            else:
                col_widths.append((total_width - id_width - date_width - geb_width) / other_cols)


        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
        ]))

        elements.append(table)

        doc = SimpleDocTemplate(
            path,
            pagesize=landscape(A4),
            leftMargin=10,
            rightMargin=10,
            topMargin=20,
            bottomMargin=20
        )
        doc.build(elements, onFirstPage=self._add_page, onLaterPages=self._add_page)

    def _add_page(self, canv, doc):
        self._footer(canv, doc)

    def show_preview(self, pdf_path):
        self.canvas.delete("all")
        self.preview_images.clear()
        doc = fitz.open(pdf_path)
        y_offset = 0
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            photo = ImageTk.PhotoImage(img)
            self.preview_images.append(photo)
            self.canvas.create_image(0, y_offset, anchor="nw", image=photo)
            y_offset += photo.height() + 20
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def print_or_save(self):
        filename = self.filename_entry.get().strip()
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        if self.printer_var.get() == "Save as PDF":
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=filename
            )
            if not file_path:
                return
        else:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            file_path = tmp.name
            tmp.close()

        self.generate_pdf(file_path)

        if self.printer_var.get() == "Save as PDF":
            messagebox.showinfo("Export", f"PDF saved:\n{file_path}")
        else:
            try:
                if win32print:
                    os.startfile(file_path, "print")
                else:
                    messagebox.showwarning("Notice", "Direct print only works on Windows.")
            except Exception as e:
                messagebox.showerror("Error", f"Print failed:\n{e}")