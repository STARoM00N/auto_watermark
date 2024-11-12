import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QSlider, 
    QProgressBar, QComboBox, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PIL import Image
import numpy as np

def pil_image_to_qimage(pil_image):
    image_array = np.array(pil_image.convert("RGBA"))
    h, w, ch = image_array.shape
    bytes_per_line = ch * w
    qimage = QImage(image_array.data, w, h, bytes_per_line, QImage.Format_RGBA8888)
    return qimage

class WatermarkApp(QMainWindow):
    def select_image_folder(self):
        self.image_folder = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์ที่มีภาพ")
        self.image_folder_label.setText(self.image_folder)
        self.update_preview()
        
    def select_watermark_image(self):
        self.watermark_image, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์ลายน้ำ", "", "Images (*.png *.jpg *.jpeg)")
        if self.watermark_image:
            self.watermark_label.setText(self.watermark_image)
            self.update_preview()
            
    def select_output_folder(self):
        self.output_folder = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์ปลายทาง")
        self.output_folder_label.setText(self.output_folder)
        
    def update_size_label(self):
        self.size_label.setText(f"{self.size_slider.value()}%")
        self.update_preview()  # เรียกเพื่ออัปเดตภาพตัวอย่างตามขนาดลายน้ำที่เปลี่ยนแปลง

    def update_opacity_label(self):
        self.opacity_label.setText(f"{self.opacity_slider.value()}%")
        self.update_preview()  # เรียกเพื่ออัปเดตภาพตัวอย่างตามค่าความโปร่งแสงที่เปลี่ยนแปลง

    def __init__(self):
        super().__init__()
        self.setWindowTitle("โปรแกรมใส่ลายน้ำในรูปภาพ by เด็กชายศิวกร")
        self.setGeometry(300, 200, 800, 600)
        self.setWindowIcon(QIcon("Asset-1.ico"))

        self.image_folder = ""
        self.watermark_image = ""
        self.output_folder = ""

        layout = QVBoxLayout()

        # โฟลเดอร์ภาพ
        self.image_folder_button = QPushButton("เลือกโฟลเดอร์ที่มีภาพ")
        self.image_folder_button.clicked.connect(self.select_image_folder)
        layout.addWidget(self.image_folder_button)
        self.image_folder_label = QLineEdit()
        self.image_folder_label.setReadOnly(True)
        layout.addWidget(self.image_folder_label)

        # ไฟล์ลายน้ำ
        self.watermark_button = QPushButton("เลือกไฟล์ลายน้ำ")
        self.watermark_button.clicked.connect(self.select_watermark_image)
        layout.addWidget(self.watermark_button)
        
        self.watermark_label = QLineEdit()
        self.watermark_label.setReadOnly(True)
        layout.addWidget(self.watermark_label)

        # โฟลเดอร์ปลายทาง
        self.output_folder_button = QPushButton("เลือกโฟลเดอร์ปลายทาง")
        self.output_folder_button.clicked.connect(self.select_output_folder)
        layout.addWidget(self.output_folder_button)
        
        self.output_folder_label = QLineEdit()
        self.output_folder_label.setReadOnly(True)
        layout.addWidget(self.output_folder_label)

        # ขนาดของลายน้ำ
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("ขนาดของลายน้ำ (%)"))
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(5, 50)
        self.size_slider.setValue(15)
        self.size_slider.valueChanged.connect(self.update_size_label)
        self.size_label = QLabel("15%")
        size_layout.addWidget(self.size_slider)
        size_layout.addWidget(self.size_label)
        layout.addLayout(size_layout)

        # ความโปร่งแสงของลายน้ำ
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("ความเข้มของลายน้ำ (%)"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.update_opacity_label)
        self.opacity_label = QLabel("100%")
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        layout.addLayout(opacity_layout)

        # ตำแหน่งของลายน้ำ
        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("ตำแหน่งของลายน้ำ"))
        self.position_combo = QComboBox()
        self.position_combo.addItems(["มุมขวาล่าง", "มุมซ้ายล่าง", "มุมขวาบน", "มุมซ้ายบน", "เลือกตำแหน่งเอง"])
        self.position_combo.currentIndexChanged.connect(self.update_xy_fields)
        position_layout.addWidget(self.position_combo)
        layout.addLayout(position_layout)
        
        # ป้อนค่า x และ y
        xy_layout = QHBoxLayout()
        xy_layout.addWidget(QLabel("ตำแหน่ง X:"))
        self.x_input = QLineEdit("10")
        self.x_input.textChanged.connect(self.update_position_and_preview)
        xy_layout.addWidget(self.x_input)
        xy_layout.addWidget(QLabel("ตำแหน่ง Y:"))
        self.y_input = QLineEdit("10")
        self.y_input.textChanged.connect(self.update_position_and_preview)
        xy_layout.addWidget(self.y_input)
        layout.addLayout(xy_layout)

        # แถบความคืบหน้า
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # ปุ่มเริ่มใส่ลายน้ำ
        self.start_button = QPushButton("เริ่มใส่ลายน้ำ")
        self.start_button.clicked.connect(self.start_watermarking)
        layout.addWidget(self.start_button)
        
        # QLabel สำหรับแสดง Preview
        self.preview_label = QLabel(self)
        self.preview_label.setFixedSize(400, 400)
        self.preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview_label, alignment=Qt.AlignCenter)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_xy_fields(self):
        position = self.position_combo.currentText()
        try:
            # โหลดตัวอย่างภาพเพื่อใช้ในการคำนวณตำแหน่ง
            preview_image_path = os.path.join(self.image_folder, os.listdir(self.image_folder)[0])
            base_image = Image.open(preview_image_path)
            watermark_image = Image.open(self.watermark_image)

            # คำนวณขนาดของลายน้ำตามตัวสไลเดอร์ขนาด
            watermark_width = int(base_image.width * self.size_slider.value() / 100)
            aspect_ratio = watermark_image.width / watermark_image.height
            watermark_height = int(watermark_width / aspect_ratio)

            if position == "มุมขวาล่าง":
                x = base_image.width - watermark_width - 10
                y = base_image.height - watermark_height - 10
            elif position == "มุมซ้ายล่าง":
                x = 10
                y = base_image.height - watermark_height - 10
            elif position == "มุมขวาบน":
                x = base_image.width - watermark_width - 10
                y = 10
            elif position == "มุมซ้ายบน":
                x = 10
                y = 10
            else:
                # ถ้าเลือก "เลือกตำแหน่งเอง" ไม่ทำการเปลี่ยนแปลง x, y
                return

            # อัพเดตค่าของช่องป้อน x และ y
            self.x_input.setText(str(x))
            self.y_input.setText(str(y))
            self.update_preview()

        except (FileNotFoundError, IndexError):
            # จัดการข้อผิดพลาดในกรณีที่ยังไม่มีภาพพื้นหลังหรือลายน้ำ
            pass

  
    def update_position_and_preview(self):
        if self.position_combo.currentText() != "เลือกตำแหน่งเอง":
            self.position_combo.setCurrentText("เลือกตำแหน่งเอง")
        self.update_preview()
        
    def check_custom_position(self):
        if self.position_combo.currentText() == "เลือกตำแหน่งเอง":
            self.custom_position = None  # ไม่เปิด dialog แต่ตั้งค่าเองโดยตรง
        else:
            self.custom_position = None
        self.update_preview()
        
    def update_preview(self):
        if self.image_folder and self.watermark_image:
            image_files = [f for f in os.listdir(self.image_folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
            if not image_files:
                self.preview_label.clear()
                return
            
            preview_image_path = os.path.join(self.image_folder, image_files[0])
            base_image = Image.open(preview_image_path).convert("RGBA")
            watermark_image = Image.open(self.watermark_image).convert("RGBA")
            
            watermark_width = int(base_image.width * self.size_slider.value() / 100)
            aspect_ratio = watermark_image.width / watermark_image.height
            watermark_height = int(watermark_width / aspect_ratio)
            watermark_image = watermark_image.resize((watermark_width, watermark_height), Image.LANCZOS)
            
            opacity = self.opacity_slider.value() / 100
            if opacity < 1.0:
                alpha = watermark_image.split()[3]
                alpha = alpha.point(lambda p: int(p * opacity))
                watermark_image.putalpha(alpha)
            
            try:
                x = int(self.x_input.text())
                y = int(self.y_input.text())
            except ValueError:
                x, y = 10, 10

            base_image.paste(watermark_image, (x, y), watermark_image)
            qimage = pil_image_to_qimage(base_image)
            preview_pixmap = QPixmap.fromImage(qimage)
            self.preview_label.setPixmap(preview_pixmap.scaled(self.preview_label.size(), Qt.KeepAspectRatio))

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
        
        base_image = Image.open(image_path).convert("RGBA")
        watermark = Image.open(watermark_path).convert("RGBA")
        
        watermark_width = int(base_image.width * scale)
        aspect_ratio = watermark.width / watermark.height
        watermark_height = int(watermark_width / aspect_ratio)
        watermark = watermark.resize((watermark_width, watermark_height), Image.LANCZOS)

        if opacity < 1.0:
            alpha = watermark.split()[3]
            alpha = alpha.point(lambda p: int(p * opacity))
            watermark.putalpha(alpha)
        
        try:
            x = int(self.x_input.text())
            y = int(self.y_input.text())
        except ValueError:
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
