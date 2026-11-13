import os
import tkinter as tk

from quiz_theme import AMBER, BG, BLUE, FONT, GREEN, GREY, LIGHT, MUTED, NAVY, RED, WHITE

# ───────────────────────── Question pictures (drawn with Canvas) ─────────────────────────
# We use these functions to draw simple pictures for the quiz questions.
PIC_W, PIC_H = 150, 84
IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
CYAN, PURPLE = "#06b6d4", "#a855f7"

def _txt(c, x, y, text, size=10, fill=NAVY):
    c.create_text(x, y, text=text, font=(FONT, size, "bold"), fill=fill)

def _cpu(c):
    for i in range(5):
        x = 55 + i * 10
        c.create_line(x, 8, x, 20, fill=AMBER, width=3)
        c.create_line(x, 64, x, 76, fill=AMBER, width=3)
    for y in (28, 38, 48, 58):
        c.create_line(35, y, 45, y, fill=AMBER, width=3)
        c.create_line(105, y, 115, y, fill=AMBER, width=3)
    c.create_rectangle(45, 20, 105, 64, fill=NAVY, outline=NAVY)
    _txt(c, 75, 42, "CPU", 13, WHITE)


def _ram(c):
    c.create_rectangle(10, 22, 140, 62, fill="#16a34a", outline=NAVY, width=2)
    for i in range(4):
        c.create_rectangle(20 + i * 30, 30, 44 + i * 30, 50, fill=NAVY)
    for i in range(15):
        c.create_line(15 + i * 8, 62, 15 + i * 8, 72, fill=AMBER, width=3)
    _txt(c, 75, 14, "RAM", 9)


