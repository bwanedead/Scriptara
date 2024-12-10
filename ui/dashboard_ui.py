from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QScrollArea, QTreeWidget, QTreeWidgetItem, QPushButton, QLabel, QMenuBar, 
    QMenu, QAction, QFrame
)
from PyQt5.QtGui import QGuiApplication, QFont, QPixmap, QPainter, QBrush, QPen, QIcon, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from ui.styles import dark_mode_stylesheet, light_mode_stylesheet, dim_mode_stylesheet
from config.metrics_registry import METRICS

class MetricCellWidget(QFrame):
    remove_requested = pyqtSignal(str)
    move_up_requested = pyqtSignal(str)
    move_down_requested = pyqtSignal(str)

    def __init__(self, metric_name):
        super().__init__()
        self.metric_name = metric_name
        self.setObjectName("MetricCell")
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        self.title_label = QLabel(metric_name)
        self.remove_button = QPushButton("Remove")
        self.move_up_button = QPushButton("▲")
        self.move_down_button = QPushButton("▼")

        self.remove_button.clicked.connect(lambda: self.remove_requested.emit(self.metric_name))
        self.move_up_button.clicked.connect(lambda: self.move_up_requested.emit(self.metric_name))
        self.move_down_button.clicked.connect(lambda: self.move_down_requested.emit(self.metric_name))

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.move_up_button)
        header_layout.addWidget(self.move_down_button)
        header_layout.addWidget(self.remove_button)

        layout.addLayout(header_layout)

        params_label = QLabel("Parameters/Controls go here")
        viz_label = QLabel("Visualization area")

        layout.addWidget(params_label)
        layout.addWidget(viz_label)

class DashboardWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Scriptara Dashboard")

        self.create_menus()

        splitter = QSplitter(self)
        splitter.setHandleWidth(1)  # Make handle very thin
        splitter.setChildrenCollapsible(False)
        self.setCentralWidget(splitter)

        # Left panel
        left_panel = QWidget()
        left_panel.setObjectName("PanelArea")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(5)

        title_label = QLabel("Metrics Panel")
        title_label.setObjectName("SidePanelTitle")
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setContentsMargins(10, 0, 0, 5)
        left_layout.addWidget(title_label)

        self.metric_tree = QTreeWidget()
        self.metric_tree.setHeaderHidden(True)

        # Adjusting indentation so parents are closer to the left
        # Let's try a smaller indentation, e.g. 10 pixels
        self.metric_tree.setIndentation(10)

        # We'll add manual spaces to sub-metrics to indent them more
        # in populate_metric_tree

        self.metric_tree.setRootIsDecorated(True)
        self.metric_tree.setExpandsOnDoubleClick(False)
        left_layout.addWidget(self.metric_tree)

        self.add_metric_button = QPushButton("Add Metric")
        left_layout.addWidget(self.add_metric_button)

        self.populate_metric_tree()

        self.metric_tree.itemDoubleClicked.connect(self.controller.add_selected_metric)
        self.metric_tree.itemClicked.connect(self.handle_item_clicked)

        # Right panel
        right_widget = QWidget()
        right_widget.setObjectName("NotebookArea")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(5)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("NotebookScrollArea")

        self.metrics_container = QWidget()
        self.metrics_layout = QVBoxLayout(self.metrics_container)
        self.metrics_layout.setSpacing(15)
        self.metrics_layout.setContentsMargins(10, 10, 10, 10)
        self.metrics_layout.addStretch()

        self.scroll_area.setWidget(self.metrics_container)
        right_layout.addWidget(self.scroll_area)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(1, 1)

        self.add_metric_button.clicked.connect(self.controller.add_selected_metric)

        self.set_dark_mode()
        self.resize_to_screen()

    def resize_to_screen(self):
        screen_size = QGuiApplication.primaryScreen().availableGeometry()
        self.resize(int(screen_size.width() * 0.8), int(screen_size.height() * 0.8))

    def create_menus(self):
        menubar = self.menuBar()
        menubar.setContentsMargins(0,0,0,0)
        view_menu = menubar.addMenu('View')

        dark_mode_action = QAction('Dark Mode', self)
        dark_mode_action.triggered.connect(self.set_dark_mode)
        light_mode_action = QAction('Light Mode', self)
        light_mode_action.triggered.connect(self.set_light_mode)
        dim_mode_action = QAction('Dim Mode', self)
        dim_mode_action.triggered.connect(self.set_dim_mode)

        view_menu.addAction(light_mode_action)
        view_menu.addAction(dark_mode_action)
        view_menu.addAction(dim_mode_action)

    def set_dark_mode(self):
        self.setStyleSheet(dark_mode_stylesheet)

    def set_light_mode(self):
        self.setStyleSheet(light_mode_stylesheet)

    def set_dim_mode(self):
        self.setStyleSheet(dim_mode_stylesheet)

    def create_arrow_icon(self, direction):
        size = 24
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)

        brush_color = QColor("#cccccc")
        brush = QBrush(brush_color)
        pen = QPen(Qt.transparent)
        painter.setPen(pen)
        painter.setBrush(brush)

        if direction == "right":
            points = [
                QPoint(int(size * 0.3), int(size * 0.2)),
                QPoint(int(size * 0.3), int(size * 0.8)),
                QPoint(int(size * 0.7), int(size * 0.5)),
            ]
        elif direction == "down":
            points = [
                QPoint(int(size * 0.2), int(size * 0.3)),
                QPoint(int(size * 0.8), int(size * 0.3)),
                QPoint(int(size * 0.5), int(size * 0.7)),
            ]
        else:
            points = []

        if points:
            painter.drawPolygon(*points)

        painter.end()
        return QIcon(pixmap)

    def populate_metric_tree(self):
        # Add a couple spaces to sub-metrics to indent them relative to parents
        parent_font = QFont()
        parent_font.setBold(True)

        for category_key, category_data in METRICS.items():
            category_item = QTreeWidgetItem([category_data["name"]])
            category_item.setData(0, Qt.UserRole, (category_key, None))
            category_item.setFont(0, parent_font)
            category_item.setIcon(0, self.create_arrow_icon("right"))

            sub_metrics = category_data.get("sub_metrics", {})
            for sub_key, sub_data in sub_metrics.items():
                # Add spaces in front of the sub-metric name to indent further than the parent's indentation
                indented_name = "          " + sub_data["name"]  # 3 spaces for extra indentation
                sub_item = QTreeWidgetItem(category_item, [indented_name])
                sub_item.setData(0, Qt.UserRole, (category_key, sub_key))

            self.metric_tree.addTopLevelItem(category_item)
            category_item.setExpanded(False)

    def handle_item_clicked(self, item, column):
        # If the clicked item is a category
        if item.childCount() > 0:
            if item.isExpanded():
                item.setExpanded(False)
                item.setIcon(0, self.create_arrow_icon("right"))
            else:
                item.setExpanded(True)
                item.setIcon(0, self.create_arrow_icon("down"))

    def get_selected_metric_keys(self):
        selected_items = self.metric_tree.selectedItems()
        if not selected_items:
            return None, None
        item = selected_items[0]
        category_key, sub_key = item.data(0, Qt.UserRole)
        if sub_key is None:
            return None, None
        return category_key, sub_key

    def add_metric_cell(self, metric_name):
        cell = MetricCellWidget(metric_name)
        self.metrics_layout.insertWidget(self.metrics_layout.count() - 1, cell)
        return cell