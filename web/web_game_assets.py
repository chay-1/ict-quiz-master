"""Shared browser visuals, sound effects and certificate generation."""
from pathlib import Path
from io import BytesIO
import base64
import html
import tempfile
import uuid

ROOT = Path(__file__).resolve().parent.parent   # the ICT_Quiz_Master folder
IMAGE_DIR = ROOT / "images"
SOUND_DIR = ROOT / "sounds"
ASSET_DIR = ROOT / "assets"


def question_visual(pic):
    """Return an animated, topic-related SVG illustration as responsive HTML."""
    if not pic:
        return "<div class='visual-placeholder'>💡 Think carefully and choose your answer.</div>"
    path = IMAGE_DIR / f"{pic}.svg"
    if not path.exists():
        return "<div class='visual-placeholder'>🖥️ ICT Quiz Challenge</div>"
    svg = path.read_text(encoding="utf-8")
    return f"""
    <div class="quiz-visual" aria-label="Question illustration">{svg}</div>
    <style>
      .quiz-visual {{ width:min(100%,390px); aspect-ratio:16/9; margin:0 auto 6px; overflow:hidden; }}
      .quiz-visual svg {{ width:100%; height:100%; display:block; border-radius:16px; }}
    </style>"""


VISUAL_HEIGHT = 228   # iframe height (px) used by Streamlit: picture 219 px + small margin


def sound_html(kind):
    """Return hidden autoplay audio (no buttons).

    Every call makes a NEW id and comment. Gradio only redraws an HTML box when its
    text changes; without this, the second correct (or wrong) answer had the same
    text as the first one, so the browser never played the sound again.
    """
    choices = {
        "correct": ("correct.mp3", "correct.wav"),
        "wrong": ("wrong.mp3", "wrong.wav"),
        "celebration": ("celebration.mp3", "celebration.wav"),
    }
    for filename in choices[kind]:
        path = SOUND_DIR / filename
        if path.is_file() and path.stat().st_size:
            mime = "audio/mpeg" if path.suffix.lower() == ".mp3" else "audio/wav"
            data = base64.b64encode(path.read_bytes()).decode("ascii")
            uid = uuid.uuid4().hex
            return (f'<!-- {uid} -->'
                    f'<audio id="snd-{uid}" autoplay preload="auto" style="display:none">'
                    f'<source src="data:{mime};base64,{data}" type="{mime}"></audio>')
    return ""


def _basic_pdf_certificate(result):
    """Create a small one-page PDF certificate using only the Python standard library."""
    import re

    def safe(value):
        value = str(value)
        # Built-in PDF Helvetica uses WinAnsi; replace unsupported glyphs safely.
        value = value.encode("cp1252", errors="replace").decode("cp1252")
        return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    name = safe(result.get("name", "Student"))
    topic = safe(result.get("topic", "ICT"))
    correct = safe(f"{result.get('correct', 0)}/{result.get('total', 10)}")
    score = safe(result.get("finalScore", 0))
    streak = safe(result.get("bestStreak", 0))
    date_text = safe(result.get("date", ""))

    commands = [
        "q", "0.09 0.20 0.40 RG", "4 w", "35 35 772 532 re S",
        "0.75 0.85 1 RG", "1.2 w", "45 45 752 512 re S", "Q",
        "BT", "/F1 25 Tf", "0.09 0.20 0.40 rg", "1 0 0 1 195 500 Tm",
        "(CERTIFICATE OF COMPLETION) Tj", "ET",
        "BT", "/F1 13 Tf", "0.14 0.35 0.75 rg", "1 0 0 1 325 468 Tm",
        "(ICT QUIZ MASTER) Tj", "ET",
        "BT", "/F1 14 Tf", "0.28 0.34 0.42 rg", "1 0 0 1 270 405 Tm",
        "(This certificate is proudly presented to) Tj", "ET",
        "BT", "/F1 27 Tf", "0.14 0.35 0.75 rg", "1 0 0 1 170 350 Tm",
        f"({name}) Tj", "ET",
        "BT", "/F1 14 Tf", "0.28 0.34 0.42 rg", "1 0 0 1 285 315 Tm",
        "(for completing the interactive ICT quiz) Tj", "ET",
        "BT", "/F1 19 Tf", "0.09 0.20 0.40 rg", "1 0 0 1 300 270 Tm",
        f"({topic}) Tj", "ET",
        "BT", "/F1 12 Tf", "0.09 0.20 0.40 rg", "1 0 0 1 175 205 Tm",
        f"(Correct answers: {correct}     Final score: {score}     Best streak: {streak}) Tj", "ET",
        "BT", "/F1 12 Tf", "0.28 0.34 0.42 rg", "1 0 0 1 350 145 Tm",
        f"(Date: {date_text}) Tj", "ET",
        "BT", "/F1 12 Tf", "0.28 0.34 0.42 rg", "1 0 0 1 255 105 Tm",
        "(Keep learning, practising and exploring technology!) Tj", "ET",
    ]
    stream = "\n".join(commands).encode("cp1252", errors="replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 842 595] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode())
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objects)+1}\n".encode())
    pdf.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        pdf.extend(f"{off:010d} 00000 n \n".encode())
    pdf.extend(
        f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    )
    return bytes(pdf)


