# app_multi_user.py
# -*- coding: utf-8 -*-
"""
Worklog Analyzer - Multi User Edition (PyQt5)
- Chọn tối đa 3 file CSV (mỗi file = 1 nhân viên)
- Tùy chọn thư mục xuất, định dạng ngày, giờ chuẩn/ngày
- Chạy pipeline ở background thread, hiển thị log & trạng thái
- Tự nạp icon từ thư mục assets (tương thích PyInstaller)
"""

import os
import sys
import traceback
from pathlib import Path

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTextEdit, QComboBox,
    QSpinBox, QGroupBox, QMessageBox, QProgressBar, QFrame
)

# ====== core xử lý ======
from worklog_core_multi_user import run_multi_user_pipeline


# ---------- tiện ích nạp tài nguyên (tương thích PyInstaller) ----------
def resource_path(rel_path: str) -> str:
    """Trả về đường dẫn file tài nguyên (khi chạy source hoặc .exe PyInstaller)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel_path)


# ---------- Worker chạy nền ----------
class WorkerThread(QThread):
    finished = pyqtSignal(dict)     # trả kết quả cuối
    error = pyqtSignal(str)         # chuỗi lỗi (đã kèm traceback)
    log = pyqtSignal(str)           # phát log nếu cần

    def __init__(self, file_paths, out_dir, date_format, standard_hours, parent=None):
        super().__init__(parent)
        self.file_paths = file_paths
        self.out_dir = out_dir
        self.date_format = date_format
        self.standard_hours = float(standard_hours)

    def run(self):
        try:
            self.log.emit("🚀 Bắt đầu xử lý...")
            result = run_multi_user_pipeline(
                self.file_paths,
                self.out_dir,
                self.date_format,
                self.standard_hours,
            )
            self.finished.emit(result)
        except Exception as e:
            tb = traceback.format_exc()
            self.error.emit(f"❌ LỖI: {e}\n\n{tb}")


# ---------- Widget chọn 1 file CSV ----------
class FileSelector(QFrame):
    def __init__(self, label_text: str, parent=None):
        super().__init__(parent)
        self.file_path = None
        self._build(label_text)

    def _build(self, label_text: str):
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setLineWidth(2)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        lab = QLabel(label_text)
        lab.setMinimumWidth(110)
        lab.setFont(QFont("Segoe UI", 10, QFont.Bold))

        self.file_label = QLabel("Chưa chọn file")
        self._set_label_idle()

        btn_pick = QPushButton("📁 Chọn File")
        btn_pick.setMinimumWidth(120)
        btn_pick.clicked.connect(self.pick_file)

        self.btn_clear = QPushButton("✖")
        self.btn_clear.setMaximumWidth(40)
        self.btn_clear.clicked.connect(self.clear_file)
        self.btn_clear.setEnabled(False)

        layout.addWidget(lab)
        layout.addWidget(self.file_label, 1)
        layout.addWidget(btn_pick)
        layout.addWidget(self.btn_clear)

    def _set_label_idle(self):
        self.file_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                padding: 8px 12px;
                background: #f8fafc;
                border-radius: 6px;
                border: 1px solid #e2e8f0;
            }
        """)
        self.file_label.setText("Chưa chọn file")

    def _set_label_selected(self, filename: str):
        self.file_label.setStyleSheet("""
            QLabel {
                color: #059669;
                padding: 8px 12px;
                background: #d1fae5;
                border-radius: 6px;
                border: 1px solid #10b981;
                font-weight: bold;
            }
        """)
        self.file_label.setText(filename)

    def pick_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file CSV 日報",
            "",
            "CSV Files (*.csv);;All Files (*)",
        )
        if path:
            self.file_path = path
            self._set_label_selected(Path(path).name)
            self.btn_clear.setEnabled(True)

    def clear_file(self):
        self.file_path = None
        self._set_label_idle()
        self.btn_clear.setEnabled(False)

    def get_file_path(self):
        return self.file_path


