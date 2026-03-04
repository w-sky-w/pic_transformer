import threading
from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, font as tkfont, messagebox, ttk

from PIL import Image


@dataclass(frozen=True)
class ConversionProfile:
    """Conversion pipeline definition for current and future formats."""

    key: str
    display_name: str
    input_patterns: tuple[str, ...]
    output_formats: tuple[str, ...]


CONVERSION_PROFILES: dict[str, ConversionProfile] = {
    "webp": ConversionProfile(
        key="webp",
        display_name="WebP 图片 (*.webp)",
        input_patterns=("*.webp",),
        output_formats=("PNG", "JPEG"),
    ),
    # 预留接口：后续可直接在这里添加更多类型
    "png": ConversionProfile(
        key="png",
        display_name="PNG 图片 (*.png) [即将支持]",
        input_patterns=("*.png",),
        output_formats=("JPEG",),
    ),
    "rpgmvp": ConversionProfile(
        key="rpgmvp",
        display_name="RPGMVP 文件 (*.rpgmvp) [即将支持]",
        input_patterns=("*.rpgmvp",),
        output_formats=("PNG",),
    ),
}

SUPPORTED_IMPLEMENTED_KEYS = {"webp"}


class WebpConverterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("图片批量转换工具")
        self.root.geometry("820x560")
        self.root.minsize(760, 520)

        self.input_files: list[Path] = []
        self.output_dir = tk.StringVar(value=str(Path.cwd()))
        self.source_type = tk.StringVar(value="webp")
        self.output_format = tk.StringVar(value="PNG")
        self.status = tk.StringVar(value="请选择文件，然后点击【确定并开始转换】")

        self.convert_btn: ttk.Button | None = None
        self.progress = tk.DoubleVar(value=0)

        self._build_ui()
        self._on_source_type_changed()

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=16)
        outer.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(outer)
        header.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(
            header,
            text="批量图片转换器",
            font=("Microsoft YaHei", 16, "bold"),
        ).pack(anchor=tk.W)
        ttk.Label(
            header,
            text="当前支持 WebP 转 PNG/JPG，已预留 PNG、RPGMVP 扩展接口。",
            foreground="#4a5568",
        ).pack(anchor=tk.W, pady=(4, 0))

        task_box = ttk.LabelFrame(outer, text="1) 选择转换任务")
        task_box.pack(fill=tk.X, pady=(0, 10))

        task_row = ttk.Frame(task_box)
        task_row.pack(fill=tk.X, padx=12, pady=10)

        ttk.Label(task_row, text="输入文件类型：").pack(side=tk.LEFT)
        source_values = [
            f"{profile.key} - {profile.display_name}" for profile in CONVERSION_PROFILES.values()
        ]
        self.source_combo = ttk.Combobox(task_row, state="readonly", width=36, values=source_values)
        self.source_combo.current(0)
        self.source_combo.pack(side=tk.LEFT, padx=(8, 14))
        self.source_combo.bind("<<ComboboxSelected>>", self._on_source_combo_selected)

        self.support_badge = ttk.Label(task_row, text="已支持", foreground="#2f855a")
        self.support_badge.pack(side=tk.LEFT)

        file_box = ttk.LabelFrame(outer, text="2) 选择待转换文件")
        file_box.pack(fill=tk.BOTH, expand=True)

        file_toolbar = ttk.Frame(file_box)
        file_toolbar.pack(fill=tk.X, padx=10, pady=(10, 8))

        ttk.Button(file_toolbar, text="添加文件", command=self.select_files).pack(side=tk.LEFT)
        ttk.Button(file_toolbar, text="清空列表", command=self.clear_files).pack(side=tk.LEFT, padx=8)
        self.file_count_label = ttk.Label(file_toolbar, text="已选择 0 个文件")
        self.file_count_label.pack(side=tk.LEFT, padx=(10, 0))

        self.file_list = tk.Listbox(file_box, height=12, activestyle="none", borderwidth=0)
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=(0, 10))

        scrollbar = ttk.Scrollbar(file_box, orient=tk.VERTICAL, command=self.file_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(4, 10), pady=(0, 10))
        self.file_list.config(yscrollcommand=scrollbar.set)

        output_box = ttk.LabelFrame(outer, text="3) 输出设置")
        output_box.pack(fill=tk.X, pady=(10, 0))

        path_row = ttk.Frame(output_box)
        path_row.pack(fill=tk.X, padx=10, pady=(10, 8))
        ttk.Label(path_row, text="输出目录：").pack(side=tk.LEFT)
        ttk.Entry(path_row, textvariable=self.output_dir).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=6
        )
        ttk.Button(path_row, text="浏览", command=self.select_output_dir).pack(side=tk.LEFT)

        format_row = ttk.Frame(output_box)
        format_row.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Label(format_row, text="输出格式：").pack(side=tk.LEFT)
        self.format_combo = ttk.Combobox(
            format_row,
            textvariable=self.output_format,
            state="readonly",
            width=10,
        )
        self.format_combo.pack(side=tk.LEFT, padx=(6, 16))
        ttk.Label(
            format_row,
            text="说明：JPG 将使用最高质量保存，无需手动设置质量参数。",
            foreground="#718096",
        ).pack(side=tk.LEFT)

        action_box = ttk.LabelFrame(outer, text="4) 开始执行")
        action_box.pack(fill=tk.X, pady=(10, 0))

        action_row = ttk.Frame(action_box)
        action_row.pack(fill=tk.X, padx=10, pady=(10, 10))

        self.convert_btn = ttk.Button(
            action_row,
            text="✅ 确定并开始转换",
            command=self.start_conversion,
        )
        self.convert_btn.pack(side=tk.RIGHT)

        ttk.Label(action_row, textvariable=self.status, foreground="#1a6a9b").pack(side=tk.LEFT)

        ttk.Progressbar(
            action_box,
            variable=self.progress,
            maximum=100,
            mode="determinate",
        ).pack(fill=tk.X, padx=10, pady=(0, 10))

    def _on_source_combo_selected(self, _event: tk.Event) -> None:
        profile_key = self.source_combo.get().split(" - ", maxsplit=1)[0]
        self.source_type.set(profile_key)
        self._on_source_type_changed()

    def _on_source_type_changed(self) -> None:
        profile = CONVERSION_PROFILES[self.source_type.get()]
        self.format_combo.configure(values=profile.output_formats)
        self.format_combo.current(0)

        if profile.key in SUPPORTED_IMPLEMENTED_KEYS:
            self.support_badge.configure(text="已支持", foreground="#2f855a")
            self.status.set("请选择文件，然后点击【确定并开始转换】")
        else:
            self.support_badge.configure(text="预留接口", foreground="#b7791f")
            self.status.set("该类型暂未实现，仅预留接口。")

    def _current_profile(self) -> ConversionProfile:
        return CONVERSION_PROFILES[self.source_type.get()]

    def select_files(self) -> None:
        profile = self._current_profile()
        filetypes = [(profile.display_name, " ".join(profile.input_patterns)), ("所有文件", "*.*")]
        file_paths = filedialog.askopenfilenames(title="选择待转换文件", filetypes=filetypes)
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
        profile = self._current_profile()
        if profile.key not in SUPPORTED_IMPLEMENTED_KEYS:
            messagebox.showinfo("暂未支持", "该文件类型的转换逻辑尚未实现，当前仅保留扩展接口。")
            return

        if not self.input_files:
            messagebox.showwarning("未选择文件", "请先选择至少一个待转换文件。")
            return

        output_dir = Path(self.output_dir.get()).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)

        self.progress.set(0)
        self.status.set("转换中，请稍候...")
        if self.convert_btn:
            self.convert_btn.config(state=tk.DISABLED)

        threading.Thread(target=self._convert_files, daemon=True).start()

    def _convert_files(self) -> None:
        target_format = self.output_format.get().upper()
        success_count = 0
        failed: list[tuple[str, str]] = []

        suffix = ".png" if target_format == "PNG" else ".jpg"
        total = len(self.input_files)

        for index, src in enumerate(self.input_files, start=1):
            try:
                out = Path(self.output_dir.get()) / f"{src.stem}{suffix}"
                with Image.open(src) as image:
                    converted = image.convert("RGB") if target_format == "JPEG" else image
                    if target_format == "JPEG":
                        converted.save(out, "JPEG", quality=100, optimize=True)
                    else:
                        converted.save(out, "PNG")
                success_count += 1
            except Exception as exc:  # noqa: BLE001
                failed.append((str(src), str(exc)))

            progress = (index / total) * 100
            self.root.after(0, lambda value=progress: self.progress.set(value))

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

        if self.convert_btn:
            self.convert_btn.config(state=tk.NORMAL)
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


def _configure_style() -> None:
    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")


def main() -> None:
    root = tk.Tk()
    _configure_default_font(root)
    _configure_style()
    app = WebpConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
