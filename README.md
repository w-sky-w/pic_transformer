# WebP 批量转换工具（Python + EXE）

这是一个用 Python 开发的桌面工具，可将 WebP 图片批量转换为 PNG 或 JPG（JPEG），并支持打包成 Windows 下可直接运行的 `.exe` 文件。

## 功能

- 批量选择 `.webp` 文件
- 输出格式可选：`PNG` / `JPEG`
- 自定义输出目录
- JPEG 质量可调（1-100）
- 图形界面（Tkinter）
- 一键打包 EXE（PyInstaller）

## 环境要求

- Python 3.10+
- Windows（用于生成 `.exe`）

## 本地运行

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## 打包 EXE（Windows）

在 Windows 命令行中运行：

```bat
build_exe.bat
```

打包完成后可在 `dist/webp_converter.exe` 找到可执行文件。

## 说明

- 转 JPG 时会自动将图片转换为 RGB，避免透明通道导致报错。
- 输出文件名默认与原文件同名，仅后缀变化。