def certificate_pdf(result):
    """Create a landscape Certificate of Completion (Bhutanese key-pattern design) as PDF bytes."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.units import mm
        from reportlab.lib.utils import ImageReader
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                        TableStyle, KeepInFrame)
    except ImportError:
        # Keep certificate downloads available even if ReportLab has not yet
        # been installed. The standard-library fallback creates a simple PDF.
        return _basic_pdf_certificate(result)

    # ── Colours (change these lines to re-colour the whole certificate) ──
    red = colors.HexColor("#b5382a")      # outer border and title
    gold = colors.HexColor("#c8892a")     # thin gold lines
    ink = colors.HexColor("#2b2b2b")      # normal text

    page_w, page_h = landscape(A4)         # landscape page: 297 mm wide, 210 mm high
    side, top, bottom = 30 * mm, 50 * mm, 24 * mm
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=side, leftMargin=side,
                            topMargin=top, bottomMargin=bottom,
                            title="ICT Quiz Master Certificate", author="ICT Quiz Master")

    styles = getSampleStyleSheet()
    def style(name, **kw):
        return ParagraphStyle(name, parent=styles["Normal"], alignment=TA_CENTER, **kw)

    student = html.escape(str(result.get("name", "Student")))
    name_size = 34 if len(student) <= 20 else 26 if len(student) <= 30 else 18
    year = str(result.get("date", ""))[:4] or "2026"
    title = style("CertTitle", fontName="Helvetica-Bold", fontSize=28, leading=33, textColor=red)
    sub = style("CertSub", fontName="Helvetica-Oblique", fontSize=12, leading=16, textColor=red)
    body = style("CertBody", fontName="Times-Roman", fontSize=15, leading=20, textColor=ink)
    name_style = style("CertName", fontName="Times-BoldItalic", fontSize=name_size,
                       leading=name_size + 10, textColor=ink)
    topic_style = style("CertTopic", fontName="Helvetica-Bold", fontSize=17, leading=24, textColor=ink)

    stats = Table([[f"Correct answers: {result.get('correct', 0)}/{result.get('total', 10)}",
                    f"Final score: {result.get('finalScore', 0)}",
                    f"Best streak: {result.get('bestStreak', 0)}"]],
                  colWidths=[65 * mm] * 3, rowHeights=[11 * mm])
    stats.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("TEXTCOLOR", (0, 0), (-1, -1), red), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEABOVE", (0, 0), (-1, 0), 1, gold), ("LINEBELOW", (0, 0), (-1, 0), 1, gold)]))

    story = [
        Paragraph("Certificate of Completion", title),
        Paragraph(f"(ICT Quiz Master Award {html.escape(year)})", sub),
        Spacer(1, 8 * mm),
        Paragraph("Awarded to", body),
        Spacer(1, 3 * mm),
        Paragraph(student, name_style),
        Spacer(1, 3 * mm),
        Paragraph("in recognition of completing the interactive ICT quiz on", body),
        Spacer(1, 2 * mm),
        Paragraph(html.escape(str(result.get("topic", "ICT"))).upper(), topic_style),
        Spacer(1, 7 * mm), stats, Spacer(1, 7 * mm),
        Paragraph("Keep learning, practising and exploring technology!", body),
        Spacer(1, 4 * mm),
        Paragraph(f"Date: {html.escape(str(result.get('date', '')))}", body),
    ]
    # KeepInFrame shrinks the content if a very long name or topic would overflow the page
    frame = KeepInFrame(page_w - 2 * side, page_h - top - bottom, story, mode="shrink",
                        hAlign="CENTER", vAlign="TOP")

    def draw_page(canvas, _doc):
        canvas.saveState()
        m = 11 * mm                                   # red border distance from the page edge
        canvas.setStrokeColor(red); canvas.setLineWidth(5)
        canvas.rect(m, m, page_w - 2 * m, page_h - 2 * m)
        g = m + 4.5 * mm                              # thin gold line inside the red border
        canvas.setStrokeColor(gold); canvas.setLineWidth(1.2)
        canvas.rect(g, g, page_w - 2 * g, page_h - 2 * g)
        try:
            key = ImageReader(str(ASSET_DIR / "druk_key.png"))
            circle = ImageReader(str(ASSET_DIR / "druk_circle.png"))
        except Exception:
            canvas.restoreState()                     # ornament pictures missing: borders only
            return
        size = 26 * mm
        # one key-pattern corner, mirrored into all four corners (flip around the page centre)
        for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            canvas.saveState()
            canvas.translate(page_w / 2, page_h / 2)
            canvas.scale(sx, sy)
            canvas.drawImage(key, -page_w / 2 + g + 1.5 * mm, page_h / 2 - g - 1.5 * mm - size,
                             size, size, mask="auto")
            canvas.restoreState()
        d = 22 * mm                                   # round emblem at the top centre
        canvas.drawImage(circle, (page_w - d) / 2, page_h - g - d - 9 * mm, d, d, mask="auto")
        # optional school logos: drop logo_left.png / logo_right.png into the assets folder
        for file, x in (("logo_left.png", g + 36 * mm), ("logo_right.png", page_w - g - 36 * mm - d)):
            path = ASSET_DIR / file
            if path.is_file():
                canvas.drawImage(ImageReader(str(path)), x, page_h - g - d - 9 * mm, d, d,
                                 mask="auto", preserveAspectRatio=True)
        canvas.restoreState()

    doc.build([frame], onFirstPage=draw_page)
    return buffer.getvalue()


def certificate_file(result):
    """Write a generated certificate to a temporary PDF for Gradio download."""
    data = certificate_pdf(result)
    safe_name = "".join(c for c in str(result.get("name", "student")) if c.isalnum() or c in "-_")
    safe_name = safe_name or "student"
    path = Path(tempfile.gettempdir()) / f"ICT_Quiz_Certificate_{safe_name}.pdf"
    path.write_bytes(data)
    return str(path)