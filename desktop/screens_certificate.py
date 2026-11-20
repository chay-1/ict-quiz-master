import os
import tkinter as tk
import webbrowser
from tkinter import filedialog

from core.certificate import build_html, certificate_info, file_name
from core.quiz_data import beep
from core.quiz_theme import BG, FONT, INK, LIME, MUTED, PURPLE, TEAL
from desktop.widgets import FlatButton, label, top_bar

PAPER, DARK, SOFT = "#fffdf7", "#173f87", "#b17918"
GOLD, GOLD_DARK, BLUE = "#c69a45", "#9b741e", "#173f87"
BASE_W, BASE_H = 900, 636          # the certificate is designed at this size, then scaled


def draw_certificate(cv, w, h, info):
    """We draw the certificate on a canvas. Every size is multiplied by s so it fits any preview size."""
    s = w / BASE_W
    X = lambda v: v * s
    cv.delete("all")
    cv.create_rectangle(0, 0, w, h, fill=PAPER, outline="")
    cv.create_rectangle(X(8), X(8), w - X(8), h - X(8), fill=PAPER, outline=GOLD, width=max(2, int(10 * s)))
    cv.create_rectangle(X(14), X(14), w - X(14), h - X(14), outline="#b88a32", width=max(1, int(3 * s)))
    cv.create_rectangle(X(39), X(39), w - X(39), h - X(39), outline=GOLD, width=max(1, int(2 * s)))

    # Blue and gold decorative bands
    cv.create_rectangle(X(8), X(8), w - X(8), X(68), fill=BLUE, outline=GOLD, width=max(1, int(3 * s)))
    cv.create_rectangle(X(8), h - X(68), w - X(8), h - X(8), fill=BLUE, outline=GOLD, width=max(1, int(3 * s)))
    cv.create_rectangle(X(8), X(68), X(39), h - X(68), fill=BLUE, outline=GOLD, width=max(1, int(3 * s)))
    cv.create_rectangle(w - X(39), X(68), w - X(8), h - X(68), fill=BLUE, outline=GOLD, width=max(1, int(3 * s)))
    for cx in range(65, 840, 28):
        cv.create_line(X(cx - 6), X(29), X(cx), X(23), X(cx + 6), X(29),
                       fill=GOLD, width=max(1, int(2 * s)))
        cv.create_line(X(cx - 6), X(47), X(cx), X(53), X(cx + 6), X(47),
                       fill=GOLD, width=max(1, int(2 * s)))
        cv.create_line(X(cx - 6), h - X(29), X(cx), h - X(23), X(cx + 6), h - X(29),
                       fill=GOLD, width=max(1, int(2 * s)))
        cv.create_line(X(cx - 6), h - X(47), X(cx), h - X(53), X(cx + 6), h - X(47),
                       fill=GOLD, width=max(1, int(2 * s)))

    # Four large diamond corners
    for cx, cy in ((30, 30), (870, 30), (30, 606), (870, 606)):
        pts = [X(cx), X(cy - 16), X(cx + 16), X(cy), X(cx), X(cy + 16), X(cx - 16), X(cy)]
        cv.create_polygon(*pts, fill=BLUE, outline=GOLD, width=max(1, int(4 * s)))
        cv.create_polygon(X(cx), X(cy - 7), X(cx + 7), X(cy), X(cx), X(cy + 7), X(cx - 7), X(cy),
                          fill=BLUE, outline="#d7b65f", width=max(1, int(2 * s)))

    cv.create_text(X(450), X(104), text="I C T   Q U I Z   M A S T E R",
                   font=(FONT, max(7, int(11 * s)), "bold"), fill=SOFT)
    cv.create_text(X(451), X(166), text=info["title"], font=("Georgia", max(14, int(54 * s)), "bold"), fill="#b88a32")
    cv.create_text(X(450), X(166), text=info["title"], font=("Georgia", max(14, int(54 * s)), "bold"), fill=DARK)
    cv.create_text(X(450), X(218), text=" ".join(info["sub"]), font=("Georgia", max(8, int(17 * s)), "bold"), fill=SOFT)
    cv.create_text(X(450), X(266), text="This certificate is proudly presented to",
                   font=("Georgia", max(8, int(14 * s)), "italic"), fill=SOFT)

    n = len(info["name"])
    size = 46 if n <= 16 else 38 if n <= 24 else 30
    cv.create_text(X(450), X(310), text=info["name"], font=("Segoe Script", max(10, int(size * s)), "italic"), fill=DARK)
    cv.create_line(X(190), X(344), X(710), X(344), fill=GOLD, width=max(2, int(5 * s)))
    cv.create_text(X(450), X(390), text=info["message"], width=X(620), justify="center",
                   font=("Georgia", max(8, int(13 * s)), "italic"), fill=DARK)

    cv.create_polygon(X(423), X(550), X(413), X(596), X(438), X(588), X(450), X(606),
                      fill=BLUE, outline=GOLD_DARK)
    cv.create_polygon(X(477), X(550), X(487), X(596), X(462), X(588), X(450), X(606),
                      fill=BLUE, outline=GOLD_DARK)
    cv.create_oval(X(405), X(515), X(495), X(605), fill="#d5ad57", outline=GOLD_DARK,
                   width=max(2, int(4 * s)))
    cv.create_oval(X(416), X(526), X(484), X(594), fill="#d5ad57", outline="#f5dda1",
                   width=max(1, int(3 * s)))
    cv.create_text(X(450), X(560), text="★", font=(FONT, max(12, int(36 * s)), "bold"), fill=DARK)
    cv.create_rectangle(X(360), X(597), X(540), X(627), fill=PAPER, outline=GOLD_DARK,
                        width=max(1, int(3 * s)))
    cv.create_text(X(450), X(612), text=info["date"], font=("Georgia", max(8, int(12 * s)), "bold"), fill=DARK)


