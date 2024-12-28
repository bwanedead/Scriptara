# dashboard_ui.py

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QTreeWidget, QTreeWidgetItem, QPushButton, QLabel, QMenuBar, 
    QMenu, QAction, QFrame, QTableWidget, QTableWidgetItem, QSizePolicy, QToolButton, QSizeGrip, QHeaderView, 
    QSplitter
)
from PyQt5.QtGui import QGuiApplication, QFont, QPixmap, QPainter, QBrush, QPen, QIcon, QColor, QWheelEvent
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QEvent, QRect
from ui.styles import dark_mode_stylesheet, light_mode_stylesheet, dim_mode_stylesheet
from config.metric_registry import METRICS, get_metric
from visualizations.cell_factory import create_cell





class CollapsibleCellWidget(QFrame):
    remove_requested = pyqtSignal(str)
    move_up_requested = pyqtSignal(str)
    move_down_requested = pyqtSignal(str)
    duplicate_requested = pyqtSignal(str)

    def __init__(self, title):
        super().__init__()
        self.setObjectName("MetricCell")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            QFrame#MetricCell {
                border: 1px solid #444444;
                border-radius: 5px;
                background-color: #2f2f2f;
                margin: 5px;
            }
        """)
        self.title = title
        self.expanded = True
        
        # Set default size
        self.default_height = 550  # Adjust this value as needed for the default cell height
        self.setMinimumHeight(self.default_height)
        self.setMaximumHeight(self.default_height)

        # Resizing logic
        self.drag_start_pos = None
        self.is_resizing = False
        self.resize_margin = 5  # Margin to detect resizing

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)

        # Top bar with controls
        top_bar = QHBoxLayout()
        self.label = QLabel(self.title)
        self.label.setStyleSheet("color: #ffffff;")
        top_bar.addWidget(self.label)

        top_bar.addStretch()

        self.move_up_button = QToolButton()
        self.move_up_button.setText("↑")
        top_bar.addWidget(self.move_up_button)

        self.move_down_button = QToolButton()
        self.move_down_button.setText("↓")
        top_bar.addWidget(self.move_down_button)

        self.duplicate_button = QToolButton()
        self.duplicate_button.setText("Duplicate")
        top_bar.addWidget(self.duplicate_button)

        self.collapse_button = QToolButton()
        self.collapse_button.setText("–")
        top_bar.addWidget(self.collapse_button)

        self.remove_button = QToolButton()
        self.remove_button.setText("X")
        top_bar.addWidget(self.remove_button)

        self.main_layout.addLayout(top_bar)

        # Content area
        self.content_layout = QVBoxLayout()
        self.main_layout.addLayout(self.content_layout)

            # Button actions with debug prints for tracing
        self.move_up_button.clicked.connect(lambda: self.emit_signal_with_debug("move_up_requested", self.title))
        self.move_down_button.clicked.connect(lambda: self.emit_signal_with_debug("move_down_requested", self.title))
        self.duplicate_button.clicked.connect(lambda: self.emit_signal_with_debug("duplicate_requested", self.title))
        self.collapse_button.clicked.connect(self.toggle_collapse)
        self.remove_button.clicked.connect(lambda: self.emit_signal_with_debug("remove_requested", self.title))

        # Enable event filtering for resizing
        self.setMouseTracking(True)
        self.installEventFilter(self)

    # Helper method for emitting signals with debug
    def emit_signal_with_debug(self, signal_name, title):
        print(f"Signal emitted: {signal_name} for cell with title '{title}'")
        getattr(self, signal_name).emit(title)

    def add_content_widget(self, widget):
        self.content_layout.addWidget(widget)
        # Set a default size for new cells
        self.setMinimumHeight(300)
        self.setMaximumHeight(300)
        self.updateGeometry()

    def toggle_collapse(self):
        if self.expanded:
            # Store the current dimensions before collapsing
            self.stored_min_height = self.minimumHeight()
            self.stored_max_height = self.maximumHeight()

            # Collapse: Switch to a minimal state
            self.clear_content()
            self.setMinimumHeight(60)
            self.setMaximumHeight(60)
            self.label.setText(self.title)
            self.label.setStyleSheet("color: #ffffff; font-weight: bold;")
            self.collapse_button.setText("+")
            self.expanded = False
        else:
            # Restore the dimensions
            self.setMinimumHeight(self.stored_min_height if hasattr(self, 'stored_min_height') else 300)
            self.setMaximumHeight(self.stored_max_height if hasattr(self, 'stored_max_height') else 300)

            self.restore_content()
            self.label.setText(self.title)
            self.collapse_button.setText("–")
            self.expanded = True


    def clear_content(self):
        # Remove all child widgets from the content layout
        while self.content_layout.count():
            child = self.content_layout.takeAt(0).widget()
            if child:
                child.setParent(None)
        # Ensure buttons remain visible
        self.move_up_button.setVisible(True)
        self.move_down_button.setVisible(True)
        self.duplicate_button.setVisible(True)
        self.collapse_button.setVisible(True)
        self.remove_button.setVisible(True)

    def restore_content(self):
        # Restore the original content widget (e.g., visualization or table)
        if hasattr(self, 'stored_content') and self.stored_content:
            self.content_layout.addWidget(self.stored_content)
            self.stored_content.setVisible(True)
        else:
            # Log or handle the case where there's no stored content
            print("No content to restore.")
    
    def add_content_widget(self, widget):
        self.stored_content = widget  # Save the content for restoration
        self.content_layout.addWidget(widget)




    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            cursor_pos = self.mapFromGlobal(event.globalPos())

            # Only intercept if near bottom edge → begin resizing
            if self.height() - self.resize_margin <= cursor_pos.y() <= self.height():
                self.drag_start_pos = event.globalPos()
                self.is_resizing = True
                return True  # swallow
            else:
                return super().eventFilter(obj, event)  # pass up to child button

        elif event.type() == QEvent.MouseButtonRelease:
            if self.is_resizing:
                # End resizing
                self.drag_start_pos = None
                self.is_resizing = False
                return True
            else:
                return super().eventFilter(obj, event)

        elif event.type() == QEvent.MouseMove:
            # Only handle if is_resizing
            if self.is_resizing:
                # do the resizing
                return True
            else:
                return super().eventFilter(obj, event)

        return super().eventFilter(obj, event)


    
    def resize_cell(self, new_height):
        """
        Resizes the cell to the specified height and adjusts its parent widget dimensions.
        """
        self.setMinimumHeight(new_height)
        self.setMaximumHeight(new_height)
        self.updateGeometry()  # Update this widget's geometry
        self.parentWidget().adjustSize()  # Adjust the notebook size
        self.parentWidget().parentWidget().adjust_scroll_area()  # Update the scroll area dynamically





class DashboardWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Scriptara Dashboard")

        self.create_menus()

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(main_widget)

        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

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
        self.metric_tree.setIndentation(10)
        self.metric_tree.setRootIsDecorated(True)
        self.metric_tree.setExpandsOnDoubleClick(False)
        left_layout.addWidget(self.metric_tree)

        self.add_metric_button = QPushButton("Add Metric")
        left_layout.addWidget(self.add_metric_button)

        self.populate_metric_tree()

        # Connections
        self.metric_tree.itemClicked.connect(self.on_item_clicked)  # Single click to expand/collapse or highlight
        self.metric_tree.itemDoubleClicked.connect(self.on_item_double_clicked)  # Double click to add metric
        self.add_metric_button.clicked.connect(self.add_highlighted_metric)  # Add highlighted metric

        splitter.addWidget(left_panel)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Show vertical scrollbar as needed
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable horizontal scrollbar
        self.scroll_area.setFocusPolicy(Qt.StrongFocus)  # Ensure proper focus handling

        self.notebook_container = QWidget()
        self.notebook_layout = QVBoxLayout(self.notebook_container)
        self.notebook_layout.setContentsMargins(10, 10, 10, 10)
        self.notebook_layout.setSpacing(10)
        self.notebook_layout.setAlignment(Qt.AlignTop)  # Align widgets to the top
        self.notebook_container.setLayout(self.notebook_layout)
        self.scroll_area.setWidget(self.notebook_container)

        self.scroll_target = None  # Tracks the current target of scrolling
        self.notebook_container.installEventFilter(self)  # Add event filter



        splitter.addWidget(self.scroll_area)
        splitter.setStretchFactor(1, 1)

        self.set_dark_mode()
        self.resize_to_screen()


    def resize_to_screen(self):
        screen_size = QGuiApplication.primaryScreen().availableGeometry()
        self.resize(int(screen_size.width() * 0.8), int(screen_size.height() * 0.8))

    def adjust_scroll_area(self):
        # Adjust the scroll area's size and ensure it scrolls properly
        self.scroll_area.widget().adjustSize()
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())


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
        parent_font = QFont()
        parent_font.setBold(True)

        freq_data = METRICS["frequency_distribution"]
        cat_item = QTreeWidgetItem([freq_data["name"]])
        cat_item.setFont(0, parent_font)
        cat_item.setIcon(0, self.create_arrow_icon("right"))
        self.metric_tree.addTopLevelItem(cat_item)
        cat_item.setExpanded(False)

        for sub_key, sub_data in freq_data["sub_metrics"].items():
            name = "          " + sub_data["name"]
            sub_item = QTreeWidgetItem(cat_item, [name])
            sub_item.setData(0, Qt.UserRole, ("frequency_distribution", sub_key))

        overlap_data = METRICS["overlap_metrics"]
        overlap_item = QTreeWidgetItem([overlap_data["name"]])
        overlap_item.setFont(0, parent_font)
        overlap_item.setIcon(0, self.create_arrow_icon("right"))
        self.metric_tree.addTopLevelItem(overlap_item)
        overlap_item.setExpanded(False)
        for sub_key, sub_data in overlap_data["sub_metrics"].items():
            name = "          " + sub_data["name"]
            sub_item = QTreeWidgetItem(overlap_item, [name])
            sub_item.setData(0, Qt.UserRole, ("overlap_metrics", sub_key))


    def on_item_clicked(self, item, column):
        # Handle single click to expand/collapse categories or highlight sub-metrics
        if item.childCount() > 0:  # Parent item
            if item.isExpanded():
                item.setExpanded(False)
                item.setIcon(0, self.create_arrow_icon("right"))
            else:
                item.setExpanded(True)
                item.setIcon(0, self.create_arrow_icon("down"))
        else:  # Child item (sub-metric)
            self.metric_tree.setCurrentItem(item)  # Highlight the selected item

    def on_item_double_clicked(self, item, column):
        # Add a metric to the notebook when double-clicking a sub-metric
        if item.childCount() == 0:  # Child item (sub-metric)
            self.controller.add_selected_metric()

    def add_highlighted_metric(self):
        selected_item = self.metric_tree.currentItem()
        if selected_item and selected_item.childCount() == 0:  # Ensure a sub-metric is selected
            self.controller.add_selected_metric()

    def get_selected_metric_keys(self):
        selected_items = self.metric_tree.selectedItems()
        if not selected_items:
            return None, None
        item = selected_items[0]
        data = item.data(0, Qt.UserRole)
        if data is None:
            return None, None
        category_key, sub_key = data
        if sub_key is None:
            return None, None
        return category_key, sub_key

    def add_cell(self, metric_name, content_widget):
        cell = CollapsibleCellWidget(metric_name)
        cell.add_content_widget(content_widget)
        self.notebook_layout.addWidget(cell)
        self.notebook_container.adjustSize()
        self.adjust_scroll_area()
        return cell

        # Add this section below the add_cell method
    def move_cell_up(self, cell):
        """Moves the specified cell up in the notebook layout."""
        layout = self.notebook_layout
        index = layout.indexOf(cell)
        if index > 0:  # Ensure we are not already at the top
            layout.removeWidget(cell)
            layout.insertWidget(index - 1, cell)
            layout.update()

    def move_cell_down(self, cell):
        """Moves the specified cell down in the notebook layout."""
        layout = self.notebook_layout
        index = layout.indexOf(cell)
        if index < layout.count() - 1:  # Ensure we are not already at the bottom
            layout.removeWidget(cell)
            layout.insertWidget(index + 1, cell)
            layout.update()

    def insert_cell_below(self, original_cell, new_cell_title, new_content_widget):
        """
        Inserts a new cell directly below the specified original cell.
        """
        new_cell = CollapsibleCellWidget(new_cell_title)
        new_cell.add_content_widget(new_content_widget)

        # Find the position of the original cell
        layout = self.notebook_layout
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget == original_cell:
                # Insert the new cell directly after the original cell
                layout.insertWidget(i + 1, new_cell)
                break

        # Adjust the scroll area and geometry
        self.notebook_container.adjustSize()
        self.adjust_scroll_area()

        # Return the newly created cell for further customization if needed
        return new_cell

    def get_cell_by_name(self, metric_name):
        """Find and return the cell widget with the given title."""
        for i in range(self.notebook_layout.count()):
            widget = self.notebook_layout.itemAt(i).widget()
            if widget and getattr(widget, "title", None) == metric_name:
                return widget
        return None


    def remove_cell_by_name(self, metric_name):
        """Removes a cell by its title."""
        layout = self.notebook_layout
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget and hasattr(widget, "title") and widget.title == metric_name:
                widget.setParent(None)
                widget.deleteLater()
                break
    
    def notebook_scroll_filter(self, obj, event):
        """
        Intercept scroll events and route them based on the initial focus.
        """
        if event.type() == QEvent.Wheel and isinstance(event, QWheelEvent):
            target_widget = QGuiApplication.widgetAt(event.globalPos())
            
            if target_widget:
                # Check if the event is inside the notebook container or a specific cell
                if target_widget is self.notebook_container or target_widget.parentWidget() is self.notebook_container:
                    # Scroll notebook
                    return False  # Allow default notebook scrolling
                elif isinstance(target_widget, QTableWidget):
                    # Forward the scroll to the table (bypass default handling)
                    target_widget.wheelEvent(event)
                    return True
                elif isinstance(target_widget, QScrollArea):
                    # Handle scroll areas specifically if needed
                    target_widget.wheelEvent(event)
                    return True

            # Default behavior for unknown widgets
            return False

        return super().eventFilter(obj, event)

    def install_scroll_filter(self):
        self.notebook_container.installEventFilter(self)
    
    def child_at_cursor(self, global_pos):
        """Finds the child widget under the cursor at the start of the scroll."""
        widget = QGuiApplication.widgetAt(global_pos)
        while widget and widget.parent() != self.notebook_container:
            widget = widget.parent()
        return widget

    def map_to_local_event(self, global_event, target_widget):
        """Maps a global wheel event to the target widget's local coordinates."""
        pos = target_widget.mapFromGlobal(global_event.globalPos())
        return QWheelEvent(
            pos,
            global_event.angleDelta(),
            global_event.buttons(),
            global_event.modifiers(),
            global_event.phase(),
            global_event.inverted(),
        )
    
    def preserve_scroll_position(self):
        """
        Capture the current vertical scroll position of the notebook container.
        """
        scroll_bar = self.scroll_area.verticalScrollBar()
        return scroll_bar.value()

    def restore_scroll_position(self, position):
        """
        Restore the vertical scroll position of the notebook container.
        """
        scroll_bar = self.scroll_area.verticalScrollBar()
        scroll_bar.setValue(position)
