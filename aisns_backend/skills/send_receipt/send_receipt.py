"""
Send Receipt Skill (stdlib-only)

Generates a receipt PNG image from structured parameters using only the
Python standard library (no Pillow / numpy / etc.). The output is a
base64-encoded PNG.

Input (stdin JSON):
  payer   - Name of the payer (required)
  payee   - Name of the payee (required)
  content - Description of goods or service (required)
  amount  - Payment amount, number or string (required)
  date    - Transaction date string (optional, default: today)

Output (stdout JSON):
  ok           - bool
  image_base64 - base64-encoded PNG data
  error        - Error message on failure
"""

import base64
import io
import json
import re
import struct
import sys
import zlib
from datetime import datetime


# ---------------------------------------------------------------------------
# Number-to-words converter (handles up to 999,999,999.99)
# ---------------------------------------------------------------------------

_ONES = [
    "", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen",
]
_TENS = [
    "", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety",
]


def _int_to_words(n: int) -> str:
    if n == 0:
        return "zero"
    if n < 0:
        return "negative " + _int_to_words(-n)

    parts = []
    if n >= 1_000_000:
        parts.append(_int_to_words(n // 1_000_000) + " million")
        n %= 1_000_000
    if n >= 1_000:
        parts.append(_int_to_words(n // 1_000) + " thousand")
        n %= 1_000
    if n >= 100:
        parts.append(_ONES[n // 100] + " hundred")
        n %= 100
    if n >= 20:
        parts.append(_TENS[n // 10])
        n %= 10
    if 1 <= n <= 19:
        parts.append(_ONES[n])
    return " ".join(parts)


def _amount_to_words(amount: float) -> str:
    dollars = int(amount)
    cents = round((amount - dollars) * 100)
    words = _int_to_words(dollars).capitalize()
    if cents:
        words += f" and {cents}/100"
    words += " dollars only"
    return words


# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph = 7 rows, each row a 5-bit pattern (LSB right).
# Covers printable ASCII needed for receipts. Unknown chars render as blank.
# ---------------------------------------------------------------------------

# Each row uses bits 4..0 (left-to-right). For example 0b11111 = 5 lit pixels.
FONT = {
    ' ': [0, 0, 0, 0, 0, 0, 0],
    '!': [0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100],
    '"': [0b01010, 0b01010, 0, 0, 0, 0, 0],
    '#': [0b01010, 0b11111, 0b01010, 0b01010, 0b11111, 0b01010, 0b00000],
    '$': [0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100],
    '%': [0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011],
    '&': [0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101],
    "'": [0b00100, 0b00100, 0, 0, 0, 0, 0],
    '(': [0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010],
    ')': [0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000],
    '*': [0, 0b10101, 0b01110, 0b11111, 0b01110, 0b10101, 0],
    '+': [0, 0, 0b00100, 0b11111, 0b00100, 0, 0],
    ',': [0, 0, 0, 0, 0, 0b00100, 0b01000],
    '-': [0, 0, 0, 0b11111, 0, 0, 0],
    '.': [0, 0, 0, 0, 0, 0b00100, 0b00100],
    '/': [0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000],
    '0': [0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110],
    '1': [0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
    '2': [0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0b01000, 0b11111],
    '3': [0b11110, 0b00001, 0b00001, 0b01110, 0b00001, 0b00001, 0b11110],
    '4': [0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010],
    '5': [0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110],
    '6': [0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110],
    '7': [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000],
    '8': [0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110],
    '9': [0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100],
    ':': [0, 0b00100, 0b00100, 0, 0b00100, 0b00100, 0],
    ';': [0, 0b00100, 0b00100, 0, 0b00100, 0b00100, 0b01000],
    '<': [0b00010, 0b00100, 0b01000, 0b10000, 0b01000, 0b00100, 0b00010],
    '=': [0, 0, 0b11111, 0, 0b11111, 0, 0],
    '>': [0b01000, 0b00100, 0b00010, 0b00001, 0b00010, 0b00100, 0b01000],
    '?': [0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0, 0b00100],
    '@': [0b01110, 0b10001, 0b10111, 0b10101, 0b10111, 0b10000, 0b01110],
    'A': [0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
    'B': [0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110],
    'C': [0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110],
    'D': [0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110],
    'E': [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111],
    'F': [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000],
    'G': [0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01110],
    'H': [0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
    'I': [0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
    'J': [0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100],
    'K': [0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001],
    'L': [0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111],
    'M': [0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001],
    'N': [0b10001, 0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001],
    'O': [0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    'P': [0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000],
    'Q': [0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101],
    'R': [0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001],
    'S': [0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110],
    'T': [0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
    'U': [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    'V': [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100],
    'W': [0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b10101, 0b01010],
    'X': [0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001],
    'Y': [0b10001, 0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100],
    'Z': [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111],
    '[': [0b01110, 0b01000, 0b01000, 0b01000, 0b01000, 0b01000, 0b01110],
    '\\': [0b10000, 0b01000, 0b01000, 0b00100, 0b00010, 0b00010, 0b00001],
    ']': [0b01110, 0b00010, 0b00010, 0b00010, 0b00010, 0b00010, 0b01110],
    '^': [0b00100, 0b01010, 0b10001, 0, 0, 0, 0],
    '_': [0, 0, 0, 0, 0, 0, 0b11111],
    '`': [0b01000, 0b00100, 0, 0, 0, 0, 0],
    'a': [0, 0, 0b01110, 0b00001, 0b01111, 0b10001, 0b01111],
    'b': [0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b10001, 0b11110],
    'c': [0, 0, 0b01110, 0b10000, 0b10000, 0b10001, 0b01110],
    'd': [0b00001, 0b00001, 0b01111, 0b10001, 0b10001, 0b10001, 0b01111],
    'e': [0, 0, 0b01110, 0b10001, 0b11111, 0b10000, 0b01110],
    'f': [0b00110, 0b01001, 0b01000, 0b11110, 0b01000, 0b01000, 0b01000],
    'g': [0, 0b01111, 0b10001, 0b10001, 0b01111, 0b00001, 0b01110],
    'h': [0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b10001, 0b10001],
    'i': [0b00100, 0, 0b01100, 0b00100, 0b00100, 0b00100, 0b01110],
    'j': [0b00010, 0, 0b00110, 0b00010, 0b00010, 0b10010, 0b01100],
    'k': [0b10000, 0b10000, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010],
    'l': [0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
    'm': [0, 0, 0b11010, 0b10101, 0b10101, 0b10001, 0b10001],
    'n': [0, 0, 0b11110, 0b10001, 0b10001, 0b10001, 0b10001],
    'o': [0, 0, 0b01110, 0b10001, 0b10001, 0b10001, 0b01110],
    'p': [0, 0, 0b11110, 0b10001, 0b11110, 0b10000, 0b10000],
    'q': [0, 0, 0b01111, 0b10001, 0b01111, 0b00001, 0b00001],
    'r': [0, 0, 0b10110, 0b11000, 0b10000, 0b10000, 0b10000],
    's': [0, 0, 0b01111, 0b10000, 0b01110, 0b00001, 0b11110],
    't': [0b01000, 0b01000, 0b11110, 0b01000, 0b01000, 0b01001, 0b00110],
    'u': [0, 0, 0b10001, 0b10001, 0b10001, 0b10001, 0b01111],
    'v': [0, 0, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100],
    'w': [0, 0, 0b10001, 0b10001, 0b10101, 0b10101, 0b01010],
    'x': [0, 0, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001],
    'y': [0, 0b10001, 0b10001, 0b10001, 0b01111, 0b00001, 0b01110],
    'z': [0, 0, 0b11111, 0b00010, 0b00100, 0b01000, 0b11111],
}

GLYPH_W = 5
GLYPH_H = 7
CHAR_GAP = 1  # spacing between characters, in unscaled pixels


# ---------------------------------------------------------------------------
# Pure-stdlib raster canvas (RGB, 8-bit per channel)
# ---------------------------------------------------------------------------

class Canvas:
    __slots__ = ("w", "h", "buf")

    def __init__(self, width: int, height: int, bg=(255, 255, 255)):
        self.w = width
        self.h = height
        # Pre-fill with background color
        row = bytes(bg) * width
        self.buf = bytearray(row * height)

    def set_px(self, x: int, y: int, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = color[0]
            self.buf[i + 1] = color[1]
            self.buf[i + 2] = color[2]

    def fill_rect(self, x1: int, y1: int, x2: int, y2: int, color):
        if x2 < x1:
            x1, x2 = x2, x1
        if y2 < y1:
            y1, y2 = y2, y1
        for y in range(max(0, y1), min(self.h, y2)):
            for x in range(max(0, x1), min(self.w, x2)):
                i = (y * self.w + x) * 3
                self.buf[i] = color[0]
                self.buf[i + 1] = color[1]
                self.buf[i + 2] = color[2]

    def hline(self, x1: int, x2: int, y: int, color, thickness: int = 2):
        self.fill_rect(x1, y, x2, y + thickness, color)

    def draw_char(self, x: int, y: int, ch: str, scale: int, color):
        glyph = FONT.get(ch)
        if glyph is None:
            # Unknown char: leave a blank slot
            return
        for row_idx in range(GLYPH_H):
            bits = glyph[row_idx]
            if not bits:
                continue
            for col_idx in range(GLYPH_W):
                if bits & (1 << (GLYPH_W - 1 - col_idx)):
                    px = x + col_idx * scale
                    py = y + row_idx * scale
                    self.fill_rect(px, py, px + scale, py + scale, color)

    def draw_text(self, x: int, y: int, text: str, scale: int = 2, color=(0, 0, 0)):
        cx = x
        step = (GLYPH_W + CHAR_GAP) * scale
        for ch in text:
            self.draw_char(cx, y, ch, scale, color)
            cx += step
        return cx


def text_width(text: str, scale: int) -> int:
    if not text:
        return 0
    # n chars * (5+1) per char, but the last gap is unnecessary -> subtract gap
    return len(text) * (GLYPH_W + CHAR_GAP) * scale - CHAR_GAP * scale


# ---------------------------------------------------------------------------
# PNG encoder (stdlib only)
# ---------------------------------------------------------------------------

def encode_png(canvas: Canvas) -> bytes:
    """Encode an RGB canvas as a PNG byte stream."""
    sig = b"\x89PNG\r\n\x1a\n"

    def chunk(tag: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    # IHDR: width, height, bit depth=8, color type=2 (RGB), compression=0,
    # filter=0, interlace=0
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)

    # IDAT: each scanline prefixed with filter byte 0 (None)
    stride = canvas.w * 3
    raw = io.BytesIO()
    for y in range(canvas.h):
        raw.write(b"\x00")
        raw.write(bytes(canvas.buf[y * stride:(y + 1) * stride]))
    idat = zlib.compress(raw.getvalue(), 9)

    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


# ---------------------------------------------------------------------------
# Receipt rendering
# ---------------------------------------------------------------------------

def _parse_amount(raw) -> float:
    if isinstance(raw, (int, float)):
        return float(raw)
    cleaned = re.sub(r"[^\d.]", "", str(raw))
    return float(cleaned) if cleaned else 0.0


def _format_amount(val: float) -> str:
    return f"${val:,.2f}"


def _wrap_text(text: str, max_chars: int):
    """Word-wrap into lines of at most max_chars characters."""
    if max_chars <= 0:
        return [text]
    lines = []
    current = ""
    for word in text.split():
        candidate = (current + " " + word).strip() if current else word
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                lines.append(current)
            # Hard-break a single word that is longer than max_chars
            while len(word) > max_chars:
                lines.append(word[:max_chars])
                word = word[max_chars:]
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def generate_receipt_png(
    payer: str,
    payee: str,
    content: str,
    amount: float,
    date_str: str,
) -> bytes:
    """Render the receipt and return PNG bytes."""
    # Layout (all in unscaled px)
    width = 900
    pad_x = 40

    title_scale = 6   # "RECEIPT" -> 30x42 per char
    body_scale = 3    # 15x21 per char
    line_h = (GLYPH_H + 2) * body_scale  # ~27 px

    # How many body characters fit between value column and right margin.
    # Width is sized so that the longest label ("For (Description):" -> 18
    # chars at body_scale=3, ~324 px) fits comfortably in the label column.
    value_x = pad_x + 340
    body_step = (GLYPH_W + CHAR_GAP) * body_scale
    max_value_chars = max(10, (width - value_x - pad_x) // body_step)

    fields = [
        ("From (Payer):", payer),
        ("To (Payee):", payee),
        ("For (Description):", content),
        ("Amount:", f"{_format_amount(amount)} ({_amount_to_words(amount)})"),
        ("Date:", date_str),
    ]

    # Pre-wrap each value to know total height
    wrapped = [(label, _wrap_text(value, max_value_chars)) for label, value in fields]

    row_padding = 18  # extra vertical padding per row
    rows_height = sum(max(line_h, line_h * len(lines)) + row_padding
                      for _, lines in wrapped)

    title_h = GLYPH_H * title_scale
    top_margin = 30
    bottom_margin = 30
    height = top_margin + title_h + 30 + rows_height + bottom_margin

    canvas = Canvas(width, height)
    black = (0, 0, 0)
    line_color = (40, 40, 40)

    # Title "RECEIPT" centered
    title = "RECEIPT"
    title_w = text_width(title, title_scale)
    canvas.draw_text((width - title_w) // 2, top_margin, title, title_scale, black)

    # "AI" tag in top-right
    ai_text = "AI"
    ai_scale = 5
    ai_w = text_width(ai_text, ai_scale)
    canvas.draw_text(width - pad_x - ai_w, top_margin + 4, ai_text, ai_scale, black)

    # Field rows
    y = top_margin + title_h + 30
    for label, value_lines in wrapped:
        # Label
        canvas.draw_text(pad_x, y + 4, label, body_scale, black)
        # Value (possibly multi-line)
        for i, line in enumerate(value_lines):
            canvas.draw_text(value_x, y + 4 + i * line_h, line, body_scale, black)
        # Compute row height taken
        used = max(line_h, line_h * len(value_lines))
        # Separator line at the bottom of the row
        sep_y = y + used + 8
        canvas.hline(pad_x, width - pad_x, sep_y, line_color, thickness=2)
        y += used + row_padding

    return encode_png(canvas)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    try:
        raw = sys.stdin.read().strip()
        if not raw:
            _emit(False, error="No input provided")
            return
        params = json.loads(raw)
    except json.JSONDecodeError as e:
        _emit(False, error=f"Invalid JSON input: {e}")
        return

    if not isinstance(params, dict):
        _emit(False, error="Input JSON must be an object")
        return

    # The LLM sometimes wraps the real arguments under a "params" key
    # (e.g. {"skill_key": "...", "params": {"payer": ...}}). Unwrap that
    # so callers can pass arguments either flat or nested.
    if isinstance(params, dict) and isinstance(params.get("params"), dict):
        inner = dict(params["params"])
        # Preserve any sibling fields that aren't shadowed by inner keys
        for k, v in params.items():
            if k != "params" and k not in inner:
                inner[k] = v
        params = inner

    payer = (params.get("payer") or "").strip()
    payee = (params.get("payee") or "").strip()
    content = (params.get("content") or "").strip()
    amount_raw = params.get("amount")
    date_str = (params.get("date") or "").strip()

    if not payer:
        _emit(False, error="'payer' is required")
        return
    if not payee:
        _emit(False, error="'payee' is required")
        return
    if not content:
        _emit(False, error="'content' is required")
        return
    if amount_raw is None or amount_raw == "":
        _emit(False, error="'amount' is required")
        return

    try:
        amount = _parse_amount(amount_raw)
    except (ValueError, TypeError):
        _emit(False, error=f"Invalid amount value: {amount_raw}")
        return

    if not date_str:
        date_str = datetime.now().strftime("%B %d, %Y")

    try:
        png_bytes = generate_receipt_png(payer, payee, content, amount, date_str)
    except Exception as e:
        _emit(False, error=f"Image generation failed: {e}")
        return

    b64 = base64.b64encode(png_bytes).decode("ascii")
    print(json.dumps({"ok": True, "image_base64": b64}, ensure_ascii=False))


def _emit(ok: bool, error: str = ""):
    out = {"ok": ok}
    if error:
        out["error"] = error
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
