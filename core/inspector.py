from pathlib import Path
from typing import Dict, List, Optional
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


def format_bytes(size_bytes: int) -> str:
    """Format ukuran file ke format yang mudah dibaca manusia."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def inspect_directory(folder_path_str: str) -> List[Dict[str, Optional[str]]]:
    """
    Memeriksa gambar-gambar di dalam direktori dan mengembalikan data list dictionary.
    """
    clean_path_str = folder_path_str.strip("\"' ")
    folder_path = Path(clean_path_str)

    if not folder_path.is_dir():
        return []

    image_files = [
        f
        for f in folder_path.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    ]

    results = []
    for img_path in sorted(image_files, key=lambda f: f.name.lower()):
        file_size_str = format_bytes(img_path.stat().st_size)
        try:
            with Image.open(img_path) as img:
                width, height = img.size
                img_format = img.format or img_path.suffix.upper().replace(".", "")
                results.append(
                    {
                        "name": img_path.name,
                        "path": str(img_path.resolve()),
                        "width": width,
                        "height": height,
                        "format": img_format,
                        "size": file_size_str,
                        "status": "OK",
                    }
                )
        except Exception as e:
            results.append(
                {
                    "name": img_path.name,
                    "path": str(img_path.resolve()),
                    "width": None,
                    "height": None,
                    "format": img_path.suffix.upper().replace(".", ""),
                    "size": file_size_str,
                    "status": f"Gagal membaca ({str(e)})",
                }
            )

    return results
