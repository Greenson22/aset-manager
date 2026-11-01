import sys
import os

def run_cli():
    import cv2
    from core.splitter import split_assets

    print("=== ASET MANAGER (CLI MODE) ===")
    while True:
        image_path = input("Masukkan nama/path file gambar (misal: semua_aset.jpeg): ").strip()
        if os.path.exists(image_path):
            break
        print("File tidak ditemukan! Silakan coba lagi.\n")

    is_transparent_input = input("Buat latar belakang transparan? (y/N) [Default: N]: ").strip().lower()
    make_transparent = is_transparent_input == 'y'
    output_dir = "aset_terpisah"

    def progress_callback(count, total, msg):
        percent = (count / total) * 100 if total > 0 else 0
        bar_length = 30
        filled_length = int(bar_length * count // total) if total > 0 else 0
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        sys.stdout.write(f"\rProgres: |{bar}| {percent:.1f}% ({count}/{total} Aset)")
        sys.stdout.flush()

    print("\nMemulai proses pemisahan...")
    success, message, total = split_assets(
        image_path=image_path,
        output_dir=output_dir,
        make_transparent=make_transparent,
        progress_callback=progress_callback
    )
    print(f"\n\n{message}")


def main():
    if "--cli" in sys.argv:
        run_cli()
    else:
        try:
            from PyQt6.QtWidgets import QApplication
            from gui.main_window import MainWindow

            app = QApplication(sys.argv)
            window = MainWindow()
            window.show()
            sys.exit(app.exec())
        except ImportError as e:
            print(f"Modul GUI belum terpasang atau tidak ditemukan: {e}")
            print("Jalankan 'pip install -r requirements.txt' terlebih dahulu.")
            print("Atau gunakan mode CLI dengan: python main.py --cli")
            sys.exit(1)


if __name__ == "__main__":
    main()
