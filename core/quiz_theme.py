"""Colours and constants used by every screen.

Theme (taken from the reference website): deep charcoal background, lime-yellow
for the main actions, purple for accents and teal-green for correct answers.
Change a colour here and the whole application changes with it.
"""

# ───────────────────────── Theme ─────────────────────────
# Backgrounds (dark)
BG = "#0f1115"            # window background (deep charcoal)
SURFACE = "#181b22"       # cards and panels
SURFACE_2 = "#222632"     # raised items: hover rows, chips
BORDER = "#2f3442"        # thin borders, empty bars, disabled buttons

# Lime (main action colour, like the "let's talk" button)
LIME = "#d6f55b"
LIME_HOVER = "#e6ff7a"
LIME_PRESS = "#b9d63f"
LIME_DARK = "#2a3410"     # dark lime tint: soft backgrounds

# Purple (accent colour, like the "fintech development" button)
PURPLE = "#8b5cf6"
PURPLE_HOVER = "#a07bff"
PURPLE_PRESS = "#6d3fe0"
PURPLE_SOFT = "#2a2145"   # dark purple tint: selected / hover backgrounds

# Teal-green (correct answers and success)
TEAL = "#19c3a0"
TEAL_HOVER = "#3fe0bd"
TEAL_SOFT = "#0f2f2b"
TEAL_EDGE = "#1f8f7a"

# Text colours
WHITE = "#ffffff"         # text on coloured buttons and pictures
INK = "#f3f4f6"           # main text (almost white)
INK_ON_LIME = "#12150a"   # dark text on lime buttons (high contrast)
MUTED = "#9aa1b2"         # secondary text

# Warning colours
RED = "#ff5d6c"
RED_SOFT = "#34161b"
RED_EDGE = "#a63a46"
AMBER = "#ffb020"
ORANGE = "#ff9a3c"
ORANGE_SOFT = "#35230f"

# ── Old names, kept so every screen still works ──
PINK, PINK_HOVER, BLUSH = PURPLE, PURPLE_HOVER, PURPLE_SOFT
GREY = BORDER
GREEN, GREEN_HOVER = TEAL, TEAL_HOVER
MINT, MINT_EDGE, DARK_GREEN = TEAL_SOFT, TEAL_EDGE, TEAL
RED_LIGHT, DARK_RED = RED_SOFT, RED
ORANGE_LIGHT = ORANGE_SOFT

FONT = "Segoe UI"
LEVEL_COLOR = {"Easy": TEAL, "Medium": AMBER, "Hard": RED}

TIME_LIMIT = 20   # seconds per question
# Each sound is a list of (frequency in Hz, length in ms). They are turned into small WAV files.
SOUNDS = {"ok": [(784, 90), (988, 90), (1319, 160)],          # correct: three rising notes
          "bad": [(330, 160), (247, 280)],                      # wrong / time up: two falling notes
          "streak": [(784, 80), (988, 80), (1319, 80), (1568, 220)],   # streak bonus / quiz passed
          "fail": [(392, 160), (330, 160), (262, 320)],         # quiz finished without passing
          "click": [(660, 35)],                                 # choosing an answer
          "tick": [(1000, 40)]}                                 # last 5 seconds of the timer
