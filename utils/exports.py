from PyQt6.QtWidgets import QApplication, QMessageBox, QFileDialog
from PIL import Image, ImageFont, ImageDraw
from utils.constants import BG_COLORS


def copy_to_clipboard(parent, ascii_text: str):
    if ascii_text:
        QApplication.clipboard().setText(ascii_text)
        QMessageBox.information(parent, "Success", "Copied to clipboard!")


def save_to_file(parent, ascii_text: str):
    if not ascii_text:
        return
    file_path, _ = QFileDialog.getSaveFileName(
        parent, "Save ASCII Art", "ascii_art.txt", "Text Files (*.txt)"
    )
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(ascii_text)


def save_as_html(parent, ascii_text: str, bg_color_name: str):
    if not ascii_text:
        return
    file_path, _ = QFileDialog.getSaveFileName(
        parent, "Save HTML", "ascii_art.html", "HTML Files (*.html)"
    )
    if file_path:
        hex_bg = BG_COLORS.get(bg_color_name, "#09090b")
        html_content = f"<html><body style='background-color:{hex_bg}; color:#06b6d4; font-family:Consolas, monospace; white-space:pre;'>\n{ascii_text}\n</body></html>"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)


def save_as_image(parent, ascii_text: str, bg_color_name: str):
    if not ascii_text:
        return
    file_path, _ = QFileDialog.getSaveFileName(
        parent, "Save as Image", "ascii_art.png", "PNG Files (*.png)"
    )
    if file_path:
        lines = ascii_text.split("\n")
        try:
            font = ImageFont.truetype("consola.ttf", 14)
        except Exception:
            font = ImageFont.load_default()

        char_w = 8
        char_h = 14
        img_w = max(len(line) for line in lines) * char_w + 40
        img_h = len(lines) * char_h + 40

        hex_bg = BG_COLORS.get(bg_color_name, "#09090b")
        img = Image.new("RGB", (img_w, img_h), color=hex_bg)
        d = ImageDraw.Draw(img)
        d.text((20, 20), ascii_text, font=font, fill="#06b6d4")
        img.save(file_path)
