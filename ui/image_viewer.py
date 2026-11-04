# -*- coding: utf-8 -*-
"""
TorahNotesOCR - Document Image Viewer
QGraphicsView supporting pan, zoom, 90-degree rotations, contrast enhancement,
and OCR line bounding box overlays.
"""

from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, 
    QGraphicsRectItem, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QSlider
)
from PyQt6.QtCore import Qt, QRectF, pyqtSignal, QPointF
from PyQt6.QtGui import (
    QPixmap, QImage, QPainter, QColor, QPen, QBrush, 
    QTransform, QWheelEvent, QMouseEvent
)
from PIL import Image, ImageEnhance, ImageOps

class DocumentViewer(QGraphicsView):
    zoom_changed = pyqtSignal(float)
    line_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Rendering options
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing | 
            QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # State
        self.current_pil_img = None
        self.pixmap_item = None
        self.rotation_angle = 0
        self.contrast_enhanced = False
        self.bounding_boxes = []
        self.rect_items = []
        self._current_zoom = 1.0

    def load_image(self, pil_image: Image.Image, rotation: int = 0):
        """Loads a PIL image into the graphics scene."""
        self.current_pil_img = pil_image
        self.rotation_angle = rotation
        self.contrast_enhanced = False
        self.bounding_boxes = []
        self._update_display()
        self.fit_to_window()

    def _update_display(self):
        """Applies rotation, contrast, and converts PIL to QPixmap."""
        if self.current_pil_img is None:
            return

        img = self.current_pil_img.copy()

        # Handle EXIF & rotation
        if self.rotation_angle % 360 != 0:
            # PIL rotate counter-clockwise by default, so use -angle
            img = img.rotate(-self.rotation_angle, expand=True)

        # Contrast enhancement if active
        if self.contrast_enhanced:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.6)
            sharpener = ImageEnhance.Sharpness(img)
            img = sharpener.enhance(1.3)

        # Convert to QPixmap
        if img.mode != "RGB":
            img = img.convert("RGB")
        data = img.tobytes("raw", "RGB")
        qimg = QImage(data, img.width, img.height, img.width * 3, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        # Update scene
        self.scene.clear()
        self.rect_items.clear()
        self.pixmap_item = self.scene.addPixmap(pixmap)
        self.scene.setSceneRect(QRectF(pixmap.rect()))

        # Re-render bounding boxes if any
        self._render_bounding_boxes()

    def rotate_cw(self):
        """Rotates image 90 degrees Clockwise."""
        self.rotation_angle = (self.rotation_angle + 90) % 360
        self._update_display()

    def rotate_ccw(self):
        """Rotates image 90 degrees Counter-Clockwise."""
        self.rotation_angle = (self.rotation_angle - 90) % 360
        self._update_display()

    def toggle_contrast(self):
        """Toggles high-contrast filter for faint ink or pencil."""
        self.contrast_enhanced = not self.contrast_enhanced
        self._update_display()
        return self.contrast_enhanced

    def fit_to_window(self):
        """Fits entire document within view."""
        if self.pixmap_item is None:
            return
        self.resetTransform()
        rect = self.scene.sceneRect()
        if rect.width() > 0 and rect.height() > 0:
            self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
            self._current_zoom = self.transform().m11()
            self.zoom_changed.emit(self._current_zoom)

    def fit_to_width(self):
        """Zooms to fit page width."""
        if self.pixmap_item is None:
            return
        self.resetTransform()
        rect = self.scene.sceneRect()
        vw = self.viewport().width() - 20
        if rect.width() > 0 and vw > 0:
            factor = vw / rect.width()
            self.scale(factor, factor)
            self._current_zoom = factor
            self.zoom_changed.emit(self._current_zoom)

    def zoom_in(self):
        self.scale(1.25, 1.25)
        self._current_zoom *= 1.25
        self.zoom_changed.emit(self._current_zoom)

    def zoom_out(self):
        self.scale(0.8, 0.8)
        self._current_zoom *= 0.8
        self.zoom_changed.emit(self._current_zoom)

    def wheelEvent(self, event: QWheelEvent):
        """Smooth mouse-wheel zooming anchored at cursor."""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier or True:
            factor = 1.15 if event.angleDelta().y() > 0 else 0.87
            self.scale(factor, factor)
            self._current_zoom *= factor
            self.zoom_changed.emit(self._current_zoom)
            event.accept()
        else:
            super().wheelEvent(event)

    def set_bounding_boxes(self, boxes: list):
        """Sets OCR line boxes for overlay display."""
        self.bounding_boxes = boxes
        self._render_bounding_boxes()

    def _render_bounding_boxes(self):
        for item in self.rect_items:
            self.scene.removeItem(item)
        self.rect_items.clear()

        pen = QPen(QColor(59, 130, 246, 180), 2)
        brush = QBrush(QColor(59, 130, 246, 35))

        for idx, box in enumerate(self.bounding_boxes):
            if isinstance(box, dict):
                x = box.get('x', 0)
                y = box.get('y', 0)
                w = box.get('w', 0)
                h = box.get('h', 0)
                rect_item = self.scene.addRect(QRectF(x, y, w, h), pen, brush)
                rect_item.setToolTip(f"Line {idx + 1}")
                self.rect_items.append(rect_item)

    def highlight_line(self, line_index: int):
        """Highlights a specific line bounding box."""
        for idx, item in enumerate(self.rect_items):
            if idx == line_index:
                item.setPen(QPen(QColor(234, 179, 8, 255), 3))
                item.setBrush(QBrush(QColor(234, 179, 8, 70)))
                self.centerOn(item)
            else:
                item.setPen(QPen(QColor(59, 130, 246, 180), 2))
                item.setBrush(QBrush(QColor(59, 130, 246, 35)))
