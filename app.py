import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, font as tkfont, messagebox, ttk

from PIL import Image


SUPPORTED_OUTPUTS = ["PNG", "JPEG"]


class WebpConverterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("WebP 批量转换工具")
        self.root.geometry("720x500")
        self.root.minsize(680, 460)

        self.input_files: list[Path] = []
        self.output_dir = tk.StringVar(value=str(Path.cwd()))
        self.output_format = tk.StringVar(value="PNG")
        self.quality = tk.IntVar(value=92)
        self.status = tk.StringVar(value="请选择 WebP 文件开始转换")

        self._build_ui()

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=14)
        outer.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(
            outer,
            text="WebP → PNG/JPG 批量转换",
            font=("Microsoft YaHei", 14, "bold"),
        )
        title.pack(anchor=tk.W)

        desc = ttk.Label(
            outer,
            text="支持多选 WebP 文件，支持输出到 PNG 或 JPG。",
        )
        desc.pack(anchor=tk.W, pady=(4, 12))

        action_row = ttk.Frame(outer)
        action_row.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(action_row, text="选择 WebP 文件", command=self.select_files).pack(
            side=tk.LEFT
        )
        ttk.Button(action_row, text="清空列表", command=self.clear_files).pack(
            side=tk.LEFT, padx=8
        )

        self.file_count_label = ttk.Label(action_row, text="已选择 0 个文件")
        self.file_count_label.pack(side=tk.LEFT, padx=(12, 0))

        list_frame = ttk.LabelFrame(outer, text="待转换文件")
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.file_list = tk.Listbox(list_frame, height=12)
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(4, 10), pady=10)
        self.file_list.config(yscrollcommand=scrollbar.set)

        output_box = ttk.LabelFrame(outer, text="输出设置")
        output_box.pack(fill=tk.X, pady=(10, 0))

        path_row = ttk.Frame(output_box)
        path_row.pack(fill=tk.X, padx=10, pady=(10, 8))
        ttk.Label(path_row, text="输出目录：").pack(side=tk.LEFT)
        ttk.Entry(path_row, textvariable=self.output_dir).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=6
        )
        ttk.Button(path_row, text="浏览", command=self.select_output_dir).pack(side=tk.LEFT)

        options_row = ttk.Frame(output_box)
        options_row.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Label(options_row, text="输出格式：").pack(side=tk.LEFT)
        format_select = ttk.Combobox(
            options_row,
            textvariable=self.output_format,
            state="readonly",
            width=10,
            values=SUPPORTED_OUTPUTS,
        )
        format_select.pack(side=tk.LEFT, padx=(6, 16))

        ttk.Label(options_row, text="JPG 质量：").pack(side=tk.LEFT)
        quality_scale = ttk.Scale(
            options_row,
            from_=1,
            to=100,
            variable=self.quality,
            command=lambda _: self.quality_value.configure(text=str(self.quality.get())),
        )
        quality_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 8))
        self.quality_value = ttk.Label(options_row, width=4, text=str(self.quality.get()))
        self.quality_value.pack(side=tk.LEFT)

        footer = ttk.Frame(outer)
        footer.pack(fill=tk.X, pady=(12, 0))

        ttk.Button(
            footer,
            text="开始转换",
            command=self.start_conversion,
        ).pack(side=tk.RIGHT)

        ttk.Label(footer, textvariable=self.status, foreground="#1a6a9b").pack(side=tk.LEFT)

    def select_files(self) -> None:
        file_paths = filedialog.askopenfilenames(
            title="选择 WebP 文件",
            filetypes=[("WebP 图片", "*.webp"), ("所有文件", "*.*")],
        )
        if not file_paths:
            return

        selected = [Path(f) for f in file_paths]
        self.input_files.extend([p for p in selected if p not in self.input_files])
        self.refresh_file_list()

    def clear_files(self) -> None:
        self.input_files.clear()
        self.refresh_file_list()

    def refresh_file_list(self) -> None:
        self.file_list.delete(0, tk.END)
        for path in self.input_files:
            self.file_list.insert(tk.END, str(path))
        self.file_count_label.config(text=f"已选择 {len(self.input_files)} 个文件")

    def select_output_dir(self) -> None:
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir.set(directory)

    def start_conversion(self) -> None:
        if not self.input_files:
            messagebox.showwarning("未选择文件", "请先选择至少一个 WebP 文件。")
            return

        output_dir = Path(self.output_dir.get()).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)

        self.status.set("转换中，请稍候...")
        threading.Thread(target=self._convert_files, daemon=True).start()

    def _convert_files(self) -> None:
        target_format = self.output_format.get().upper()
        success_count = 0
        failed: list[tuple[str, str]] = []

        suffix = ".png" if target_format == "PNG" else ".jpg"

        for src in self.input_files:
            try:
                out = Path(self.output_dir.get()) / f"{src.stem}{suffix}"
                with Image.open(src) as image:
                    converted = image.convert("RGB") if target_format == "JPEG" else image
                    if target_format == "JPEG":
                        converted.save(out, "JPEG", quality=int(self.quality.get()), optimize=True)
                    else:
                        converted.save(out, "PNG")
                success_count += 1
            except Exception as exc:  # noqa: BLE001
                failed.append((str(src), str(exc)))

        self.root.after(0, lambda: self._show_result(success_count, failed))

    def _show_result(self, success_count: int, failed: list[tuple[str, str]]) -> None:
        if failed:
            err_text = "\n".join(f"- {name}: {reason}" for name, reason in failed)
            messagebox.showwarning(
                "部分文件转换失败",
                f"成功 {success_count} 个，失败 {len(failed)} 个。\n\n{err_text}",
            )
        else:
            messagebox.showinfo("转换完成", f"成功转换 {success_count} 个文件。")

        self.status.set(f"完成：成功 {success_count} 个，失败 {len(failed)} 个")


def _configure_default_font(root: tk.Tk) -> None:
    """Set a readable default UI font without breaking on unsupported systems."""
    default_font = tkfont.nametofont("TkDefaultFont")
    available = set(tkfont.families(root))

    if "Microsoft YaHei" in available:
        default_font.configure(family="Microsoft YaHei", size=10)
    elif "Segoe UI" in available:
        default_font.configure(family="Segoe UI", size=10)
    else:
        default_font.configure(size=10)


def main() -> None:
    root = tk.Tk()
    _configure_default_font(root)
    app = WebpConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
