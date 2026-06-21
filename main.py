"""
TempNote — Windows 桌面便签

模块结构（自上而下）：
    常量与国际化 → 图形效果 → Markdown 编辑器 → 外观对话框
    → 便签控件/窗口 → 全局快捷键 → 应用管理器 → 入口
"""

import sys
import json
import os
import re
import uuid
import copy
import ctypes
import ctypes.wintypes

from PySide6.QtWidgets import (
    QApplication, QTextEdit, QWidget, QVBoxLayout, QMenu, QColorDialog,
    QInputDialog, QWidgetAction, QSlider, QHBoxLayout,
    QLabel, QGraphicsDropShadowEffect, QPushButton,
    QCheckBox, QSpinBox, QFontComboBox, QScrollArea, QGroupBox, QButtonGroup,
    QSystemTrayIcon, QGridLayout, QMessageBox, QDialogButtonBox,
)
from PySide6.QtCore import Qt, QTimer, QPoint, QRectF, QPointF, QSize
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtGui import (
    QColor, QFont, QAction, QPainter, QPen, QPixmap, QIcon,
    QTextCharFormat, QTextCursor, QTextBlockFormat, QTextDocument,
    QPolygonF,
)


# ──────────────────────────────────────────────────────────
# 数据文件路径（打包为 exe 时定位到 exe 同级目录）
# ──────────────────────────────────────────────────────────

if getattr(sys, "frozen", False):
    _app_dir = os.path.dirname(sys.executable)
else:
    _app_dir = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(_app_dir, "notes.json")

# ──────────────────────────────────────────────────────────
# 国际化
# ──────────────────────────────────────────────────────────

STRINGS: dict[str, dict[str, str]] = {
    "zh": {
        # 右键菜单
        "rename_note":     "重命名便签…",
        "new_note":        "新建便签",
        "note_list":       "便签列表",
        "note_current":    "当前",
        "note_show":       "显示",
        "note_hide":       "隐藏",
        "note_delete":     "删除",
        "edit_md":         "编辑便签…",
        "appearance":      "外观设置…",
        "always_on_top":   "始终置顶",
        "lock":            "锁定",
        "language":        "语言",
        "clear_notes":     "清空所有便签…",
        "minimize":        "最小化到托盘",
        "quit":            "退出",
        "tray_show_all":   "显示全部便签",
        "tray_tooltip":    "TempNote — 双击恢复便签",
        # 对话框
        "rename_title":    "重命名便签",
        "rename_prompt":   "请输入便签名称：",
        "delete_title":    "删除便签",
        "delete_prompt":   "确认删除「{name}」？",
        # 外观设置窗口
        "ap_title":        "外观设置 — {name}",
        "col_group":       "颜色",
        "col_bg":          "背景颜色",
        "col_text":        "文字颜色",
        "opacity":         "透明度",
        "font_group":      "字体",
        "font_lbl":        "字体",
        "size_lbl":        "字号",
        "spacing_group":   "间距",
        "l_spacing":       "字间距",
        "ln_spacing":      "行  距",
        "fx_group":        "文字效果",
        "glow_on":         "启用发光",
        "glow_col_pick":   "选择发光颜色",
        "stroke_on":       "启用描边",
        "stroke_col_pick": "选择描边颜色",
        "width_lbl":       "宽度",
        "fx_hint":         "* 发光与描边互斥",
        "border_group":    "边框",
        "border_on":       "启用边框",
        "border_col_pick": "选择边框颜色",
        "border_w_lbl":    "边框宽度",
        "border_r_lbl":    "圆角半径",
        "layout_group":    "布局",
        "padding_x_lbl":   "水平边距",
        "padding_y_lbl":   "垂直边距",
        "align_lbl":       "对齐",
        "save":            "保存",
        "cancel":          "取消",
        "yes":             "是",
        "no":              "否",
        "clear_notes_prompt": "确认删除全部便签？此操作不可撤销。",
        # Markdown 编辑器
        "md_title":        "Markdown 编辑器 — {name}",
        # 语言选项显示名
        "lang_name_zh":    "中文",
        "lang_name_en":    "English",
    },
    "en": {
        "rename_note":     "Rename Note…",
        "new_note":        "New Note",
        "note_list":       "Notes",
        "note_current":    "current",
        "note_show":       "Show",
        "note_hide":       "Hide",
        "note_delete":     "Delete",
        "edit_md":         "Edit Note…",
        "appearance":      "Appearance…",
        "always_on_top":   "Always on Top",
        "lock":            "Lock",
        "language":        "Language",
        "clear_notes":     "Clear All Notes…",
        "minimize":        "Minimize to Tray",
        "quit":            "Quit",
        "tray_show_all":   "Show All Notes",
        "tray_tooltip":    "TempNote — Double-click to restore",
        "rename_title":    "Rename Note",
        "rename_prompt":   "Enter note name:",
        "delete_title":    "Delete Note",
        "delete_prompt":   'Delete "{name}"?',
        "ap_title":        "Appearance — {name}",
        "col_group":       "Colors",
        "col_bg":          "Background",
        "col_text":        "Text",
        "opacity":         "Opacity",
        "font_group":      "Font",
        "font_lbl":        "Font",
        "size_lbl":        "Size",
        "spacing_group":   "Spacing",
        "l_spacing":       "Letters",
        "ln_spacing":      "Lines",
        "fx_group":        "Text Effects",
        "glow_on":         "Enable Glow",
        "glow_col_pick":   "Glow Color",
        "stroke_on":       "Enable Stroke",
        "stroke_col_pick": "Stroke Color",
        "width_lbl":       "Width",
        "fx_hint":         "* Glow and stroke are mutually exclusive",
        "border_group":    "Border",
        "border_on":       "Enable Border",
        "border_col_pick": "Border Color",
        "border_w_lbl":    "Width",
        "border_r_lbl":    "Radius",
        "layout_group":    "Layout",
        "padding_x_lbl":   "H-Padding",
        "padding_y_lbl":   "V-Padding",
        "align_lbl":       "Align",
        "save":            "Save",
        "cancel":          "Cancel",
        "yes":             "Yes",
        "no":              "No",
        "clear_notes_prompt": "Delete all notes? This cannot be undone.",
        "md_title":        "Markdown Editor — {name}",
        "lang_name_zh":    "中文",
        "lang_name_en":    "English",
    },
}

_lang = "zh"


def set_lang(lang: str):
    global _lang
    _lang = lang if lang in STRINGS else "zh"


def t(key: str, **kw) -> str:
    s = STRINGS.get(_lang, STRINGS["zh"]).get(key) or STRINGS["zh"].get(key, key)
    return s.format(**kw) if kw else s


def _ask_yes_no(
    parent: QWidget | None,
    title: str,
    text: str,
    *,
    center_buttons: bool = False,
) -> bool:
    """显示是/否确认框。center_buttons=True 时按钮水平居中。"""
    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    box.setDefaultButton(QMessageBox.StandardButton.No)
    box.button(QMessageBox.StandardButton.Yes).setText(t("yes"))
    box.button(QMessageBox.StandardButton.No).setText(t("no"))
    if center_buttons:
        btn_box = box.findChild(QDialogButtonBox)
        if btn_box:
            btn_box.setCenterButtons(True)
    return box.exec() == QMessageBox.StandardButton.Yes


class _WinMsg(ctypes.Structure):
    """Windows MSG 结构，供 nativeEvent 解析消息。"""
    _fields_ = [
        ("hWnd",    ctypes.wintypes.HWND),
        ("message", ctypes.wintypes.UINT),
        ("wParam",  ctypes.wintypes.WPARAM),
        ("lParam",  ctypes.wintypes.LPARAM),
        ("time",    ctypes.wintypes.DWORD),
        ("pt",      ctypes.wintypes.POINT),
    ]


# ──────────────────────────────────────────────────────────
# 默认设置与外观键列表
# ──────────────────────────────────────────────────────────

APPEARANCE_KEYS = [
    "bg_opacity", "text_opacity", "bg_color", "text_color",
    "font_family", "font_size",
    "letter_spacing", "line_spacing",
    "glow_enabled", "glow_color", "glow_opacity",
    "stroke_enabled", "stroke_color", "stroke_width",
    "border_enabled", "border_color", "border_width", "border_radius",
    "padding_x", "padding_y", "text_align",
]

DEFAULT_SETTINGS = {
    "content": "",
    "x": 200, "y": 200, "width": 320, "height": 320,
    "always_on_top": True,
    "bg_opacity": 50,  "text_opacity": 100,
    "bg_color": "#000000", "text_color": "#FFFFFF",
    "font_family": "Microsoft YaHei", "font_size": 12,
    "letter_spacing": 0, "line_spacing": 100,
    "glow_enabled": True, "glow_color": "#FFFF00", "glow_opacity": 100,
    "stroke_enabled": False, "stroke_color": "#55007f", "stroke_width": 2,
    "border_enabled": False, "border_color": "#FFFFFF",
    "border_width": 1, "border_radius": 0,
    "padding_x": 8,
    "padding_y": 8,
    "text_align": "top-left",
    "locked": False,
}


