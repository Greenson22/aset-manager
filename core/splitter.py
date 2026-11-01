import os
from typing import Callable, Optional, Tuple
import cv2
import numpy as np


def split_assets(
    image_path: str,
    output_dir: str,
    make_transparent: bool = False,
    threshold_value: int = 240,
    min_size: int = 20,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
    cancel_check: Optional[Callable[[], bool]] = None,
) -> Tuple[bool, str, int]:
    """
    Memisahkan aset individual dari satu gambar komposit.

    :param image_path: Path file gambar input.
    :param output_dir: Direktori tempat menyimpan aset hasil potongan.
    :param make_transparent: Apakah background dijadikan transparan (alpha channel).
    :param threshold_value: Nilai ambang batas binarisasi (default: 240).
    :param min_size: Ukuran minimum (width & height) agar tidak terdeteksi sebagai noise.
    :param progress_callback: Callback fn(current, total, status_message).
    :param cancel_check: Callback fn() -> bool untuk mengecek apakah proses dibatalkan.
    :return: (sukses, pesan, jumlah_aset_ditemukan)
    """
    if not os.path.exists(image_path):
        return False, f"File gambar tidak ditemukan: {image_path}", 0

    image = cv2.imread(image_path)
    if image is None:
        return False, "Gagal membaca gambar. Pastikan format file didukung.", 0

    os.makedirs(output_dir, exist_ok=True)

    # Ubah ke grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Thresholding biner terbalik (background putih menjadi hitam, objek menjadi putih)
    _, thresh = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY_INV)

    # Cari kontur objek
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter kontur berdasarkan ukuran minimum
    valid_contours = [
        c
        for c in contours
        if cv2.boundingRect(c)[2] >= min_size and cv2.boundingRect(c)[3] >= min_size
    ]

    total_assets = len(valid_contours)
    if total_assets == 0:
        return False, "Tidak ada aset yang terdeteksi dengan parameter saat ini.", 0

    if progress_callback:
        progress_callback(0, total_assets, f"Ditemukan {total_assets} aset. Memulai pemrosesan...")

    # Urutkan kontur dari atas ke bawah, kiri ke kanan untuk penomoran yang rapi
    valid_contours = sorted(
        valid_contours,
        key=lambda c: (cv2.boundingRect(c)[1] // 50, cv2.boundingRect(c)[0]),
    )

    saved_count = 0
    for count, contour in enumerate(valid_contours, start=1):
        if cancel_check and cancel_check():
            return False, f"Proses dibatalkan. {saved_count} aset tersimpan.", saved_count

        x, y, w, h = cv2.boundingRect(contour)

        if make_transparent:
            # Masker khusus objek
            mask = np.zeros((h, w), dtype=np.uint8)
            contour_shifted = contour - [x, y]
            cv2.drawContours(mask, [contour_shifted], -1, 255, thickness=cv2.FILLED)

            crop_bgr = image[y : y + h, x : x + w]
            b, g, r = cv2.split(crop_bgr)
            cropped_asset = cv2.merge([b, g, r, mask])
        else:
            cropped_asset = image[y : y + h, x : x + w]

        file_name = os.path.join(output_dir, f"aset_{count}.png")
        cv2.imwrite(file_name, cropped_asset)
        saved_count += 1

        if progress_callback:
            progress_callback(count, total_assets, f"Menyimpan aset {count} dari {total_assets}...")

    return True, f"Berhasil memisahkan {saved_count} aset ke '{output_dir}'.", saved_count
