import sys
import os
import numpy as np
from PIL import Image, ImageDraw
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsView, QGraphicsScene, 
                             QGraphicsPixmapItem, QFileDialog, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QSlider, QLabel, QFrame, QMessageBox,
                             QComboBox)
from PyQt5.QtCore import Qt, QSize, QRectF
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QFont

# 配置入口
CAR_MODELS = {
    "cybertruck": "cybertruck.png",
    "焕新款model3": "model3-2024-base.png",
    "焕新款model3高性能版": "model3-2024-performance.png",
    "Model3": "model3.png",
    "焕新款modely": "modely-2025-base.png",
    "焕新款modely高性能版": "modely-2025-performance.png",
    "焕新款modely长续航版": "modely-2025-premium.png",
    "Modely L": "modely-l.png",
    "Modely": "modely.png",
}

# 画布背景色 (定义变量方便统一)
CANVAS_BG_COLOR = "#2b2b2b"

# 样式表 (修复版)
MODERN_STYLE = f"""
    QMainWindow {{
        background-color: #1e1e1e;
    }}
    /* 右侧面板样式 */
    QFrame#ControlPanel {{
        background-color: #333333;
        border-left: 1px solid #444444;
    }}
    QLabel {{
        color: #f0f0f0;
        font-family: "Segoe UI", "PingFang SC", sans-serif;
        font-size: 13px;
    }}
    QLabel#Title {{
        font-size: 18px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 12px;
    }}
    
    /* 按钮样式 */
    QPushButton {{
        background-color: #444444;
        color: white;
        border: 1px solid #555555;
        border-radius: 6px;
        padding: 10px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: #555555;
        border-color: #666666;
    }}
    QPushButton:pressed {{
        background-color: #222222;
    }}
    QPushButton#PrimaryBtn {{
        background-color: #0078d4;
        border: 1px solid #0078d4;
    }}
    QPushButton#PrimaryBtn:hover {{
        background-color: #1086e0;
    }}
    QPushButton#DangerBtn {{
        background-color: #c42b1c;
        border: 1px solid #c42b1c;
    }}
    QPushButton#DangerBtn:hover {{
        background-color: #d83b2a;
    }}

    /* === 修复下拉框看不清的问题 === */
    QComboBox {{
        background-color: #444444;
        color: white;
        border: 1px solid #555555;
        border-radius: 6px;
        padding: 8px;
        font-size: 13px;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    /* 强制设置下拉列表的颜色 */
    QComboBox QAbstractItemView {{
        background-color: #444444;
        color: white;
        selection-background-color: #0078d4;
        selection-color: white;
        border: 1px solid #555555;
        outline: none;
    }}

    /* 滑块样式 */
    QSlider::groove:horizontal {{
        height: 4px;
        background: #555555;
        margin: 2px 0;
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: #0078d4;
        width: 16px;
        height: 16px;
        margin: -6px 0;
        border-radius: 8px;
        border: 1px solid #1086e0;
    }}
"""

