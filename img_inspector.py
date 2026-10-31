import os
from pathlib import Path
from PIL import Image

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".webp",
    ".tiff",
    ".svg",
}


def inspect_image_dimensions(folder_path_str: str) -> None:
    # Bersihkan tanda kutip tunggal/ganda dan spasi dari input string terlebih dahulu
    clean_path_str = folder_path_str.strip("\"' ")
    folder_path = Path(clean_path_str)

    if not folder_path.is_dir():
        print(f"\n[Error] Folder '{folder_path}' tidak ditemukan!")
        return

    image_files = [
        f
        for f in folder_path.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    ]

    if not image_files:
        print(f"\nTidak ditemukan file gambar di dalam folder: {folder_path}")
        return

    print(f"\nFound {len(image_files)} image(s) in: {folder_path.resolve()}\n")
    print(f"{'Nama File':<35} | {'Width (px)':<12} | {'Height (px)':<12}")
    print("-" * 65)

    valid_count = 0
    for img_path in image_files:
        try:
            with Image.open(img_path) as img:
                width, height = img.size
                print(f"{img_path.name:<35} | {width:<12} | {height:<12}")
                valid_count += 1
        except Exception:
            print(f"{img_path.name:<35} | [Gagal Membaca Gambar]")

    print("-" * 65)
    print(f"Selesai! Berhasil memproses {valid_count} dari {len(image_files)} gambar.\n")


if __name__ == "__main__":
    print("=== IMAGE DIMENSION INSPECTOR ===")
    user_input = input("Masukkan path/lokasi folder gambar: ")
    inspect_image_dimensions(user_input)