# ──────────────────────────────────────────────────────────
# 图形效果（发光 / 描边）
# ──────────────────────────────────────────────────────────

class ClippedGlowEffect(QGraphicsDropShadowEffect):
    """裁剪版 QGraphicsDropShadowEffect：边界矩形不向外扩展，避免效果溢出窗口。"""
    def boundingRectFor(self, rect: QRectF) -> QRectF:
        return rect


class TextStrokeEffect(QGraphicsDropShadowEffect):
    """
    真实文字描边：将源像素图染色后在四周偏移绘制，再盖上原图。
    继承 QGraphicsDropShadowEffect 仅为利用 Qt 的图形效果注册机制；
    实际渲染完全在 draw() 中自定义。
    """

    def __init__(self, color: QColor, width: int, parent=None):
        super().__init__(parent)
        self._stroke_color = QColor(color)
        self._stroke_width = max(1, width)
        # 禁用父类阴影，以免干扰
        self.setBlurRadius(0)
        self.setOffset(0, 0)
        self.setColor(QColor(0, 0, 0, 0))

    def boundingRectFor(self, rect: QRectF) -> QRectF:
        return rect  # 裁剪到控件边界，避免窗口渲染错误

    def draw(self, painter: QPainter):
        # PySide6 中 sourcePixmap 直接返回 QPixmap，偏移量固定为 (0, 0)
        src = self.sourcePixmap(Qt.CoordinateSystem.LogicalCoordinates)
        if src.isNull():
            self.drawSource(painter)
            return

        # 用描边颜色对源像素图染色
        stroke_px = QPixmap(src.size())
        stroke_px.fill(Qt.GlobalColor.transparent)
        sp = QPainter(stroke_px)
        sp.drawPixmap(0, 0, src)
        sp.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        sp.fillRect(stroke_px.rect(), self._stroke_color)
        sp.end()

        # 在圆形范围内的各偏移位置绘制描边层
        # 最外圈做透明度渐出，消除硬边锯齿
        w = self._stroke_width
        r2 = w * w
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        for dx in range(-w, w + 1):
            for dy in range(-w, w + 1):
                if dx == 0 and dy == 0:
                    continue
                dist2 = dx * dx + dy * dy
                if dist2 <= r2:
                    dist = dist2 ** 0.5
                    edge = dist - (w - 1.0)
                    alpha = max(0.0, 1.0 - edge) if edge > 0 else 1.0
                    painter.setOpacity(alpha)
                    painter.drawPixmap(QPointF(dx, dy), stroke_px)
        painter.setOpacity(1.0)
        painter.restore()

        # 原始内容盖在最上层
        self.drawSource(painter)


# ──────────────────────────────────────────────────────────
# Markdown 编辑器（输入控件 + 对话框）
# ──────────────────────────────────────────────────────────

class MDSourceEdit(QTextEdit):
    """Markdown 源码编辑框：Tab 缩进、自动列表续行。"""
    def keyPressEvent(self, event):
        key  = event.key()
        mods = event.modifiers()
        Mod  = Qt.KeyboardModifier

        if key == Qt.Key.Key_Tab and not (mods & Mod.ShiftModifier):
            self.textCursor().insertText('\t')
            return

        if key == Qt.Key.Key_Backtab or (
            key == Qt.Key.Key_Tab and (mods & Mod.ShiftModifier)
        ):
            cursor = self.textCursor()
            cursor.select(cursor.SelectionType.LineUnderCursor)
            line = cursor.selectedText()
            if line.startswith('\t'):
                cursor.insertText(line[1:])
            elif line.startswith('    '):
                cursor.insertText(line[4:])
            return

        if key == Qt.Key.Key_Return and not (mods & Mod.ShiftModifier):
            cursor   = self.textCursor()
            line     = cursor.block().text()
            indent   = len(line) - len(line.lstrip('\t '))
            ind_str  = line[:indent]
            stripped = line.lstrip()

            m = re.match(r'^([-*+]) ', stripped)
            if m:
                if stripped.strip() == m.group(1):
                    cursor.select(cursor.SelectionType.LineUnderCursor)
                    cursor.insertText('')
                else:
                    cursor.insertText('\n' + ind_str + m.group(1) + ' ')
                return

            m = re.match(r'^(\d+)\. ', stripped)
            if m:
                if stripped.strip() == m.group(0).strip():
                    cursor.select(cursor.SelectionType.LineUnderCursor)
                    cursor.insertText('')
                else:
                    cursor.insertText('\n' + ind_str + str(int(m.group(1)) + 1) + '. ')
                return

            cursor.insertText('\n' + ind_str)
            return

        super().keyPressEvent(event)


# ──────────────────────────────────────────────────────────
# Markdown 编辑对话框
# ──────────────────────────────────────────────────────────

class MarkdownEditorDialog(QWidget):
    def __init__(self, note_window: "NoteWindow"):
        super().__init__()
        self._note = note_window
        self.resize(580, 500)
        self.setWindowFlag(Qt.WindowType.Window)
        self._apply_theme()

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        self.src = MDSourceEdit()
        root.addWidget(self.src)

        self._live_timer = QTimer(self)
        self._live_timer.setSingleShot(True)
        self._live_timer.setInterval(600)
        self._live_timer.timeout.connect(self._live_update)
        self.src.textChanged.connect(self._live_timer.start)

        bar = QHBoxLayout()
        bar.addStretch()
        btn_save = QPushButton(t("save"))
        btn_save.clicked.connect(self.save)
        bar.addWidget(btn_save)
        root.addLayout(bar)

    def _apply_theme(self):
        palette = QApplication.palette()
        is_dark = palette.color(palette.ColorRole.Window).lightness() < 128
        if is_dark:
            self.setStyleSheet("""
                QWidget { background: #1e1e1e; color: #d4d4d4; }
                QTextEdit {
                    background: #252526; color: #d4d4d4;
                    border: 1px solid #3c3c3c; border-radius: 4px;
                    font-family: 'Consolas', 'Microsoft YaHei', monospace;
                    font-size: 13px;
                }
                QPushButton {
                    background: #0e639c; color: #ffffff;
                    border: none; border-radius: 4px;
                    padding: 5px 18px;
                }
                QPushButton:hover { background: #1177bb; }
                QPushButton:pressed { background: #0a4f7e; }
            """)
        else:
            self.setStyleSheet("""
                QWidget { background: #f3f3f3; color: #1e1e1e; }
                QTextEdit {
                    background: #ffffff; color: #1e1e1e;
                    border: 1px solid #c8c8c8; border-radius: 4px;
                    font-family: 'Consolas', 'Microsoft YaHei', monospace;
                    font-size: 13px;
                }
                QPushButton {
                    background: #0065bd; color: #ffffff;
                    border: none; border-radius: 4px;
                    padding: 5px 18px;
                }
                QPushButton:hover { background: #0074d4; }
                QPushButton:pressed { background: #004f96; }
            """)

    def open_with_content(self, content: str):
        name = self._note.settings.get("name", "便签")
        self.setWindowTitle(t("md_title", name=name))
        self._apply_theme()
        self.src.setPlainText(content)
        cursor = self.src.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.src.setTextCursor(cursor)
        self.show()
        self.activateWindow()
        self.raise_()

    def _live_update(self):
        content = self.src.toPlainText()
        self._note.settings["content"] = content
        self._note.render_content(content)

    def save(self):
        self._live_update()
        self._note._manager.save()
        self.hide()

    def closeEvent(self, event):
        if self._note and self._note._manager._quitting:
            event.accept()
            return
        event.ignore()
        self.hide()


# ──────────────────────────────────────────────────────────
# 外观设置对话框
# ──────────────────────────────────────────────────────────

