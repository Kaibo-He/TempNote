# TempNote

**中文** | [English](#english)

---

## 中文

一款基于 PySide6 的 Windows 桌面便签应用，支持 Markdown 渲染、多便签管理与丰富的外观定制，所有功能均通过右键菜单访问。

### 下载

前往 [Releases](../../releases) 页面下载 `TempNote.exe`，无需安装 Python，直接运行。

> 数据文件 `notes.json` 会在 exe 同目录下自动生成，迁移时一并复制即可。

---

### 功能特性

#### 便签管理

- 同时显示多个便签窗口，每个便签独立设置外观与内容
- 右键菜单 → 便签列表：查看全部便签，支持单独显示/隐藏/删除
- 右键菜单 → 清空所有便签：一键清空并创建新的空白便签
- 新建便签自动出现在当前便签右侧，避免重叠
- 所有内容与设置实时自动保存，重启后自动恢复
- 单实例运行：重复启动时自动唤起已运行的程序

#### 内容编辑

- 支持 GitHub Flavored Markdown（标题、粗体、斜体、代码块、链接、表格等）
- **双击**便签正文直接打开 Markdown 编辑器，输入时实时预览
- 编辑器界面跟随系统深色/浅色主题

#### 窗口管理

- 左键拖动任意位置移动
- 四边及四角均可拖动调整窗口大小，调整区域与页边距一致
- 支持始终置顶开关
- **最小化到系统托盘**：右键 → 最小化到托盘；双击托盘图标或托盘右键 → 显示全部便签
- **锁定模式**：锁定后窗口不可移动、文字不可编辑，鼠标完全穿透至下层窗口；`Ctrl + Alt + 右键` 可在锁定状态下打开菜单

#### 外观定制

所有外观选项集中在"外观设置"窗口，修改后实时预览，点击保存生效，取消还原。

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
| 显示/隐藏全部便签（切换） | `Ctrl + Alt + H` |

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
- **管理员权限：** 生成的 exe 启动时会请求 UAC（全局快捷键需要）
- **中间文件：** `build/`、`dist/` 已在 `.gitignore` 中，无需提交

手动调用 PyInstaller 时也可参考 `build.py` 生成的 `build/TempNote.spec`。

### 数据存储

所有便签内容和设置保存在 `notes.json`（与 `main.py` / exe 同目录）。删除该文件将重置所有数据。

---

## English

<a name="english"></a>

A Windows desktop sticky note app built with PySide6. Supports Markdown rendering, multiple notes, and rich appearance customization — all accessible via right-click menu.

### Download

Head to the [Releases](../../releases) page and download `TempNote.exe`. No Python installation required — just run it.

> Notes and settings are saved to `notes.json` in the same folder as the exe. Copy it along when migrating.

---

### Features

#### Note Management

- Multiple note windows open simultaneously, each with independent appearance and content
- Right-click → Notes list: view all notes with per-note show / hide / delete
- Right-click → Clear All Notes: wipe everything and start with one fresh note
- New notes appear to the right of the current note to avoid overlap
- All content and settings are auto-saved; restored automatically on restart
- Single-instance: re-launching the app brings the running instance to the front

#### Content Editing

- GitHub Flavored Markdown (headings, bold, italic, code blocks, links, tables, etc.)
- **Double-click** the note body to open the Markdown editor with live preview
- Editor UI follows the system dark/light theme

#### Window Management

- Drag anywhere to move
- All four edges and corners are resizable (drag zone matches the padding size)
- Always-on-top toggle
- **Minimize to tray**: right-click → Minimize to Tray; double-click the tray icon or use tray → Show All Notes to restore
- **Lock mode**: freezes movement and editing, enables full mouse passthrough to windows below; `Ctrl + Alt + Right-click` opens the menu while locked

#### Appearance

All options live in the Appearance Settings window with live preview. Cancel reverts all changes.

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
| Toggle show / hide all notes | `Ctrl + Alt + H` |

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
- **Admin / UAC:** the built exe requests elevation on launch (required for global hotkeys)
- **Generated dirs:** `build/` and `dist/` are gitignored — no need to commit them

For manual PyInstaller runs, see the generated `build/TempNote.spec`.

### Data Storage

All notes and settings are saved in `notes.json` next to `main.py` or the exe. Deleting this file resets everything to defaults.
