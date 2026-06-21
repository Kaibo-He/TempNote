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
)
from PySide6.QtCore import Qt, QTimer, QPoint, QRectF, QPointF
from PySide6.QtGui import (
    QColor, QFont, QAction, QPainter, QPen, QPixmap,
    QTextCharFormat, QTextCursor, QTextBlockFormat,
)

# 打包为 exe 时用 sys.executable 定位，确保 notes.json 始终在 exe 旁边
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
        "delete_note":     "删除此便签",
        "edit_md":         "编辑 Markdown…",
        "appearance":      "外观设置…",
        "always_on_top":   "始终置顶",
        "lock":            "锁定",
        "language":        "语言",
        "minimize":        "最小化",
        "quit":            "退出",
        # 对话框
        "rename_title":    "重命名便签",
        "rename_prompt":   "请输入便签名称：",
        "delete_title":    "删除便签",
        "delete_prompt":   "确认删除「{name}」？\n输入 Y 后按确定：",
        # 外观设置窗口
        "ap_title":        "外观设置 — TempNote",
        "col_group":       "颜色",
        "col_bg":          "背景颜色",
        "col_text":        "文字颜色",
        "opacity":         "透明度",
        "font_group":      "字体",
        "font_lbl":        "字体",
        "size_lbl":        "字号",
        "bold":            "加粗",
        "underline":       "下划线",
        "spacing_group":   "间距",
        "l_spacing":       "字间距",
        "ln_spacing":      "行  距",
        "fx_group":        "文字效果",
        "glow_on":         "启用发光",
        "glow_col_pick":   "选择发光颜色",
        "stroke_on":       "启用描边",
        "stroke_col_pick": "选择描边颜色",
        "width_lbl":       "宽度",
        "fx_hint":         "发光与描边互斥，后启用者生效",
        "border_group":    "边框",
        "border_on":       "启用边框",
        "border_col_pick": "选择边框颜色",
        "border_w_lbl":    "边框宽度",
        "border_r_lbl":    "圆角半径",
        "outer_glow_group":    "外边框发光",
        "outer_glow_on":       "启用外发光",
        "outer_glow_col_pick": "选择发光颜色",
        "outer_glow_radius_lbl":   "发光半径",
        "outer_glow_strength_lbl": "发光强度",
        "layout_group":    "布局",
        "padding_x_lbl":   "水平边距",
        "padding_y_lbl":   "垂直边距",
        "align_lbl":       "对齐",
        "align_left":      "居左",
        "align_center":    "居中",
        "align_right":     "居右",
        "save":            "保存",
        "cancel":          "取消",
        # Markdown 编辑器
        "md_title":        "Markdown 编辑器 — TempNote",
        # 语言选项显示名
        "lock_hint":       "🔒 锁定中 · Ctrl+Shift+右键 打开菜单",
        "lang_name_zh":    "中文",
        "lang_name_en":    "English",
    },
    "en": {
        "rename_note":     "Rename Note…",
        "new_note":        "New Note",
        "note_list":       "Notes",
        "note_current":    "current",
        "delete_note":     "Delete This Note",
        "edit_md":         "Edit Markdown…",
        "appearance":      "Appearance…",
        "always_on_top":   "Always on Top",
        "lock":            "Lock",
        "language":        "Language",
        "minimize":        "Minimize",
        "quit":            "Quit",
        "rename_title":    "Rename Note",
        "rename_prompt":   "Enter note name:",
        "delete_title":    "Delete Note",
        "delete_prompt":   'Delete "{name}"?\nType Y to confirm:',
        "ap_title":        "Appearance — TempNote",
        "col_group":       "Colors",
        "col_bg":          "Background",
        "col_text":        "Text",
        "opacity":         "Opacity",
        "font_group":      "Font",
        "font_lbl":        "Font",
        "size_lbl":        "Size",
        "bold":            "Bold",
        "underline":       "Underline",
        "spacing_group":   "Spacing",
        "l_spacing":       "Letters",
        "ln_spacing":      "Lines",
        "fx_group":        "Text Effects",
        "glow_on":         "Enable Glow",
        "glow_col_pick":   "Glow Color",
        "stroke_on":       "Enable Stroke",
        "stroke_col_pick": "Stroke Color",
        "width_lbl":       "Width",
        "fx_hint":         "Glow and stroke are mutually exclusive",
        "border_group":    "Border",
        "border_on":       "Enable Border",
        "border_col_pick": "Border Color",
        "border_w_lbl":    "Width",
        "border_r_lbl":    "Radius",
        "outer_glow_group":    "Outer Glow",
        "outer_glow_on":       "Enable",
        "outer_glow_col_pick": "Glow Color",
        "outer_glow_radius_lbl":   "Radius",
        "outer_glow_strength_lbl": "Strength",
        "layout_group":    "Layout",
        "padding_x_lbl":   "H-Padding",
        "padding_y_lbl":   "V-Padding",
        "align_lbl":       "Align",
        "align_left":      "Left",
        "align_center":    "Center",
        "align_right":     "Right",
        "save":            "Save",
        "cancel":          "Cancel",
        "md_title":        "Markdown Editor — TempNote",
        "lock_hint":       "🔒 Locked · Ctrl+Shift+RClick for menu",
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


# ──────────────────────────────────────────────────────────
# 设置常量
# ──────────────────────────────────────────────────────────

APPEARANCE_KEYS = [
    "bg_opacity", "text_opacity", "bg_color", "text_color",
    "font_family", "font_size", "bold", "underline",
    "letter_spacing", "line_spacing",
    "glow_enabled", "glow_color", "glow_opacity",
    "stroke_enabled", "stroke_color", "stroke_width",
    "border_enabled", "border_color", "border_width", "border_radius",
    "outer_glow_enabled", "outer_glow_color", "outer_glow_radius", "outer_glow_strength",
    "padding_x", "padding_y", "text_align",
]

DEFAULT_SETTINGS = {
    "content": "右键在 Markdown 中编辑",
    "x": 200, "y": 200, "width": 320, "height": 320,
    "always_on_top": False,
    "bg_opacity": 100, "text_opacity": 100,
    "bg_color": "#1E1E1E", "text_color": "#F5F5F5",
    "font_family": "等线", "font_size": 13,
    "bold": False, "underline": False,
    "letter_spacing": 0, "line_spacing": 100,
    "glow_enabled": False, "glow_color": "#FFFF00", "glow_opacity": 80,
    "stroke_enabled": False, "stroke_color": "#000000", "stroke_width": 2,
    "border_enabled": False, "border_color": "#BDBDBD",
    "border_width": 1, "border_radius": 0,
    "outer_glow_enabled": False, "outer_glow_color": "#FFFFFF",
    "outer_glow_radius": 12, "outer_glow_strength": 60,
    "padding_x": 8,      # 水平页边距 px（0-40）
    "padding_y": 8,      # 垂直页边距 px（0-40）
    "text_align": "left",  # "left" | "center" | "right"
    "locked": False,
}


# ──────────────────────────────────────────────────────────
# ClippedGlowEffect
# ──────────────────────────────────────────────────────────

class ClippedGlowEffect(QGraphicsDropShadowEffect):
    def boundingRectFor(self, rect: QRectF) -> QRectF:
        return rect


class TextStrokeEffect(QGraphicsDropShadowEffect):
    """
    真实文字描边：将 source 像素图染色后在四周偏移绘制，再盖上原图。
    继承 QGraphicsDropShadowEffect 仅为利用其 Qt 注册机制；
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

    def set_params(self, color: QColor, width: int):
        self._stroke_color = QColor(color)
        self._stroke_width = max(1, width)
        self.update()

    def boundingRectFor(self, rect: QRectF) -> QRectF:
        return rect  # 裁剪到控件边界，避免窗口渲染错误

    def draw(self, painter: QPainter):
        # PySide6 中 sourcePixmap 直接返回 QPixmap，偏移量固定为原点
        src = self.sourcePixmap(Qt.CoordinateSystem.LogicalCoordinates)
        if src.isNull():
            self.drawSource(painter)
            return
        offset = QPointF(0, 0)

        # 用描边颜色染色 source pixmap
        stroke_px = QPixmap(src.size())
        stroke_px.fill(Qt.GlobalColor.transparent)
        sp = QPainter(stroke_px)
        sp.drawPixmap(0, 0, src)
        sp.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        sp.fillRect(stroke_px.rect(), self._stroke_color)
        sp.end()

        # 在圆形范围内的各偏移位置绘制描边层
        w = self._stroke_width
        r2 = w * w
        painter.save()
        for dx in range(-w, w + 1):
            for dy in range(-w, w + 1):
                if dx == 0 and dy == 0:
                    continue
                if dx * dx + dy * dy <= r2:
                    painter.drawPixmap(offset + QPointF(dx, dy), stroke_px)
        painter.restore()

        # 原始内容盖在最上层
        self.drawSource(painter)


# ──────────────────────────────────────────────────────────
# MDSourceEdit
# ──────────────────────────────────────────────────────────

class MDSourceEdit(QTextEdit):
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
# MarkdownEditorDialog
# ──────────────────────────────────────────────────────────

class MarkdownEditorDialog(QWidget):
    def __init__(self, note_window: "NoteWindow"):
        super().__init__()
        self._note = note_window
        self.setWindowTitle(t("md_title"))
        self.resize(580, 500)
        self.setWindowFlag(Qt.WindowType.Window)

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

    def open_with_content(self, content: str):
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
        content = self.src.toPlainText()
        self._note.settings["content"] = content
        self._note.render_content(content)
        self._note._manager.save()
        self.hide()

    def closeEvent(self, event):
        event.ignore()
        self.hide()


# ──────────────────────────────────────────────────────────
# AppearanceDialog
# ──────────────────────────────────────────────────────────

class AppearanceDialog(QWidget):
    def __init__(self, note_window: "NoteWindow"):
        super().__init__()
        self._note = note_window
        self._original: dict = {}
        self._refreshers: list = []

        self.setWindowTitle(t("ap_title"))
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
        inner_vb.addWidget(self._build_outer_glow_group())
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

        row2 = QWidget()
        h2 = QHBoxLayout(row2)
        h2.setContentsMargins(0, 0, 0, 0)
        h2.setSpacing(20)
        h2.addWidget(self._checkbox("bold",      t("bold"),      lambda _: apply()))
        h2.addWidget(self._checkbox("underline", t("underline"), lambda _: apply()))
        h2.addStretch()
        vb.addWidget(row2)

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
                setting_key, 0, 40, "px",
                lambda: self._note._apply_padding()
            )
            ph.addWidget(lbl)
            ph.addWidget(sl_w, 1)
            vb.addWidget(pad_row)

        # 对齐按钮组
        align_row = QWidget()
        ah = QHBoxLayout(align_row)
        ah.setContentsMargins(0, 0, 0, 0)
        ah.setSpacing(8)
        ah.addWidget(QLabel(t("align_lbl")))

        btn_grp = QButtonGroup(align_row)
        btn_grp.setExclusive(True)
        current_align = self._note.settings.get("text_align", "left")
        align_btns: dict[str, QPushButton] = {}

        for align_val, str_key in (
            ("left",   "align_left"),
            ("center", "align_center"),
            ("right",  "align_right"),
        ):
            btn = QPushButton(t(str_key))
            btn.setCheckable(True)
            btn.setChecked(current_align == align_val)
            btn_grp.addButton(btn)
            ah.addWidget(btn)
            align_btns[align_val] = btn

        def _on_align(btn_checked: bool):
            if not btn_checked:
                return
            for av, b in align_btns.items():
                if b.isChecked():
                    self._note.settings["text_align"] = av
                    self._note.render_content(self._note.settings.get("content", ""))
                    break

        for b in align_btns.values():
            b.toggled.connect(_on_align)

        ah.addStretch()
        vb.addWidget(align_row)

        # 刷新时同步控件状态
        self._refreshers.append(
            lambda bmap=align_btns: [
                b.blockSignals(True) or
                b.setChecked(self._note.settings.get("text_align", "left") == av) or
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

        glow_cb_ref:   list = [None]
        stroke_cb_ref: list = [None]

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

    def _build_outer_glow_group(self) -> QGroupBox:
        group = QGroupBox(t("outer_glow_group"))
        vb = QVBoxLayout(group)
        vb.setContentsMargins(10, 16, 10, 8)
        vb.setSpacing(8)

        def apply():
            self._note._apply_padding()
            self._note.update()

        row1 = QWidget()
        h1 = QHBoxLayout(row1)
        h1.setContentsMargins(0, 0, 0, 0)
        h1.setSpacing(8)
        h1.addWidget(self._checkbox("outer_glow_enabled", t("outer_glow_on"), lambda _: apply()))
        h1.addWidget(self._color_btn("outer_glow_color", t("outer_glow_col_pick"), apply))
        h1.addStretch()
        vb.addWidget(row1)

        for label, key, lo, hi, suffix in (
            (t("outer_glow_radius_lbl"),   "outer_glow_radius",   1, 40, "px"),
            (t("outer_glow_strength_lbl"), "outer_glow_strength", 1, 100, "%"),
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
        if self._note is None:
            # 便签已被删除，直接允许关闭
            event.accept()
            return
        event.ignore()
        self._cancel()


# ──────────────────────────────────────────────────────────
# NoteEdit
# ──────────────────────────────────────────────────────────

class NoteEdit(QTextEdit):
    def __init__(self, window: "NoteWindow"):
        super().__init__(window)
        self._win = window
        self._drag_pos = None
        self.setReadOnly(True)
        self.setAutoFillBackground(False)
        self.viewport().setAutoFillBackground(False)
        self.setStyleSheet("background: transparent; border: none;")
        self.viewport().setStyleSheet("background: transparent;")

    def contextMenuEvent(self, event):
        self._win.show_context_menu(event.globalPos())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint()
                - self._win.frameGeometry().topLeft()
            )
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self._win.move(event.globalPosition().toPoint() - self._drag_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = None
        super().mouseReleaseEvent(event)


# ──────────────────────────────────────────────────────────
# NoteWindow
# ──────────────────────────────────────────────────────────

class NoteWindow(QWidget):
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
        layout.addWidget(self.editor)

        self._md_editor: MarkdownEditorDialog | None = None
        self._appearance_editor: AppearanceDialog | None = None

        self._initialized = False
        self._apply_all_settings()
        self._restore_content()
        self._initialized = True

    # ── 初始化 ────────────────────────────────────────────

    def _init_window(self):
        s = self.settings
        flags = Qt.Window | Qt.FramelessWindowHint
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
        full_rect = QRectF(self.rect())

        # 计算外发光占用的边距
        og_enabled = s.get("outer_glow_enabled", False)
        og_radius = s.get("outer_glow_radius", 12) if og_enabled else 0

        # 背景所在的内矩形（外发光绘制在四周透明边距中）
        bg_rect = full_rect.adjusted(og_radius, og_radius, -og_radius, -og_radius)

        # 清空整个窗口为透明
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        # 外边框发光：从 bg_rect 向外扩散，逐层降低 alpha
        if og_enabled and og_radius > 0:
            og_color  = QColor(s.get("outer_glow_color", "#FFFFFF"))
            og_strength = s.get("outer_glow_strength", 60)
            painter.setPen(Qt.PenStyle.NoPen)
            for i in range(og_radius, 0, -1):
                # 越靠近 bg_rect 越亮（i 越小越亮）
                progress = 1.0 - i / og_radius          # 0(外边缘) → 接近 1(内边缘)
                alpha = int(og_strength / 100 * 255 * progress * progress)
                ring_color = QColor(og_color.red(), og_color.green(), og_color.blue(), alpha)
                painter.setBrush(ring_color)
                ring_rect = bg_rect.adjusted(-i, -i, i, i)
                r = radius + i if radius > 0 else 0
                if r > 0:
                    painter.drawRoundedRect(ring_rect, r, r)
                else:
                    painter.drawRect(ring_rect)

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
        og = self.settings.get("outer_glow_radius", 12) if self.settings.get("outer_glow_enabled", False) else 0
        self.layout().setContentsMargins(px + og, py + og, px + og, py + og)

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
        self.update()
        if self._initialized:
            self.render_content(self.settings.get("content", ""))

    def _apply_font(self):
        s = self.settings
        font = QFont(s["font_family"], s["font_size"])
        font.setBold(s["bold"])
        font.setUnderline(s["underline"])
        self.editor.setFont(font)
        if self._initialized:
            self.render_content(self.settings.get("content", ""))

    def _apply_text_effect(self):
        s = self.settings
        if s.get("glow_enabled"):
            effect = ClippedGlowEffect(self.editor)
            effect.setOffset(0, 0)
            effect.setBlurRadius(15)
            color = QColor(s["glow_color"])
            color.setAlpha(round(s.get("glow_opacity", 80) / 100 * 255))
            effect.setColor(color)
            self.editor.setGraphicsEffect(effect)
        elif s.get("stroke_enabled"):
            effect = TextStrokeEffect(
                QColor(s.get("stroke_color", "#000000")),
                max(1, s.get("stroke_width", 2)),
                self.editor,
            )
            self.editor.setGraphicsEffect(effect)
        else:
            self.editor.setGraphicsEffect(None)

    def render_content(self, content: str):
        self.editor.setMarkdown(content)
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
        align_map = {
            "left":   Qt.AlignmentFlag.AlignLeft,
            "center": Qt.AlignmentFlag.AlignHCenter,
            "right":  Qt.AlignmentFlag.AlignRight,
        }
        align = align_map.get(s.get("text_align", "left"), Qt.AlignmentFlag.AlignLeft)

        cursor.movePosition(QTextCursor.MoveOperation.Start)
        while True:
            blk_fmt = QTextBlockFormat(cursor.blockFormat())
            blk_fmt.setLineHeight(
                line_sp,
                QTextBlockFormat.LineHeightTypes.ProportionalHeight.value
            )
            blk_fmt.setAlignment(align)
            cursor.setBlockFormat(blk_fmt)
            if not cursor.movePosition(QTextCursor.MoveOperation.NextBlock):
                break

    def _restore_content(self):
        self.render_content(self.settings.get("content", ""))

    # ── 保存 ──────────────────────────────────────────────

    def _save_geometry(self):
        geo = self.geometry()
        self.settings.update({
            "x": geo.x(), "y": geo.y(),
            "width": geo.width(), "height": geo.height(),
        })
        self._manager.save()

    def _save_all(self):
        geo = self.geometry()
        self.settings.update({
            "x": geo.x(), "y": geo.y(),
            "width": geo.width(), "height": geo.height(),
        })
        self._manager.save()

    def _open_md_editor(self):
        if self._md_editor is None:
            self._md_editor = MarkdownEditorDialog(self)
        self._md_editor.open_with_content(self.settings.get("content", ""))

    def _open_appearance(self):
        if self._appearance_editor is None:
            self._appearance_editor = AppearanceDialog(self)
        self._appearance_editor.open()

    # ── 右键菜单 ──────────────────────────────────────────

    def show_context_menu(self, global_pos):
        menu = QMenu(self)

        name_lbl = QLabel(f"  \U0001f4dd  {self.settings.get('name', '便签')}")
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

        notes_menu = QMenu(t("note_list"), menu)
        for nid, note in self._manager.notes().items():
            note_name = note.get("name", "")
            is_current = (nid == self._note_id)
            if is_current:
                act_n = QAction(f"● {note_name}（{t('note_current')}）", notes_menu)
                act_n.setEnabled(False)
            else:
                is_visible = note.get("visible", True)
                act_n = QAction(("✓ " if is_visible else "    ") + note_name, notes_menu)
                act_n.setCheckable(True)
                act_n.setChecked(is_visible)

                def _make_toggle(n_id):
                    def _toggle(checked):
                        if checked:
                            self._manager.show_note(n_id)
                        else:
                            self._manager.hide_note(n_id)
                    return _toggle

                act_n.triggered.connect(_make_toggle(nid))
            notes_menu.addAction(act_n)

        if len(self._manager.notes()) > 1:
            notes_menu.addSeparator()
            act_del = QAction(t("delete_note"), notes_menu)
            act_del.triggered.connect(self._delete_note)
            notes_menu.addAction(act_del)

        menu.addMenu(notes_menu)

        menu.addSeparator()

        act_edit = QAction(t("edit_md"), self)
        act_edit.triggered.connect(self._open_md_editor)
        menu.addAction(act_edit)

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

        act_min = QAction(t("minimize"), self)
        act_min.triggered.connect(self.showMinimized)
        menu.addAction(act_min)

        act_quit = QAction(t("quit"), self)
        act_quit.triggered.connect(self._quit)
        menu.addAction(act_quit)

        menu.exec(global_pos)

    # ── 菜单动作 ──────────────────────────────────────────

    def _rename_note(self):
        name, ok = QInputDialog.getText(
            self, t("rename_title"), t("rename_prompt"),
            text=self.settings.get("name", "")
        )
        if ok and name.strip():
            self.settings["name"] = name.strip()
            self._manager.save()

    def _new_note(self):
        nid = self._manager.create_note()
        self._manager.show_note(nid)

    def _delete_note(self):
        name = self.settings.get("name", "")
        confirm, ok = QInputDialog.getText(
            self, t("delete_title"), t("delete_prompt", name=name)
        )
        if ok and confirm.strip().lower() == "y":
            self._manager.delete_note(self._note_id)

    def _toggle_lock(self, checked: bool):
        self.settings["locked"] = checked
        self.update()
        self._manager.save()

    def _toggle_always_on_top(self, checked: bool):
        self.settings["always_on_top"] = checked
        flags = Qt.Window | Qt.FramelessWindowHint
        if checked:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()
        self._manager.save()

    def _quit(self):
        self._save_all()
        self._manager.quit()

    # ── 窗口事件 ──────────────────────────────────────────

    def moveEvent(self, event):
        super().moveEvent(event)
        QTimer.singleShot(300, self._save_geometry)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(300, self._save_geometry)

    def closeEvent(self, event):
        if self._really_closing or self._manager._quitting:
            self._save_all()
            event.accept()
        else:
            self._manager.hide_note(self._note_id)
            event.ignore()

    # ── Windows 原生消息 ──────────────────────────────────

    def nativeEvent(self, eventType, message):
        if eventType != b"windows_generic_MSG":
            return super().nativeEvent(eventType, message)

        class MSG(ctypes.Structure):
            _fields_ = [
                ("hWnd",    ctypes.wintypes.HWND),
                ("message", ctypes.wintypes.UINT),
                ("wParam",  ctypes.wintypes.WPARAM),
                ("lParam",  ctypes.wintypes.LPARAM),
                ("time",    ctypes.wintypes.DWORD),
                ("pt",      ctypes.wintypes.POINT),
            ]

        msg = MSG.from_address(int(message))

        if msg.message == 0x00A5:
            x = ctypes.c_short(msg.lParam & 0xFFFF).value
            y = ctypes.c_short((msg.lParam >> 16) & 0xFFFF).value
            self.show_context_menu(QPoint(x, y))
            return True, 0

        if msg.message == 0x0084:
            if self.settings.get("locked", False):
                ctrl  = ctypes.windll.user32.GetKeyState(0x11) & 0x8000
                shift = ctypes.windll.user32.GetKeyState(0x10) & 0x8000
                if ctrl and shift:
                    return True, 1
                return True, -1

            x = ctypes.c_short(msg.lParam & 0xFFFF).value
            y = ctypes.c_short((msg.lParam >> 16) & 0xFFFF).value
            pos = self.mapFromGlobal(QPoint(x, y))
            px, py = pos.x(), pos.y()
            w, h = self.width(), self.height()
            B = 6

            if py < B and px < B:       return True, 13
            if py < B and px > w - B:   return True, 14
            if py > h - B and px < B:   return True, 16
            if py > h - B and px > w-B: return True, 17
            if py < B:                  return True, 12
            if py > h - B:              return True, 15
            if px < B:                  return True, 10
            if px > w - B:              return True, 11
            return True, 1

        return super().nativeEvent(eventType, message)


# ──────────────────────────────────────────────────────────
# NoteManager
# ──────────────────────────────────────────────────────────

class NoteManager:
    def __init__(self):
        self._data: dict = {}
        self._windows: dict[str, NoteWindow] = {}
        self._quitting = False
        self._load()

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
        for k, v in DEFAULT_SETTINGS.items():
            note.setdefault(k, v)
        note.setdefault("name", "便签")
        note.setdefault("visible", True)

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
        self.save()

    def save(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存失败: {e}")

    def notes(self) -> dict:
        return self._data["notes"]

    def create_note(self) -> str:
        nid = self._new_id()
        existing = {n.get("name", "") for n in self._data["notes"].values()}
        idx = len(self._data["notes"]) + 1
        name = f"便签 {idx}"
        while name in existing:
            idx += 1
            name = f"便签 {idx}"
        offset = len(self._data["notes"]) * 25
        self._data["notes"][nid] = {
            **DEFAULT_SETTINGS,
            "name": name,
            "visible": True,
            "x": DEFAULT_SETTINGS["x"] + offset,
            "y": DEFAULT_SETTINGS["y"] + offset,
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

    def start(self):
        shown = 0
        for nid, note in self._data["notes"].items():
            if note.get("visible", True):
                win = NoteWindow(nid, self)
                self._windows[nid] = win
                win.show()
                shown += 1
        if shown == 0 and self._data["notes"]:
            self.show_note(next(iter(self._data["notes"])))

    def quit(self):
        self._quitting = True
        self.save()
        QApplication.quit()


# ──────────────────────────────────────────────────────────
# 入口
# ──────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("TempNote")
    manager = NoteManager()
    manager.start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