class AppearanceDialog(QWidget):
    def __init__(self, note_window: "NoteWindow"):
        super().__init__()
        self._note = note_window
        self._original: dict = {}
        self._refreshers: list = []

        self.setWindowFlag(Qt.WindowType.Window)
        self.resize(480, 580)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        inner = QWidget()
        inner_vb = QVBoxLayout(inner)
        inner_vb.setContentsMargins(14, 10, 14, 10)
        inner_vb.setSpacing(10)
        scroll.setWidget(inner)
        root.addWidget(scroll, 1)

        inner_vb.addWidget(self._build_color_group())
        inner_vb.addWidget(self._build_font_group())
        inner_vb.addWidget(self._build_spacing_group())
        inner_vb.addWidget(self._build_layout_group())
        inner_vb.addWidget(self._build_effect_group())
        inner_vb.addWidget(self._build_border_group())
        inner_vb.addStretch()

        bar_w = QWidget()
        bar_h = QHBoxLayout(bar_w)
        bar_h.setContentsMargins(8, 6, 8, 6)
        bar_h.addStretch()
        btn_cancel = QPushButton(t("cancel"))
        btn_cancel.clicked.connect(self._cancel)
        btn_save = QPushButton(t("save"))
        btn_save.clicked.connect(self._save)
        bar_h.addWidget(btn_cancel)
        bar_h.addSpacing(4)
        bar_h.addWidget(btn_save)
        root.addWidget(bar_w)

    # ── 控件构建辅助 ──────────────────────────────────────

    def _color_btn(self, key: str, title: str, on_change=None) -> QPushButton:
        btn = QPushButton()
        btn.setFixedSize(32, 22)
        self._set_color_style(btn, self._note.settings.get(key, "#FFFFFF"))
        self._refreshers.append(
            lambda b=btn, k=key: self._set_color_style(b, self._note.settings.get(k, "#FFFFFF"))
        )

        def _pick(_, k=key, b=btn, cb=on_change):
            c = QColorDialog.getColor(QColor(self._note.settings.get(k, "#FFFFFF")), self, title)
            if c.isValid():
                self._note.settings[k] = c.name()
                self._set_color_style(b, c.name())
                if cb:
                    cb()

        btn.clicked.connect(_pick)
        return btn

    @staticmethod
    def _set_color_style(btn: QPushButton, color: str):
        btn.setStyleSheet(
            f"QPushButton{{background:{color};border:1px solid #888;border-radius:3px;}}"
            f"QPushButton:hover{{border-color:#42A5F5;}}"
        )

    def _slider_row(self, key: str, lo: int, hi: int, suffix: str,
                    on_change=None) -> tuple[QWidget, QSlider]:
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)

        sl = QSlider(Qt.Orientation.Horizontal)
        sl.setRange(lo, hi)
        sl.setValue(int(self._note.settings.get(key, lo)))

        val_lbl = QLabel(f"{sl.value()}{suffix}")
        val_lbl.setFixedWidth(44)
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self._refreshers.append(
            lambda s=sl, k=key, d=lo: s.setValue(int(self._note.settings.get(k, d)))
        )

        def _on(v, k=key, lbl=val_lbl, cb=on_change):
            lbl.setText(f"{v}{suffix}")
            self._note.settings[k] = v
            if cb:
                cb()

        sl.valueChanged.connect(_on)
        h.addWidget(sl)
        h.addWidget(val_lbl)
        return row, sl

    def _checkbox(self, key: str, label: str, on_change=None) -> QCheckBox:
        cb = QCheckBox(label)
        cb.setChecked(bool(self._note.settings.get(key, False)))
        self._refreshers.append(
            lambda c=cb, k=key: c.setChecked(bool(self._note.settings.get(k, False)))
        )

        def _on(checked, k=key, callback=on_change):
            self._note.settings[k] = checked
            if callback:
                callback(checked)

        cb.toggled.connect(_on)
        return cb

    # ── 颜色组 ────────────────────────────────────────────

    def _build_color_group(self) -> QGroupBox:
        group = QGroupBox(t("col_group"))
        vb = QVBoxLayout(group)
        vb.setContentsMargins(10, 16, 10, 8)
        vb.setSpacing(8)

        def apply():
            self._note._apply_colors()

        for label, ck, ok in (
            (t("col_bg"),   "bg_color",   "bg_opacity"),
            (t("col_text"), "text_color", "text_opacity"),
        ):
            row = QWidget()
            h = QHBoxLayout(row)
            h.setContentsMargins(0, 0, 0, 0)
            h.setSpacing(8)
            lbl = QLabel(label)
            lbl.setFixedWidth(54)
            h.addWidget(lbl)
            h.addWidget(self._color_btn(ck, label, apply))
            h.addSpacing(6)
            h.addWidget(QLabel(t("opacity")))
            sl_w, _ = self._slider_row(ok, 0, 100, "%", apply)
            h.addWidget(sl_w, 1)
            vb.addWidget(row)

        return group

    # ── 字体组 ────────────────────────────────────────────

    def _build_font_group(self) -> QGroupBox:
        group = QGroupBox(t("font_group"))
        vb = QVBoxLayout(group)
        vb.setContentsMargins(10, 16, 10, 8)
        vb.setSpacing(8)

        def apply():
            self._note._apply_font()

        row1 = QWidget()
        h1 = QHBoxLayout(row1)
        h1.setContentsMargins(0, 0, 0, 0)
        h1.setSpacing(8)

        font_combo = QFontComboBox()
        font_combo.setCurrentFont(QFont(self._note.settings.get("font_family", "Microsoft YaHei")))
        self._refreshers.append(
            lambda fc=font_combo: fc.setCurrentFont(
                QFont(self._note.settings.get("font_family", "Microsoft YaHei"))
            )
        )

        def on_font(font: QFont):
            self._note.settings["font_family"] = font.family()
            apply()

        font_combo.currentFontChanged.connect(on_font)

        size_spin = QSpinBox()
        size_spin.setRange(6, 72)
        size_spin.setValue(int(self._note.settings.get("font_size", 13)))
        self._refreshers.append(
            lambda s=size_spin: s.setValue(int(self._note.settings.get("font_size", 13)))
        )

        def on_size(v):
            self._note.settings["font_size"] = v
            apply()

        size_spin.valueChanged.connect(on_size)

        h1.addWidget(QLabel(t("font_lbl")))
        h1.addWidget(font_combo, 1)
        h1.addWidget(QLabel(t("size_lbl")))
        h1.addWidget(size_spin)
        vb.addWidget(row1)

        return group

    # ── 间距组 ────────────────────────────────────────────

    def _build_spacing_group(self) -> QGroupBox:
        group = QGroupBox(t("spacing_group"))
        vb = QVBoxLayout(group)
        vb.setContentsMargins(10, 16, 10, 8)
        vb.setSpacing(8)

        def apply():
            self._note.render_content(self._note.settings.get("content", ""))

        for label, key, lo, hi, suffix in (
            (t("l_spacing"),  "letter_spacing", -3,  20, "px"),
            (t("ln_spacing"), "line_spacing",   80, 300, "%"),
        ):
            row = QWidget()
            h = QHBoxLayout(row)
            h.setContentsMargins(0, 0, 0, 0)
            h.setSpacing(8)
            lbl = QLabel(label)
            lbl.setFixedWidth(46)
            sl_w, _ = self._slider_row(key, lo, hi, suffix, apply)
            h.addWidget(lbl)
            h.addWidget(sl_w, 1)
            vb.addWidget(row)

        return group

    # ── 布局组（页边距 + 对齐）────────────────────────────

    def _build_layout_group(self) -> QGroupBox:
        group = QGroupBox(t("layout_group"))
        vb = QVBoxLayout(group)
        vb.setContentsMargins(10, 16, 10, 8)
        vb.setSpacing(8)

        # 页边距滑块（水平 / 垂直分开）
        for lbl_key, setting_key in (
            ("padding_x_lbl", "padding_x"),
            ("padding_y_lbl", "padding_y"),
        ):
            pad_row = QWidget()
            ph = QHBoxLayout(pad_row)
            ph.setContentsMargins(0, 0, 0, 0)
            ph.setSpacing(8)
            lbl = QLabel(t(lbl_key))
            lbl.setFixedWidth(54)
            sl_w, _ = self._slider_row(
                setting_key, 0, 300, "px",
                lambda: self._note._apply_padding()
            )
            ph.addWidget(lbl)
            ph.addWidget(sl_w, 1)
            vb.addWidget(pad_row)

        # 九宫格对齐
        align_outer = QWidget()
        ao = QHBoxLayout(align_outer)
        ao.setContentsMargins(0, 0, 0, 0)
        ao.setSpacing(8)
        ao.addWidget(QLabel(t("align_lbl")))

        grid_w = QWidget()
        grid = QGridLayout(grid_w)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(2)

        # 九宫格按钮：(行, 列) → (对齐值, 显示符号)
        GRID_CELLS = [
            ("top-left",     "↖"), ("top-center",    "↑"), ("top-right",    "↗"),
            ("middle-left",  "←"), ("middle-center", "·"), ("middle-right", "→"),
            ("bottom-left",  "↙"), ("bottom-center", "↓"), ("bottom-right", "↘"),
        ]
        btn_grp9 = QButtonGroup(grid_w)
        btn_grp9.setExclusive(True)
        align_btns9: dict[str, QPushButton] = {}
        current_align9 = self._note.settings.get("text_align", "top-left")

        def _on_align9(checked: bool):
            if not checked:
                return
            for av, b in align_btns9.items():
                if b.isChecked():
                    self._note.settings["text_align"] = av
                    self._note.render_content(self._note.settings.get("content", ""))
                    break

        for idx, (val, label) in enumerate(GRID_CELLS):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setChecked(val == current_align9)
            btn.setFixedSize(28, 28)
            btn_grp9.addButton(btn)
            grid.addWidget(btn, idx // 3, idx % 3)
            align_btns9[val] = btn
            btn.toggled.connect(_on_align9)

        ao.addWidget(grid_w)
        ao.addStretch()
        vb.addWidget(align_outer)

        # 刷新时同步控件状态
        self._refreshers.append(
            lambda bmap=align_btns9: [
                b.blockSignals(True) or
                b.setChecked(self._note.settings.get("text_align", "top-left") == av) or
                b.blockSignals(False)
                for av, b in bmap.items()
            ]
        )

        return group

    # ── 文字效果组 ────────────────────────────────────────

    def _build_effect_group(self) -> QGroupBox:
        group = QGroupBox(t("fx_group"))
        vb = QVBoxLayout(group)
        vb.setContentsMargins(10, 16, 10, 8)
        vb.setSpacing(8)

        def apply():
            self._note._apply_text_effect()

        stroke_cb_ref: list = [None]
        glow_cb_ref:   list = [None]

        def on_glow(checked):
            if checked:
                sc = stroke_cb_ref[0]
                if sc:
                    sc.blockSignals(True)
                    sc.setChecked(False)
                    sc.blockSignals(False)
                self._note.settings["stroke_enabled"] = False
            apply()

        def on_stroke(checked):
            if checked:
                gc = glow_cb_ref[0]
                if gc:
                    gc.blockSignals(True)
                    gc.setChecked(False)
                    gc.blockSignals(False)
                self._note.settings["glow_enabled"] = False
            apply()

        glow_row = QWidget()
        gh = QHBoxLayout(glow_row)
        gh.setContentsMargins(0, 0, 0, 0)
        gh.setSpacing(8)
        glow_cb = self._checkbox("glow_enabled", t("glow_on"), on_glow)
        glow_cb_ref[0] = glow_cb
        gh.addWidget(glow_cb)
        gh.addWidget(self._color_btn("glow_color", t("glow_col_pick"), apply))
        gh.addWidget(QLabel(t("opacity")))
        sl_w, _ = self._slider_row("glow_opacity", 1, 100, "%", apply)
        gh.addWidget(sl_w, 1)
        vb.addWidget(glow_row)

        stroke_row = QWidget()
        sh = QHBoxLayout(stroke_row)
        sh.setContentsMargins(0, 0, 0, 0)
        sh.setSpacing(8)
        stroke_cb = self._checkbox("stroke_enabled", t("stroke_on"), on_stroke)
        stroke_cb_ref[0] = stroke_cb
        sh.addWidget(stroke_cb)
        sh.addWidget(self._color_btn("stroke_color", t("stroke_col_pick"), apply))
        sh.addWidget(QLabel(t("width_lbl")))
        sl_w2, _ = self._slider_row("stroke_width", 1, 8, "px", apply)
        sh.addWidget(sl_w2, 1)
        vb.addWidget(stroke_row)

        vb.addWidget(QLabel(t("fx_hint")))
        return group

    # ── 边框组 ────────────────────────────────────────────

    def _build_border_group(self) -> QGroupBox:
        group = QGroupBox(t("border_group"))
        vb = QVBoxLayout(group)
        vb.setContentsMargins(10, 16, 10, 8)
        vb.setSpacing(8)

        def apply():
            self._note.update()

        row1 = QWidget()
        h1 = QHBoxLayout(row1)
        h1.setContentsMargins(0, 0, 0, 0)
        h1.setSpacing(8)
        h1.addWidget(self._checkbox("border_enabled", t("border_on"), lambda _: apply()))
        h1.addWidget(self._color_btn("border_color", t("border_col_pick"), apply))
        h1.addStretch()
        vb.addWidget(row1)

        for label, key, lo, hi, suffix in (
            (t("border_w_lbl"), "border_width",  1,  10, "px"),
            (t("border_r_lbl"), "border_radius", 0,  30, "px"),
        ):
            row = QWidget()
            h = QHBoxLayout(row)
            h.setContentsMargins(0, 0, 0, 0)
            h.setSpacing(8)
            lbl = QLabel(label)
            lbl.setFixedWidth(54)
            sl_w, _ = self._slider_row(key, lo, hi, suffix, apply)
            h.addWidget(lbl)
            h.addWidget(sl_w, 1)
            vb.addWidget(row)

        return group

    # ── 打开 / 保存 / 取消 ───────────────────────────────

    def open(self):
        name = self._note.settings.get("name", "便签")
        self.setWindowTitle(t("ap_title", name=name))
        self._original = {k: copy.deepcopy(self._note.settings.get(k))
                          for k in APPEARANCE_KEYS}
        for r in self._refreshers:
            r()
        self.show()
        self.activateWindow()
        self.raise_()

    def _save(self):
        self._note._manager.save()
        self.hide()

    def _cancel(self):
        if self._note is None:
            self.hide()
            return
        for k, v in self._original.items():
            self._note.settings[k] = v
        self._note._apply_all_settings()
        self._note.render_content(self._note.settings.get("content", ""))
        self.hide()

    def closeEvent(self, event):
        if self._note is None or self._note._manager._quitting:
            event.accept()
            return
        event.ignore()
        self._cancel()


# ──────────────────────────────────────────────────────────
# 便签内容控件（只读展示 + 拖动 + checkbox 点击）
# ──────────────────────────────────────────────────────────

class NoteEdit(QTextEdit):
    """便签正文区：只读展示 Markdown，响应拖动与 checkbox 点击。"""
    def __init__(self, window: "NoteWindow"):
        super().__init__(window)
        self._win = window
        self._drag_pos = None
        self.setReadOnly(True)
        self.setAutoFillBackground(False)
        self.viewport().setAutoFillBackground(False)
        self.setStyleSheet("background: transparent; border: none;")
        self.viewport().setStyleSheet("background: transparent;")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setPlaceholderText("双击以编辑，支持 Markdown 格式")
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)

    def minimumSizeHint(self):
        return QSize(0, 0)

    def sizeHint(self):
        return QSize(0, 0)

    def contextMenuEvent(self, event):
        self._win.show_context_menu(event.globalPos())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self._win.settings.get("locked", False):
                # 检测是否点击了 checkbox 字符
                hit = self.cursorForPosition(event.position().toPoint())
                doc = self.document()
                for check_pos in (hit.position(), hit.position() - 1):
                    if check_pos < 0:
                        continue
                    c = QTextCursor(doc)
                    c.setPosition(check_pos)
                    c.movePosition(
                        QTextCursor.MoveOperation.Right,
                        QTextCursor.MoveMode.KeepAnchor,
                    )
                    if c.selectedText() in (
                        self._win._CB_UNCHECKED, self._win._CB_CHECKED
                    ):
                        self._win._toggle_checkbox(check_pos)
                        return  # 不触发拖动
            self._drag_pos = (
                event.globalPosition().toPoint()
                - self._win.frameGeometry().topLeft()
            )
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self._win.move(event.globalPosition().toPoint() - self._drag_pos)
        super().mouseMoveEvent(event)
        if not self._win.settings.get("locked", False):
            self.viewport().setCursor(Qt.CursorShape.ArrowCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if (event.button() == Qt.MouseButton.LeftButton
                and not self._win.settings.get("locked", False)):
            self._win._open_md_editor()
        else:
            super().mouseDoubleClickEvent(event)


# ──────────────────────────────────────────────────────────
# 便签窗口（无边框透明，含所有样式与交互逻辑）
# ──────────────────────────────────────────────────────────

class NoteWindow(QWidget):
    """单个便签窗口：渲染、样式、Checklist 交互、右键菜单、窗口管理。"""
    def __init__(self, note_id: str, manager: "NoteManager"):
        super().__init__()
        self._note_id = note_id
        self._manager = manager
        self.settings = manager.notes()[note_id]
        self._bg_color = QColor(self.settings.get("bg_color", "#1E1E1E"))
        self._really_closing = False

        self._init_window()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.editor = NoteEdit(self)
        self.editor.setMinimumSize(0, 0)   # 允许 layout 分配任意大的边距
        layout.addWidget(self.editor)

        self._md_editor: MarkdownEditorDialog | None = None
        self._appearance_editor: AppearanceDialog | None = None

        self._initialized = False
        self._apply_all_settings()
        self.render_content(self.settings.get("content", ""))
        self._initialized = True

    # ── 初始化 ────────────────────────────────────────────

    def _init_window(self):
        s = self.settings
        flags = Qt.Tool | Qt.FramelessWindowHint
        if s["always_on_top"]:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setGeometry(s["x"], s["y"], s["width"], s["height"])

    # ── 绘制 ──────────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        s = self.settings
        radius = s.get("border_radius", 0)
        bg_rect = QRectF(self.rect())

        # 清空整个窗口为透明
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        # 背景
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._bg_color)
        if radius > 0:
            painter.drawRoundedRect(bg_rect, radius, radius)
        else:
            painter.drawRect(bg_rect)

        # 边框
        if s.get("border_enabled", False):
            bw = s.get("border_width", 1)
            pen = QPen(QColor(s.get("border_color", "#BDBDBD")), bw)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            adj = bw / 2
            br = bg_rect.adjusted(adj, adj, -adj, -adj)
            if radius > 0:
                painter.drawRoundedRect(br, radius, radius)
            else:
                painter.drawRect(br)

        painter.end()

    # ── 应用样式 ──────────────────────────────────────────

    def _apply_all_settings(self):
        self._apply_colors()
        self._apply_font()
        self._apply_text_effect()
        self._apply_padding()

    def _apply_padding(self):
        px = self.settings.get("padding_x", 8)
        py = self.settings.get("padding_y", 8)
        self.layout().setContentsMargins(px, py, px, py)

    def _apply_vertical_align(self):
        """在文字区内部用根框架 topMargin 实现垂直对齐，不改动布局边距。"""
        raw = self.settings.get("text_align", "top-left")
        parts = raw.split("-")
        v_part = parts[0] if len(parts) == 2 else "top"

        doc = self.editor.document()

        # 先清零 topMargin，再测量内容原始高度
        fmt = doc.rootFrame().frameFormat()
        fmt.setTopMargin(0.0)
        doc.rootFrame().setFrameFormat(fmt)

        if v_part == "top":
            return

        content_h = doc.size().height()
        vh = self.editor.viewport().height()

        if content_h <= 0 or vh <= content_h:
            return

        extra = vh - content_h
        top_margin = extra / 2 if v_part == "middle" else extra

        fmt = doc.rootFrame().frameFormat()
        fmt.setTopMargin(top_margin)
        doc.rootFrame().setFrameFormat(fmt)

    def _apply_colors(self):
        s = self.settings
        bg = QColor(s["bg_color"])
        bg.setAlpha(max(5, round(s["bg_opacity"] / 100 * 255)))
        self._bg_color = bg

        text = QColor(s["text_color"])
        text_a = round(s["text_opacity"] / 100 * 255)
        self.editor.setStyleSheet(
            f"QTextEdit {{"
            f"  background: transparent;"
            f"  color: rgba({text.red()},{text.green()},{text.blue()},{text_a});"
            f"  border: none;"
            f"}}"
        )
        # placeholder 颜色跟随正文，但透明度更低
        ph_color = QColor(text)
        ph_color.setAlpha(max(0, text_a - 120))
        palette = self.editor.palette()
        palette.setColor(palette.ColorRole.PlaceholderText, ph_color)
        self.editor.setPalette(palette)
        self.update()
        if self._initialized:
            self.render_content(self.settings.get("content", ""))

    def _apply_font(self):
        s = self.settings
        font = QFont(s["font_family"], s["font_size"])
        self.editor.setFont(font)
        if self._initialized:
            self.render_content(self.settings.get("content", ""))

    def _apply_text_effect(self):
        s = self.settings
        glow_on   = bool(s.get("glow_enabled"))
        stroke_on = bool(s.get("stroke_enabled"))

        if glow_on:
            # 发光效果：使用裁剪版阴影（GPU 加速），质量更高
            effect = ClippedGlowEffect(self.editor)
            effect.setOffset(0, 0)
            effect.setBlurRadius(6)
            color = QColor(s["glow_color"])
            color.setAlpha(round(s.get("glow_opacity", 80) / 100 * 255))
            effect.setColor(color)
            self.editor.setGraphicsEffect(effect)
        elif stroke_on:
            effect = TextStrokeEffect(
                QColor(s.get("stroke_color", "#000000")),
                max(1, s.get("stroke_width", 2)),
                self.editor,
            )
            self.editor.setGraphicsEffect(effect)
        else:
            self.editor.setGraphicsEffect(None)

    # ── Markdown 渲染 ──────────────────────────────────────

    # checkbox 显示用的 Unicode 字符
    _CB_UNCHECKED = "☐"
    _CB_CHECKED   = "☑"

    # 匹配 [ ] / [x] / [X]，排除 Markdown 链接语法 [文字](url)
    _RE_CB_ANY = re.compile(r'\[([ xX])\](?!\()')

    # 表格分隔行与列对齐标记
    _RE_TABLE_SEP = re.compile(r'^\s*\|(.+)\|\s*$')
    _RE_SEP_CELL  = re.compile(r'^:?-+:?$')

    def _preprocess_md(self, content: str) -> str:
        """将 `[ ]` / `[x]` 替换为 Unicode checkbox 字符后再交给 setMarkdown。
        覆盖任务列表（- [ ]）和表格单元格（| [ ] |）两种用法。
        """
        def _replace(m: re.Match) -> str:
            return self._CB_CHECKED if m.group(1).lower() == "x" else self._CB_UNCHECKED
        return self._RE_CB_ANY.sub(_replace, content)

    def render_content(self, content: str):
        if not content.strip():
            self.editor.clear()
            return
        display = self._preprocess_md(content)
        self.editor.document().setMarkdown(
            display,
            QTextDocument.MarkdownFeature.MarkdownDialectGitHub,
        )
        s = self.settings
        text = QColor(s["text_color"])
        text.setAlpha(round(s["text_opacity"] / 100 * 255))
        char_fmt = QTextCharFormat()
        char_fmt.setForeground(text)
        cursor = self.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.mergeCharFormat(char_fmt)
        cursor.clearSelection()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.editor.setTextCursor(cursor)
        self._apply_spacing()
        self._apply_table_column_alignments(content)
        QTimer.singleShot(0, self._apply_vertical_align)

    def _apply_spacing(self):
        s = self.settings
        doc = self.editor.document()

        char_fmt = QTextCharFormat()
        char_fmt.setFontLetterSpacingType(QFont.SpacingType.AbsoluteSpacing)
        char_fmt.setFontLetterSpacing(float(s.get("letter_spacing", 0)))
        cursor = QTextCursor(doc)
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.mergeCharFormat(char_fmt)
        cursor.clearSelection()

        line_sp = s.get("line_spacing", 100)
        raw_align = s.get("text_align", "top-left")
        h_part = raw_align.split("-")[-1]   # 如 "top-left" → "left"
        align_map = {
            "left":   Qt.AlignmentFlag.AlignLeft,
            "center": Qt.AlignmentFlag.AlignHCenter,
            "right":  Qt.AlignmentFlag.AlignRight,
        }
        align = align_map.get(h_part, Qt.AlignmentFlag.AlignLeft)

        cursor.movePosition(QTextCursor.MoveOperation.Start)
        visited_tables: set[int] = set()
        while True:
            table = cursor.currentTable()
            blk_fmt = QTextBlockFormat(cursor.blockFormat())
            blk_fmt.setLineHeight(
                line_sp,
                QTextBlockFormat.LineHeightTypes.ProportionalHeight.value
            )
            if table:
                # 对表格整体定位，不改单元格内文字对齐
                tid = id(table)
                if tid not in visited_tables:
                    visited_tables.add(tid)
                    tbl_fmt = table.format()
                    tbl_fmt.setAlignment(align)
                    table.setFormat(tbl_fmt)
            else:
                blk_fmt.setAlignment(align)
            cursor.setBlockFormat(blk_fmt)
            if not cursor.movePosition(QTextCursor.MoveOperation.NextBlock):
                break

    def _apply_table_column_alignments(self, md_source: str):
        """解析 :---: / ---: / :--- 列对齐标记，并应用到 QTextTable 各单元格。"""
        # 按文档顺序收集每个表格的列对齐列表
        table_aligns: list[list[Qt.AlignmentFlag]] = []
        lines = md_source.splitlines()
        i = 0
        while i < len(lines) - 1:
            hdr = lines[i]
            sep = lines[i + 1]
            hm = self._RE_TABLE_SEP.match(hdr)
            sm = self._RE_TABLE_SEP.match(sep)
            if hm and sm:
                cols = [c.strip() for c in sm.group(1).split('|')]
                if cols and all(self._RE_SEP_CELL.match(c) for c in cols if c):
                    aligns: list[Qt.AlignmentFlag] = []
                    for c in cols:
                        c = c.strip()
                        if c.startswith(':') and c.endswith(':'):
                            aligns.append(Qt.AlignmentFlag.AlignHCenter)
                        elif c.endswith(':'):
                            aligns.append(Qt.AlignmentFlag.AlignRight)
                        else:
                            aligns.append(Qt.AlignmentFlag.AlignLeft)
                    table_aligns.append(aligns)
                    i += 2
                    continue
            i += 1

        if not table_aligns:
            return

        doc = self.editor.document()
        cursor = QTextCursor(doc)
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        visited: set[int] = set()
        tbl_idx = 0

        while tbl_idx < len(table_aligns):
            tbl = cursor.currentTable()
            if tbl:
                tid = id(tbl)
                if tid not in visited:
                    visited.add(tid)
                    aligns = table_aligns[tbl_idx]
                    for row in range(tbl.rows()):
                        for col in range(min(tbl.columns(), len(aligns))):
                            cell = tbl.cellAt(row, col)
                            c = cell.firstCursorPosition()
                            last = cell.lastCursorPosition()
                            while c.position() <= last.position():
                                fmt = QTextBlockFormat(c.blockFormat())
                                fmt.setAlignment(aligns[col])
                                c.setBlockFormat(fmt)
                                if not c.movePosition(
                                    QTextCursor.MoveOperation.NextBlock
                                ):
                                    break
                    tbl_idx += 1
            if not cursor.movePosition(QTextCursor.MoveOperation.NextBlock):
                break

    # ── Checklist 交互 ─────────────────────────────────────

    def _toggle_checkbox(self, char_pos: int):
        """点击 checkbox 字符时，切换 [ ]/[x] 并对行内其余文字加/去删除线。"""
        doc = self.editor.document()
        full_text = doc.toPlainText()
        text_before = full_text[:char_pos]
        idx = text_before.count(self._CB_UNCHECKED) + text_before.count(self._CB_CHECKED)

        source = self.settings.get("content", "")
        matches = list(self._RE_CB_ANY.finditer(source))
        if idx >= len(matches):
            return

        m = matches[idx]
        currently_checked = m.group(1).lower() == 'x'

        # 找到该 checkbox 所在行
        line_start = source.rfind('\n', 0, m.start()) + 1
        nl_pos = source.find('\n', m.end())
        line_end = nl_pos if nl_pos != -1 else len(source)
        line = source[line_start:line_end]

        cb_pos_in_line = m.start() - line_start

        stripped = line.strip()
        if stripped.startswith('|') and stripped.endswith('|'):
            new_line = self._toggle_table_row(line, currently_checked, cb_pos_in_line)
        else:
            new_line = self._toggle_list_item(
                line, m.start() - line_start, m.end() - line_start, currently_checked
            )

        new_source = source[:line_start] + new_line + source[line_end:]
        self.settings["content"] = new_source
        self._manager.save()
        self.render_content(new_source)

    @staticmethod
    def _add_strike(text: str) -> str:
        t = text.strip()
        if not t or (t.startswith('~~') and t.endswith('~~')):
            return text
        return text.replace(t, f'~~{t}~~', 1)

    @staticmethod
    def _remove_strike(text: str) -> str:
        t = text.strip()
        if t.startswith('~~') and t.endswith('~~') and len(t) > 4:
            return text.replace(t, t[2:-2], 1)
        return text

    def _toggle_table_row(self, line: str, currently_checked: bool, cb_pos_in_line: int) -> str:
        """切换表格行的 checkbox：
        - checkbox 在第一列且该格仅有 checkbox（无其他文字）→ 其余所有列加/去删除线
        - 其他情况（格内有额外文字 / 非第一列）→ 仅对同格内 checkbox 后的文字加/去删除线
        用 cb_pos_in_line 精确定位被点击的列，避免一行多 checkbox 时操作错列。
        """
        stripped = line.strip()
        cells = stripped[1:-1].split('|')

        # 统计 checkbox 位置之前有几个 |，确定列号（从 0 起算）
        pipes_before = line[:cb_pos_in_line].count('|')
        cb_idx = max(0, pipes_before - 1)          # 减 1：第一个 | 是行首分隔符
        cb_idx = min(cb_idx, len(cells) - 1)       # 防越界

        # 判断该格去掉 checkbox 后是否还有其他文字
        cell_extra = self._RE_CB_ANY.sub('', cells[cb_idx]).strip()
        whole_row_mode = (cb_idx == 0) and (cell_extra == '')

        new_cells = []
        for i, cell in enumerate(cells):
            content = cell.strip()
            if i == cb_idx:
                if whole_row_mode:
                    content = self._RE_CB_ANY.sub('[ ]' if currently_checked else '[x]', content)
                else:
                    content = self._toggle_cell_inline(content, currently_checked)
            elif whole_row_mode:
                content = self._remove_strike(content) if currently_checked else self._add_strike(content)
            new_cells.append(f' {content} ')

        indent = len(line) - len(line.lstrip())
        return ' ' * indent + '|' + '|'.join(new_cells) + '|'

    def _toggle_cell_inline(self, content: str, currently_checked: bool) -> str:
        """在单个格内切换 checkbox，并对 checkbox 之后的文字加/去删除线。"""
        m = self._RE_CB_ANY.search(content)
        if not m:
            return content
        before = content[:m.start()]
        after  = content[m.end():]
        new_cb = '[ ]' if currently_checked else '[x]'
        leading_sp = len(after) - len(after.lstrip(' '))
        text = after[leading_sp:]
        if currently_checked:
            text = re.sub(r'^~~(.*)~~$', r'\1', text)
        else:
            if text:
                text = f'~~{text}~~'
        return before + new_cb + ' ' * leading_sp + text

    def _toggle_list_item(self, line: str, cb_start: int, cb_end: int, currently_checked: bool) -> str:
        """切换列表项的 checkbox，并对后续文字加/去删除线。"""
        before = line[:cb_start]    # '- ' 等前缀
        after  = line[cb_end:]      # ' 室女之魂晶…' 等后续文字

        leading_sp = len(after) - len(after.lstrip(' '))
        text = after[leading_sp:]

        if currently_checked:
            new_cb = '[ ]'
            text = re.sub(r'^~~(.*)~~$', r'\1', text)
        else:
            new_cb = '[x]'
            if text:
                text = f'~~{text}~~'

        return before + new_cb + ' ' * leading_sp + text

    # ── 对话框 ────────────────────────────────────────────

    def _open_md_editor(self):
        if self._md_editor is None:
            self._md_editor = MarkdownEditorDialog(self)
        self._md_editor.open_with_content(self.settings.get("content", ""))

    def _open_appearance(self):
        if self._appearance_editor is None:
            self._appearance_editor = AppearanceDialog(self)
        self._appearance_editor.open()

    # ── 保存 ──────────────────────────────────────────────

    def _save_geometry(self):
        geo = self.geometry()
        self.settings.update({
            "x": geo.x(), "y": geo.y(),
            "width": geo.width(), "height": geo.height(),
        })
        self._manager.save()

    # ── 右键菜单 ──────────────────────────────────────────

    def show_context_menu(self, global_pos):
        menu = QMenu(self)

        name_lbl = QLabel(f"  ◆  {self.settings.get('name', '便签')}")
        name_wa = QWidgetAction(menu)
        name_wa.setDefaultWidget(name_lbl)
        menu.addAction(name_wa)

        act_rename = QAction(t("rename_note"), self)
        act_rename.triggered.connect(self._rename_note)
        menu.addAction(act_rename)

        menu.addSeparator()

        act_new = QAction(t("new_note"), self)
        act_new.triggered.connect(self._new_note)
        menu.addAction(act_new)

        act_edit = QAction(t("edit_md"), self)
        act_edit.triggered.connect(self._open_md_editor)
        menu.addAction(act_edit)

        notes_menu = QMenu(t("note_list"), menu)
        for nid, note in self._manager.notes().items():
            note_name = note.get("name", "")
            is_current = (nid == self._note_id)
            if is_current:
                act_n = QAction(f"{note_name}（{t('note_current')}）", notes_menu)
                act_n.setEnabled(False)
                notes_menu.addAction(act_n)
            else:
                is_visible = note.get("visible", True)
                prefix = "✓ " if is_visible else "    "
                sub = QMenu(prefix + note_name, notes_menu)

                def _make_toggle(n_id, visible):
                    def _do():
                        if visible:
                            self._manager.hide_note(n_id)
                        else:
                            self._manager.show_note(n_id)
                    return _do

                def _make_delete(n_id, n_name):
                    def _do():
                        if _ask_yes_no(
                            self,
                            t("delete_title"),
                            t("delete_prompt").format(name=n_name),
                        ):
                            self._manager.delete_note(n_id)
                    return _do

                vis_label = t("note_hide") if is_visible else t("note_show")
                act_vis = QAction(vis_label, sub)
                act_vis.triggered.connect(_make_toggle(nid, is_visible))
                sub.addAction(act_vis)

                sub.addSeparator()

                act_del_n = QAction(t("note_delete"), sub)
                act_del_n.triggered.connect(_make_delete(nid, note_name))
                sub.addAction(act_del_n)

                notes_menu.addMenu(sub)

        menu.addMenu(notes_menu)

        menu.addSeparator()

        act_ap = QAction(t("appearance"), self)
        act_ap.triggered.connect(self._open_appearance)
        menu.addAction(act_ap)

        menu.addSeparator()

        act_top = QAction(t("always_on_top"), self)
        act_top.setCheckable(True)
        act_top.setChecked(self.settings["always_on_top"])
        act_top.triggered.connect(self._toggle_always_on_top)
        menu.addAction(act_top)

        act_lock = QAction(t("lock"), self)
        act_lock.setCheckable(True)
        act_lock.setChecked(self.settings["locked"])
        act_lock.triggered.connect(self._toggle_lock)
        menu.addAction(act_lock)

        # 语言子菜单
        lang_menu = QMenu(t("language"), menu)
        current_lang = self._manager.language()
        for code, name_key in (("zh", "lang_name_zh"), ("en", "lang_name_en")):
            act_lang = QAction(t(name_key), lang_menu)
            act_lang.setCheckable(True)
            act_lang.setChecked(current_lang == code)

            def _make_set_lang(lc):
                def _set():
                    self._manager.set_language(lc)
                return _set

            act_lang.triggered.connect(_make_set_lang(code))
            lang_menu.addAction(act_lang)
        menu.addMenu(lang_menu)

        menu.addSeparator()

        act_clear = QAction(t("clear_notes"), self)
        act_clear.triggered.connect(lambda: self._manager.clear_all_notes(self))
        menu.addAction(act_clear)

        act_min = QAction(t("minimize"), self)
        act_min.triggered.connect(self._manager.minimize_to_tray)
        menu.addAction(act_min)

        act_quit = QAction(t("quit"), self)
        act_quit.triggered.connect(self._quit)
        menu.addAction(act_quit)

        menu.exec(global_pos)

    # ── 菜单动作 ──────────────────────────────────────────

    def _rename_note(self):
        dlg = QInputDialog(self)
        dlg.setWindowTitle(t("rename_title"))
        dlg.setLabelText(t("rename_prompt"))
        dlg.setTextValue(self.settings.get("name", ""))
        dlg.setOkButtonText(t("save"))
        dlg.setCancelButtonText(t("cancel"))
        if dlg.exec() and dlg.textValue().strip():
            self.settings["name"] = dlg.textValue().strip()
            self._manager.save()

    def _new_note(self):
        nid = self._manager.create_note(source_win=self)
        self._manager.show_note(nid)

    def _toggle_lock(self, checked: bool):
        self.settings["locked"] = checked
        self.update()
        self._apply_lock_passthrough()
        self._manager.save()

    def _apply_lock_passthrough(self):
        """锁定时设置 WS_EX_TRANSPARENT，实现真正的鼠标穿透（跨进程生效）。"""
        _GWL_EXSTYLE      = -20
        _WS_EX_TRANSPARENT = 0x00000020
        hwnd = int(self.winId())
        ex = ctypes.windll.user32.GetWindowLongW(hwnd, _GWL_EXSTYLE)
        if self.settings.get("locked", False):
            ctypes.windll.user32.SetWindowLongW(hwnd, _GWL_EXSTYLE, ex | _WS_EX_TRANSPARENT)
            # WS_EX_TRANSPARENT 会让窗口收不到任何鼠标消息，
            # 改用定时器轮询来检测 Ctrl+Alt+右键，以替代原先的 nativeEvent 方案
            if not hasattr(self, "_lock_timer"):
                self._lock_timer = QTimer(self)
                self._lock_timer.setInterval(80)
                self._lock_timer.timeout.connect(self._poll_lock_menu)
                self._lock_menu_active = False
            self._lock_timer.start()
        else:
            ctypes.windll.user32.SetWindowLongW(hwnd, _GWL_EXSTYLE, ex & ~_WS_EX_TRANSPARENT)
            if hasattr(self, "_lock_timer"):
                self._lock_timer.stop()

    def _poll_lock_menu(self):
        """80ms 轮询：检测 Ctrl+Alt+右键，光标在窗口范围内时弹出菜单。"""
        ctrl = ctypes.windll.user32.GetKeyState(0x11) & 0x8000
        alt  = ctypes.windll.user32.GetKeyState(0x12) & 0x8000
        rbtn = ctypes.windll.user32.GetKeyState(0x02) & 0x8000
        if ctrl and alt and rbtn:
            if not self._lock_menu_active:
                pt = ctypes.wintypes.POINT()
                ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
                if self.geometry().contains(QPoint(pt.x, pt.y)):
                    self._lock_menu_active = True
                    self.show_context_menu(QPoint(pt.x, pt.y))
        else:
            self._lock_menu_active = False

    def _toggle_always_on_top(self, checked: bool):
        self.settings["always_on_top"] = checked
        flags = Qt.Tool | Qt.FramelessWindowHint
        if checked:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()
        # setWindowFlags 后 show() 会重建原生窗口，需重新应用穿透样式
        QTimer.singleShot(0, self._apply_lock_passthrough)
        self._manager.save()

    def _quit(self):
        self._save_geometry()
        self._manager.quit()

    # ── 窗口事件 ──────────────────────────────────────────

    def showEvent(self, event):
        super().showEvent(event)
        # 窗口（重）显示后补充应用穿透样式，确保 setWindowFlags 重建后不丢失
        QTimer.singleShot(0, self._apply_lock_passthrough)

    def moveEvent(self, event):
        super().moveEvent(event)
        QTimer.singleShot(300, self._save_geometry)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self._apply_vertical_align)
        QTimer.singleShot(300, self._save_geometry)

    def closeEvent(self, event):
        if self._really_closing or self._manager._quitting:
            self._save_geometry()
            event.accept()
        else:
            self._manager.hide_note(self._note_id)
            event.ignore()

    # ── Windows 原生消息处理 ──────────────────────────────

    def nativeEvent(self, eventType, message):
        if eventType != b"windows_generic_MSG":
            return super().nativeEvent(eventType, message)

        msg = _WinMsg.from_address(int(message))

        if msg.message == 0x00A5:   # WM_RBUTTONUP，客户区坐标
            cx = ctypes.c_short(msg.lParam & 0xFFFF).value
            cy = ctypes.c_short((msg.lParam >> 16) & 0xFFFF).value
            self.show_context_menu(self.mapToGlobal(QPoint(cx, cy)))
            return True, 0
        if msg.message == 0x00A6:   # WM_NCRBUTTONUP，屏幕坐标
            sx = ctypes.c_short(msg.lParam & 0xFFFF).value
            sy = ctypes.c_short((msg.lParam >> 16) & 0xFFFF).value
            self.show_context_menu(QPoint(sx, sy))
            return True, 0

        if msg.message == 0x0084:  # WM_NCHITTEST，命中测试（缩放/拖动区域）
            x = ctypes.c_short(msg.lParam & 0xFFFF).value
            y = ctypes.c_short((msg.lParam >> 16) & 0xFFFF).value
            pos = self.mapFromGlobal(QPoint(x, y))
            cx, cy = pos.x(), pos.y()
            w, h = self.width(), self.height()
            # 拖拽区域与页边距保持一致，保证缩放后视觉边距不变
            Bx = max(6, self.settings.get("padding_x", 8))
            By = max(6, self.settings.get("padding_y", 8))

            if cy < By and cx < Bx:        return True, 13  # 左上角
            if cy < By and cx > w - Bx:    return True, 14  # 右上角
            if cy > h - By and cx < Bx:    return True, 16  # 左下角
            if cy > h - By and cx > w - Bx: return True, 17  # 右下角
            if cy < By:                    return True, 12  # 上边
            if cy > h - By:                return True, 15  # 下边
            if cx < Bx:                    return True, 10  # 左边
            if cx > w - Bx:                return True, 11  # 右边
            return True, 1   # 客户区（拖动移动）

        return super().nativeEvent(eventType, message)


