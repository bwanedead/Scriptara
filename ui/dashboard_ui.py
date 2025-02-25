# dashboard_ui.py

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QTreeWidget, QTreeWidgetItem, QPushButton, QLabel, QMenuBar, 
    QMenu, QAction, QFrame, QTableWidget, QTableWidgetItem, QSizePolicy, QToolButton, QSizeGrip, QHeaderView, 
    QSplitter, QInputDialog, QDialog, QMessageBox
)
from PyQt5.QtGui import QGuiApplication, QFont, QPixmap, QPainter, QBrush, QPen, QIcon, QColor, QWheelEvent
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QEvent, QRect
from ui.styles import dark_mode_stylesheet, light_mode_stylesheet, dim_mode_stylesheet
from config.metric_registry import METRICS, get_metric
from visualizations.cell_factory import create_cell
import os





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
        if event.type() == QEvent.MouseMove:
            cursor_pos = self.mapFromGlobal(event.globalPos())

            # Change cursor to resize indicator when hovering near the bottom edge
            if self.height() - self.resize_margin <= cursor_pos.y() <= self.height():
                self.setCursor(Qt.SizeVerCursor)
            else:
                self.unsetCursor()

            # Handle resizing if active
            if self.is_resizing:
                delta_y = event.globalPos().y() - self.drag_start_pos.y()
                new_height = max(60, self.initial_height + delta_y)  # Minimum height is 60

                # Apply the new height
                self.resize_cell(new_height)

                return True  # Intercept the event during resizing

        elif event.type() == QEvent.MouseButtonPress:
            cursor_pos = self.mapFromGlobal(event.globalPos())

            # Start resizing if clicking near the bottom edge
            if self.height() - self.resize_margin <= cursor_pos.y() <= self.height():
                self.drag_start_pos = event.globalPos()
                self.initial_height = self.height()
                self.is_resizing = True
                return True  # Intercept the event for resizing

        elif event.type() == QEvent.MouseButtonRelease:
            if self.is_resizing:
                # End resizing
                self.drag_start_pos = None
                self.is_resizing = False
                self.unsetCursor()
                return True  # Intercept the event for resizing

        # Pass all other events to the default implementation
        return super().eventFilter(obj, event)






    def perform_resize(self, global_mouse_pos):
        """
        Adjust the cell's height dynamically based on mouse movement.
        """
        if self.drag_start_pos:
            # Calculate the difference in vertical mouse movement
            diff = global_mouse_pos.y() - self.drag_start_pos.y()

            # Calculate the new height while enforcing a minimum size
            new_height = max(100, self.height() + diff)  # Minimum height is 100px
            self.resize_cell(new_height)

            # Update the starting position for the next move
            self.drag_start_pos = global_mouse_pos

    
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

        # Left panel with Corpora Viewer section
        left_panel = QWidget()
        left_panel.setObjectName("PanelArea")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(5)

        # Corpora Viewer Section
        self.corpora_viewer_container = QWidget()
        corpora_viewer_main_layout = QVBoxLayout(self.corpora_viewer_container)
        corpora_viewer_main_layout.setContentsMargins(0, 0, 0, 0)
        corpora_viewer_main_layout.setSpacing(0)

        # Header: fixed height with title, add button, and toggle button
        self.corpora_viewer_header = QWidget()
        header_layout = QHBoxLayout(self.corpora_viewer_header)
        header_layout.setContentsMargins(10, 5, 10, 5)
        header_layout.setSpacing(5)
        
        # Title with count
        self.corpora_title_label = QLabel("Corpora (0)")
        self.corpora_title_label.setObjectName("SidePanelSubTitle")
        self.corpora_title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(self.corpora_title_label)
        header_layout.addStretch()
        
        # Add corpus button (plus sign)
        self.add_corpus_button = QToolButton()
        self.add_corpus_button.setText("+")
        self.add_corpus_button.setToolTip("Add Corpus")
        self.add_corpus_button.setStyleSheet("""
            QToolButton {
                border: none;
                color: #888888;
                padding: 2px;
            }
            QToolButton:hover {
                color: #ffffff;
            }
        """)
        header_layout.addWidget(self.add_corpus_button)
        
        # Toggle button
        self.toggle_corpora_button = QToolButton()
        self.toggle_corpora_button.setText("▶")
        self.toggle_corpora_button.setToolTip("Expand Corpora Viewer")
        self.toggle_corpora_button.setStyleSheet("""
            QToolButton {
                border: none;
                color: #888888;
                padding: 2px;
            }
            QToolButton:hover {
                color: #ffffff;
            }
        """)
        header_layout.addWidget(self.toggle_corpora_button)
        
        # Make header fixed vertically
        self.corpora_viewer_header.setSizePolicy(
            QSizePolicy.Preferred, 
            QSizePolicy.Fixed
        )
        
        corpora_viewer_main_layout.addWidget(self.corpora_viewer_header)

        # Expandable tree container
        self.corpora_tree_container = QWidget()
        tree_layout = QVBoxLayout(self.corpora_tree_container)
        tree_layout.setContentsMargins(10, 0, 10, 0)
        tree_layout.setSpacing(0)
        
        self.corpora_tree = QTreeWidget()
        self.corpora_tree.setHeaderHidden(True)
        self.corpora_tree.setIndentation(15)
        self.corpora_tree.setStyleSheet("""
            QTreeWidget {
                background-color: transparent;
                border: none;
            }
            QTreeWidget::item {
                padding: 4px;
            }
            QTreeWidget::item:hover {
                background-color: #3a3a3a;
            }
        """)
        tree_layout.addWidget(self.corpora_tree)
        
        # Initially collapsed
        self.corpora_tree_container.setVisible(False)
        corpora_viewer_main_layout.addWidget(self.corpora_tree_container)
        
        left_layout.addWidget(self.corpora_viewer_container)

        # Connect signals
        self.add_corpus_button.clicked.connect(self.on_add_corpus)
        self.toggle_corpora_button.clicked.connect(self.toggle_corpora_viewer)
        self.corpora_tree.itemClicked.connect(self.on_corpus_item_clicked)

        # Add existing metrics panel section
        metrics_title_label = QLabel("Metrics Panel")
        metrics_title_label.setObjectName("SidePanelTitle")
        metrics_title_label.setAlignment(Qt.AlignLeft)
        metrics_title_label.setContentsMargins(10, 0, 0, 5)
        left_layout.addWidget(metrics_title_label)

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
        
        # Ensure we have access to the main controller's corpora
        if hasattr(self.controller, 'main_controller'):
            self.main_controller = self.controller.main_controller
            self.populate_corpora_tree()  # Initial population


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

        for category_key, category_data in METRICS.items():
            # Create a top-level category item
            cat_item = QTreeWidgetItem([category_data["name"]])
            cat_item.setFont(0, parent_font)
            self.metric_tree.addTopLevelItem(cat_item)

            for sub_key, sub_data in category_data.get("sub_metrics", {}).items():
                # Create sub-metric item
                sub_item = QTreeWidgetItem(cat_item, [sub_data["name"]])
                sub_item.setData(0, Qt.UserRole, (category_key, sub_key, None))

                # Check for nested sub-metrics (e.g., bo_score's sub-metrics)
                for sub_sub_key, sub_sub_data in sub_data.get("sub_metrics", {}).items():
                    sub_sub_item = QTreeWidgetItem(sub_item, [sub_sub_data["name"]])
                    sub_sub_item.setData(0, Qt.UserRole, (category_key, sub_key, sub_sub_key))


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
            return None, None, None
        item = selected_items[0]
        data = item.data(0, Qt.UserRole)
        if not data:
            return None, None, None
        # Return 3-tuple: (category_key, sub_key, sub_sub_key)
        return data  # Already structured as (category_key, sub_key, sub_sub_key)



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

    def toggle_corpora_viewer(self):
        """Toggle the visibility of the corpora tree container."""
        if self.corpora_tree_container.isVisible():
            self.corpora_tree_container.setVisible(False)
            self.toggle_corpora_button.setText("▶")
            self.toggle_corpora_button.setToolTip("Expand Corpora Viewer")
        else:
            self.corpora_tree_container.setVisible(True)
            self.toggle_corpora_button.setText("▼")
            self.toggle_corpora_button.setToolTip("Collapse Corpora Viewer")

    def populate_corpora_tree(self):
        """
        Populate the corpora tree with available corpora and their files.
        Each corpus shows its file count and contained files when expanded.
        """
        self.corpora_tree.clear()
        
        if hasattr(self, 'main_controller') and hasattr(self.main_controller, 'corpora'):
            corpora = self.main_controller.corpora
            total_count = len(corpora)
            self.corpora_title_label.setText(f"Corpora ({total_count})")
            
            for corpus_name, corpus in corpora.items():
                # Create corpus header widget
                header_widget = QWidget()
                header_layout = QHBoxLayout(header_widget)
                header_layout.setContentsMargins(5, 2, 5, 2)
                
                # Get file count
                files = corpus.get_files() if hasattr(corpus, 'get_files') else []
                file_count = len(files)
                
                # Corpus name and count
                name_label = QLabel(f"{corpus_name} ({file_count})")
                header_layout.addWidget(name_label)
                header_layout.addStretch()
                
                # Management buttons
                manage_btn = QToolButton()
                manage_btn.setText("⚙")  # Gear icon
                manage_btn.setToolTip("Manage Files")
                manage_btn.clicked.connect(lambda _, c=corpus_name: self.manage_corpus_files(c))
                
                remove_btn = QToolButton()
                remove_btn.setText("−")  # Minus sign
                remove_btn.setToolTip("Remove Corpus")
                remove_btn.clicked.connect(lambda _, c=corpus_name: self.remove_corpus(c))
                
                header_layout.addWidget(manage_btn)
                header_layout.addWidget(remove_btn)
                
                # Create corpus item
                corpus_item = QTreeWidgetItem()
                corpus_item.setFlags(corpus_item.flags() | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.corpora_tree.addTopLevelItem(corpus_item)
                self.corpora_tree.setItemWidget(corpus_item, 0, header_widget)
                
                # Add files as child items
                for file_path in files:
                    file_item = QTreeWidgetItem([os.path.basename(file_path)])
                    file_item.setToolTip(0, file_path)
                    file_item.setForeground(0, QColor("#aaaaaa"))
                    corpus_item.addChild(file_item)
                
                # Add the "Add Files" button as a child item
                add_files_item = QTreeWidgetItem(["+ Add Files"])
                add_files_item.setForeground(0, QColor("#888888"))
                add_files_item.setData(0, Qt.UserRole, "add_files_action")
                corpus_item.addChild(add_files_item)
                
                print(f"Added corpus to tree: {corpus_name} with {file_count} files")

    def manage_corpus_files(self, corpus_name):
        """Open file management dialog for a corpus."""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Manage Files - {corpus_name}")
        dialog.setWindowFlags(Qt.FramelessWindowHint)  # Remove window frame
        dialog.resize(900, 600)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        # Custom title bar
        title_bar = QWidget()
        title_bar.setStyleSheet("background-color: #1e1e1e;")
        title_bar.setFixedHeight(40)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 0, 15, 0)
        
        title_label = QLabel("Select Files to Remove")
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        close_btn = QToolButton()
        close_btn.setText("✕")
        close_btn.setStyleSheet("""
            QToolButton {
                color: #888888;
                border: none;
                font-size: 16px;
                padding: 4px;
            }
            QToolButton:hover {
                color: #ffffff;
                background-color: #c42b1c;
            }
        """)
        close_btn.clicked.connect(dialog.close)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(close_btn)
        
        # Main content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(15, 15, 15, 15)
        
        # File list with selection
        file_list = QTreeWidget()
        file_list.setHeaderHidden(True)  # Hide the header
        file_list.setSelectionMode(QTreeWidget.ExtendedSelection)
        file_list.setStyleSheet("""
            QTreeWidget {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #4a4a4a;
            }
            QTreeWidget::item:hover {
                background-color: #363636;
            }
        """)
        
        # Get files from corpus
        corpus = self.main_controller.corpora[corpus_name]
        for file_path in corpus.get_files():
            item = QTreeWidgetItem([os.path.basename(file_path)])
            item.setToolTip(0, file_path)
            file_list.addTopLevelItem(item)
        
        content_layout.addWidget(file_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        remove_btn = QPushButton("Remove Selected")
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_selected_files(corpus_name, file_list, dialog))
        
        cancel_btn = QPushButton("Close")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        cancel_btn.clicked.connect(dialog.close)
        
        button_layout.addWidget(remove_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        content_layout.addLayout(button_layout)
        
        # Add all components to main layout
        layout.addWidget(title_bar)
        layout.addWidget(content)
        
        # Make window draggable from title bar
        def mousePressEvent(event):
            if event.button() == Qt.LeftButton:
                dialog._drag_pos = event.globalPos() - dialog.pos()
                event.accept()

        def mouseMoveEvent(event):
            if event.buttons() & Qt.LeftButton:
                dialog.move(event.globalPos() - dialog._drag_pos)
                event.accept()

        title_bar.mousePressEvent = mousePressEvent
        title_bar.mouseMoveEvent = mouseMoveEvent
        
        dialog.exec_()

    def remove_selected_files(self, corpus_name, file_list, dialog):
        """Remove selected files from corpus after confirmation."""
        selected_items = file_list.selectedItems()
        if not selected_items:
            return
        
        selected_files = [item.toolTip(0) for item in selected_items]
        
        if selected_files:
            reply = QMessageBox.question(
                self,
                "Remove Files",
                f"Remove {len(selected_files)} files from {corpus_name}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                corpus = self.main_controller.corpora[corpus_name]
                for file_path in selected_files:
                    corpus.remove_file(file_path)
                
                # Add this code to re-run analysis if modifying the active corpus
                if hasattr(self.main_controller, 'active_corpus') and \
                   self.main_controller.active_corpus and \
                   self.main_controller.active_corpus.name == corpus_name:
                    # Re-run analysis to update reports with the modified corpus
                    print(f"[DEBUG] Running analysis after removing files from active corpus")
                    self.main_controller.run_analysis()
                
                self.populate_corpora_tree()
                dialog.close()

    def remove_corpus(self, corpus_name):
        """Remove entire corpus after confirmation."""
        reply = QMessageBox.question(
            self,
            "Remove Corpus",
            f"Remove entire corpus '{corpus_name}'?\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if hasattr(self.main_controller, 'remove_corpus'):
                self.main_controller.remove_corpus(corpus_name)
                self.populate_corpora_tree()

    def on_corpus_item_clicked(self, item, column):
        """Handle clicks on corpus items."""
        if not item.parent():  # Top-level item (corpus)
            # Toggle expansion state
            item.setExpanded(not item.isExpanded())
            
            # Get corpus name from header widget
            header_widget = self.corpora_tree.itemWidget(item, 0)
            if header_widget:
                name_label = header_widget.findChild(QLabel)
                if name_label:
                    corpus_name = name_label.text().split(" (")[0]
                    if hasattr(self.main_controller, 'set_active_corpus'):
                        self.main_controller.set_active_corpus(corpus_name)
                        print(f"Selected corpus: {corpus_name}")
        else:  # Child item
            if item.data(0, Qt.UserRole) == "add_files_action":
                corpus_name = item.parent().text(0).split(" (")[0]
                if hasattr(self.main_controller, 'add_files_to_corpus'):
                    self.main_controller.add_files_to_corpus(corpus_name)
                    self.populate_corpora_tree()

    def on_add_corpus(self):
        """Handle adding a new corpus."""
        new_corpus_name, ok = QInputDialog.getText(self, "Add Corpus", "Enter name for new corpus:")
        if ok and new_corpus_name:
            if hasattr(self, 'main_controller'):
                self.main_controller.add_corpus(new_corpus_name)
                self.populate_corpora_tree()  # Refresh the tree
                print(f"Added new corpus: {new_corpus_name}")
            else:
                print("Error: No main_controller available")
