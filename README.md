# TempNote

**中文** | [English](#english)

---

一款基于 PySide6 的 Windows 桌面便签应用，支持 Markdown 渲染、多便签管理，可通过设置调整语言与外观，所有功能均通过右键菜单访问。

### 下载

前往 [Releases](../../releases) 页面下载 `TempNote.exe`，无需安装 Python，直接运行。

> 首次运行自动生成 `notes.json` 与 `attachments/`；迁移数据见下方「数据存储」。

---

### 功能特性

#### 便签管理

- 多便签并行，内容与外观各自独立
- 右键菜单：便签列表（显示/隐藏/删除）、清空便签、清空所有便签
- 新建便签出现在当前便签右侧；自动保存并在重启后恢复；单实例运行

#### 内容编辑

- 支持 GitHub Flavored Markdown；部分常用 HTML 标签亦可渲染（非完整 HTML，复杂用法不保证有效），不可与 Markdown 混用
- **双击**便签正文直接打开 Markdown 编辑器，输入时实时预览
- 编辑器界面跟随系统深色/浅色主题
- **拖入图片**：在编辑器中将本地图片文件拖入即可插入（支持 PNG、JPG、GIF、BMP、WebP、SVG、ICO），复制到 `attachments/` 并以 `![描述](attachments/xxx.png)` 引用；便签中随窗口宽度自动缩放显示

#### 窗口管理

- 左键拖动任意位置移动
- 四边及四角均可拖动调整窗口大小，调整区域与页边距一致
- 支持始终置顶开关
- **最小化到系统托盘**：右键 → 最小化到托盘；双击托盘图标或托盘右键 → 显示全部便签
- **锁定模式**：锁定后窗口不可移动、文字不可编辑，鼠标完全穿透至下层窗口；`Ctrl + Alt + 右键` 可在锁定状态下打开菜单（单张便签）

#### 设置

右键菜单 → **设置…** 打开设置窗口，修改后实时预览；**保存** 生效，**取消** 还原。

- **通用**：界面语言（中文 / English），切换后立即生效
- **外观**（针对当前便签）：颜色、字体、间距、布局、文字效果、高亮文字、边框等

---

### 快捷操作

| 操作 | 方式 |
|:-----|:-----|
| 打开右键菜单 | 右键单击便签 |
| 移动便签 | 左键拖动 |
| 调整大小 | 拖动四边或四角 |
| 打开 Markdown 编辑器 | 双击便签正文 |
| 锁定状态下打开菜单 | `Ctrl + Alt + 右键` |
| **全局快捷键** | |
| 新建便签 | `Ctrl + Alt + N` |
| 显示/最小化全部便签 | `Ctrl + Alt + H` |
| 锁定/解锁全部便签 | `Ctrl + Alt + L` |

---

### 从源码运行

**环境要求：** Windows 10 / 11，Python 3.10+

```bash
pip install PySide6
python main.py
```

### 自行打包

**环境要求：** 与从源码运行相同，需已安装 Python 3.10+。

项目根目录提供了 `build.py`，会自动安装依赖、生成 spec 并调用 PyInstaller 打包：

```bash
python build.py           # 交互输入版本号（格式 x.x.x，如 1.1.0）
python build.py 1.1.0     # 直接指定版本号
```

- **输出路径：** `dist/v{版本号}/TempNote.exe`（例如 `dist/v1.1.0/TempNote.exe`）
- **同版本重打包：** 会先删除 `dist/v{版本号}/` 与 `build/pyinstaller/` 缓存，再生成新 exe，避免残留旧文件
- **管理员权限：** 默认以管理员身份运行（启动时 UAC 提权），全局快捷键需此权限
- **中间文件：** `build/`、`dist/` 已在 `.gitignore` 中，无需提交

手动调用 PyInstaller 时也可参考 `build.py` 生成的 `build/TempNote.spec`。

### 数据存储

- `notes.json` — 便签内容与设置，自动保存，与程序同目录
- `attachments/` — 图片相对路径引用、迁移时需一并复制
- 清理与重置 — 未引用图片保存时自动清理；删除 `notes.json` 重置全部数据

迁移数据：将 `notes.json` 与 `attachments/` 复制到新环境程序同目录下即可。

---

<a name="english"></a>

A Windows desktop sticky note app built with PySide6. Supports Markdown rendering, multiple notes, and configurable language and appearance — all accessible via right-click menu.

### Download

Head to the [Releases](../../releases) page and download `TempNote.exe`. No Python installation required — just run it.

> Created automatically on first run; see **Data Storage** below for migration.

---

### Features

#### Note Management

- Multiple notes with independent content and appearance
- Right-click menu: notes list (show / hide / delete), clear note, clear all notes
- New notes open beside the current one; auto-save and restore on restart; single-instance

#### Content Editing

- GitHub Flavored Markdown; some common HTML tags also render (not a full HTML engine — complex usage not guaranteed), not mixable with Markdown
- **Double-click** the note body to open the Markdown editor with live preview
- Editor UI follows the system dark/light theme
- **Drag & drop images**: drop a local image file into the editor to insert it (PNG, JPG, GIF, BMP, WebP, SVG, ICO); copied to `attachments/` and referenced as `![alt](attachments/xxx.png)`; images scale to the note width

#### Window Management

- Drag anywhere to move
- All four edges and corners are resizable (drag zone matches the padding size)
- Always-on-top toggle
- **Minimize to tray**: right-click → Minimize to Tray; double-click the tray icon or use tray → Show All Notes to restore
- **Lock mode**: freezes movement and editing, enables full mouse passthrough to windows below; `Ctrl + Alt + Right-click` opens the menu while locked (per note)

#### Settings

Right-click → **Settings…** opens the settings window with live preview; **Save** applies changes, **Cancel** reverts.

- **General**: UI language (中文 / English), takes effect immediately
- **Appearance** (per note): colors, font, spacing, layout, text effects, highlight, border, etc.

---

### Shortcuts

| Action | How |
|:-------|:----|
| Open context menu | Right-click on note |
| Move note | Left-click drag |
| Resize note | Drag any edge or corner |
| Open Markdown editor | Double-click note body |
| Menu while locked | `Ctrl + Alt + Right-click` |
| **Global hotkeys** | |
| New note | `Ctrl + Alt + N` |
| Toggle show all notes / minimize to tray | `Ctrl + Alt + H` |
| Lock / unlock all notes | `Ctrl + Alt + L` |

---

### Run from Source

**Requirements:** Windows 10 / 11, Python 3.10+

```bash
pip install PySide6
python main.py
```

### Build Yourself

**Requirements:** Same as running from source — Python 3.10+.

Use `build.py` in the project root. It installs dependencies, generates the spec file, and invokes PyInstaller:

```bash
python build.py           # prompt for version (x.x.x, e.g. 1.1.0)
python build.py 1.1.0     # specify version on the command line
```

- **Output:** `dist/v{version}/TempNote.exe` (e.g. `dist/v1.1.0/TempNote.exe`)
- **Rebuild same version:** removes `dist/v{version}/` and the `build/pyinstaller/` cache first, then produces a fresh exe
- **Admin / UAC:** runs as administrator by default (UAC prompt on launch); required for global hotkeys
- **Generated dirs:** `build/` and `dist/` are gitignored — no need to commit them

For manual PyInstaller runs, see the generated `build/TempNote.spec`.

### Data Storage

- `notes.json` — note content and settings; auto-saved in the same folder as the app
- `attachments/` — images referenced by relative paths; copy together when migrating
- Cleanup & reset — unreferenced images removed on save; deleting `notes.json` resets all data

To migrate: copy `notes.json` and `attachments/` to the same folder as the app on the new machine.
