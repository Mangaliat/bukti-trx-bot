import logging
import re
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, MessageHandler, CommandHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from image_editor import buat_gambar, format_tanggal
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# =============================================
BOT_TOKEN = "8991685406:AAEJpyiHlxStNlCcP0kA4IWmFngHCYEZZGU"
SPREADSHEET_NAME = "Bukti Transaksi"
CREDENTIALS_FILE = "credentials.json"
# =============================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =============================================
# GOOGLE SHEETS
# =============================================
def get_sheet(nama):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open(SPREADSHEET_NAME)
    try:
        return spreadsheet.worksheet(nama)
    except:
        sheet = spreadsheet.add_worksheet(title=nama, rows=1000, cols=10)
        return sheet

def init_sheet():
    # Sheet Pemasukan
    sheet_masuk = get_sheet("Pemasukan")
    if sheet_masuk.cell(1, 1).value != "Tanggal":
        sheet_masuk.insert_row(["Tanggal", "Waktu", "Jumlah (Rp)", "Bank", "Pengirim", "Dicatat Oleh"], 1)

    # Sheet Pengeluaran
    sheet_keluar = get_sheet("Pengeluaran")
    if sheet_keluar.cell(1, 1).value != "Tanggal":
        sheet_keluar.insert_row(["Tanggal", "Waktu", "Jumlah (Rp)", "Kategori", "Keterangan", "Dicatat Oleh"], 1)

# =============================================
# MENU UTAMA
# =============================================
def menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📸 Buat Bukti TF", callback_data="bukti_tf"),
        ],
        [
            InlineKeyboardButton("💰 Catat Pemasukan", callback_data="catat_masuk"),
            InlineKeyboardButton("💸 Catat Pengeluaran", callback_data="catat_keluar"),
        ],
        [
            InlineKeyboardButton("📊 Rekap Keuangan", callback_data="rekap")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def tombol_menu():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🔙 Menu Utama", callback_data="menu")
    ]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Halo! Selamat datang.\nPilih menu di bawah ini:",
        reply_markup=menu_keyboard()
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Pilih menu:",
        reply_markup=menu_keyboard()
    )

# =============================================
# CALLBACK HANDLER
# =============================================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "menu":
        await query.message.reply_text("📌 Pilih menu:", reply_markup=menu_keyboard())

    elif query.data == "bukti_tf":
        context.user_data["mode"] = "bukti_tf"
        await query.message.reply_text(
            "📸 *Buat Bukti TF*\n\nKirim nominal transfer:\nContoh: Rp 550.000",
            parse_mode="Markdown"
        )

    elif query.data == "catat_masuk":
        context.user_data["mode"] = "catat_masuk"
        context.user_data["step"] = "jumlah"
        await query.message.reply_text(
            "💰 *Catat Pemasukan*\n\nMasukkan jumlah yang diterima:\nContoh: 550000",
            parse_mode="Markdown"
        )

    elif query.data == "catat_keluar":
        context.user_data["mode"] = "catat_keluar"
        context.user_data["step"] = "jumlah"
        await query.message.reply_text(
            "💸 *Catat Pengeluaran*\n\nMasukkan jumlah pengeluaran:\nContoh: 150000",
            parse_mode="Markdown"
        )

    elif query.data == "rekap":
        await tampilkan_rekap(query.message)

    elif query.data.startswith("bank_"):
        bank = query.data.replace("bank_", "")
        context.user_data["bank"] = bank
        context.user_data["step"] = "penerima"
        await query.message.reply_text(f"✅ Bank: {bank}\n\n👤 Nama pengirim/customer:")

    elif query.data.startswith("kategori_"):
        kategori = query.data.replace("kategori_", "")
        context.user_data["kategori"] = kategori
        context.user_data["step"] = "keterangan"
        await query.message.reply_text(f"✅ Kategori: {kategori}\n\n📝 Keterangan pengeluaran (contoh: Beli pulsa, Makan siang):")

