"""
ALAT CEK KOORDINAT TEMPLATE
============================
Jalankan script ini untuk menemukan posisi (x, y) yang tepat
di template PNG kamu.

Cara pakai:
    python cek_koordinat.py

Klik di gambar yang muncul, koordinat akan tampil di terminal.
Tekan 'Q' untuk keluar.
"""

import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import sys

TEMPLATE_PATH = "template.png"

class CekKoordinat:
    def __init__(self, root, img_path):
        self.root = root
        self.root.title("Klik untuk cek koordinat — Tekan Q untuk keluar")
        
        img = Image.open(img_path)
        
        # Resize jika terlalu besar untuk layar
        max_lebar, max_tinggi = 900, 700
        rasio = min(max_lebar / img.width, max_tinggi / img.height, 1.0)
        self.skala = rasio
        
        if rasio < 1.0:
            w = int(img.width * rasio)
            h = int(img.height * rasio)
            img = img.resize((w, h), Image.LANCZOS)
        
        self.img_asli = Image.open(img_path)
        self.tk_img = ImageTk.PhotoImage(img)
        
        # Label info
        self.info = tk.Label(root, text="Klik pada gambar untuk melihat koordinat asli",
                             font=("Arial", 12), bg="#222", fg="white", pady=8)
        self.info.pack(fill=tk.X)
        
        # Canvas gambar
        self.canvas = tk.Canvas(root, width=img.width, height=img.height,
                                cursor="crosshair", bg="#111")
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
        
        self.canvas.bind("<Button-1>", self.klik)
        self.root.bind("<q>", lambda e: root.destroy())
        self.root.bind("<Q>", lambda e: root.destroy())
        
        # Panel log koordinat
        self.log = tk.Text(root, height=6, font=("Courier", 11),
                           bg="#1a1a2e", fg="#00ff88")
        self.log.pack(fill=tk.X, padx=4, pady=4)
        self.log.insert(tk.END, "📍 Koordinat yang diklik akan muncul di sini...\n")
        
    def klik(self, event):
        # Konversi ke koordinat gambar asli
        x_asli = int(event.x / self.skala)
        y_asli = int(event.y / self.skala)
        
        pesan = f"➤ Klik di ({event.x}, {event.y}) tampilan  →  Koordinat asli: x={x_asli}, y={y_asli}\n"
        self.log.insert(tk.END, pesan)
        self.log.see(tk.END)
        
        self.info.config(
            text=f"✅ Koordinat asli: x = {x_asli}   |   y = {y_asli}   (gambar {self.img_asli.width}×{self.img_asli.height}px)"
        )
        print(pesan.strip())


def main():
    try:
        img = Image.open(TEMPLATE_PATH)
        print(f"✅ Template ditemukan: {img.width}×{img.height}px")
    except FileNotFoundError:
        print(f"❌ File '{TEMPLATE_PATH}' tidak ditemukan!")
        print("   Pastikan template.png ada di folder yang sama.")
        sys.exit(1)
    
    root = tk.Tk()
    root.configure(bg="#222")
    app = CekKoordinat(root, TEMPLATE_PATH)
    root.mainloop()


if __name__ == "__main__":
    main()
