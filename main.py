import sys
import os
import copy
import cv2
from PIL import Image

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QPushButton,
    QComboBox,
    QPlainTextEdit,
    QTabWidget,
    QMessageBox,
    QCheckBox,
    QLineEdit,
    QFileDialog,
    QSlider,
    QSpinBox,
    QScrollArea,
    QGridLayout,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QFont

from utils.constants import BG_COLORS, CHAR_SETS
from utils.exports import copy_to_clipboard, save_to_file, save_as_html, save_as_image
from core.ascii_engine import AsciiEngine
from core.draw_engine import DrawEngine


# Popular figlet fonts to show in the card gallery
GALLERY_FONTS = [
    "standard",
    "big",
    "banner",
    "block",
    "bubble",
    "chunky",
    "colossal",
    "computer",
    "digital",
    "doh",
    "dotmatrix",
    "epic",
    "gothic",
    "graffiti",
    "isometric1",
    "isometric2",
    "isometric3",
    "lean",
    "mini",
    "mirror",
    "ogre",
    "puffy",
    "roman",
    "rounded",
    "script",
    "shadow",
    "slant",
    "small",
    "speed",
    "starwars",
    "stop",
    "thin",
    "univers",
    "weird",
]


# ─────────────────────────── Font Card Widget ───────────────────────────