def resource_path(relative_path):
    """ 获取资源的绝对路径，兼容所有打包模式 """
    if hasattr(sys, 'frozen'):
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class CarWrapTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("专业车身改色系统 V3.2")
        self.resize(1350, 850)
        self.setStyleSheet(MODERN_STYLE)
        
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.overlay_item = None
        self.selected_item = None
        
        self.init_ui()
        
        # 默认加载第一辆车
        if CAR_MODELS:
            self.load_built_in_template(list(CAR_MODELS.keys())[0])

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # === 左侧预览区域 ===
        # 使用变量设置背景色，确保与遮罩颜色一致
        self.view.setStyleSheet(f"background-color: {CANVAS_BG_COLOR}; border: none;")
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view.setDragMode(QGraphicsView.RubberBandDrag) # 允许框选
        layout.addWidget(self.view, stretch=4)

        # === 右侧控制面板 ===
        controls = QFrame()
        controls.setObjectName("ControlPanel")
        controls.setFixedWidth(320)
        
        # 使用 Shadow 增加层次感
        shadow = QFrame()
        shadow.setFrameShape(QFrame.VLine)
        shadow.setStyleSheet("color: #111111; width: 1px;")
        
        control_layout = QVBoxLayout(controls)
        control_layout.setContentsMargins(25, 30, 25, 30)
        control_layout.setSpacing(18)
        
        layout.addWidget(controls)

        # 标题
        title = QLabel("DESIGN STUDIO")
        title.setObjectName("Title")
        control_layout.addWidget(title)
        
        control_layout.addWidget(QLabel("1. 车型选择 (Select Model)"))
        self.combo_models = QComboBox()
        self.combo_models.addItems(CAR_MODELS.keys())
        self.combo_models.currentTextChanged.connect(self.load_built_in_template)
        control_layout.addWidget(self.combo_models)
        
        # 分割线
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setStyleSheet("background-color: #444444;")
        control_layout.addWidget(line1)

        control_layout.addWidget(QLabel("2. 贴图管理 (Layers)"))
        btn_add = QPushButton("＋ 导入图案/改色膜")
        btn_add.setObjectName("PrimaryBtn")
        btn_add.clicked.connect(self.add_texture_layer)
        control_layout.addWidget(btn_add)

        self.btn_delete = QPushButton("－ 删除选中层")
        self.btn_delete.setObjectName("DangerBtn")
        self.btn_delete.clicked.connect(self.delete_selected_texture)
        control_layout.addWidget(self.btn_delete)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setStyleSheet("background-color: #444444;")
        control_layout.addWidget(line2)

        # 调整组
        self.lbl_status = QLabel("3. 调整参数 (Transform)")
        control_layout.addWidget(self.lbl_status)

        control_layout.addWidget(QLabel("旋转角度 (Rotation)"))
        self.slider_rotate = QSlider(Qt.Horizontal)
        self.slider_rotate.setRange(0, 360)
        self.slider_rotate.valueChanged.connect(self.update_transform)
        control_layout.addWidget(self.slider_rotate)

        control_layout.addWidget(QLabel("缩放比例 (Scale)"))
        self.slider_scale = QSlider(Qt.Horizontal)
        self.slider_scale.setRange(5, 400)
        self.slider_scale.setValue(100)
        self.slider_scale.valueChanged.connect(self.update_transform)
        control_layout.addWidget(self.slider_scale)

        control_layout.addStretch()

        # 导出
        btn_save = QPushButton("💾 导出设计图 (Export)")
        btn_save.clicked.connect(self.save_image)
        btn_save.setCursor(Qt.PointingHandCursor)
        control_layout.addWidget(btn_save)

        # 事件监听
        self.scene.selectionChanged.connect(self.on_selection_changed)

    def process_template_mask(self, image_path):
        """
        核心修复：
        1. 识别黑色线条 -> 转为浅白色 (以便在深色背景显示)
        2. 识别外部白色 -> 转为画布背景色 (CANVAS_BG_COLOR)
        3. 识别内部白色 -> 透明
        """
        try:
            pil_img = Image.open(image_path).convert("RGBA")
            np_img = np.array(pil_img)

            # 提取亮度
            brightness = np.mean(np_img[:, :, :3], axis=2)
            # 二值化：亮度大于200视为白背景，小于200视为黑线
            binary = np.where(brightness > 200, 255, 0).astype(np.uint8)

            # 泛洪填充算法识别“车身外部”
            h, w = binary.shape
            mask = Image.fromarray(binary)
            # 从左上角开始填充灰色(127)来标记外部
            ImageDraw.floodfill(mask, (0, 0), 127)
            mask_np = np.array(mask)

            new_data = np.zeros((h, w, 4), dtype=np.uint8)

            # === 颜色逻辑修改 ===
            
            # 1. 线条区域 (binary == 0)
            # 原本是黑色，现在改为浅白色 (RGBA: 220, 220, 220, 255) 配合深色背景
            new_data[binary == 0] = [220, 220, 220, 255]

            # 2. 外部遮罩 (mask_np == 127)
            # 改为与 CANVAS_BG_COLOR (#2b2b2b) 一致的颜色
            # #2b2b2b 对应的 RGB 是 (43, 43, 43)
            new_data[mask_np == 127] = [43, 43, 43, 255]

            # 3. 内部区域 (mask_np == 255)
            # 保持全透明
            new_data[mask_np == 255] = [0, 0, 0, 0]

            return Image.fromarray(new_data)

        except Exception as e:
            QMessageBox.critical(self, "Mask Error", str(e))
            return None

    def load_built_in_template(self, model_name):
        filename = CAR_MODELS.get(model_name)
        if not filename: return
        full_path = resource_path(os.path.join("assets", filename))
        
        if not os.path.exists(full_path):
            QMessageBox.warning(self, "资源丢失", f"找不到文件: {filename}")
            return

        if self.overlay_item: 
            self.scene.removeItem(self.overlay_item)

        processed_pil = self.process_template_mask(full_path)
        
        if processed_pil:
            r, g, b, a = processed_pil.split()
            qt_img = Image.merge("RGBA", (b, g, r, a))
            qim = QImage(qt_img.tobytes("raw", "RGBA"), qt_img.size[0], qt_img.size[1], QImage.Format_RGBA8888)
            
            pixmap = QPixmap.fromImage(qim)
            self.overlay_item = QGraphicsPixmapItem(pixmap)
            self.overlay_item.setZValue(1000) # 顶层
            self.overlay_item.setAcceptedMouseButtons(Qt.NoButton) # 鼠标穿透
            
            self.scene.addItem(self.overlay_item)
            # 设置场景大小与图片一致
            self.scene.setSceneRect(QRectF(pixmap.rect()))

    def add_texture_layer(self):
        path, _ = QFileDialog.getOpenFileName(self, "导入素材", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            pix = QPixmap(path)
            item = QGraphicsPixmapItem(pix)
            item.setZValue(1) # 中间层
            item.setFlags(QGraphicsPixmapItem.ItemIsMovable | QGraphicsPixmapItem.ItemIsSelectable)
            
            # 设置中心点
            item.setTransformOriginPoint(pix.width()/2, pix.height()/2)
            
            # 放置在视图中心
            if self.scene.width() > 0:
                center_pos = self.scene.sceneRect().center()
                item.setPos(center_pos.x() - pix.width()/2, center_pos.y() - pix.height()/2)
            else:
                item.setPos(0, 0)
                
            self.scene.addItem(item)
            item.setSelected(True)

    def delete_selected_texture(self):
        for item in self.scene.selectedItems():
            if item != self.overlay_item:
                self.scene.removeItem(item)

    def on_selection_changed(self):
        items = self.scene.selectedItems()
        if items:
            self.selected_item = items[0]
            self.lbl_status.setText("状态: ✅ 已选中涂层，可调整")
            self.slider_rotate.blockSignals(True)
            self.slider_scale.blockSignals(True)
            self.slider_rotate.setValue(int(self.selected_item.rotation()))
            self.slider_scale.setValue(int(self.selected_item.scale() * 100))
            self.slider_rotate.blockSignals(False)
            self.slider_scale.blockSignals(False)
        else:
            self.selected_item = None
            self.lbl_status.setText("状态: 未选中")

    def update_transform(self):
        if self.selected_item:
            self.selected_item.setRotation(self.slider_rotate.value())
            self.selected_item.setScale(self.slider_scale.value() / 100.0)

    def save_image(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出图片", "design_v3.png", "PNG (*.png)")
        if path:
            self.scene.clearSelection()
            # 创建与场景一样大的画布
            image = QImage(self.scene.sceneRect().size().toSize(), QImage.Format_ARGB32)
            # 使用配置的背景色填充
            image.fill(QColor(CANVAS_BG_COLOR))
            
            painter = QPainter(image)
            self.scene.render(painter)
            painter.end()
            image.save(path)
            QMessageBox.information(self, "成功", f"设计图已保存至:\n{path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    window = CarWrapTool()
    window.show()
    sys.exit(app.exec_())