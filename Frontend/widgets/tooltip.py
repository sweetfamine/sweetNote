import customtkinter as ctk

class Tooltip:
    def __init__(self, widget, text: str, delay_ms: int = 300):
        self.widget = widget
        self.text = text
        self.delay_ms = delay_ms
        self._after_id = None
        self._tip = None

        widget.bind("<Enter>", self._schedule)
        widget.bind("<Leave>", self._hide)
        widget.bind("<Motion>", self._move)

    def _schedule(self, event=None):
        self._cancel()
        self._after_id = self.widget.after(self.delay_ms, lambda: self._show(event))

    def _cancel(self):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None

    def _show(self, event=None):
        if self._tip or not self.text:
            return
        x = (event.x_root if event else self.widget.winfo_rootx()) + 12
        y = (event.y_root if event else self.widget.winfo_rooty()) + 16

        self._tip = tip = ctk.CTkToplevel(self.widget)
        tip.wm_overrideredirect(True)
        tip.attributes("-topmost", True)
        tip.geometry(f"+{x}+{y}")

        ctk.CTkLabel(
            tip, text=self.text,
            fg_color="black", text_color="white",
            corner_radius=6, padx=8, pady=4
        ).pack()

    def _move(self, event):
        if self._tip:
            self._tip.geometry(f"+{event.x_root+12}+{event.y_root+16}")

    def _hide(self, event=None):
        self._cancel()
        if self._tip:
            self._tip.destroy()
            self._tip = None
