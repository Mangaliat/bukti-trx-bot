# 🤖 Bot Telegram - Kirim Struk Otomatis

Bot ini membaca nominal seperti `Rp 750.000`, mengedit template PNG,
lalu mengirim gambar 2 menit kemudian dengan jam & tanggal otomatis.

---

## 📁 Struktur File

```
telegram-bot/
├── bot.py              ← File utama bot
├── image_editor.py     ← Editor gambar (atur posisi teks di sini)
├── cek_koordinat.py    ← Alat bantu cari posisi x,y di template
├── requirements.txt    ← Daftar library
├── template.png        ← ⬅️ TARUH TEMPLATE CANVA KAMU DI SINI
└── output/             ← Folder otomatis untuk hasil gambar
```

---

## 🚀 Cara Setup

### 1. Install Python
Download Python 3.11+ dari https://python.org

### 2. Install library
Buka terminal/CMD di folder ini, lalu jalankan:
```bash
pip install -r requirements.txt
```

### 3. Buat Bot Telegram
- Buka Telegram, cari `@BotFather`
- Ketik `/newbot` dan ikuti instruksinya
- Salin **token** yang diberikan

### 4. Isi Token
Buka `bot.py`, cari baris ini:
```python
BOT_TOKEN = "ISI_TOKEN_BOT_KAMU_DI_SINI"
```
Ganti dengan token dari BotFather.

### 5. Siapkan Template
- Export design Canva kamu sebagai **PNG**
- Rename menjadi `template.png`
- Taruh di folder yang sama dengan `bot.py`

### 6. Sesuaikan Posisi Teks
Jalankan alat bantu koordinat:
```bash
python cek_koordinat.py
```
- Klik pada area **nominal** di gambar → catat koordinat x, y
- Klik pada area **jam** → catat koordinat
- Klik pada area **tanggal** → catat koordinat

Lalu buka `image_editor.py` dan isi nilai yang sesuai:
```python
NOMINAL_X = 400   # Ganti dengan x dari klik
NOMINAL_Y = 300   # Ganti dengan y dari klik

JAM_X = 400
JAM_Y = 420

TANGGAL_X = 400
TANGGAL_Y = 490
```

### 7. (Opsional) Custom Font
Jika kamu punya file font (.ttf), taruh di folder `font/` lalu atur:
```python
FONT_PATH = "font/NamaFont.ttf"
```

### 8. Jalankan Bot
```bash
python bot.py
```

---

## 💬 Cara Pakai Bot

Kirim pesan ke bot kamu di Telegram:
```
Rp 750.000
```
Bot akan membalas konfirmasi, lalu **2 menit kemudian** mengirim gambar 
hasil edit dengan nominal, jam, dan tanggal.

Format yang didukung:
- `Rp 750.000`
- `Rp750000`
- `rp 1.500.000`
- `1500000`

---

## ❓ Troubleshooting

**Bot tidak merespons?**
→ Pastikan token benar dan bot sedang berjalan (`python bot.py`)

**Gambar teks posisinya salah?**
→ Gunakan `cek_koordinat.py` untuk mencari posisi yang tepat

**Error "template.png tidak ditemukan"?**
→ Pastikan file template ada di folder yang sama dengan bot.py
