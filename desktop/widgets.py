import tkinter as tk

from core.quiz_theme import (
    BORDER, FONT, INK, INK_ON_LIME, LIME, LIME_HOVER, LIME_PRESS, MUTED, PURPLE,
    PURPLE_HOVER, PURPLE_PRESS, RED, SURFACE, SURFACE_2, TEAL, TEAL_HOVER, WHITE,
)


class FlatButton(tk.Label):
    """A styled button that behaves like a website button.

    It has 5 states: normal, hover, pressed, keyboard focus and disabled.
    It works with the mouse AND the keyboard (Tab to reach it, Enter or Space to press).
    """
    STYLES = {  # text colour, normal bg, hover bg, pressed bg, border colour
        "primary":   (INK_ON_LIME, LIME, LIME_HOVER, LIME_PRESS, LIME),
        "secondary": (INK, SURFACE, SURFACE_2, BORDER, BORDER),      # outline / ghost button
        "success":   (INK_ON_LIME, TEAL, TEAL_HOVER, "#12997d", TEAL),
        "danger":    (WHITE, RED, "#ff7f8b", "#d94453", RED),
        "pink":      (WHITE, PURPLE, PURPLE_HOVER, PURPLE_PRESS, PURPLE),  # purple accent
    }

    def __init__(self, parent, text, command, style="primary", size=12):
        super().__init__(parent, text=text, font=(FONT, size, "bold"), padx=24, pady=12,
                         highlightthickness=2, takefocus=True)
        self.command, self.style, self.enabled = command, style, True
        self.hover = self.pressed = self.focused = False
        self.bind("<Enter>", lambda e: self._set(hover=True))
        self.bind("<Leave>", lambda e: self._set(hover=False, pressed=False))
        self.bind("<ButtonPress-1>", self._down)
        self.bind("<ButtonRelease-1>", self._up)
        self.bind("<FocusIn>", lambda e: self._set(focused=True))
        self.bind("<FocusOut>", lambda e: self._set(focused=False))
        for key in ("<Return>", "<space>"):
            self.bind(key, self._key)
        self._paint()

    # ----- behaviour -----
    def _set(self, **state):
        for k, v in state.items():
            setattr(self, k, v)
        self._paint()

    def _down(self, e):
        if self.enabled:
            self._set(pressed=True)

    def _up(self, e):
        was_pressed = self.pressed
        self._set(pressed=False)
        inside = 0 <= e.x < self.winfo_width() and 0 <= e.y < self.winfo_height()
        if self.enabled and was_pressed and inside:
            self.command()

    def _key(self, e):
        if self.enabled:
            self.command()
        return "break"

    # ----- look -----
    def _paint(self, hover=None):
        if hover is not None:          # old code calls _paint(True/False)
            self.hover = hover
        fg, bg, hov, press, edge = self.STYLES[self.style]
        if not self.enabled:
            self.config(bg=SURFACE_2, fg=MUTED, cursor="arrow", highlightbackground=SURFACE_2,
                        highlightcolor=SURFACE_2)
            return
        shade = press if self.pressed else hov if self.hover else bg
        border = INK if self.focused else (LIME if self.hover and self.style == "secondary" else edge)
        self.config(bg=shade, fg=fg, cursor="hand2", highlightbackground=border,
                    highlightcolor=INK)

    def set_enabled(self, value):
        self.enabled = value
        self.config(takefocus=bool(value))
        self._paint()


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
    fg = fg if fg is not None else INK
    return tk.Label(parent, text=text, font=(FONT, size, "bold" if bold else "normal"),
                    fg=fg, bg=bg, **kw)


# We use a white card to group related information.
def card(parent, **kw):
    return tk.Frame(parent, bg=SURFACE, highlightthickness=1, highlightbackground=BORDER, **kw)


# We build the shared header shown at the top of each screen.
def top_bar(parent, title="ICT Quiz Master"):
    bar = tk.Frame(parent, bg=SURFACE, highlightthickness=1, highlightbackground=BORDER)
    bar.pack(fill="x")
    tk.Label(bar, text=" Q ", bg=LIME, fg=INK_ON_LIME, font=(FONT, 11, "bold")).pack(side="left", padx=(24, 8), pady=14)
    label(bar, title, 15, True).pack(side="left")
    SoundToggle(bar, parent.winfo_toplevel()).pack(side="right", padx=16, pady=5)
    return bar


# We make a row of buttons that work like radio buttons.
def chip_group(parent, options, var, size=10, command=None):
    """A row of buttons that behave like radio buttons. options = [(value, text), ...]"""
    btns = {}

    def paint():
        for value, b in btns.items():
            b.style = "primary" if var.get() == value else "secondary"
            b._paint()

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