# ---------- Main Window ----------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker: WorkerThread | None = None
        self._build_ui()
        self._apply_styles()
        self._load_icon()

    # ----- UI -----
    def _build_ui(self):
        self.setWindowTitle("📊 Worklog Analyzer - Multi User Edition")
        self.resize(1200, 800)

        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(20)
        root.setContentsMargins(30, 30, 30, 30)

        # Header
        header = QLabel("📊 Worklog Analyzer - Multi User Edition")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Segoe UI", 24, QFont.Bold))
        header.setStyleSheet("""
            QLabel {
                color: #667eea;
                padding: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f8fafc, stop:1 #e0e7ff);
                border-radius: 16px;
                border: 2px solid #c7d2fe;
            }
        """)
        root.addWidget(header)

        # File group (3 users)
        grp_files = QGroupBox("📂 Chọn File CSV (Tối đa 3 users)")
        grp_files.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lay_files = QVBoxLayout(grp_files)
        lay_files.setSpacing(12)

        self.sel1 = FileSelector("👤 User 1:")
        self.sel2 = FileSelector("👤 User 2:")
        self.sel3 = FileSelector("👤 User 3:")

        lay_files.addWidget(self.sel1)
        lay_files.addWidget(self.sel2)
        lay_files.addWidget(self.sel3)

        root.addWidget(grp_files)

        # Settings
        grp_set = QGroupBox("⚙️ Cài Đặt")
        grp_set.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lay_set = QHBoxLayout(grp_set)
        lay_set.setSpacing(30)

        # Output
        out_box = QVBoxLayout()
        lab_out = QLabel("📁 Thư mục kết quả:")
        lab_out.setFont(QFont("Segoe UI", 10, QFont.Bold))
        row_out = QHBoxLayout()
        self.lbl_out = QLabel("./output")
        self.lbl_out.setStyleSheet("""
            QLabel {
                padding: 10px;
                background: #f8fafc;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                color: #475569;
                font-size: 11px;
            }
        """)
        btn_out = QPushButton("📂 Chọn")
        btn_out.clicked.connect(self.pick_output)
        btn_out.setMinimumWidth(100)
        row_out.addWidget(self.lbl_out, 1)
        row_out.addWidget(btn_out)
        out_box.addWidget(lab_out)
        out_box.addLayout(row_out)

        # Date format
        date_box = QVBoxLayout()
        lab_date = QLabel("📅 Định dạng ngày:")
        lab_date.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.cmb_date = QComboBox()
        self.cmb_date.addItems(["Ngày/Tháng/Năm (DD/MM/YYYY)", "Tháng/Ngày/Năm (MM/DD/YYYY)"])
        self.cmb_date.setMinimumWidth(250)
        date_box.addWidget(lab_date)
        date_box.addWidget(self.cmb_date)

        # Standard hours
        hour_box = QVBoxLayout()
        lab_hour = QLabel("⏰ Giờ chuẩn/ngày:")
        lab_hour.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.spin_hours = QSpinBox()
        self.spin_hours.setRange(1, 24)
        self.spin_hours.setValue(8)
        self.spin_hours.setSuffix(" giờ")
        self.spin_hours.setMinimumWidth(150)
        hour_box.addWidget(lab_hour)
        hour_box.addWidget(self.spin_hours)

        lay_set.addLayout(out_box, 2)
        lay_set.addLayout(date_box, 1)
        lay_set.addLayout(hour_box, 1)
        root.addWidget(grp_set)

        # Run button
        self.btn_run = QPushButton("🚀 Xử Lý & Tạo Báo Cáo")
        self.btn_run.setMinimumHeight(60)
        self.btn_run.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.btn_run.clicked.connect(self.process)
        root.addWidget(self.btn_run)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setTextVisible(False)
        self.progress.setMaximumHeight(8)
        root.addWidget(self.progress)

        # Logs
        lab_log = QLabel("📋 Nhật ký xử lý:")
        lab_log.setFont(QFont("Segoe UI", 11, QFont.Bold))
        root.addWidget(lab_log)

        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setFont(QFont("Consolas", 9))
        self.txt.setPlaceholderText("Chọn file CSV và nhấn 'Xử Lý' để bắt đầu...")
        root.addWidget(self.txt, 1)

        # Status bar
        self.statusBar().showMessage("✨ Sẵn sàng xử lý")
        self.statusBar().setFont(QFont("Segoe UI", 10))

    def _apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #f8fafc; }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cbd5e1;
                border-radius: 12px;
                margin-top: 12px;
                padding: 20px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #334155;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #5a67d8);
                color: white; border: none; border-radius: 10px;
                padding: 12px 24px; font-weight: bold; font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a67d8, stop:1 #4c51bf);
            }
            QPushButton:pressed { background: #4c51bf; }
            QPushButton:disabled { background: #cbd5e1; color: #94a3b8; }
            QComboBox, QSpinBox {
                padding: 10px; border: 2px solid #e2e8f0;
                border-radius: 8px; background: white;
                font-size: 11px; color: #475569;
            }
            QComboBox:hover, QSpinBox:hover { border-color: #667eea; }
            QTextEdit {
                border: 2px solid #e2e8f0; border-radius: 10px;
                padding: 12px; background: #ffffff; color: #334155;
            }
            QProgressBar { border: none; border-radius: 4px; background: #e2e8f0; }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 4px;
            }
        """)

    def _load_icon(self):
        """Đặt icon cho app & cửa sổ (ưu tiên PNG cho UI; ICO dùng ở lúc build exe)."""
        png = resource_path(os.path.join("assets", "app.png"))
        if os.path.exists(png):
            icon = QIcon(png)
            self.setWindowIcon(icon)
            QApplication.instance().setWindowIcon(icon)

    # ----- helpers -----
    def _log(self, msg: str):
        self.txt.append(msg)
        self.txt.verticalScrollBar().setValue(self.txt.verticalScrollBar().maximum())

    def pick_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục lưu kết quả")
        if folder:
            self.lbl_out.setText(folder)

    # ----- run -----
    def process(self):
        files = [w.get_file_path() for w in (self.sel1, self.sel2, self.sel3) if w.get_file_path()]
        if not files:
            QMessageBox.warning(self, "⚠️ Thiếu File", "Vui lòng chọn ít nhất 1 file CSV để xử lý!")
            return

        self.txt.clear()
        self._log(f"🎯 Bắt đầu xử lý {len(files)} file CSV...")
        self._log("=" * 70)

        out_dir = self.lbl_out.text().strip() or "./output"
        fmt = "day_first" if self.cmb_date.currentIndex() == 0 else "month_first"
        std_hours = self.spin_hours.value()

        # UI state
        self.btn_run.setEnabled(False)
        self.btn_run.setText("⏳ Đang xử lý...")
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.statusBar().showMessage("🔄 Đang xử lý...")

        # start worker
        self.worker = WorkerThread(files, out_dir, fmt, std_hours, self)
        self.worker.log.connect(self._log)
        self.worker.finished.connect(self._on_done)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_done(self, result: dict):
        self.progress.setVisible(False)
        self.btn_run.setEnabled(True)
        self.btn_run.setText("🚀 Xử Lý & Tạo Báo Cáo")
        self.statusBar().showMessage("✅ Xử lý thành công!")

        self._log("\n" + "=" * 70)
        self._log("✅ HOÀN TẤT!")
        self._log(f"📊 Đã xử lý {result['total_employees']} nhân viên:")
        for name in result.get("employee_names", []):
            self._log(f"   • {name}")
        self._log(f"📝 Tổng số bản ghi: {result.get('total_records', 0)}")
        self._log("\n📁 Các file đã tạo:")
        for k, p in result.get("outputs", {}).items():
            self._log(f"   • {Path(p).name}")
        self._log("=" * 70)

        # thông báo
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("✅ Thành công")
        msg.setText(f"Đã tạo báo cáo tổng hợp cho {result['total_employees']} nhân viên!")
        try:
            folder = Path(result["outputs"]["excel"]).parent
            msg.setInformativeText(f"Các file được lưu tại:\n{folder}")
        except Exception:
            pass
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def _on_error(self, err: str):
        self.progress.setVisible(False)
        self.btn_run.setEnabled(True)
        self.btn_run.setText("🚀 Xử Lý & Tạo Báo Cáo")
        self.statusBar().showMessage("❌ Xử lý thất bại")

        self._log("\n" + err)
        QMessageBox.critical(self, "❌ Lỗi", "Đã xảy ra lỗi khi xử lý. Xem nhật ký để biết chi tiết.", QMessageBox.Ok)


# ---------- Entry ----------
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # font & palette nhẹ nhàng
    app.setFont(QFont("Segoe UI", 10))
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(248, 250, 252))
    pal.setColor(QPalette.WindowText, QColor(30, 41, 59))
    app.setPalette(pal)

    # icon toàn app (nếu có)
    png = resource_path(os.path.join("assets", "app.png"))
    if os.path.exists(png):
        app.setWindowIcon(QIcon(png))

    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()