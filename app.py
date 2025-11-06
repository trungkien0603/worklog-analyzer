# app.py
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import webbrowser

# dùng core đã viết
from worklog_core import run_pipeline

APP_NAME = "Work Log Analyzer"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("640x360")
        self.resizable(False, False)

        self.csv_path = tk.StringVar()
        self.out_dir = tk.StringVar(value=str(Path.home() / "WorkLog_Outputs"))
        self.date_format = tk.StringVar(value="day_first")
        self.std_hours = tk.DoubleVar(value=8.0)

        self._build_ui()

    def _build_ui(self):
        pad = {'padx': 10, 'pady': 8}
        frm = ttk.Frame(self); frm.pack(fill='both', expand=True, **pad)

        # CSV
        ttk.Label(frm, text="File CSV 日報:").grid(row=0, column=0, sticky='w')
        ttk.Entry(frm, textvariable=self.csv_path, width=60).grid(row=0, column=1, sticky='we', padx=6)
        ttk.Button(frm, text="Chọn...", command=self.pick_csv).grid(row=0, column=2)

        # Output
        ttk.Label(frm, text="Thư mục xuất kết quả:").grid(row=1, column=0, sticky='w')
        ttk.Entry(frm, textvariable=self.out_dir, width=60).grid(row=1, column=1, sticky='we', padx=6)
        ttk.Button(frm, text="Chọn...", command=self.pick_outdir).grid(row=1, column=2)

        # Date format
        ttk.Label(frm, text="Định dạng ngày trong CSV:").grid(row=2, column=0, sticky='w')
        f2 = ttk.Frame(frm); f2.grid(row=2, column=1, sticky='w', padx=6)
        ttk.Radiobutton(f2, text="day_first (dd/mm)", value="day_first", variable=self.date_format).pack(side='left', padx=6)
        ttk.Radiobutton(f2, text="month_first (mm/dd)", value="month_first", variable=self.date_format).pack(side='left')

        # Standard hours
        ttk.Label(frm, text="Giờ làm việc tiêu chuẩn/ngày:").grid(row=3, column=0, sticky='w')
        ttk.Spinbox(frm, from_=1.0, to=16.0, increment=0.5, textvariable=self.std_hours, width=10).grid(row=3, column=1, sticky='w', padx=6)

        # Run button
        ttk.Button(frm, text="Chạy phân tích", command=self.run).grid(row=4, column=1, sticky='e', pady=12)

        # Log box
        self.txt = tk.Text(frm, height=10)
        self.txt.grid(row=5, column=0, columnspan=3, sticky='nsew')
        frm.rowconfigure(5, weight=1)
        frm.columnconfigure(1, weight=1)

    def pick_csv(self):
        path = filedialog.askopenfilename(title="Chọn CSV 日報", filetypes=[("CSV", "*.csv"), ("All files", "*.*")])
        if path: self.csv_path.set(path)

    def pick_outdir(self):
        path = filedialog.askdirectory(title="Chọn thư mục lưu kết quả")
        if path: self.out_dir.set(path)

    def log(self, msg):
        self.txt.insert('end', msg + "\n"); self.txt.see('end'); self.update_idletasks()

    def run(self):
        csv_path = self.csv_path.get().strip()
        out_dir = self.out_dir.get().strip()
        if not csv_path:
            messagebox.showwarning(APP_NAME, "Hãy chọn file CSV.")
            return
        try:
            self.txt.delete('1.0', 'end')
            self.log("🔍 Đang chạy pipeline...")
            result = run_pipeline(csv_path, out_dir, self.date_format.get(), float(self.std_hours.get()))
            self.log("✅ Hoàn tất!")
            for k, v in result["outputs"].items():
                self.log(f" - {k}: {v}")
            if messagebox.askyesno(APP_NAME, "Mở thư mục kết quả?"):
                webbrowser.open(f'file:///{Path(out_dir).absolute()}')
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Lỗi: {e}")
            
from app_multi_user import main
if __name__ == "__main__":
    main()