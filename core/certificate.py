"""Certificate rules and the downloadable certificate file (no window code here).

Every student who finishes a quiz receives a certificate as a token of appreciation:
  - passed the quiz            -> CERTIFICATE OF ACHIEVEMENT
  - finished, but not passed   -> CERTIFICATE OF PARTICIPATION (thanks for the effort)
The downloadable file is a landscape A4 page (.html). It opens in any browser, and the
"Print / Save as PDF" button on the page turns it into a PDF.
"""
import html
import re
from datetime import date

from core.quiz_data import PASS_MARK


def certificate_info(entry):
    """We decide the title and the message from the student's result."""
    passed = entry["correct"] >= PASS_MARK
    topic = entry["topic"]
    if passed:
        title, sub = "CERTIFICATE", "OF ACHIEVEMENT"
        message = (f"for successfully passing the {topic} quiz with {entry['correct']} out of "
                   f"{entry['total']} correct answers. Thank you for your effort and hard work!")
    else:
        title, sub = "CERTIFICATE", "OF PARTICIPATION"
        message = (f"in appreciation of completing the {topic} quiz. Thank you for your effort "
                   f"and willingness to learn. Keep practising, every attempt makes you stronger!")
    return {"passed": passed, "title": title, "sub": sub, "message": message,
            "name": entry["name"].strip() or "Student", "topic": topic,
            "score": f"{entry['correct']}/{entry['total']}", "final": entry["finalScore"],
            "streak": entry.get("bestStreak", 0), "date": pretty_date(entry.get("date"))}


def pretty_date(iso):
    try:
        return date.fromisoformat(iso).strftime("%d %B %Y")
    except (TypeError, ValueError):
        return date.today().strftime("%d %B %Y")


def file_name(entry):
    """A safe file name such as Certificate_Sangay_Networking.html"""
    clean = lambda t: re.sub(r"[^A-Za-z0-9]+", "_", t).strip("_") or "Student"
    return f"Certificate_{clean(entry['name'])}_{clean(entry['topic'])}.html"


