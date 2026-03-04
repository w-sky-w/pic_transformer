# 图片批量转换工具（Python + EXE）

这是一个用 Python 开发的桌面工具，当前可将 WebP 图片批量转换为 PNG 或 JPG（JPEG），并支持打包成 Windows 下可直接运行的 `.exe` 文件。

## 功能

- 批量选择并转换文件
- 明确的“✅ 确定并开始转换”按钮
- 输出格式可选：`PNG` / `JPEG`
- 自定义输出目录
- 转换进度条与状态提示
- 图形界面（Tkinter + ttk）
- 一键打包 EXE（PyInstaller）

## 扩展能力（预留接口）

代码已抽象为“转换任务配置”结构，后续可直接扩展更多输入类型（例如 PNG、RPGMVP 等）。

> 当前仅 `webp` 转换逻辑已实现；`png` / `rpgmvp` 作为后续扩展入口保留在 UI 与配置中。

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
- JPG 默认按最高质量（quality=100）导出，不再提供质量滑杆。
- 输出文件名默认与原文件同名，仅后缀变化。

## 常见问题

### 打开 EXE 报错：`expected integer but got "YaHei"`

这是因为某些环境下 Tk 对字体字符串解析不兼容。当前版本已改为通过 Tk 的字体对象设置默认字体，并带有自动回退（`Microsoft YaHei` → `Segoe UI` → 系统默认字体），不再使用容易触发解析问题的字符串方式。
