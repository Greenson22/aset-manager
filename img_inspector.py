import sys
from core.inspector import inspect_directory


def inspect_image_dimensions(folder_path_str: str) -> None:
    results = inspect_directory(folder_path_str)

    if not results:
        print(f"\nFolder tidak ditemukan atau tidak berisi gambar: {folder_path_str}")
        return

    print(f"\nFound {len(results)} image(s) in: {folder_path_str}\n")
    print(f"{'Nama File':<35} | {'Width (px)':<12} | {'Height (px)':<12} | {'Ukuran':<10}")
    print("-" * 75)

    valid_count = 0
    for item in results:
        if item["status"] == "OK":
            print(f"{item['name']:<35} | {item['width']:<12} | {item['height']:<12} | {item['size']:<10}")
            valid_count += 1
        else:
            print(f"{item['name']:<35} | [Gagal Membaca Gambar]  | {item['size']:<10}")

    print("-" * 75)
    print(f"Selesai! Berhasil memproses {valid_count} dari {len(results)} gambar.\n")


if __name__ == "__main__":
    print("=== IMAGE DIMENSION INSPECTOR ===")
    user_input = input("Masukkan path/lokasi folder gambar: ")
    inspect_image_dimensions(user_input)
