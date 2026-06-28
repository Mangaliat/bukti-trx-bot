from PIL import Image, ImageDraw, ImageFont
import os
import uuid
from datetime import datetime

# =============================================
TEMPLATE_PATH = "template.png"
OUTPUT_FOLDER = "output"

FONT_LEAGUE_SPARTAN_BOLD    = "font/Arimo/League_Spartan/static/LeagueSpartan-Bold.ttf"
FONT_LEAGUE_SPARTAN_REGULAR = "font/Arimo/League_Spartan/static/LeagueSpartan-Regular.ttf"
FONT_ARIMO                  = "font/Arimo/Arimo/Arimo-VariableFont_wght.ttf"

# --- NOMINAL ---
NOMINAL_X         = 73
NOMINAL_Y         = 679
NOMINAL_FONT_SIZE = 52
NOMINAL_WARNA     = "#000000"
NOMINAL_ALIGN     = "left"

# --- JAM ATAS ---
JAM_ATAS_X         = 45
JAM_ATAS_Y         = 23
JAM_ATAS_FONT_SIZE = 32
JAM_ATAS_WARNA     = "#000000"
JAM_ATAS_ALIGN     = "left"

# --- JAM BAWAH ---
JAM_BAWAH_X         = 597
JAM_BAWAH_Y         = 777
JAM_BAWAH_FONT_SIZE = 25
JAM_BAWAH_WARNA     = "#000000"
JAM_BAWAH_ALIGN     = "left"

# --- TANGGAL ---
TANGGAL_X         = 74
TANGGAL_Y         = 777
TANGGAL_FONT_SIZE = 24
TANGGAL_WARNA     = "#000000"
TANGGAL_ALIGN     = "left"
# =============================================

BULAN_ID = {
    "January": "Januari", "February": "Februari", "March": "Maret",
    "April": "April", "May": "Mei", "June": "Juni",
    "July": "Juli", "August": "Agustus", "September": "September",
    "October": "Oktober", "November": "November", "December": "Desember"
}

def format_tanggal(dt: datetime) -> str:
    hari = dt.strftime("%A")
    tanggal = int(dt.strftime("%d"))
    bulan = BULAN_ID[dt.strftime("%B")]
    tahun = dt.strftime("%Y")
    return f"{hari}, {tanggal} {bulan} {tahun}"

def _load_font(path: str, ukuran: int):
    try:
        return ImageFont.truetype(path, ukuran)
    except Exception as e:
        print(f"⚠️ Font tidak ditemukan: {path} — Error: {e}")
        return ImageFont.load_default()

def _tulis_teks(draw, teks, x, y, font, warna, align):
    anchor_map = {"left": "la", "center": "ma", "right": "ra"}
    anchor = anchor_map.get(align, "la")
    draw.text((x, y), teks, font=font, fill=warna, anchor=anchor)

def buat_gambar(nominal: str, jam: str, tanggal: str) -> str:
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Template '{TEMPLATE_PATH}' tidak ditemukan!")

    img = Image.open(TEMPLATE_PATH).convert("RGBA")
    draw = ImageDraw.Draw(img)

    font_nominal   = _load_font(FONT_LEAGUE_SPARTAN_BOLD, NOMINAL_FONT_SIZE)      # Bold
    font_jam_atas  = _load_font(FONT_LEAGUE_SPARTAN_BOLD, JAM_ATAS_FONT_SIZE)     # Bold
    font_jam_bawah = _load_font(FONT_LEAGUE_SPARTAN_REGULAR, JAM_BAWAH_FONT_SIZE) # Regular
    font_tanggal   = _load_font(FONT_ARIMO, TANGGAL_FONT_SIZE)                    # Arimo

    _tulis_teks(draw, f"Rp{nominal}", NOMINAL_X, NOMINAL_Y,
                font_nominal, NOMINAL_WARNA, NOMINAL_ALIGN)

    _tulis_teks(draw, jam, JAM_ATAS_X, JAM_ATAS_Y,
                font_jam_atas, JAM_ATAS_WARNA, JAM_ATAS_ALIGN)

    _tulis_teks(draw, jam, JAM_BAWAH_X, JAM_BAWAH_Y,
                font_jam_bawah, JAM_BAWAH_WARNA, JAM_BAWAH_ALIGN)

    _tulis_teks(draw, tanggal, TANGGAL_X, TANGGAL_Y,
                font_tanggal, TANGGAL_WARNA, TANGGAL_ALIGN)

    nama_file = f"{OUTPUT_FOLDER}/hasil_{uuid.uuid4().hex[:8]}.png"
    img.save(nama_file, "PNG")
    return nama_file