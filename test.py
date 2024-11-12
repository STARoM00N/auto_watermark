import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QSlider, QProgressBar, QComboBox, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QMessageBox, QDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PIL import Image

class PositionPreviewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("เลือกตำแหน่งลายน้ำ")
        self.setFixedSize(300, 300)
        self.setStyleSheet("background-color: #d0d0d0; border: 1px solid #000;")
        self.selected_position = None

        self.preview_label = QLabel(self)
        self.preview_label.setFixedSize(300, 300)
        self.preview_label.setStyleSheet("background-color: #d0d0d0; border: 1px solid #000;")
        self.preview_label.mousePressEvent = self.set_custom_position

    def set_custom_position(self, event):
        x_ratio = event.pos().x() / self.preview_label.width()
        y_ratio = event.pos().y() / self.preview_label.height()
        self.selected_position = (x_ratio, y_ratio)
        self.accept()

    def get_position(self):
        return self.selected_position

class WatermarkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("โปรแกรมใส่ลายน้ำในรูปภาพ by เด็กชายศิวกร")
        self.setGeometry(300, 200, 400, 400)
        self.setWindowIcon(QIcon("Asset-1.ico"))

        layout = QVBoxLayout()
        
        self.image_folder_button = QPushButton("เลือกโฟลเดอร์ที่มีภาพ")
        self.image_folder_button.clicked.connect(self.select_image_folder)
        layout.addWidget(self.image_folder_button)
        
        self.image_folder_label = QLineEdit()
        self.image_folder_label.setReadOnly(True)
        layout.addWidget(self.image_folder_label)

        self.watermark_button = QPushButton("เลือกไฟล์ลายน้ำ")
        self.watermark_button.clicked.connect(self.select_watermark_image)
        layout.addWidget(self.watermark_button)
        
        self.watermark_label = QLineEdit()
        self.watermark_label.setReadOnly(True)
        layout.addWidget(self.watermark_label)

        self.output_folder_button = QPushButton("เลือกโฟลเดอร์ปลายทาง")
        self.output_folder_button.clicked.connect(self.select_output_folder)
        layout.addWidget(self.output_folder_button)
        
        self.output_folder_label = QLineEdit()
        self.output_folder_label.setReadOnly(True)
        layout.addWidget(self.output_folder_label)

        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("ขนาดของลายน้ำ (%)"))
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(5, 50)
        self.size_slider.setValue(15)
        self.size_slider.valueChanged.connect(self.update_size_label)
        size_layout.addWidget(self.size_slider)
        
        self.size_label = QLabel("15%")
        size_layout.addWidget(self.size_label)
        layout.addLayout(size_layout)

        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("ความเข้มของลายน้ำ (%)"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.update_opacity_label)
        opacity_layout.addWidget(self.opacity_slider)
        
        self.opacity_label = QLabel("100%")
        opacity_layout.addWidget(self.opacity_label)
        layout.addLayout(opacity_layout)

        layout.addWidget(QLabel("ตำแหน่งของลายน้ำ"))
        self.position_combo = QComboBox()
        self.position_combo.addItems(["มุมขวาล่าง", "มุมซ้ายล่าง", "มุมขวาบน", "มุมซ้ายบน", "เลือกตำแหน่งเอง"])
        self.position_combo.currentIndexChanged.connect(self.check_custom_position)
        layout.addWidget(self.position_combo)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #4caf50; }")
        layout.addWidget(self.progress_bar)
        
        layout.addSpacing(15)
        self.start_button = QPushButton("เริ่มใส่ลายน้ำ")
        self.start_button.clicked.connect(self.start_watermarking)
        layout.addWidget(self.start_button)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.image_folder = ""
        self.watermark_image = ""
        self.output_folder = ""
        self.custom_position = None

    def select_image_folder(self):
        self.image_folder = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์ที่มีภาพ")
        self.image_folder_label.setText(self.image_folder)
    
    def select_watermark_image(self):
        self.watermark_image, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์ลายน้ำ", "", "Images (*.png *.jpg *.jpeg)")
        self.watermark_label.setText(self.watermark_image)
    
    def select_output_folder(self):
        self.output_folder = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์ปลายทาง")
        self.output_folder_label.setText(self.output_folder)

    def update_size_label(self):
        self.size_label.setText(f"{self.size_slider.value()}%")
    
    def update_opacity_label(self):
        self.opacity_label.setText(f"{self.opacity_slider.value()}%")

    def check_custom_position(self):
        if self.position_combo.currentText() == "เลือกตำแหน่งเอง":
            preview_dialog = PositionPreviewDialog(self)
            if preview_dialog.exec_():
                self.custom_position = preview_dialog.get_position()
        else:
            self.custom_position = None

    def start_watermarking(self):
        if self.image_folder and self.watermark_image and self.output_folder:
            images = [f for f in os.listdir(self.image_folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
            total_images = len(images)
            
            if total_images == 0:
                self.show_message("ไม่พบภาพในโฟลเดอร์")
                return
            
            self.progress_bar.setValue(0)
            for i, filename in enumerate(images, start=1):
                image_path = os.path.join(self.image_folder, filename)
                output_path = os.path.join(self.output_folder, filename)
                
                self.add_watermark(image_path, self.watermark_image, output_path)
                
                progress_percentage = int((i / total_images) * 100)
                self.progress_bar.setValue(progress_percentage)
            self.show_message("การใส่ลายน้ำเสร็จสมบูรณ์!")
            self.progress_bar.setValue(0)
    
    def add_watermark(self, image_path, watermark_path, output_path):
        scale = self.size_slider.value() / 100
        opacity = self.opacity_slider.value() / 100
        position = self.position_combo.currentText()
        
        base_image = Image.open(image_path).convert("RGBA")
        watermark = Image.open(watermark_path).convert("RGBA")
        
        watermark_width = int(base_image.width * scale)
        aspect_ratio = watermark.width / watermark.height
        watermark_height = int(watermark_width / aspect_ratio)
        watermark = watermark.resize((watermark_width, watermark_height), Image.LANCZOS)

        if opacity < 1.0:
            alpha = watermark.split()[3]
            alpha = alpha.point(lambda p: p * opacity)
            watermark.putalpha(alpha)
        
        if position == "มุมขวาล่าง":
            x = base_image.width - watermark.width - 10
            y = base_image.height - watermark.height - 10
        elif position == "มุมซ้ายล่าง":
            x = 10
            y = base_image.height - watermark.height - 10
        elif position == "มุมขวาบน":
            x = base_image.width - watermark.width - 10
            y = 10
        elif position == "มุมซ้ายบน":
            x, y = 10, 10
        elif position == "เลือกตำแหน่งเอง" and self.custom_position:
            x = int(base_image.width * self.custom_position[0])
            y = int(base_image.height * self.custom_position[1])
        else:
            x, y = 10, 10

        base_image.paste(watermark, (x, y), watermark)
        combined = base_image.convert("RGB")
        combined.save(output_path, "JPEG")

    def show_message(self, message):
        QMessageBox.information(self, "แจ้งเตือน", message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("Asset-1.ico"))
    window = WatermarkApp()
    window.show()
    sys.exit(app.exec_())
