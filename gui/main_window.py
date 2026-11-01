import os
import sys
from pathlib import Path
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon, QFont
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QCheckBox,
    QProgressBar,
    QMessageBox,
    QSpinBox,
    QSlider,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)

from core.splitter import split_assets
from core.inspector import inspect_directory


class SplitterWorker(QThread):
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(bool, str, int)

    def __init__(self, image_path: str, output_dir: str, transparent: bool, threshold: int, min_size: int):
        super().__init__()
        self.image_path = image_path
        self.output_dir = output_dir
        self.transparent = transparent
        self.threshold = threshold
        self.min_size = min_size
        self._is_cancelled = False

    def run(self):
        def progress_cb(current, total, msg):
            self.progress.emit(current, total, msg)

        def cancel_check():
            return self._is_cancelled

        success, message, count = split_assets(
            image_path=self.image_path,
            output_dir=self.output_dir,
            make_transparent=self.transparent,
            threshold_value=self.threshold,
            min_size=self.min_size,
            progress_callback=progress_cb,
            cancel_check=cancel_check,
        )
        self.finished.emit(success, message, count)

    def cancel(self):
        self._is_cancelled = True


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aset Manager - Splitter & Inspector")
        self.setMinimumSize(850, 650)
        self.worker = None
        self.inspector_data = []

        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Segoe UI", 10))
        main_layout.addWidget(self.tabs)

        # Tab 1: Asset Splitter
        self.splitter_tab = QWidget()
        self._setup_splitter_tab()
        self.tabs.addTab(self.splitter_tab, "✂️ Pemisah Aset (Splitter)")

        # Tab 2: Image Dimension Inspector
        self.inspector_tab = QWidget()
        self._setup_inspector_tab()
        self.tabs.addTab(self.inspector_tab, "🔍 Pemeriksa Dimensi (Inspector)")

    # -------------------------------------------------------------
    # TAB 1: SPLITTER
    # -------------------------------------------------------------
    def _setup_splitter_tab(self):
        layout = QVBoxLayout(self.splitter_tab)
        layout.setSpacing(12)

        # Group 1: File & Folder
        path_group = QGroupBox("Pengaturan File & Folder")
        path_layout = QVBoxLayout(path_group)

        # Input File
        h_file = QHBoxLayout()
        h_file.addWidget(QLabel("File Gambar:"))
        self.txt_image_path = QLineEdit()
        self.txt_image_path.setPlaceholderText("Pilih file gambar (PNG, JPG, JPEG, dll.)...")
        self.txt_image_path.textChanged.connect(self._on_image_path_changed)
        btn_browse_file = QPushButton("Pilih File...")
        btn_browse_file.clicked.connect(self._browse_image_file)
        h_file.addWidget(self.txt_image_path)
        h_file.addWidget(btn_browse_file)
        path_layout.addLayout(h_file)

        # Output Folder
        h_out = QHBoxLayout()
        h_out.addWidget(QLabel("Folder Output:"))
        default_out = str(Path(os.getcwd()) / "aset_terpisah")
        self.txt_output_dir = QLineEdit(default_out)
        btn_browse_out = QPushButton("Pilih Folder...")
        btn_browse_out.clicked.connect(self._browse_output_dir)
        h_out.addWidget(self.txt_output_dir)
        h_out.addWidget(btn_browse_out)
        path_layout.addLayout(h_out)

        layout.addWidget(path_group)

        # Group 2: Preview & Options (side by side)
        mid_layout = QHBoxLayout()

        # Left: Preview Box
        preview_group = QGroupBox("Preview Gambar Input")
        preview_layout = QVBoxLayout(preview_group)
        self.lbl_preview = QLabel("Belum ada gambar yang dipilih")
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_preview.setStyleSheet("border: 1px dashed #aaa; background-color: #f9f9f9; min-height: 180px;")
        preview_layout.addWidget(self.lbl_preview)
        mid_layout.addWidget(preview_group, stretch=1)

        # Right: Settings
        settings_group = QGroupBox("Parameter Pemisahan")
        settings_layout = QVBoxLayout(settings_group)

        self.chk_transparent = QCheckBox("Buat Latar Belakang Transparan (PNG Alpha)")
        self.chk_transparent.setChecked(True)
        settings_layout.addWidget(self.chk_transparent)

        # Threshold
        settings_layout.addWidget(QLabel("Threshold Latar Belakang (1 - 255):"))
        h_thresh = QHBoxLayout()
        self.slider_thresh = QSlider(Qt.Orientation.Horizontal)
        self.slider_thresh.setRange(50, 255)
        self.slider_thresh.setValue(240)
        self.spin_thresh = QSpinBox()
        self.spin_thresh.setRange(50, 255)
        self.spin_thresh.setValue(240)
        self.slider_thresh.valueChanged.connect(self.spin_thresh.setValue)
        self.spin_thresh.valueChanged.connect(self.slider_thresh.setValue)
        h_thresh.addWidget(self.slider_thresh)
        h_thresh.addWidget(self.spin_thresh)
        settings_layout.addLayout(h_thresh)

        # Min Object Size
        settings_layout.addWidget(QLabel("Filter Ukuran Minimal Objek (Noise Filter, px):"))
        h_size = QHBoxLayout()
        self.slider_size = QSlider(Qt.Orientation.Horizontal)
        self.slider_size.setRange(5, 200)
        self.slider_size.setValue(20)
        self.spin_size = QSpinBox()
        self.spin_size.setRange(5, 200)
        self.spin_size.setValue(20)
        self.slider_size.valueChanged.connect(self.spin_size.setValue)
        self.spin_size.valueChanged.connect(self.slider_size.setValue)
        h_size.addWidget(self.slider_size)
        h_size.addWidget(self.spin_size)
        settings_layout.addLayout(h_size)

        settings_layout.addStretch()
        mid_layout.addWidget(settings_group, stretch=1)

        layout.addLayout(mid_layout)

        # Progress & Status
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        self.lbl_status = QLabel("Siap memproses.")
        self.lbl_status.setStyleSheet("color: #555;")
        layout.addWidget(self.lbl_status)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("🚀 Mulai Pisahkan Aset")
        self.btn_start.setFixedHeight(38)
        self.btn_start.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.btn_start.setStyleSheet("background-color: #007acc; color: white; border-radius: 4px;")
        self.btn_start.clicked.connect(self._start_splitting)

        self.btn_open_output = QPushButton("📂 Buka Folder Hasil")
        self.btn_open_output.setFixedHeight(38)
        self.btn_open_output.clicked.connect(self._open_output_folder)

        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_open_output)
        layout.addLayout(btn_layout)

    def _browse_image_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Pilih File Gambar",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.webp *.tiff);;All Files (*)",
        )
        if file_path:
            self.txt_image_path.setText(file_path)

    def _browse_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Pilih Folder Output", self.txt_output_dir.text())
        if dir_path:
            self.txt_output_dir.setText(dir_path)

    def _on_image_path_changed(self, path):
        path = path.strip("\"' ")
        if os.path.exists(path) and os.path.isfile(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    260, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                )
                self.lbl_preview.setPixmap(scaled_pixmap)
                return
        self.lbl_preview.setText("Belum ada gambar yang dipilih")
        self.lbl_preview.setPixmap(QPixmap())

    def _start_splitting(self):
        img_path = self.txt_image_path.text().strip("\"' ")
        out_dir = self.txt_output_dir.text().strip("\"' ")

        if not img_path:
            QMessageBox.warning(self, "Peringatan", "Harap pilih file gambar terlebih dahulu!")
            return

        if not os.path.exists(img_path):
            QMessageBox.critical(self, "Error", f"File gambar tidak ditemukan:\n{img_path}")
            return

        if not out_dir:
            QMessageBox.warning(self, "Peringatan", "Harap tentukan folder output!")
            return

        self.btn_start.setEnabled(False)
        self.progress_bar.setValue(0)
        self.lbl_status.setText("Sedang memproses gambar...")

        self.worker = SplitterWorker(
            image_path=img_path,
            output_dir=out_dir,
            transparent=self.chk_transparent.isChecked(),
            threshold=self.spin_thresh.value(),
            min_size=self.spin_size.value(),
        )
        self.worker.progress.connect(self._on_split_progress)
        self.worker.finished.connect(self._on_split_finished)
        self.worker.start()

    def _on_split_progress(self, current, total, msg):
        if total > 0:
            val = int((current / total) * 100)
            self.progress_bar.setValue(val)
        self.lbl_status.setText(msg)

    def _on_split_finished(self, success, message, count):
        self.btn_start.setEnabled(True)
        if success:
            self.progress_bar.setValue(100)
            self.lbl_status.setText(message)
            QMessageBox.information(
                self,
                "Selesai",
                f"Proses Berhasil!\n{message}\nTotal aset: {count}",
            )
        else:
            self.lbl_status.setText(f"Gagal: {message}")
            QMessageBox.warning(self, "Perhatian", message)

    def _open_output_folder(self):
        out_dir = self.txt_output_dir.text().strip("\"' ")
        if not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        os.startfile(out_dir)

    # -------------------------------------------------------------
    # TAB 2: INSPECTOR
    # -------------------------------------------------------------
    def _setup_inspector_tab(self):
        layout = QVBoxLayout(self.inspector_tab)
        layout.setSpacing(10)

        # Top Bar: Folder Selection
        h_dir = QHBoxLayout()
        h_dir.addWidget(QLabel("Folder Gambar:"))
        self.txt_inspect_dir = QLineEdit(os.getcwd())
        btn_browse = QPushButton("Pilih Folder...")
        btn_browse.clicked.connect(self._browse_inspect_dir)
        btn_scan = QPushButton("🔍 Scan Gambar")
        btn_scan.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")
        btn_scan.clicked.connect(self._scan_directory)

        h_dir.addWidget(self.txt_inspect_dir)
        h_dir.addWidget(btn_browse)
        h_dir.addWidget(btn_scan)
        layout.addLayout(h_dir)

        # Search Bar
        h_search = QHBoxLayout()
        h_search.addWidget(QLabel("Filter Nama File:"))
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Ketik untuk mencari nama file...")
        self.txt_search.textChanged.connect(self._filter_table)
        h_search.addWidget(self.txt_search)
        layout.addLayout(h_search)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Nama File", "Format", "Width (px)", "Height (px)", "Ukuran File"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        # Bottom Bar: Summary & Open Folder
        h_bottom = QHBoxLayout()
        self.lbl_inspector_status = QLabel("Klik 'Scan Gambar' untuk mulai memeriksa folder.")
        btn_open_folder = QPushButton("📂 Buka Folder")
        btn_open_folder.clicked.connect(self._open_inspect_folder)

        h_bottom.addWidget(self.lbl_inspector_status, stretch=1)
        h_bottom.addWidget(btn_open_folder)
        layout.addLayout(h_bottom)

    def _browse_inspect_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Pilih Folder untuk Diperiksa", self.txt_inspect_dir.text())
        if dir_path:
            self.txt_inspect_dir.setText(dir_path)
            self._scan_directory()

    def _scan_directory(self):
        folder = self.txt_inspect_dir.text().strip("\"' ")
        if not os.path.isdir(folder):
            QMessageBox.critical(self, "Error", f"Folder tidak ditemukan:\n{folder}")
            return

        self.inspector_data = inspect_directory(folder)
        self._populate_table(self.inspector_data)
        self.lbl_inspector_status.setText(f"Ditemukan {len(self.inspector_data)} file gambar di folder.")

    def _populate_table(self, data):
        self.table.setRowCount(0)
        for row_idx, item in enumerate(data):
            self.table.insertRow(row_idx)

            col_name = QTableWidgetItem(item["name"])
            col_format = QTableWidgetItem(str(item["format"]))
            col_w = QTableWidgetItem(str(item["width"]) if item["width"] is not None else "-")
            col_h = QTableWidgetItem(str(item["height"]) if item["height"] is not None else "-")
            col_size = QTableWidgetItem(item["size"])

            # Alignments
            col_w.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            col_h.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            col_format.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            col_size.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            if item["status"] != "OK":
                col_name.setToolTip(item["status"])
                col_name.setForeground(Qt.GlobalColor.red)

            self.table.setItem(row_idx, 0, col_name)
            self.table.setItem(row_idx, 1, col_format)
            self.table.setItem(row_idx, 2, col_w)
            self.table.setItem(row_idx, 3, col_h)
            self.table.setItem(row_idx, 4, col_size)

    def _filter_table(self, keyword):
        keyword = keyword.lower().strip()
        filtered = [item for item in self.inspector_data if keyword in item["name"].lower()]
        self._populate_table(filtered)

    def _open_inspect_folder(self):
        folder = self.txt_inspect_dir.text().strip("\"' ")
        if os.path.isdir(folder):
            os.startfile(folder)
        else:
            QMessageBox.warning(self, "Peringatan", "Folder tidak ditemukan!")


def run_app():
    app = QMainWindow()  # Placeholder if needed
    from PyQt6.QtWidgets import QApplication

    qt_app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(qt_app.exec())