def build_html(entry):
    """We build the whole certificate page. Student text is escaped so it can never break the page."""
    c = {k: html.escape(str(v)) for k, v in certificate_info(entry).items() if k != "passed"}
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Certificate - {c['name']}</title>
<style>
  @page {{ size: A4 landscape; margin: 0; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: #e8e3d8; font-family: "Segoe UI", Arial, sans-serif;
         display: flex; flex-direction: column; align-items: center; padding: 24px 0; }}
  .toolbar {{ margin-bottom: 18px; }}
  .toolbar button {{ background: #d6f55b; color: #12150a; border: 0; padding: 12px 26px;
         font-weight: 700; font-size: 15px; border-radius: 6px; cursor: pointer; }}
  .toolbar button:hover {{ background: #e6ff7a; }}
  .page {{ width: 297mm; height: 210mm; background: #fffdf7; position: relative;
         border: 2.7mm solid #c69a45; padding: 0; overflow: hidden; }}
  .page::before {{ content: ""; position: absolute; inset: 1.7mm;
         border: 0.8mm solid #b88a32; pointer-events: none; }}
  .blue-band {{ position: absolute; left: 2.7mm; right: 2.7mm; height: 18mm;
         background: #173f87;
         background-image: repeating-linear-gradient(45deg, transparent 0 3mm, rgba(198,154,69,.9) 3mm 3.5mm),
                           repeating-linear-gradient(-45deg, transparent 0 3mm, rgba(198,154,69,.5) 3mm 3.5mm);
         border: 0.7mm solid #c69a45; z-index: 1; }}
  .top {{ top: 2.7mm; }} .bottom {{ bottom: 2.7mm; }}
  .side {{ position: absolute; top: 20mm; bottom: 20mm; width: 10mm;
         background: repeating-linear-gradient(45deg, #173f87 0 2mm, #b88a32 2mm 2.5mm, #173f87 2.5mm 4.5mm);
         border-left: 0.7mm solid #c69a45; border-right: 0.7mm solid #c69a45; z-index: 1; }}
  .side-left {{ left: 2.7mm; }} .side-right {{ right: 2.7mm; }}
  .inner {{ position: absolute; left: 13mm; right: 13mm; top: 20mm; bottom: 20mm;
         border: 0.5mm solid #c69a45; text-align: center; z-index: 2; }}
  .brand {{ margin-top: 7mm; color: #173f87; font-size: 10pt; font-weight: 800;
         letter-spacing: 2.4mm; line-height: 1; }}
  h1 {{ font-family: Georgia, serif; font-size: 42pt; line-height: 1; margin: 8mm 0 1mm;
         color: #173f87; letter-spacing: 0.7mm; text-shadow: 0.4mm 0.4mm 0 #b88a32; }}
  h2 {{ font-family: Georgia, serif; font-size: 14pt; margin: 1.5mm 0 5mm;
         color: #b17918; letter-spacing: 2mm; }}
  .lead {{ color: #b17918; font-family: Georgia, serif; font-style: italic;
         font-size: 12pt; margin: 0; }}
  .name {{ font-family: "Segoe Script", "Brush Script MT", cursive; font-size: 31pt;
         color: #173f87; display: block; width: 64%; margin: 2mm auto 3mm;
         padding-bottom: 1mm; border-bottom: 0.7mm solid #c69a45; }}
  .msg {{ width: 72%; margin: 0 auto; color: #173f87; font-family: Georgia, serif;
         font-style: italic; font-size: 11pt; line-height: 1.55; }}
  .medal {{ position: absolute; left: 50%; bottom: 9mm; transform: translateX(-50%);
         width: 15mm; height: 15mm; border-radius: 50%; background: #d5ad57;
         border: 1mm solid #9b741e; box-shadow: 0 0 0 0.7mm #c69a45, inset 0 0 0 0.8mm #f5dda1;
         display: flex; align-items: center; justify-content: center; color: #173f87;
         font-family: Georgia, serif; font-size: 24pt; z-index: 4; }}
  .medal::before {{ content: ""; position: absolute; width: 5mm; height: 12mm;
         background: #173f87; left: 2.5mm; bottom: -8mm; transform: rotate(7deg); z-index: -1; }}
  .medal::after {{ content: ""; position: absolute; width: 5mm; height: 12mm;
         background: #173f87; right: 2.5mm; bottom: -8mm; transform: rotate(-7deg); z-index: -1; }}
  .date {{ position: absolute; left: 50%; bottom: -8.5mm; transform: translateX(-50%);
         min-width: 45mm; height: 10mm; background: #fffdf7; border: 0.8mm double #b88a32;
         display: flex; align-items: center; justify-content: center; color: #173f87;
         font-family: Georgia, serif; font-weight: bold; font-size: 10pt; z-index: 5; }}
  .corner {{ position: absolute; width: 13mm; height: 13mm; border: 1.1mm solid #c69a45;
         transform: rotate(45deg); background: #173f87; z-index: 3; }}
  .c1 {{ left: 6mm; top: 6mm; }} .c2 {{ right: 6mm; top: 6mm; }}
  .c3 {{ left: 6mm; bottom: 6mm; }} .c4 {{ right: 6mm; bottom: 6mm; }}
  .gold-node {{ position: absolute; width: 4.5mm; height: 4.5mm; border-radius: 50%;
         background: #c69a45; border: 0.5mm solid #173f87; z-index: 4;
         box-shadow: 0 0 0 0.6mm #d5ad57; }}
  .n1 {{ left: 19mm; top: 3mm; }} .n2 {{ right: 19mm; top: 3mm; }}
  .n3 {{ left: 19mm; bottom: 3mm; }} .n4 {{ right: 19mm; bottom: 3mm; }}
  @media print {{ body {{ background: none; padding: 0; display: block; }} .toolbar {{ display: none; }}
         .page {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }} }}
</style></head>
<body>
  <div class="toolbar"><button onclick="window.print()">Print / Save as PDF</button></div>
  <div class="page">
    <div class="corner c1"></div><div class="corner c2"></div>
    <div class="corner c3"></div><div class="corner c4"></div>
    <div class="gold-node n1"></div><div class="gold-node n2"></div>
    <div class="gold-node n3"></div><div class="gold-node n4"></div>
    <div class="blue-band top"></div><div class="blue-band bottom"></div>
    <div class="side side-left"></div><div class="side side-right"></div>
    <div class="inner">
    <div class="brand">ICT QUIZ MASTER</div>
    <h1>{c['title']}</h1>
    <h2>{c['sub']}</h2>
    <p class="lead">This certificate is proudly presented to</p>
    <div class="name">{c['name']}</div>
    <p class="msg">{c['message']}</p>
    <div class="medal">★<div class="date">{c['date']}</div></div>
  </div>
  </div>
</body></html>
"""