def _os(c):
    c.create_rectangle(22, 8, 128, 76, fill=WHITE, outline=NAVY, width=2)
    c.create_rectangle(22, 8, 128, 20, fill=NAVY, outline=NAVY)
    for i, col in enumerate((BLUE, GREEN, AMBER, RED)):
        x, y = 36 + (i % 2) * 42, 28 + (i // 2) * 24
        c.create_rectangle(x, y, x + 36, y + 20, fill=col, outline=col)


def _router(c):
    c.create_line(35, 46, 25, 12, fill=NAVY, width=4)
    c.create_line(115, 46, 125, 12, fill=NAVY, width=4)
    c.create_rectangle(15, 44, 135, 70, fill=NAVY, outline=NAVY)
    for i in range(4):
        c.create_oval(30 + i * 16, 53, 38 + i * 16, 61, fill=GREEN, outline=GREEN)
    c.create_rectangle(100, 53, 125, 61, fill=BLUE, outline=BLUE)


def _star(c, label="SW"):
    nodes = [(22, 16), (75, 10), (128, 16), (22, 68), (128, 68)]
    for x, y in nodes:
        c.create_line(75, 42, x, y, fill=MUTED, width=2)
    c.create_oval(60, 30, 90, 54, fill=BLUE, outline=NAVY, width=2)
    _txt(c, 75, 42, label, 10, WHITE)
    for x, y in nodes:
        c.create_rectangle(x - 13, y - 8, x + 13, y + 8, fill=NAVY, outline=NAVY)


def _envelope(c, alert=False):
    c.create_rectangle(28, 20, 122, 68, fill=WHITE, outline=NAVY, width=2)
    c.create_line(28, 20, 75, 50, 122, 20, fill=NAVY, width=2)
    if alert:
        c.create_oval(106, 6, 134, 34, fill=RED, outline=WHITE, width=2)
        _txt(c, 120, 20, "!", 14, WHITE)


def _table(hr=None, hc=None):
    def draw(c):
        xs, ys = (12, 48, 100, 138), (8, 24, 40, 56, 72)
        rows = (("ID", "Name", "Age"), ("1", "Tashi", "15"), ("2", "Pema", "16"), ("3", "Dema", "15"))
        for r in range(4):
            for k in range(3):
                head = r == 0
                fill = NAVY if head else "#fde68a" if (r == hr or k == hc) else WHITE
                c.create_rectangle(xs[k], ys[r], xs[k + 1], ys[r + 1], fill=fill, outline=MUTED)
                _txt(c, (xs[k] + xs[k + 1]) // 2, (ys[r] + ys[r + 1]) // 2, rows[r][k], 8,
                     WHITE if head else NAVY)
    return draw


def _cylinder(c):
    c.create_oval(40, 56, 110, 76, fill=BLUE, outline=NAVY, width=2)
    c.create_rectangle(40, 20, 110, 66, fill=BLUE, outline=BLUE)
    c.create_line(40, 20, 40, 66, fill=NAVY, width=2)
    c.create_line(110, 20, 110, 66, fill=NAVY, width=2)
    c.create_arc(40, 56, 110, 76, start=180, extent=180, style="arc", outline=NAVY, width=2)
    c.create_arc(40, 38, 110, 58, start=180, extent=180, style="arc", outline=WHITE, width=2)
    c.create_oval(40, 10, 110, 30, fill="#93c5fd", outline=NAVY, width=2)


def _padlock(c):
    c.create_arc(55, 8, 95, 52, start=0, extent=180, style="arc", outline=NAVY, width=7)
    c.create_rectangle(45, 34, 105, 74, fill=AMBER, outline=NAVY, width=2)
    c.create_oval(68, 44, 82, 58, fill=NAVY)
    c.create_rectangle(72, 54, 78, 66, fill=NAVY)


def _shield(c):
    c.create_polygon(75, 6, 118, 18, 118, 46, 75, 78, 32, 46, 32, 18, fill=BLUE, outline=NAVY, width=3)
    c.create_line(54, 40, 70, 56, 98, 26, fill=WHITE, width=7)


def _bug(c):
    for i in range(3):
        y = 36 + i * 11
        c.create_line(58, y, 40, y - 6 + i * 6, fill=NAVY, width=3)
        c.create_line(92, y, 110, y - 6 + i * 6, fill=NAVY, width=3)
    c.create_line(68, 16, 58, 6, fill=NAVY, width=2)
    c.create_line(82, 16, 92, 6, fill=NAVY, width=2)
    c.create_oval(55, 26, 95, 76, fill=RED, outline=NAVY, width=2)
    c.create_oval(63, 12, 87, 32, fill=NAVY)
    c.create_line(75, 32, 75, 74, fill=NAVY, width=2)


def _wifi(c):
    for r in (16, 30, 44):
        c.create_arc(75 - r, 66 - r, 75 + r, 66 + r, start=45, extent=90, style="arc", outline=BLUE, width=6)
    c.create_oval(68, 62, 82, 76, fill=BLUE, outline=BLUE)


def _computer(c):
    c.create_rectangle(14, 8, 104, 56, fill=NAVY, outline=NAVY)
    c.create_rectangle(20, 14, 98, 50, fill="#93c5fd", outline="#93c5fd")
    c.create_rectangle(53, 56, 65, 66, fill=NAVY, outline=NAVY)
    c.create_rectangle(38, 66, 80, 72, fill=NAVY, outline=NAVY)
    c.create_rectangle(114, 12, 140, 72, fill=GREY, outline=NAVY, width=2)
    c.create_line(120, 22, 134, 22, fill=NAVY, width=2)
    c.create_line(120, 30, 134, 30, fill=NAVY, width=2)
    c.create_oval(123, 58, 131, 66, fill=GREEN, outline=GREEN)


def _io(c):
    c.create_line(4, 42, 40, 42, fill=NAVY, width=3, arrow=tk.LAST)
    c.create_rectangle(42, 22, 108, 62, fill=BLUE, outline=NAVY, width=2)
    _txt(c, 75, 42, "Computer", 9, WHITE)
    c.create_line(110, 42, 146, 42, fill=NAVY, width=3, arrow=tk.LAST)
    _txt(c, 22, 30, "IN", 9)
    _txt(c, 128, 30, "OUT", 9)


def _binary(c):
    for i, row in enumerate(("10110010111010", "01101001011100", "11010010110101")):
        _txt(c, 75, 16 + i * 26, row, 11, BLUE if i % 2 == 0 else NAVY)


def _power(c):
    c.create_arc(45, 12, 105, 72, start=120, extent=300, style="arc", outline=NAVY, width=7)
    c.create_line(75, 6, 75, 40, fill=NAVY, width=7)


def _disc(c):
    c.create_oval(35, 6, 115, 78, fill="#cbd5e1", outline=NAVY, width=2)
    c.create_oval(58, 29, 92, 55, fill=WHITE, outline=NAVY)
    c.create_oval(69, 37, 81, 47, fill=BG, outline=NAVY)
    c.create_arc(45, 16, 105, 68, start=110, extent=50, style="arc", outline=WHITE, width=4)


def _code(c):
    c.create_rectangle(30, 6, 120, 78, fill=WHITE, outline=NAVY, width=2)
    for x1, y, x2, col in ((40, 16, 82, BLUE), (50, 28, 104, GREEN), (50, 40, 94, AMBER),
                           (50, 52, 80, PURPLE), (40, 64, 70, BLUE)):
        c.create_rectangle(x1, y, x2, y + 6, fill=col, outline=col)


def _browser(c):
    c.create_rectangle(8, 6, 142, 78, fill=WHITE, outline=NAVY, width=2)
    c.create_rectangle(8, 6, 142, 18, fill=GREY, outline=NAVY)
    c.create_rectangle(16, 24, 134, 38, fill=LIGHT, outline=MUTED)
    _txt(c, 75, 31, "www.example.com", 8, BLUE)
    c.create_rectangle(16, 46, 66, 70, fill=GREY, outline=GREY)
    for y in (48, 58, 68):
        c.create_rectangle(76, y - 2, 134, y + 2, fill=GREY, outline=GREY)


def _ip_q(c):
    for i in range(4):
        x = 4 + i * 37
        c.create_rectangle(x, 28, x + 31, 54, fill=LIGHT, outline=BLUE, width=2)
        _txt(c, x + 15, 41, "?", 14, BLUE)
        if i < 3:
            c.create_oval(x + 33, 50, x + 36, 53, fill=NAVY)


def _globe(c):
    c.create_oval(35, 6, 115, 78, fill=LIGHT, outline=BLUE, width=2)
    c.create_oval(55, 6, 95, 78, outline=BLUE, width=2)
    c.create_line(75, 6, 75, 78, fill=BLUE, width=2)
    for y in (26, 42, 58):
        c.create_line(38, y, 112, y, fill=BLUE, width=2)


def _cable(c):
    c.create_line(30, 42, 50, 18, 75, 66, 100, 18, 120, 42, smooth=True, fill=NAVY, width=4)
    for x in (6, 120):
        c.create_rectangle(x, 32, x + 24, 52, fill=GREY, outline=NAVY, width=2)
        for k in range(3):
            c.create_line(x + 6 + k * 6, 36, x + 6 + k * 6, 48, fill=AMBER, width=2)


def _hook(c):
    c.create_line(75, 4, 75, 44, fill=NAVY, width=4)
    c.create_arc(53, 32, 97, 76, start=180, extent=180, style="arc", outline=NAVY, width=4)
    c.create_line(97, 54, 97, 40, fill=NAVY, width=4)
    c.create_line(53, 54, 46, 44, fill=NAVY, width=4)


def _folder(c):
    c.create_rectangle(20, 12, 62, 26, fill=AMBER, outline=NAVY, width=2)
    c.create_rectangle(20, 24, 130, 72, fill="#fbbf24", outline=NAVY, width=2)
    c.create_rectangle(32, 34, 118, 62, fill=WHITE, outline=WHITE)
    for y in (40, 48, 56):
        c.create_line(38, y, 112, y, fill=MUTED, width=2)


def _phone(c):
    c.create_rectangle(48, 4, 102, 80, fill=NAVY, outline=NAVY)
    c.create_rectangle(53, 12, 97, 66, fill=LIGHT, outline=LIGHT)
    c.create_oval(70, 69, 80, 77, fill=GREY, outline=GREY)
    c.create_rectangle(58, 20, 88, 28, fill=BLUE, outline=BLUE)
    c.create_rectangle(62, 34, 92, 42, fill=GREY, outline=GREY)
    c.create_rectangle(58, 48, 82, 56, fill=BLUE, outline=BLUE)


def _pointer(c):
    c.create_polygon(52, 6, 52, 64, 66, 51, 76, 76, 88, 70, 78, 46, 98, 46,
                     fill=NAVY, outline=WHITE, width=2)


def _laptop(c):
    c.create_rectangle(30, 6, 120, 54, fill=NAVY, outline=NAVY)
    c.create_rectangle(36, 12, 114, 48, fill="#93c5fd", outline="#93c5fd")
    c.create_polygon(16, 54, 134, 54, 142, 70, 8, 70, fill=GREY, outline=NAVY, width=2)
    c.create_line(62, 62, 88, 62, fill=MUTED, width=3)


def _building(c):
    c.create_polygon(16, 30, 75, 6, 134, 30, fill=RED, outline=NAVY, width=2)
    c.create_rectangle(24, 30, 126, 78, fill="#fde68a", outline=NAVY, width=2)
    c.create_rectangle(66, 48, 84, 78, fill=NAVY, outline=NAVY)
    for x in (34, 98):
        c.create_rectangle(x, 40, x + 18, 56, fill="#93c5fd", outline=NAVY)


def _switch(c):
    c.create_rectangle(8, 26, 142, 62, fill="#334155", outline=NAVY, width=2)
    for i in range(8):
        c.create_rectangle(16 + i * 15, 38, 26 + i * 15, 52, fill=BLUE, outline=WHITE)
        c.create_oval(19 + i * 15, 30, 23 + i * 15, 34, fill=GREEN, outline=GREEN)


def _key(c):
    c.create_rectangle(58, 38, 132, 47, fill=AMBER, outline=NAVY, width=2)
    c.create_rectangle(106, 47, 114, 62, fill=AMBER, outline=NAVY, width=2)
    c.create_rectangle(120, 47, 128, 57, fill=AMBER, outline=NAVY, width=2)
    c.create_oval(14, 20, 62, 64, fill=AMBER, outline=NAVY, width=3)
    c.create_oval(30, 34, 46, 50, fill=BG, outline=NAVY, width=2)


def _two_tables(c):
    for x0 in (6, 82):
        for r in range(4):
            for k in range(2):
                fill = NAVY if r == 0 else WHITE
                c.create_rectangle(x0 + k * 31, 14 + r * 14, x0 + 31 + k * 31, 28 + r * 14,
                                   fill=fill, outline=MUTED)


def _clipboard(c):
    c.create_rectangle(38, 10, 112, 80, fill="#a16207", outline=NAVY, width=2)
    c.create_rectangle(46, 20, 104, 72, fill=WHITE, outline=WHITE)
    c.create_rectangle(60, 4, 90, 16, fill=GREY, outline=NAVY, width=2)
    for y in (30, 40, 50, 60):
        c.create_line(52, y, 98, y, fill=MUTED, width=2)


def _cabinet(c):
    c.create_rectangle(38, 4, 112, 80, fill="#94a3b8", outline=NAVY, width=2)
    for i in range(3):
        y = 10 + i * 24
        c.create_rectangle(44, y, 106, y + 20, fill=GREY, outline=NAVY)
        c.create_rectangle(67, y + 7, 83, y + 11, fill=NAVY, outline=NAVY)


def _funnel(c):
    c.create_polygon(28, 8, 122, 8, 84, 46, 84, 74, 66, 80, 66, 46, fill=BLUE, outline=NAVY, width=2)
    c.create_line(40, 16, 110, 16, fill="#93c5fd", width=3)


def _drive(c):
    c.create_rectangle(24, 14, 116, 66, fill="#334155", outline=NAVY, width=2)
    c.create_rectangle(34, 22, 106, 36, fill=GREY, outline=GREY)
    c.create_oval(98, 50, 108, 60, fill=GREEN, outline=GREEN)
    c.create_line(116, 40, 146, 40, fill=NAVY, width=4)


def _flame(c):
    c.create_polygon(75, 4, 96, 30, 106, 54, 92, 78, 58, 78, 44, 54, 56, 32, 66, 42,
                     smooth=True, fill="#f97316", outline="#ea580c", width=2)
    c.create_polygon(75, 38, 88, 56, 82, 74, 64, 74, 60, 56, smooth=True, fill=AMBER, outline=AMBER)


def _gear(c):
    import math
    pts = []
    for i in range(32):
        a = i * 2 * math.pi / 32
        r = 38 if i % 4 in (0, 1) else 30
        pts += [75 + r * math.cos(a), 42 + r * math.sin(a)]
    c.create_polygon(*pts, fill="#64748b", outline=NAVY, width=2)
    c.create_oval(61, 28, 89, 56, fill=BG, outline=NAVY, width=2)


def _paperclip(c):
    c.create_line(50, 72, 50, 26, 60, 12, 76, 12, 88, 24, 88, 60, 78, 70, 68, 70, 60, 62, 60, 34,
                  66, 28, 72, 28, 76, 34, 76, 56, smooth=True, fill="#64748b", width=5)


DRAWERS = {"computer": _computer, "ram": _ram, "os": _os, "io": _io, "binary": _binary, "power": _power,
           "disc": _disc, "pointer": _pointer, "cpu": _cpu, "code": _code,
           "laptop": _laptop, "router": _router, "browser": _browser, "building": _building,
           "hub_q": lambda c: _star(c, "?"), "ip_q": _ip_q, "globe": _globe, "switch": _switch,
           "envelope": _envelope, "cable": _cable,
           "table": _table(), "key": _key, "clipboard": _clipboard, "table_row": _table(hr=2),
           "cabinet": _cabinet, "table_col": _table(hc=1), "cylinder": _cylinder,
           "two_tables": _two_tables, "funnel": _funnel, "drive": _drive,
           "hook": _hook, "bug": _bug, "padlock": _padlock, "flame": _flame, "shield": _shield,
           "folder": _folder, "paperclip": _paperclip, "gear": _gear, "phone": _phone, "wifi": _wifi}


# We show a PNG picture if available; otherwise, we draw it on the canvas.
def draw_picture(cv, key):
    """Draw the picture for `key`. If images/<key>.png exists, that photo is used instead."""
    cv.delete("all")
    if not key:
        return
    path = os.path.join(IMG_DIR, key + ".png")
    if os.path.exists(path):
        try:
            cv.img = tk.PhotoImage(file=path)
            cv.create_image(PIC_W // 2, PIC_H // 2, image=cv.img)
            return
        except tk.TclError:
            pass
    DRAWERS.get(key, lambda c: None)(cv)
