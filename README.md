# Aset Manager

Aplikasi desktop berbasis Python & PyQt6 untuk manajemen dan pemrosesan aset gambar:
1. **Pemisah Aset (Asset Splitter)**: Memisahkan aset-aset individual dari gambar komposit / spritesheet, mendukung background transparan (PNG Alpha), custom threshold, dan noise filter.
2. **Pemeriksa Dimensi (Image Inspector)**: Memeriksa dimensi (Width × Height), format gambar, dan ukuran file di dalam folder dengan tampilan tabel yang interaktif dan fitur filter pencarian.

---

## 📦 Instalasi Dependensi

Jalankan perintah berikut di terminal/PowerShell:

```bash
pip install -r requirements.txt
```

---

## 🚀 Cara Menjalankan Aplikasi

### 1. Menjalankan GUI (PyQt6)
Cukup jalankan:
```bash
python main.py
```

### 2. Menjalankan Mode CLI (Terminal)
Jika ingin menggunakan antarmuka terminal:
```bash
# Untuk pemisah aset:
python main.py --cli

# Untuk pemeriksa dimensi gambar:
python img_inspector.py
```

---

## 📁 Struktur Proyek
```text
aset-manager/
├── core/
│   ├── splitter.py       # Logika OpenCV untuk pemisahan aset
│   └── inspector.py      # Logika inspeksi dimensi & metadata gambar
├── gui/
│   └── main_window.py    # Antarmuka desktop PyQt6 dengan multi-threading (QThread)
├── img_inspector.py      # Entry point CLI pemeriksa gambar
├── main.py               # Entry point utama (menjalankan GUI secara default)
├── requirements.txt      # Daftar dependensi paket Python
└── README.md             # Petunjuk penggunaan
```