# ──────────────────────────────────────────────────────────
# 全局快捷键监听
# ──────────────────────────────────────────────────────────

class HotkeyListener(QWidget):
    """隐藏窗口：注册全局快捷键，通过 WM_HOTKEY 消息回调 NoteManager。

    快捷键：
        Ctrl+Alt+N  新建便签
        Ctrl+Alt+H  显示/隐藏全部便签（切换）
    """

    _MOD_ALT     = 0x0001
    _MOD_CONTROL = 0x0002
    _WM_HOTKEY   = 0x0312

    # 热键 ID → (修饰键, 虚拟键码)
    _HOTKEYS: dict[int, tuple[int, int]] = {
        1: (_MOD_CONTROL | _MOD_ALT, 0x4E),   # Ctrl+Alt+N
        2: (_MOD_CONTROL | _MOD_ALT, 0x48),   # Ctrl+Alt+H
    }

    def __init__(self, manager: "NoteManager"):
        super().__init__()
        self._manager = manager
        self._hwnd: int | None = None
        # 不显示在任务栏，1×1 窗口放在屏幕外
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        self.resize(1, 1)
        self.move(-200, -200)

    def start(self):
        """注册所有快捷键。若某键已被其他程序占用则静默跳过。"""
        self.show()   # 必须先 show()，winId() 才有效
        self._hwnd = int(self.winId())
        for hid, (mods, vk) in self._HOTKEYS.items():
            ctypes.windll.user32.RegisterHotKey(self._hwnd, hid, mods, vk)

    def stop(self):
        """注销所有快捷键。"""
        if self._hwnd:
            for hid in self._HOTKEYS:
                ctypes.windll.user32.UnregisterHotKey(self._hwnd, hid)
        self.hide()

    def nativeEvent(self, eventType, message):
        if eventType == b"windows_generic_MSG":
            msg = _WinMsg.from_address(int(message))
            if msg.message == self._WM_HOTKEY:
                hid = int(msg.wParam)
                if hid == 1:
                    self._manager._hotkey_new_note()
                elif hid == 2:
                    self._manager._toggle_all_notes()
                return True, 0
        return super().nativeEvent(eventType, message)


