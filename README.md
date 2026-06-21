# TempNote

**中文** | [English](#english)

---

## 中文

一款基于 PySide6 的 Windows 桌面便签应用，支持 Markdown 渲染、多便签管理、丰富的外观定制，所有功能均通过右键菜单访问。

### 下载

前往 [Releases](../../releases) 页面下载 `TempNote.exe`，无需安装 Python，直接运行。

> 数据文件 `notes.json` 会在 exe 同目录下自动生成，迁移时一并复制即可。

### 功能特性

**便签管理**
- 支持同时显示多个便签窗口
- 右键菜单新建、重命名、显示/隐藏、删除便签
- 所有便签内容与设置自动保存，重启后自动恢复

**内容编辑**
- 支持 Markdown 语法，右键打开专用 Markdown 编辑器，实时预览
- 编辑器为纯文本界面，点击保存后关闭并更新预览

**窗口管理**
- 无边框窗口，左键拖动任意位置移动
- 右下角可拖动调整窗口大小
- 支持始终置顶开关
- 支持最小化
- 支持锁定模式：锁定后窗口不可移动、文字不可编辑，鼠标可穿透点击下层内容；`Ctrl + Shift + 右键` 可在锁定状态下打开菜单

**外观定制**

所有外观选项集中在"外观设置"窗口中，修改后实时预览，点击保存生效，取消还原。

| 分组 | 选项 |
|------|------|
| 颜色 | 背景颜色与透明度、文字颜色与透明度（独立调整） |
| 字体 | 字体、字号、加粗、下划线 |
| 间距 | 字间距（px）、行距（%） |
| 布局 | 水平页边距、垂直页边距、文字对齐（居左/居中/居右） |
| 文字效果 | 外发光（透明度可调）或文字描边（像素级轮廓，颜色/宽度可调），二者互斥 |
| 边框 | 启用/禁用、颜色、宽度、圆角半径 |
| 外边框发光 | 窗口外侧柔光晕，颜色/半径/强度可调 |

**其他**
- 界面语言切换（中文 / English）
- 右键菜单可直接切换便签、新建、重命名、删除

### 快捷操作

| 操作 | 方式 |
|------|------|
| 打开右键菜单 | 右键单击便签 |
| 移动便签 | 左键拖动 |
| 调整大小 | 拖动右下角 |
| 锁定状态下打开菜单 | `Ctrl + Shift + 右键` |

### 从源码运行

**环境要求：** Windows 10 / 11，Python 3.10+

```bash
pip install PySide6
python main.py
```

### 自行打包

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name TempNote main.py
# 输出在 dist/TempNote.exe
```

### 数据存储

所有便签内容和设置保存在 `notes.json`（与 `main.py` / exe 同目录），删除该文件将重置所有数据。

---

## English

<a name="english"></a>

A Windows desktop sticky note application built with PySide6. Supports Markdown rendering, multiple notes, and rich appearance customization — all accessible via right-click menu.

### Download

Head to the [Releases](../../releases) page and download `TempNote.exe`. No Python installation required — just run it.

> Settings and notes are saved to `notes.json` in the same folder as the exe. Copy it along when migrating.

### Features

**Note Management**
- Multiple note windows open simultaneously
- Create, rename, show/hide, and delete notes via right-click menu
- All content and settings are auto-saved and restored on restart

**Content Editing**
- Markdown syntax with a dedicated plain-text editor and live preview
- Clicking Save closes the editor and updates the preview instantly

**Window Management**
- Frameless window; drag anywhere to move
- Resize by dragging the bottom-right corner
- Always-on-top toggle
- Minimize support
- Lock mode: freezes movement and editing, enables mouse passthrough so clicks reach content underneath; `Ctrl + Shift + Right-click` opens the menu while locked

**Appearance**

All appearance options are in the Appearance Settings window with live preview. Changes apply immediately; Cancel reverts them.

| Group | Options |
|-------|---------|
| Colors | Background color & opacity, text color & opacity (independent) |
| Font | Family, size, bold, underline |
| Spacing | Letter spacing (px), line height (%) |
| Layout | H-padding, V-padding, text alignment (left / center / right) |
| Text Effects | Outer glow (adjustable opacity) or stroke (pixel-accurate outline, color & width) — mutually exclusive |
| Border | Enable/disable, color, width, corner radius |
| Outer Glow | Soft halo around the window edge — color, radius, strength |

**Other**
- UI language toggle (中文 / English)
- Switch, create, rename, or delete notes directly from the right-click menu

### Shortcuts

| Action | How |
|--------|-----|
| Open context menu | Right-click on note |
| Move note | Left-click drag |
| Resize note | Drag bottom-right corner |
| Menu while locked | `Ctrl + Shift + Right-click` |

### Run from Source

**Requirements:** Windows 10 / 11, Python 3.10+

```bash
pip install PySide6
python main.py
```

### Build Yourself

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name TempNote main.py
# Output: dist/TempNote.exe
```

### Data Storage

All notes and settings are saved in `notes.json` next to `main.py` or the exe. Deleting this file resets everything to defaults.