class FontCard(QFrame):
    use_clicked = pyqtSignal(str)  # emits ascii text

    def __init__(self, font_name: str, ascii_text: str, parent=None):
        super().__init__(parent)
        self.font_name = font_name
        self.ascii_text = ascii_text
        self._build(font_name, ascii_text)

    def _build(self, font_name, ascii_text):
        self.setStyleSheet("""
            FontCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #16161a, stop:1 #1c1c24);
                border: 1px solid #2a2a35;
                border-radius: 12px;
            }
            FontCard:hover {
                border: 1px solid #06b6d4;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #18182a, stop:1 #1e1e2e);
            }
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        # Header
        header = QHBoxLayout()
        # Font name badge
        name_lbl = QLabel(f"  {font_name}  ")
        name_lbl.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0e3a5c, stop:1 #0c2d4a);
            color: #22d3ee; font-size: 11px; font-weight: bold;
            border-radius: 6px; padding: 3px 8px;
            border: 1px solid #164e63;
        """)
        header.addWidget(name_lbl)
        header.addStretch()

        use_btn = QPushButton("⬆ Use")
        use_btn.setFixedSize(60, 26)
        use_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0284c7, stop:1 #06b6d4);
                border: none; border-radius: 6px;
                font-size: 10px; font-weight: bold; color: white;
                padding: 2px 6px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0369a1, stop:1 #0891b2);
            }
            QPushButton:pressed {
                background: #0e7490;
            }
        """)
        use_btn.clicked.connect(lambda: self.use_clicked.emit(self.ascii_text))
        header.addWidget(use_btn)
        layout.addLayout(header)

        # Preview text
        preview = QPlainTextEdit()
        preview.setReadOnly(True)
        preview.setPlainText(
            ascii_text if ascii_text else f"<font '{font_name}' unavailable>"
        )
        preview.setFont(QFont("Consolas", 6))
        preview.setStyleSheet("""
            QPlainTextEdit {
                background: #0a0a10;
                color: #8892b0;
                border: 1px solid #1e1e2e;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        preview.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        # Fix height based on lines
        line_count = min(ascii_text.count("\n") + 1, 12) if ascii_text else 3
        preview.setFixedHeight(max(66, line_count * 9 + 22))
        layout.addWidget(preview)


# ─────────────────────────── Font Gallery Worker ───────────────────────────


class FontRenderWorker(QObject):
    finished = pyqtSignal(list)  # list of (font_name, ascii_text)
    progress = pyqtSignal(str, str)  # incremental: font_name, ascii_text

    def __init__(self, text: str, fonts: list):
        super().__init__()
        self.text = text
        self.fonts = fonts
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        results = []
        for font in self.fonts:
            if self._cancelled:
                break
            result = AsciiEngine.text_to_ascii(self.text, font) or ""
            results.append((font, result))
            self.progress.emit(font, result)
        self.finished.emit(results)


# ─────────────────────────── Main Window ───────────────────────────


class ASCIIArtGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASCII Art Studio")
        self.resize(1440, 900)
        self.setMinimumSize(1100, 700)

        # State
        self.current_image = None
        self.current_ascii = ""
        self.gif_frames = []
        self.gif_frame_index = 0
        self.is_animating = False
        self.webcam_active = False
        self.cap = None
        self.bg_color_name = "Pitch Black"
        self.art_width = 120
        self.contrast = 1.0
        self.brightness = 1.0
        self.zoom_level = 11

        # Draw state
        self.active_tool = "Pencil"
        self.draw_brush_char = "@"
        self.draw_engine = DrawEngine(80, 30)
        self._draw_history = []

        # Timers
        self.webcam_timer = QTimer(self)
        self.webcam_timer.timeout.connect(self.update_webcam)
        self.gif_timer = QTimer(self)
        self.gif_timer.timeout.connect(self._advance_gif_frame)

        # Text gallery debounce
        self._text_debounce = QTimer(self)
        self._text_debounce.setSingleShot(True)
        self._text_debounce.timeout.connect(self._rebuild_font_gallery)
        self._render_worker = None
        self._render_thread = None

        self._apply_stylesheet()
        self.setup_ui()

    # ─── Stylesheet ───

    def _apply_stylesheet(self):
        self.setStyleSheet("""
            /* ─── Base ─── */
            QMainWindow {
                background-color: #07070a;
            }
            QWidget {
                color: #e2e8f0;
                font-family: 'Segoe UI', Inter, Arial, sans-serif;
            }

            /* ─── Tab Bar ─── */
            QTabWidget::pane {
                border: none;
                background: #07070a;
            }
            QTabBar {
                background: #08080d;
                padding: 0 12px;
            }
            QTabBar::tab {
                background: #111118;
                color: #52525b;
                padding: 12px 32px;
                border: 1px solid #1a1a25;
                border-bottom: none;
                font-size: 13px;
                font-weight: 700;
                margin-right: 4px;
                margin-top: 4px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                letter-spacing: 0.5px;
            }
            QTabBar::tab:selected {
                color: #22d3ee;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #141422, stop:1 #07070a);
                border: 1px solid #06b6d4;
                border-bottom: none;
                margin-top: 0px;
                padding-top: 14px;
            }
            QTabBar::tab:hover:!selected {
                color: #a1a1aa;
                background: #16161e;
                border-color: #2a2a38;
            }

            /* ─── Sidebar ─── */
            QFrame#Sidebar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #111116, stop:1 #0d0d12);
                border-right: 1px solid #1e1e28;
            }

            /* ─── Text Editors ─── */
            QPlainTextEdit, QTextEdit {
                background: #0a0a0f;
                color: #06b6d4;
                border: 1px solid #1a1a25;
                border-radius: 10px;
                padding: 16px;
                font-family: 'Cascadia Code', Consolas, monospace;
                selection-background-color: #164e63;
            }

            /* ─── Buttons ─── */
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a32, stop:1 #222228);
                padding: 8px 16px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 12px;
                border: 1px solid #3a3a45;
                color: #e2e8f0;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #38384a, stop:1 #2e2e3a);
                border: 1px solid #52527a;
            }
            QPushButton:pressed {
                background: #1e1e2a;
            }
            QPushButton#Primary {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0284c7, stop:1 #06b6d4);
                border: none; color: white;
                border-radius: 8px;
            }
            QPushButton#Primary:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0369a1, stop:1 #0891b2);
            }
            QPushButton#Danger {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #dc2626, stop:1 #ef4444);
                border: none; color: white;
                border-radius: 8px;
            }
            QPushButton#Danger:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #b91c1c, stop:1 #dc2626);
            }

            /* ─── ComboBox ─── */
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a32, stop:1 #202028);
                padding: 7px 12px;
                border-radius: 8px;
                border: 1px solid #3a3a45;
                font-size: 12px;
                min-height: 18px;
            }
            QComboBox:hover {
                border: 1px solid #06b6d4;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
            QComboBox QAbstractItemView {
                background: #1a1a22;
                border: 1px solid #2a2a35;
                border-radius: 8px;
                padding: 4px;
                selection-background-color: #164e63;
            }

            /* ─── Sliders ─── */
            QSlider::groove:horizontal {
                background: #1e1e28;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    fx:0.5, fy:0.3, stop:0 #22d3ee, stop:1 #0284c7);
                width: 16px; height: 16px;
                margin: -5px 0;
                border-radius: 8px;
                border: 2px solid #0e7490;
            }
            QSlider::handle:horizontal:hover {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    fx:0.5, fy:0.3, stop:0 #67e8f9, stop:1 #06b6d4);
                border: 2px solid #22d3ee;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0284c7, stop:1 #06b6d4);
                border-radius: 3px;
            }

            /* ─── LineEdit ─── */
            QLineEdit {
                background: #16161e;
                border: 1px solid #2a2a35;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e2e8f0;
                font-size: 13px;
                selection-background-color: #164e63;
            }
            QLineEdit:focus {
                border: 1px solid #06b6d4;
                background: #1a1a24;
            }

            /* ─── Checkbox ─── */
            QCheckBox {
                spacing: 8px;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 18px; height: 18px;
                border-radius: 5px;
                border: 2px solid #3a3a45;
                background: #1a1a22;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #06b6d4;
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0284c7, stop:1 #06b6d4);
                border-color: #0891b2;
            }

            /* ─── ScrollBars ─── */
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                border-radius: 4px;
                margin: 4px 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(100,100,130,80);
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(6,182,212,120);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            QScrollBar:horizontal {
                background: transparent;
                height: 8px;
                border-radius: 4px;
                margin: 0 4px;
            }
            QScrollBar::handle:horizontal {
                background: rgba(100,100,130,80);
                border-radius: 4px;
                min-width: 30px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgba(6,182,212,120);
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0;
            }

            /* ─── SpinBox ─── */
            QSpinBox {
                background: #1a1a22;
                border: 1px solid #2a2a35;
                border-radius: 6px;
                padding: 4px 8px;
                color: #e2e8f0;
                font-size: 12px;
            }
            QSpinBox:focus {
                border: 1px solid #06b6d4;
            }

            /* ─── Tooltips ─── */
            QToolTip {
                background: #1a1a24;
                color: #e2e8f0;
                border: 1px solid #2a2a35;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 11px;
            }

            QLabel#Hint { color: #3f3f50; font-size: 11px; }
        """)

    # ─── UI Setup ───

    def setup_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        vbox = QVBoxLayout(root)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        # Top bar
        vbox.addWidget(self._build_topbar())

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        vbox.addWidget(self.tabs, 1)

        self._build_image_tab()
        self._build_text_tab()
        self._build_draw_tab()

        # Status bar
        vbox.addWidget(self._build_statusbar())

    # ─── Top Bar ───

    def _build_topbar(self):
        bar = QWidget()
        bar.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0d0d14, stop:0.5 #111118, stop:1 #0d0d14);
            border-bottom: 1px solid #1a1a28;
        """)
        bar.setFixedHeight(52)
        row = QHBoxLayout(bar)
        row.setContentsMargins(24, 0, 24, 0)
        row.setSpacing(8)

        # App icon / title
        title = QLabel("🎨 ASCII Art Studio")
        title.setStyleSheet("""
            font-size: 18px; font-weight: 800; color: #f1f5f9;
            letter-spacing: 0.5px;
        """)
        row.addWidget(title)

        # Subtle version badge
        ver = QLabel("v2.0")
        ver.setStyleSheet("""
            background: rgba(6,182,212,30); color: #22d3ee;
            font-size: 9px; font-weight: bold;
            border-radius: 4px; padding: 2px 6px;
            border: 1px solid rgba(6,182,212,40);
        """)
        row.addWidget(ver)
        row.addStretch()

        # Zoom controls with pill container
        zoom_container = QWidget()
        zoom_container.setStyleSheet("""
            background: rgba(255,255,255,5);
            border-radius: 8px;
            border: 1px solid #1e1e2e;
        """)
        zoom_row = QHBoxLayout(zoom_container)
        zoom_row.setContentsMargins(8, 4, 8, 4)
        zoom_row.setSpacing(4)
        zoom_icon = QLabel("🔍")
        zoom_icon.setStyleSheet("font-size: 12px; border:none; background:transparent;")
        zoom_row.addWidget(zoom_icon)

        zm = QLabel("−")
        zm.setFixedSize(28, 28)
        zm.setAlignment(Qt.AlignmentFlag.AlignCenter)
        zm.setStyleSheet("""
            QLabel { color:#94a3b8; font-size:18px; font-weight:bold;
                    border:none; background:transparent; border-radius:6px; }
            QLabel:hover { background:rgba(255,255,255,15); color:#e2e8f0; }
        """)
        zm.setToolTip("Zoom out")
        zm.setCursor(Qt.CursorShape.PointingHandCursor)
        zm.mousePressEvent = lambda e: self.zoom_out()

        self.zoom_lbl = QLabel(str(self.zoom_level))
        self.zoom_lbl.setFixedWidth(28)
        self.zoom_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_lbl.setStyleSheet(
            "color:#67e8f9; font-size:13px; font-weight:bold; background:transparent; border:none;"
        )

        zp = QLabel("+")
        zp.setFixedSize(28, 28)
        zp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        zp.setStyleSheet("""
            QLabel { color:#94a3b8; font-size:18px; font-weight:bold;
                    border:none; background:transparent; border-radius:6px; }
            QLabel:hover { background:rgba(255,255,255,15); color:#e2e8f0; }
        """)
        zp.setToolTip("Zoom in")
        zp.setCursor(Qt.CursorShape.PointingHandCursor)
        zp.mousePressEvent = lambda e: self.zoom_in()

        zoom_row.addWidget(zm)
        zoom_row.addWidget(self.zoom_lbl)
        zoom_row.addWidget(zp)
        row.addWidget(zoom_container)

        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setStyleSheet("color: #1e1e2e; max-height: 24px;")
        row.addWidget(sep1)

        # BG color
        bg_lbl = QLabel("🖥️")
        bg_lbl.setToolTip("Background color")
        bg_lbl.setStyleSheet("font-size:14px;")
        row.addWidget(bg_lbl)
        self.bg_combo = QComboBox()
        self.bg_combo.addItems(list(BG_COLORS.keys()))
        self.bg_combo.setFixedWidth(130)
        self.bg_combo.setToolTip("Canvas background color")
        self.bg_combo.currentTextChanged.connect(self.on_bg_change)
        row.addWidget(self.bg_combo)

        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.VLine)
        sep2.setStyleSheet("color: #1e1e2e; max-height: 24px;")
        row.addWidget(sep2)

        # Export buttons with pill styling
        for label, slot, tip in [
            ("📋 Copy", self.copy_to_clipboard, "Copy ASCII to clipboard"),
            ("🌐 HTML", self.save_as_html, "Export as HTML file"),
            ("💾 TXT", self.save_to_file, "Save as text file"),
            ("🖼️ PNG", self.save_as_image, "Export as PNG image"),
        ]:
            btn = QPushButton(label)
            btn.setFixedHeight(32)
            btn.setToolTip(tip)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,5);
                    border: 1px solid #1e1e2e;
                    border-radius: 8px;
                    padding: 4px 14px;
                    font-size: 11px;
                    font-weight: 600;
                    color: #94a3b8;
                }
                QPushButton:hover {
                    background: rgba(6,182,212,20);
                    border: 1px solid #164e63;
                    color: #e2e8f0;
                }
                QPushButton:pressed {
                    background: rgba(6,182,212,35);
                }
            """)
            btn.clicked.connect(slot)
            row.addWidget(btn)

        return bar

    def _build_statusbar(self):
        bar = QWidget()
        bar.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0d0d14, stop:0.5 #111118, stop:1 #0d0d14);
            border-top: 1px solid #1a1a28;
        """)
        bar.setFixedHeight(30)
        row = QHBoxLayout(bar)
        row.setContentsMargins(20, 0, 20, 0)

        # Status indicator dot
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #22c55e; font-size: 8px;")
        row.addWidget(self.status_dot)

        self.status_lbl = QLabel("Ready")
        self.status_lbl.setStyleSheet("color:#64748b; font-size:11px; font-weight:500;")
        row.addWidget(self.status_lbl)
        row.addStretch()

        hint = QLabel('⌨ Ctrl+Scroll to zoom  ·  Click "Use" to apply font')
        hint.setStyleSheet("color:#2e2e3e; font-size:10px; letter-spacing:0.3px;")
        row.addWidget(hint)
        return bar

    # ─── IMAGE TAB ───

    def _build_image_tab(self):
        page = QWidget()
        row = QHBoxLayout(page)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        # Sidebar
        sidebar = self._make_sidebar()
        slayout = sidebar.layout()

        self._section(slayout, "LOAD")
        btn_row = QHBoxLayout()
        load_btn = QPushButton("📁 Load Image")
        load_btn.setObjectName("Primary")
        load_btn.clicked.connect(self.load_image)
        btn_row.addWidget(load_btn)
        self.webcam_btn = QPushButton("📷 Webcam")
        self.webcam_btn.clicked.connect(self.toggle_webcam)
        btn_row.addWidget(self.webcam_btn)
        slayout.addLayout(btn_row)

        self.gif_btn = QPushButton("🎞️ GIF / Animate")
        self.gif_btn.clicked.connect(self.load_gif)
        slayout.addWidget(self.gif_btn)
        self.gif_stop_btn = QPushButton("⏹️ Stop Animation")
        self.gif_stop_btn.setObjectName("Danger")
        self.gif_stop_btn.clicked.connect(self.stop_gif)
        self.gif_stop_btn.setVisible(False)
        slayout.addWidget(self.gif_stop_btn)

        self._section(slayout, "CHARACTER SET")
        self.charset_combo = QComboBox()
        self.charset_combo.addItems(list(CHAR_SETS.keys()))
        self.charset_combo.currentTextChanged.connect(self.update_preview)
        slayout.addWidget(self.charset_combo)

        # Custom character set input
        self._section(slayout, "CUSTOM CHARSET")
        self.custom_charset_input = QLineEdit()
        self.custom_charset_input.setPlaceholderText("e.g.  .:-=+*#%@")
        self.custom_charset_input.setToolTip(
            "Enter your own characters from darkest to brightest.\n"
            "First char = darkest (space), last = brightest."
        )
        self.custom_charset_input.textChanged.connect(self._on_custom_charset)
        slayout.addWidget(self.custom_charset_input)
        custom_hint = QLabel("Type chars dark→bright, then select 'Custom' above")
        custom_hint.setObjectName("Hint")
        custom_hint.setWordWrap(True)
        slayout.addWidget(custom_hint)

        self._section(slayout, "WIDTH")
        self.width_slider, self.width_lbl = self._slider(40, 240, self.art_width)
        self.width_slider.valueChanged.connect(self._on_width)
        slayout.addWidget(self._slider_widget(self.width_slider, self.width_lbl))

        self._section(slayout, "CONTRAST")
        self.contrast_slider, self.contrast_lbl = self._slider(50, 300, 100)
        self.contrast_slider.valueChanged.connect(self._on_contrast)
        slayout.addWidget(self._slider_widget(self.contrast_slider, self.contrast_lbl))

        self._section(slayout, "BRIGHTNESS")
        self.brightness_slider, self.brightness_lbl = self._slider(50, 300, 100)
        self.brightness_slider.valueChanged.connect(self._on_brightness)
        slayout.addWidget(
            self._slider_widget(self.brightness_slider, self.brightness_lbl)
        )

        self.invert_check = QCheckBox("Invert Colors")
        self.invert_check.stateChanged.connect(self.update_preview)
        slayout.addWidget(self.invert_check)
        slayout.addStretch()

        row.addWidget(sidebar)
        row.addWidget(self._make_canvas_panel(), 1)
        self.tabs.addTab(page, "🖼️  Image")

    # ─── TEXT TAB ───

    def _build_text_tab(self):
        page = QWidget()
        page.setStyleSheet("background:#09090b;")
        vbox = QVBoxLayout(page)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        # Input bar at top
        input_bar = QWidget()
        input_bar.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0f0f16, stop:0.5 #131320, stop:1 #0f0f16);
            border-bottom: 1px solid #1a1a28;
        """)
        input_bar.setFixedHeight(60)
        irow = QHBoxLayout(input_bar)
        irow.setContentsMargins(24, 0, 24, 0)
        irow.setSpacing(12)

        lbl = QLabel("✏️  Text:")
        lbl.setStyleSheet("font-weight:bold; color:#67e8f9; font-size:13px;")
        irow.addWidget(lbl)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type something to see it in all fonts…")
        self.text_input.setFixedHeight(38)
        self.text_input.setStyleSheet("""
            QLineEdit {
                background: #0e0e16;
                border: 1px solid #1e1e2e;
                border-radius: 10px;
                padding: 8px 16px;
                color: #e2e8f0;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #06b6d4;
                background: #111120;
            }
        """)
        self.text_input.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.text_input.textChanged.connect(self._on_text_changed)
        irow.addWidget(self.text_input, 1)

        self.text_status_lbl = QLabel("Start typing to generate font previews")
        self.text_status_lbl.setStyleSheet(
            "color:#475569; font-size:11px; min-width:200px; font-weight:500;"
        )
        irow.addWidget(self.text_status_lbl)

        vbox.addWidget(input_bar)

        # Scrollable card gallery
        self.gallery_scroll = QScrollArea()
        self.gallery_scroll.setWidgetResizable(True)
        self.gallery_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.gallery_scroll.setStyleSheet("background:#07070a;")

        self.gallery_widget = QWidget()
        self.gallery_widget.setStyleSheet("background:#07070a;")
        self.gallery_layout = QGridLayout(self.gallery_widget)
        self.gallery_layout.setContentsMargins(24, 24, 24, 24)
        self.gallery_layout.setSpacing(16)
        self.gallery_layout.setColumnStretch(0, 1)
        self.gallery_layout.setColumnStretch(1, 1)

        self._show_gallery_placeholder()

        self.gallery_scroll.setWidget(self.gallery_widget)
        vbox.addWidget(self.gallery_scroll, 1)

        self.tabs.addTab(page, "✏️  Text")

    def _show_gallery_placeholder(self):
        self._clear_gallery()
        placeholder_container = QWidget()
        placeholder_layout = QVBoxLayout(placeholder_container)
        placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_lbl = QLabel("⌨️")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 36px; padding: 10px;")
        placeholder_layout.addWidget(icon_lbl)

        text_lbl = QLabel(
            "Type text above to see ASCII art\npreviews in dozens of fonts"
        )
        text_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_lbl.setStyleSheet(
            "color:#3a3a4a; font-size:15px; line-height:1.6; padding:10px;"
        )
        placeholder_layout.addWidget(text_lbl)

        self.gallery_layout.addWidget(placeholder_container, 0, 0, 1, 2)

    def _clear_gallery(self):
        while self.gallery_layout.count():
            item = self.gallery_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _on_text_changed(self, text):
        if not text.strip():
            self._show_gallery_placeholder()
            self.text_status_lbl.setText("Start typing to generate font previews")
            return
        # Cancel any ongoing render
        if self._render_worker:
            self._render_worker.cancel()
        self.text_status_lbl.setText("Generating…")
        self._text_debounce.start(300)  # 300ms debounce

    def _rebuild_font_gallery(self):
        text = self.text_input.text().strip()
        if not text:
            return

        self._clear_gallery()

        # Loading indicator
        loading = QLabel("✨ Rendering fonts…")
        loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading.setStyleSheet(
            "color:#06b6d4; font-size:14px; padding:40px; font-weight:500;"
        )
        self.gallery_layout.addWidget(loading, 0, 0, 1, 2)

        # Build in background thread
        if self._render_thread and self._render_thread.isRunning():
            self._render_worker.cancel()
            self._render_thread.quit()
            self._render_thread.wait(500)

        self._render_worker = FontRenderWorker(text, GALLERY_FONTS)
        self._render_thread = QThread()
        self._render_worker.moveToThread(self._render_thread)
        self._render_thread.started.connect(self._render_worker.run)
        self._render_worker.finished.connect(self._on_gallery_finished)
        self._render_worker.finished.connect(self._render_thread.quit)
        self._render_thread.start()

    def _on_gallery_finished(self, results):
        self._clear_gallery()
        row = 0
        col = 0
        count = 0
        for font_name, ascii_text in results:
            if not ascii_text or not ascii_text.strip():
                continue
            card = FontCard(font_name, ascii_text)
            card.use_clicked.connect(self._use_font_art)
            self.gallery_layout.addWidget(card, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1
            count += 1

        self.text_status_lbl.setText(f"{count} fonts rendered")
        self.status_lbl.setText(f"Text gallery: {count} fonts")

    def _use_font_art(self, ascii_text: str):
        self.current_ascii = ascii_text
        # Switch to Image tab canvas to display
        self._image_canvas.setPlainText(ascii_text)
        self.status_lbl.setText(
            "Font applied to canvas — switch to Image tab to export"
        )
        QMessageBox.information(
            self,
            "Applied",
            "Font art applied! Switch to the 🖼️ Image tab to see it on the canvas and export.",
        )

    # ─── DRAW TAB ───

    def _build_draw_tab(self):
        page = QWidget()
        row = QHBoxLayout(page)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        sidebar = self._make_sidebar()
        sl = sidebar.layout()

        self._section(sl, "TOOL")
        self.tool_combo = QComboBox()
        self.tool_combo.addItems(["Pencil", "Eraser", "Bucket", "Line", "Rect"])
        self.tool_combo.currentTextChanged.connect(self.on_tool_change)
        sl.addWidget(self.tool_combo)

        self._section(sl, "BRUSH CHARACTER")
        self.brush_combo = QComboBox()
        self.brush_combo.addItems(
            [
                "@",
                "#",
                "8",
                "&",
                "%",
                "O",
                "X",
                "+",
                ":",
                ".",
                "█",
                "▓",
                "▒",
                "░",
                "*",
                "=",
                "-",
                "|",
                "/",
                "\\",
                "~",
                "^",
                "!",
                "?",
                "$",
            ]
        )
        self.brush_combo.setEditable(True)
        self.brush_combo.currentTextChanged.connect(self.on_brush_change)
        sl.addWidget(self.brush_combo)

        self._section(sl, "CANVAS SIZE")
        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("W:"))
        self.canvas_w_spin = QSpinBox()
        self.canvas_w_spin.setRange(20, 200)
        self.canvas_w_spin.setValue(80)
        self.canvas_w_spin.setStyleSheet(
            "background:#27272a; border:1px solid #3f3f46; border-radius:4px; padding:3px;"
        )
        size_row.addWidget(self.canvas_w_spin)
        size_row.addWidget(QLabel("H:"))
        self.canvas_h_spin = QSpinBox()
        self.canvas_h_spin.setRange(10, 100)
        self.canvas_h_spin.setValue(30)
        self.canvas_h_spin.setStyleSheet(
            "background:#27272a; border:1px solid #3f3f46; border-radius:4px; padding:3px;"
        )
        size_row.addWidget(self.canvas_h_spin)
        sl.addLayout(size_row)

        resize_btn = QPushButton("↔ Apply Size")
        resize_btn.clicked.connect(self.resize_draw_canvas)
        sl.addWidget(resize_btn)

        clear_btn = QPushButton("🗑️ Clear Canvas")
        clear_btn.setObjectName("Danger")
        clear_btn.clicked.connect(self.init_draw_canvas)
        sl.addWidget(clear_btn)

        tool_row = QHBoxLayout()
        undo_btn = QPushButton("↩ Undo")
        undo_btn.clicked.connect(self.undo_draw)
        tool_row.addWidget(undo_btn)
        fill_btn = QPushButton("▪ Fill All")
        fill_btn.clicked.connect(self.fill_all_draw)
        tool_row.addWidget(fill_btn)
        sl.addLayout(tool_row)

        sl.addStretch()
        row.addWidget(sidebar)

        # Draw canvas
        self._draw_canvas_panel = self._make_canvas_panel(for_draw=True)
        row.addWidget(self._draw_canvas_panel, 1)

        self.tabs.addTab(page, "🎨  Draw")
        self.tabs.currentChanged.connect(self._on_tab_changed)

    # ─── Canvas Panel ───

    def _make_canvas_panel(self, for_draw=False):
        wrapper = QFrame()
        wrapper.setStyleSheet("background:#07070a;")
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(20, 20, 20, 20)

        canvas = QPlainTextEdit()
        canvas.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        canvas.setReadOnly(True)
        canvas.setPlainText("\n\n\n\n          Load an image to get started")
        canvas.setFont(QFont("Cascadia Code", self.zoom_level))
        canvas.setStyleSheet("""
            QPlainTextEdit {
                background: #0a0a10;
                color: #06b6d4;
                border: 2px solid #2a2a3a;
                border-radius: 12px;
                padding: 20px;
                font-family: 'Cascadia Code', Consolas, monospace;
                selection-background-color: #164e63;
            }
        """)

        if for_draw:
            self._draw_canvas = canvas
            canvas.setPlainText("")
            canvas.installEventFilter(self)
            canvas.viewport().installEventFilter(self)
        else:
            self._image_canvas = canvas

        layout.addWidget(canvas)
        return wrapper

    # ─── Helpers ───

    def _make_sidebar(self):
        frame = QFrame()
        frame.setObjectName("Sidebar")
        frame.setFixedWidth(270)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 20, 18, 18)
        layout.setSpacing(10)
        return frame

    def _section(self, layout, text):
        # Section header with accent bar
        container = QWidget()
        container.setStyleSheet("""
            border-left: 3px solid #0891b2;
            padding-left: 8px;
            margin-top: 4px;
        """)
        clayout = QHBoxLayout(container)
        clayout.setContentsMargins(8, 2, 0, 2)
        lbl = QLabel(text)
        lbl.setStyleSheet("""
            color: #475569;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.5px;
            background: transparent;
            border: none;
        """)
        clayout.addWidget(lbl)
        layout.addWidget(container)

    def _slider(self, mn, mx, val):
        s = QSlider(Qt.Orientation.Horizontal)
        s.setMinimum(mn)
        s.setMaximum(mx)
        s.setValue(val)
        lbl = QLabel(str(val))
        lbl.setFixedWidth(36)
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return s, lbl

    def _slider_widget(self, slider, label):
        w = QWidget()
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(slider)
        row.addWidget(label)
        return w

    # ─── Slider callbacks ───

    def _on_width(self, v):
        self.art_width = v
        self.width_lbl.setText(str(v))
        self.update_preview()

    def _on_contrast(self, v):
        self.contrast = v / 100.0
        self.contrast_lbl.setText(f"{self.contrast:.1f}x")
        self.update_preview()

    def _on_brightness(self, v):
        self.brightness = v / 100.0
        self.brightness_lbl.setText(f"{self.brightness:.1f}x")
        self.update_preview()

    def _on_custom_charset(self, text):
        """When user types in the custom charset field, update CHAR_SETS and auto-select."""
        if text and len(text) >= 2:
            CHAR_SETS["Custom"] = text
            # Add 'Custom' to combo if not present
            idx = self.charset_combo.findText("Custom")
            if idx == -1:
                self.charset_combo.addItem("Custom")
                idx = self.charset_combo.findText("Custom")
            self.charset_combo.setCurrentIndex(idx)
            self.update_preview()

    # ─── Zoom ───

    def zoom_in(self):
        if self.zoom_level < 28:
            self.zoom_level += 1
            self._apply_zoom()

    def zoom_out(self):
        if self.zoom_level > 4:
            self.zoom_level -= 1
            self._apply_zoom()

    def _apply_zoom(self):
        self.zoom_lbl.setText(str(self.zoom_level))
        f = QFont("Cascadia Code", self.zoom_level)
        self._image_canvas.setFont(f)
        self._draw_canvas.setFont(f)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.zoom_in() if event.angleDelta().y() > 0 else self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    # ─── BG color ───

    def on_bg_change(self, name):
        self.bg_color_name = name
        hex_c = BG_COLORS.get(name, "#09090b")
        css = f"""
            QPlainTextEdit {{
                background: {hex_c};
                color: #06b6d4;
                border: 2px solid #2a2a3a;
                border-radius: 12px;
                padding: 20px;
                font-family: 'Cascadia Code', Consolas, monospace;
                selection-background-color: #164e63;
            }}
        """
        self._image_canvas.setStyleSheet(css)
        self._draw_canvas.setStyleSheet(css)

    # ─── Tab change ───

    def _on_tab_changed(self, idx):
        if self.tabs.tabText(idx).strip().startswith("🎨"):  # Draw tab
            self._update_cursor_for_tool(self.active_tool)
            if not self.draw_engine.render_to_string().strip():
                self.init_draw_canvas()
        else:
            if hasattr(self, "_draw_canvas"):
                self._draw_canvas.viewport().setCursor(Qt.CursorShape.ArrowCursor)

    # ─── Display / status ───

    def display_ascii(self, text):
        self.current_ascii = text
        self._image_canvas.setPlainText(text)

    def _status(self, text):
        self.status_lbl.setText(text)

    # ─── Canvas Reset ───

    def _reset_canvas_state(self):
        """Clear all previous input state so sources don't overlap."""
        # Stop GIF animation
        self.gif_timer.stop()
        self.is_animating = False
        self.gif_frames = []
        self.gif_frame_index = 0
        self.gif_stop_btn.setVisible(False)

        # Stop webcam
        if self.webcam_active:
            self.webcam_active = False
            self.webcam_btn.setText("📷 Webcam")
            if self.cap:
                self.cap.release()
                self.cap = None
            self.webcam_timer.stop()

        # Clear canvas content
        self.current_image = None
        self.current_ascii = ""
        self._image_canvas.setPlainText("")

    # ─── Image Mode ───

    def load_image(self):
        fp, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif *.xpm)"
        )
        if fp:
            try:
                self._reset_canvas_state()
                img = Image.open(fp)
                self.current_image = img.convert("RGB")
                self.update_preview()
                self._status(f"Loaded: {os.path.basename(fp)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image: {e}")

    def update_preview(self):
        if self.current_image:
            txt = AsciiEngine.image_to_ascii(
                self.current_image,
                self.charset_combo.currentText(),
                self.art_width,
                self.contrast,
                self.brightness,
                self.invert_check.isChecked(),
            )
            self.display_ascii(txt)
            self._status(
                f"Width: {self.art_width}px | Contrast: {self.contrast:.1f}x | Brightness: {self.brightness:.1f}x"
            )

    # ─── GIF ───

    def load_gif(self):
        fp, _ = QFileDialog.getOpenFileName(
            self, "Open GIF", "", "GIF (*.gif);;All Images (*.*)"
        )
        if not fp:
            return
        self._reset_canvas_state()
        try:
            gif = Image.open(fp)
            self.gif_frames = []
            cs = self.charset_combo.currentText()
            invert = self.invert_check.isChecked()
            try:
                while True:
                    f = gif.copy().convert("RGB")
                    self.gif_frames.append(
                        AsciiEngine.image_to_ascii(
                            f,
                            cs,
                            self.art_width,
                            self.contrast,
                            self.brightness,
                            invert,
                        )
                    )
                    gif.seek(gif.tell() + 1)
            except EOFError:
                pass
            if self.gif_frames:
                self.gif_frame_index = 0
                self.is_animating = True
                self.gif_stop_btn.setVisible(True)
                self.gif_timer.start(max(50, gif.info.get("duration", 100)))
                self._status(f"Animating: {len(self.gif_frames)} frames")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load GIF: {e}")

    def _advance_gif_frame(self):
        if self.gif_frames:
            self.display_ascii(self.gif_frames[self.gif_frame_index])
            self.gif_frame_index = (self.gif_frame_index + 1) % len(self.gif_frames)

    def stop_gif(self):
        self.is_animating = False
        self.gif_timer.stop()
        self.gif_stop_btn.setVisible(False)
        self._status("Animation stopped")

    # ─── Tool / Brush ───

    def on_tool_change(self, tool):
        self.active_tool = tool
        self._update_cursor_for_tool(tool)
        self._status(f"Tool: {tool}")

    def on_brush_change(self, char):
        if char:
            self.draw_brush_char = char[0]

    def _update_cursor_for_tool(self, tool):
        cursors = {
            "Pencil": Qt.CursorShape.CrossCursor,
            "Eraser": Qt.CursorShape.PointingHandCursor,
            "Bucket": Qt.CursorShape.UpArrowCursor,
            "Line": Qt.CursorShape.CrossCursor,
            "Rect": Qt.CursorShape.CrossCursor,
        }
        if hasattr(self, "_draw_canvas"):
            self._draw_canvas.viewport().setCursor(
                cursors.get(tool, Qt.CursorShape.ArrowCursor)
            )

    # ─── Draw Canvas ───

    def init_draw_canvas(self):
        w = self.canvas_w_spin.value() if hasattr(self, "canvas_w_spin") else 80
        h = self.canvas_h_spin.value() if hasattr(self, "canvas_h_spin") else 30
        self.draw_engine = DrawEngine(w, h)
        self._draw_history = []
        self._render_draw()
        self._status("Canvas cleared")

    def resize_draw_canvas(self):
        self.init_draw_canvas()

    def _render_draw(self):
        raw = self.draw_engine.render_to_string()
        w = self.draw_engine.width
        # Wrap with box-drawing frame
        top = "┌" + "─" * w + "┐"
        bot = "└" + "─" * w + "┘"
        lines = raw.split("\n")
        framed = [top] + ["│" + ln.ljust(w) + "│" for ln in lines] + [bot]
        txt = "\n".join(framed)
        self.current_ascii = raw  # keep raw for export
        self._draw_canvas.setPlainText(txt)

    def undo_draw(self):
        if self._draw_history:
            self.draw_engine.matrix = self._draw_history.pop()
            self._render_draw()
            self._status("Undo")

    def fill_all_draw(self):
        self._save_draw_history()
        for r in range(self.draw_engine.height):
            for c in range(self.draw_engine.width):
                self.draw_engine.matrix[r][c] = self.draw_brush_char
        self._render_draw()

    def _save_draw_history(self):
        if len(self._draw_history) > 50:
            self._draw_history.pop(0)
        self._draw_history.append(copy.deepcopy(self.draw_engine.matrix))

    # ─── Draw Event Filter ───

    def eventFilter(self, source, event):
        draw_canvas = getattr(self, "_draw_canvas", None)
        if draw_canvas and (source == draw_canvas or source == draw_canvas.viewport()):
            t = event.type()
            if t == event.Type.MouseButtonPress:
                self._handle_paint(
                    event, is_preview=(self.active_tool in ["Line", "Rect"])
                )
                return True
            elif t == event.Type.MouseMove:
                if event.buttons() & Qt.MouseButton.LeftButton:
                    self._handle_paint(
                        event, is_preview=(self.active_tool in ["Line", "Rect"])
                    )
                    return True
            elif t == event.Type.MouseButtonRelease:
                if self.active_tool in ["Line", "Rect"]:
                    self._handle_paint(event, is_preview=False)
                self._is_drawing = False
                return True
        return super().eventFilter(source, event)

    def _handle_paint(self, event, is_preview):
        cursor = self._draw_canvas.cursorForPosition(event.pos())
        # Offset by -1 to account for the box-drawing frame
        r = cursor.blockNumber() - 1
        c = cursor.positionInBlock() - 1
        tool = self.active_tool
        char = self.draw_brush_char if tool != "Eraser" else " "

        if tool in ["Pencil", "Eraser"]:
            if not getattr(self, "_is_drawing", False):
                self._is_drawing = True
                self._save_draw_history()
            self.draw_engine.paint(r, c, char)
            self._render_draw()
        elif tool == "Bucket" and not is_preview:
            self._save_draw_history()
            self.draw_engine.flood_fill(r, c, char)
            self._render_draw()
        elif tool in ["Line", "Rect"]:
            if self.draw_engine.shape_start_pos is None:
                self.draw_engine.begin_shape(r, c)
                self._save_draw_history()
            if tool == "Line":
                self.draw_engine.preview_line(r, c, char)
            else:
                self.draw_engine.preview_rect(r, c, char)
            self._render_draw()
            if not is_preview:
                self.draw_engine.end_shape()

    # ─── Exports ───

    def copy_to_clipboard(self):
        copy_to_clipboard(self, self.current_ascii)

    def save_to_file(self):
        save_to_file(self, self.current_ascii)

    def save_as_html(self):
        save_as_html(self, self.current_ascii, self.bg_color_name)

    def save_as_image(self):
        save_as_image(self, self.current_ascii, self.bg_color_name)

    # ─── Webcam ───

    def toggle_webcam(self):
        if not self.webcam_active:
            self._reset_canvas_state()
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                QMessageBox.critical(self, "Error", "Webcam not found.")
                return
            self.webcam_active = True
            self.webcam_btn.setText("🛑 Stop")
            self.webcam_timer.start(50)
            self._status("Webcam live")
        else:
            self.webcam_active = False
            self.webcam_btn.setText("📷 Webcam")
            if self.cap:
                self.cap.release()
                self.cap = None
            self.webcam_timer.stop()
            self._status("Webcam stopped")

    def update_webcam(self):
        if self.webcam_active and self.cap:
            ret, frame = self.cap.read()
            if ret:
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                txt = AsciiEngine.image_to_ascii(
                    img,
                    self.charset_combo.currentText(),
                    self.art_width,
                    self.contrast,
                    self.brightness,
                    self.invert_check.isChecked(),
                )
                self.display_ascii(txt)

    def closeEvent(self, event):
        if self._render_worker:
            self._render_worker.cancel()
        if self._render_thread and self._render_thread.isRunning():
            self._render_thread.quit()
            self._render_thread.wait(200)
        if self.webcam_active and self.cap:
            self.cap.release()
        self.gif_timer.stop()
        self.webcam_timer.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ASCIIArtGenerator()
    window.show()
    sys.exit(app.exec())