# ──────────────────────────────────────────────────────────
# 应用管理器（数据、窗口、托盘、IPC、生命周期）
# ──────────────────────────────────────────────────────────

class NoteManager:
    """管理所有便签数据、窗口实例、系统托盘及单实例 IPC。"""

    def __init__(self, app: QApplication | None = None):
        self._app = app or QApplication.instance()
        self._data: dict = {}
        self._windows: dict[str, NoteWindow] = {}
        self._quitting = False
        self._tray: QSystemTrayIcon | None = None
        self._ipc_server: QLocalServer | None = None
        self._hotkey_listener: HotkeyListener | None = None
        self._load()

    # ── 数据加载与迁移 ────────────────────────────────────

    def _load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                if "notes" in raw:
                    self._data = raw
                    for note in self._data["notes"].values():
                        self._migrate_note(note)
                else:
                    self._migrate_note(raw)
                    nid = self._new_id()
                    raw.setdefault("name", "便签 1")
                    raw.setdefault("visible", True)
                    self._data = {"notes": {nid: raw}}
                set_lang(self._data.get("language", "zh"))
                return
            except Exception:
                pass
        nid = self._new_id()
        self._data = {"notes": {nid: {
            **DEFAULT_SETTINGS, "name": "便签 1", "visible": True,
        }}}

    @staticmethod
    def _migrate_note(note: dict):
        if "opacity" in note and "bg_opacity" not in note:
            note["bg_opacity"] = note.pop("opacity")
        if "glow_radius" in note and "glow_opacity" not in note:
            note["glow_opacity"] = min(100, int(note.pop("glow_radius")))
        elif "glow_radius" in note:
            note.pop("glow_radius")
        # 清理已废弃的外发光 / 边框发光字段
        for dead_key in ("outer_glow_strength", "outer_glow_opacity",
                         "border_glow_strength", "border_glow_opacity",
                         "outer_glow_enabled", "outer_glow_color",
                         "border_glow_enabled", "border_glow_color", "border_glow_radius"):
            note.pop(dead_key, None)
        # 旧的 text_align 仅有 left/center/right 三种，迁移为九宫格格式
        old_align = note.get("text_align", "")
        if old_align in ("left", "center", "right"):
            note["text_align"] = f"top-{old_align}"
        for k, v in DEFAULT_SETTINGS.items():
            note.setdefault(k, v)
        note.setdefault("name", "便签")
        note.setdefault("visible", True)

    # ── 语言 ──────────────────────────────────────────────

    def _new_id(self) -> str:
        return uuid.uuid4().hex[:8]

    def language(self) -> str:
        return self._data.get("language", "zh")

    def set_language(self, lang: str):
        self._data["language"] = lang
        set_lang(lang)
        # 销毁所有子对话框，下次打开时以新语言重建
        for win in self._windows.values():
            for attr in ("_md_editor", "_appearance_editor"):
                dlg = getattr(win, attr, None)
                if dlg:
                    dlg.hide()
                    setattr(win, attr, None)
        self._rebuild_tray_menu()
        self.save()

    # ── 系统托盘 ──────────────────────────────────────────

    def _make_tray_icon(self) -> QIcon:
        size = 32
        px = QPixmap(size, size)
        px.fill(Qt.GlobalColor.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # 便签背景
        p.setBrush(QColor("#FFD54F"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(2, 2, size - 4, size - 4, 4, 4)
        # 折角
        p.setBrush(QColor("#FFA000"))
        corner = 9
        poly = QPolygonF([
            QPointF(size - 2 - corner, 2),
            QPointF(size - 2, 2 + corner),
            QPointF(size - 2 - corner, 2 + corner),
        ])
        p.drawPolygon(poly)
        # 文字横线
        p.setPen(QPen(QColor("#5D4037"), 2))
        for y in [13, 18, 23]:
            p.drawLine(7, y, size - 10, y)
        p.end()
        return QIcon(px)

    def _build_tray_menu(self) -> QMenu:
        menu = QMenu()
        act_show = QAction(t("tray_show_all"), menu)
        act_show.triggered.connect(self._show_all_notes)
        menu.addAction(act_show)
        menu.addSeparator()
        act_quit = QAction(t("quit"), menu)
        act_quit.triggered.connect(self.quit)
        menu.addAction(act_quit)
        return menu

    def _rebuild_tray_menu(self):
        if self._tray:
            self._tray.setContextMenu(self._build_tray_menu())
            self._tray.setToolTip(t("tray_tooltip"))

    def _create_tray(self):
        self._tray = QSystemTrayIcon(self._make_tray_icon())
        self._tray.setToolTip(t("tray_tooltip"))
        self._tray.setContextMenu(self._build_tray_menu())
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_all_notes()

    def _show_all_notes(self):
        for note_id, note in self._data["notes"].items():
            if note.get("visible", True):
                if note_id in self._windows:
                    self._windows[note_id].show()
                    self._windows[note_id].activateWindow()
                    self._windows[note_id].raise_()

    def minimize_to_tray(self):
        for win in self._windows.values():
            win.hide()

    def _toggle_all_notes(self):
        """Ctrl+Alt+H：有便签可见则全部隐藏，否则全部显示。"""
        any_visible = any(w.isVisible() for w in self._windows.values())
        if any_visible:
            self.minimize_to_tray()
        else:
            self._show_all_notes()

    def clear_all_notes(self, source_win: "NoteWindow | None" = None):
        title = t("clear_notes").rstrip("…").rstrip("...")
        if not _ask_yes_no(source_win, title, t("clear_notes_prompt"), center_buttons=True):
            # 对话框关闭后，确保所有应可见的便签窗口被重新显示
            self._show_all_notes()
            return
        # 关闭所有窗口
        for win in list(self._windows.values()):
            win._really_closing = True
            win.close()
        self._windows.clear()
        self._data["notes"] = {}
        # 新建一个空白便签
        nid = self.create_note()
        self.save()
        self.show_note(nid)

    # ── 持久化 ────────────────────────────────────────────

    def save(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存失败: {e}")

    # ── 便签生命周期 ───────────────────────────────────────

    def notes(self) -> dict:
        return self._data["notes"]

    def create_note(self, source_win: "NoteWindow | None" = None) -> str:
        nid = self._new_id()
        existing = {n.get("name", "") for n in self._data["notes"].values()}
        idx = len(self._data["notes"]) + 1
        name = f"便签 {idx}"
        while name in existing:
            idx += 1
            name = f"便签 {idx}"

        if source_win is not None:
            geo = source_win.frameGeometry()
            new_x = geo.right() + 10
            new_y = geo.top()
        else:
            offset = len(self._data["notes"]) * 25
            new_x = DEFAULT_SETTINGS["x"] + offset
            new_y = DEFAULT_SETTINGS["y"] + offset

        self._data["notes"][nid] = {
            **DEFAULT_SETTINGS,
            "name": name,
            "visible": True,
            "x": new_x,
            "y": new_y,
        }
        self.save()
        return nid

    def show_note(self, note_id: str):
        self._data["notes"][note_id]["visible"] = True
        if note_id in self._windows:
            self._windows[note_id].show()
            self._windows[note_id].activateWindow()
        else:
            win = NoteWindow(note_id, self)
            self._windows[note_id] = win
            win.show()
        self.save()

    def hide_note(self, note_id: str):
        self._data["notes"][note_id]["visible"] = False
        if note_id in self._windows:
            self._windows[note_id].hide()
        self.save()

    def delete_note(self, note_id: str):
        if note_id in self._windows:
            win = self._windows.pop(note_id)
            win._really_closing = True
            for attr in ("_md_editor", "_appearance_editor"):
                dlg = getattr(win, attr, None)
                if dlg:
                    try:
                        dlg._note = None
                    except Exception:
                        pass
                    dlg.close()
            win.close()
        del self._data["notes"][note_id]
        self.save()

    # ── 应用生命周期 ───────────────────────────────────────

    def start(self):
        self._create_tray()
        self._ipc_server = QLocalServer(self._app)
        self._ipc_server.newConnection.connect(self._on_ipc_connection)
        self._ipc_server.listen("TempNote_SingleInstance")
        self._hotkey_listener = HotkeyListener(self)
        self._hotkey_listener.start()
        shown = 0
        for nid, note in self._data["notes"].items():
            if note.get("visible", True):
                win = NoteWindow(nid, self)
                self._windows[nid] = win
                win.show()
                shown += 1
        if shown == 0 and self._data["notes"]:
            self.show_note(next(iter(self._data["notes"])))

    def _on_ipc_connection(self):
        conn = self._ipc_server.nextPendingConnection()
        if conn:
            conn.disconnectFromServer()
        self._show_all_notes()

    def _hotkey_new_note(self):
        """Ctrl+Alt+N：新建便签，出现在最后一个可见便签的右侧。"""
        source = next((w for w in self._windows.values() if w.isVisible()), None)
        nid = self.create_note(source_win=source)
        self.show_note(nid)

    def quit(self):
        self._quitting = True
        if self._hotkey_listener:
            self._hotkey_listener.stop()
        if self._tray:
            self._tray.hide()
        if self._ipc_server:
            self._ipc_server.close()
        self.save()
        QApplication.quit()


# ──────────────────────────────────────────────────────────
# 入口
# ──────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("TempNote")

    # 单实例检测：尝试连接已运行的实例
    sock = QLocalSocket()
    sock.connectToServer("TempNote_SingleInstance")
    if sock.waitForConnected(300):
        # 已有实例在运行，通知它显示便签后退出
        sock.disconnectFromServer()
        sys.exit(0)
    sock.close()

    # 清理可能残留的 socket（上次异常退出时留下）
    QLocalServer.removeServer("TempNote_SingleInstance")

    manager = NoteManager(app)
    manager.start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