class CertificateScreen(tk.Frame):
    """We show the student's certificate and let them download it."""

    def __init__(self, app, topic, r, entry):
        super().__init__(app, bg=BG)
        # The preview shrinks on small windows so the buttons below are never cut off.
        self.H = max(300, min(452, app.winfo_height() - 250))
        self.W = int(self.H * BASE_W / BASE_H)
        self.app, self.topic, self.r, self.entry = app, topic, r, entry
        self.saved_path = None
        top_bar(self, "ICT Quiz Master · Your Certificate")

        dock = tk.Frame(self, bg=BG)                       # buttons pinned to the bottom: always visible
        dock.pack(side="bottom", fill="x", pady=(0, 10))
        self.status = label(dock, "", 10, True, TEAL)
        self.status.pack(pady=(0, 6))
        row = tk.Frame(dock, bg=BG)
        row.pack()
        self.dl_btn = FlatButton(row, "⬇  DOWNLOAD CERTIFICATE", self.download, "primary", 11)
        self.dl_btn.config(padx=20, pady=8)
        self.dl_btn.pack(side="left", padx=5)
        self.open_btn = FlatButton(row, "OPEN IN BROWSER", self.open_file, "pink", 11)
        self.open_btn.config(padx=16, pady=8)
        self.open_btn.pack(side="left", padx=5)
        self.open_btn.set_enabled(False)
        for text, cmd in (("BACK TO RESULT", self.back), ("HOME", app.show_welcome)):
            b = FlatButton(row, text, cmd, "secondary", 11)
            b.config(padx=16, pady=8)
            b.pack(side="left", padx=5)

        info = certificate_info(entry)
        head = "🎓 Congratulations!" if info["passed"] else "🎓 Thank you for taking part!"
        label(self, head, 18, True, LIME).pack(pady=(12, 0))
        label(self, "This certificate is a token of appreciation for your effort.", 10, fg=MUTED).pack(pady=(0, 8))
        cv = tk.Canvas(self, width=self.W, height=self.H, highlightthickness=2, highlightbackground=PURPLE)
        cv.pack()
        draw_certificate(cv, self.W, self.H, info)
        app.bind("<Return>", lambda e: self.download())    # Enter = download

    def destroy(self):
        try:
            self.app.unbind("<Return>")
        except Exception:
            pass
        super().destroy()

    def download(self):
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        path = filedialog.asksaveasfilename(
            parent=self.app, title="Save your certificate", defaultextension=".html",
            initialdir=downloads if os.path.isdir(downloads) else os.path.expanduser("~"),
            initialfile=file_name(self.entry),
            filetypes=[("Certificate (opens in your browser)", "*.html")])
        if not path:
            return                                          # the student pressed Cancel
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(build_html(self.entry))
        except OSError as err:
            self.status.config(text=f"Could not save the file: {err}", fg="#ff5d6c")
            return
        self.saved_path = path
        self.status.config(text=f"✓ Saved: {path}   (open it and press 'Print / Save as PDF' for a PDF)", fg=TEAL)
        self.open_btn.set_enabled(True)
        beep("ok", self.app)

    def open_file(self):
        if self.saved_path:
            webbrowser.open("file:///" + self.saved_path.replace("\\", "/"))

    def back(self):
        from desktop.screens_quiz import ResultScreen
        self.app.swap(ResultScreen, self.topic, self.r, self.entry, False)