# =============================================
# HANDLER PESAN TEKS
# =============================================
def parse_nominal(teks: str):
    teks_bersih = teks.upper().replace("RP", "").strip()
    hanya_angka = re.sub(r"[^\d.,]", "", teks_bersih)
    if not hanya_angka:
        return None
    return hanya_angka

async def handle_pesan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teks = update.message.text.strip()
    mode = context.user_data.get("mode")
    step = context.user_data.get("step")

    # ---- BUKTI TF ----
    if mode == "bukti_tf":
        nominal = parse_nominal(teks)
        if nominal is None:
            await update.message.reply_text("❌ Format tidak dikenali.\nContoh: Rp 550.000")
            return
        waktu = datetime.now() + timedelta(minutes=2)
        jam_str = waktu.strftime("%H:%M")
        tanggal_str = format_tanggal(waktu)
        path_gambar = buat_gambar(nominal=nominal, jam=jam_str, tanggal=tanggal_str)
        with open(path_gambar, "rb") as f:
            await update.message.reply_photo(
                photo=f,
                caption=f"✅ *Rp {nominal}*",
                parse_mode="Markdown",
                reply_markup=tombol_menu()
            )
        context.user_data["mode"] = None

    # ---- CATAT PEMASUKAN ----
    elif mode == "catat_masuk":
        if step == "jumlah":
            angka = teks.replace(".", "").replace(",", "")
            if not angka.isdigit():
                await update.message.reply_text("❌ Masukkan angka saja. Contoh: 550000")
                return
            context.user_data["jumlah"] = int(angka)
            context.user_data["step"] = "bank"
            keyboard = [
                [InlineKeyboardButton("SeaBank", callback_data="bank_SeaBank"),
                 InlineKeyboardButton("BCA", callback_data="bank_BCA"),
                 InlineKeyboardButton("BRI", callback_data="bank_BRI")],
                [InlineKeyboardButton("Mandiri", callback_data="bank_Mandiri"),
                 InlineKeyboardButton("BNI", callback_data="bank_BNI"),
                 InlineKeyboardButton("DANA", callback_data="bank_DANA")],
                [InlineKeyboardButton("OVO", callback_data="bank_OVO"),
                 InlineKeyboardButton("GoPay", callback_data="bank_GoPay"),
                 InlineKeyboardButton("Lainnya", callback_data="bank_Lainnya")]
            ]
            await update.message.reply_text(
                "🏦 Transfer dari bank apa?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif step == "penerima":
            pengirim = teks
            jumlah = context.user_data["jumlah"]
            bank = context.user_data["bank"]
            user = update.message.from_user.first_name
            now = datetime.now()
            tanggal = now.strftime("%d/%m/%Y")
            waktu = now.strftime("%H:%M")
            try:
                sheet = get_sheet("Pemasukan")
                sheet.append_row([tanggal, waktu, jumlah, bank, pengirim, user])
                await update.message.reply_text(
                    f"✅ *Pemasukan Dicatat!*\n\n"
                    f"📅 {tanggal} {waktu}\n"
                    f"💰 Rp{jumlah:,}\n"
                    f"🏦 {bank}\n"
                    f"👤 {pengirim}",
                    parse_mode="Markdown",
                    reply_markup=tombol_menu()
                )
            except Exception as e:
                await update.message.reply_text(f"❌ Gagal simpan: {e}")
            context.user_data.clear()

    # ---- CATAT PENGELUARAN ----
    elif mode == "catat_keluar":
        if step == "jumlah":
            angka = teks.replace(".", "").replace(",", "")
            if not angka.isdigit():
                await update.message.reply_text("❌ Masukkan angka saja. Contoh: 150000")
                return
            context.user_data["jumlah"] = int(angka)
            context.user_data["step"] = "kategori"
            keyboard = [
                [InlineKeyboardButton("🍔 Makan & Minum", callback_data="kategori_Makan & Minum"),
                 InlineKeyboardButton("🚗 Transport", callback_data="kategori_Transport")],
                [InlineKeyboardButton("🛒 Belanja", callback_data="kategori_Belanja"),
                 InlineKeyboardButton("💡 Tagihan", callback_data="kategori_Tagihan")],
                [InlineKeyboardButton("📦 Operasional", callback_data="kategori_Operasional"),
                 InlineKeyboardButton("📝 Lainnya", callback_data="kategori_Lainnya")]
            ]
            await update.message.reply_text(
                "📂 Pilih kategori pengeluaran:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif step == "keterangan":
            keterangan = teks
            jumlah = context.user_data["jumlah"]
            kategori = context.user_data["kategori"]
            user = update.message.from_user.first_name
            now = datetime.now()
            tanggal = now.strftime("%d/%m/%Y")
            waktu = now.strftime("%H:%M")
            try:
                sheet = get_sheet("Pengeluaran")
                sheet.append_row([tanggal, waktu, jumlah, kategori, keterangan, user])
                await update.message.reply_text(
                    f"✅ *Pengeluaran Dicatat!*\n\n"
                    f"📅 {tanggal} {waktu}\n"
                    f"💸 Rp{jumlah:,}\n"
                    f"📂 {kategori}\n"
                    f"📝 {keterangan}",
                    parse_mode="Markdown",
                    reply_markup=tombol_menu()
                )
            except Exception as e:
                await update.message.reply_text(f"❌ Gagal simpan: {e}")
            context.user_data.clear()

    # ---- TIDAK ADA MODE ----
    else:
        await update.message.reply_text("📌 Pilih menu:", reply_markup=menu_keyboard())

# =============================================
# REKAP
# =============================================
async def tampilkan_rekap(message):
    try:
        # Pemasukan
        sheet_masuk = get_sheet("Pemasukan")
        data_masuk = sheet_masuk.get_all_records()
        total_masuk = sum(int(r["Jumlah (Rp)"]) for r in data_masuk if str(r["Jumlah (Rp)"]).isdigit())

        # Pengeluaran
        sheet_keluar = get_sheet("Pengeluaran")
        data_keluar = sheet_keluar.get_all_records()
        total_keluar = sum(int(r["Jumlah (Rp)"]) for r in data_keluar if str(r["Jumlah (Rp)"]).isdigit())

        saldo = total_masuk - total_keluar

        # 3 pemasukan terakhir
        detail_masuk = ""
        for r in reversed(data_masuk[-3:]):
            detail_masuk += f"  • {r['Tanggal']} | Rp{int(r['Jumlah (Rp)']):,} | {r['Pengirim']}\n"

        # 3 pengeluaran terakhir
        detail_keluar = ""
        for r in reversed(data_keluar[-3:]):
            detail_keluar += f"  • {r['Tanggal']} | Rp{int(r['Jumlah (Rp)']):,} | {r['Keterangan']}\n"

        saldo_icon = "🟢" if saldo >= 0 else "🔴"

        await message.reply_text(
            f"📊 *Rekap Keuangan*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💰 Total Pemasukan: *Rp{total_masuk:,}*\n"
            f"💸 Total Pengeluaran: *Rp{total_keluar:,}*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{saldo_icon} Saldo: *Rp{saldo:,}*\n\n"
            f"💰 *3 Pemasukan Terakhir:*\n{detail_masuk or '  Belum ada'}\n"
            f"💸 *3 Pengeluaran Terakhir:*\n{detail_keluar or '  Belum ada'}",
            parse_mode="Markdown",
            reply_markup=tombol_menu()
        )
    except Exception as e:
        await message.reply_text(f"❌ Gagal ambil data: {e}")

# =============================================
# MAIN
# =============================================
def main():
    init_sheet()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_pesan))

    print("🤖 Bot berjalan... Tekan Ctrl+C untuk berhenti.")
    app.run_polling()

if __name__ == "__main__":
    main()