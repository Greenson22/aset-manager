import cv2
import numpy as np
import os
import sys

# 1. Minta masukan nama file dari pengguna di terminal
while True:
    image_path = input("Masukkan nama/path file gambar (misal: semua_aset.jpeg): ").strip()
    
    if os.path.exists(image_path):
        image = cv2.imread(image_path)
        if image is not None:
            break
        else:
            print("Gagal membaca file gambar. Pastikan format file benar.\n")
    else:
        print("File tidak ditemukan! Silakan coba lagi.\n")

# 2. Minta pilihan opsi transparansi (Default: Tidak Transparan)
is_transparent_input = input("Buat latar belakang transparan? (y/N) [Default: N]: ").strip().lower()
make_transparent = is_transparent_input == 'y'

output_dir = "aset_terpisah"   # Folder untuk menyimpan hasil

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print("\nSedang memproses gambar...")

# 3. Ubah ke grayscale (abu-abu)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 4. Ubah ke gambar biner (Hitam-Putih) menggunakan Thresholding
_, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

# 5. Cari kontur objek di dalam gambar
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Saring kontur untuk mengabaikan noise (objek < 20px)
valid_contours = [c for c in contours if cv2.boundingRect(c)[2] > 20 and cv2.boundingRect(c)[3] > 20]
total_assets = len(valid_contours)

if total_assets == 0:
    print("Tidak ada aset yang terdeteksi.")
    sys.exit()

mode_text = "Transparan (PNG Alpha)" if make_transparent else "Tidak Transparan (Asli)"
print(f"Ditemukan {total_assets} aset. Mode: {mode_text}")
print("Memulai proses pemisahan...\n")

# 6. Iterasi dan eksekusi pemisahan dengan indikator progres
for count, contour in enumerate(valid_contours, start=1):
    x, y, w, h = cv2.boundingRect(contour)
    
    if make_transparent:
        # Buat masker khusus untuk bagian objek
        mask = np.zeros((h, w), dtype=np.uint8)
        # Geser koordinat kontur agar sesuai dengan ukuran hasil potong (crop)
        contour_shifted = contour - [x, y]
        cv2.drawContours(mask, [contour_shifted], -1, 255, thickness=cv2.FILLED)
        
        # Potong area gambar asli
        crop_bgr = image[y:y+h, x:x+w]
        
        # Pisahkan saluran B, G, R dan tambahkan saluran Alfa (Transparansi) berdasarkan masker
        b, g, r = cv2.split(crop_bgr)
        cropped_asset = cv2.merge([b, g, r, mask])
    else:
        # Ambil potong gambar asli tanpa perubahan latar belakang
        cropped_asset = image[y:y+h, x:x+w]
    
    # Simpan hasil
    file_name = f"{output_dir}/aset_{count}.png"
    cv2.imwrite(file_name, cropped_asset)
    
    # Buat dan tampilkan progress bar di terminal
    percent = (count / total_assets) * 100
    bar_length = 30
    filled_length = int(bar_length * count // total_assets)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    
    sys.stdout.write(f"\rProgres: |{bar}| {percent:.1f}% ({count}/{total_assets} Aset)")
    sys.stdout.flush()

print("\n\nSelesai! Semua aset berhasil dipisahkan ke dalam folder 'aset_terpisah'.")
