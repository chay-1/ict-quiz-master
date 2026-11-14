import tkinter as tk

from core.quiz_theme import BLUE, FONT, GREEN, GREY, LIGHT, MUTED, NAVY, RED, WHITE


class FlatButton(tk.Label):
    """We use this label as a styled clickable button."""
    STYLES = {  # normal bg, text colour, hover bg
        "primary": (BLUE, WHITE, "#1d4ed8"),
        "secondary": (WHITE, NAVY, LIGHT),
        "success": (GREEN, WHITE, "#059669"),
        "danger": (RED, WHITE, "#dc2626"),
        "blue": (BLUE, WHITE, "#1d4ed8"),
    }

    def __init__(self, parent, text, command, style="primary", size=12):
        super().__init__(parent, text=text, font=(FONT, size, "bold"), padx=24, pady=12,
                         highlightthickness=1)
        self.command, self.style, self.enabled = command, style, True
        self.bind("<Button-1>", lambda e: self.enabled and self.command())
        self.bind("<Enter>", lambda e: self._paint(True))
        self.bind("<Leave>", lambda e: self._paint(False))
        self._paint(False)

    def _paint(self, hover):
        bg, fg, hov = self.STYLES[self.style]
        if not self.enabled:
            self.config(bg=GREY, fg=MUTED, cursor="arrow", highlightbackground=GREY)
        else:
            self.config(bg=hov if hover else bg, fg=fg, cursor="hand2",
                        highlightbackground=GREY if self.style == "secondary" else bg)

    def set_enabled(self, value):
        self.enabled = value
        self._paint(False)


class SoundToggle(FlatButton):
    """We use this button to turn sound effects on or off."""
    def __init__(self, parent, app):
        self.app = app
        super().__init__(parent, self._label(), self.toggle, "secondary", 9)

    def _label(self):
        return "🔊 SOUND ON" if self.app.sound_enabled else "🔇 SOUND OFF"

    def toggle(self):
        self.app.sound_enabled = not self.app.sound_enabled
        self.config(text=self._label())


# We connect the same mouse or keyboard action to a widget and its children.
def bind_all(widget, sequence, func):
    widget.bind(sequence, func)
    for child in widget.winfo_children():
        bind_all(child, sequence, func)


# We make labels with the same font and colours.
def label(parent, text, size=12, bold=False, fg=None, bg=None, **kw):
    bg = bg if bg is not None else parent.cget("bg")
    fg = fg if fg is not None else NAVY
    if fg == MUTED and bg == WHITE:
        fg = "#64748b"
    return tk.Label(parent, text=text, font=(FONT, size, "bold" if bold else "normal"),
                    fg=fg, bg=bg, **kw)


# We use a white card to group related information.
def card(parent, **kw):
    return tk.Frame(parent, bg=WHITE, highlightthickness=1, highlightbackground=GREY, **kw)


# We build the shared header shown at the top of each screen.
def top_bar(parent, title="ICT Quiz Master"):
    bar = tk.Frame(parent, bg=WHITE, highlightthickness=1, highlightbackground=GREY)
    bar.pack(fill="x")
    tk.Label(bar, text=" Q ", bg=BLUE, fg=WHITE, font=(FONT, 11, "bold")).pack(side="left", padx=(24, 8), pady=14)
    label(bar, title, 15, True).pack(side="left")
    SoundToggle(bar, parent.winfo_toplevel()).pack(side="right", padx=16, pady=5)
    return bar


# We make a row of buttons that work like radio buttons.
def chip_group(parent, options, var, size=10, command=None):
    """A row of buttons that behave like radio buttons. options = [(value, text), ...]"""
    btns = {}

    def paint():
        for value, b in btns.items():
            b.style = "blue" if var.get() == value else "secondary"
            b._paint(False)

    def pick(value):
        var.set(value)
        paint()
        if command:
            command()

    for value, text in options:
        b = FlatButton(parent, text, lambda v=value: pick(v), "secondary", size)
        b.config(padx=14, pady=7)
        b.pack(side="left", padx=3)
        btns[value] = b
    paint()
