# styles.py

dark_mode_stylesheet = """
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
        font-size: 14px;
        font-family: Arial;
    }

    QMainWindow {
        background-color: #2b2b2b;
        border: none;
    }

    QMenuBar {
        background-color: #2b2b2b; 
        border: none;
        padding: 0px;
        margin: 0px;
    }
    QMenuBar::item:selected {
        background: transparent;
    }
    QMenuBar::item:focus {
        outline: none;
        border: none;
    }

    #PanelArea {
        background-color: #333333;
        border: none;
        margin-right: 0px;
        padding: 0px;
    }

    #SidePanelTitle {
        font-size: 16px; 
        font-weight: bold;
        color: #ffffff;
        padding-left: 10px;
        margin-bottom: 5px;
        background: transparent;
        border: none;
    }

    #NotebookArea {
        background-color: #3b3b3b;
        border: none;
        padding: 10px;
    }

    QScrollArea, QScrollArea > QWidget, QScrollArea > QViewport {
        background-color: #3b3b3b;
        border: none;
    }

    #MetricCell {
        background-color: #2f2f2f;
        border: 2px solid #555555;
        border-radius: 8px;
        padding: 10px;
    }

    QPushButton {
        background-color: #555555;
        color: white;
        border: 2px solid #3e3e3e;
        border-radius: 5px;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #777777;
    }
    QPushButton:pressed {
        background-color: #555555;
    }
    QPushButton:focus {
        outline: none;
        border: none;
    }

    QLabel:focus, QTreeWidget:focus, QTreeWidget::item:focus, QTreeView:focus {
        outline: none;
        border: none;
    }

    QTreeWidget {
        background-color: #333333;
        border: none;
    }

    QTreeWidget::item {
        border-radius: 4px;
        padding: 4px;
        margin: 2px;
        background-clip: padding;
    }

    QTreeWidget::item:selected {
        background: #444444; 
        border: none; 
    }
    QTreeWidget::item:selected:focus {
        outline: none;
        border: none;
    }

    QTreeView::branch {
        background-clip: padding;
        border-radius: 4px;
        margin: 2px;
    }

    QTreeView::branch:closed:has-children {
        background: none; 
        image: url(images/arrow-right.png);
    }

    QTreeView::branch:open:has-children {
        background: none; 
        image: url(images/arrow-down.png);
    }

    /* Remove splitter handle line ("nub") */
    QSplitter::handle {
        background: none;
        border: none;
    }
    QSplitter::handle:horizontal {
        width: 1px;
        background: none;
    }
    QSplitter::handle:vertical {
        height: 1px;
        background: none;
    }
"""

sleek_scrollbar_style = """
QScrollBar:vertical {
    border: none;
    background: #2b2b2b; /* Background color of scrollbar track */
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #555555; /* Color of the scrollbar handle */
    border-radius: 5px; /* Rounded edges */
    min-height: 20px; /* Minimum handle height */
}

QScrollBar::handle:vertical:hover {
    background: #777777; /* Hover color */
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px; /* Hide up/down arrows */
    width: 0px; /* Hide up/down arrows */
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none; /* Transparent for the remaining track */
}
"""

dark_mode_stylesheet += sleek_scrollbar_style

light_mode_stylesheet = """
    QWidget {
        background-color: #f0f0f0;
        color: #000000;
        font-size: 14px;
        font-family: Arial;
    }

    QMainWindow {
        background-color: #f0f0f0;
        border: none;
    }

    QMenuBar {
        background-color: #f0f0f0; 
        border: none;
        padding: 0px;
        margin: 0px;
    }
    QMenuBar::item:selected {
        background: transparent;
    }
    QMenuBar::item:focus {
        outline: none;
        border: none;
    }

    #PanelArea {
        background-color: #e6e6e6;
        border: none;
        margin-right: 0px;
        padding: 0px;
    }

    #SidePanelTitle {
        font-size: 16px;
        font-weight: bold;
        color: #000000;
        padding-left: 10px;
        margin-bottom: 5px;
        background: transparent;
        border: none;
    }

    #NotebookArea {
        background-color: #ffffff;
        border: none;
        padding: 10px;
    }

    QScrollArea, QScrollArea > QWidget, QScrollArea > QViewport {
        background-color: #ffffff;
        border: none;
    }

    #MetricCell {
        background-color: #dddddd;
        border: 1px solid #cccccc;
        border-radius: 8px;
        padding: 10px;
    }

    QPushButton {
        background-color: #e0e0e0;
        color: black;
        border: 2px solid #cccccc;
        border-radius: 5px;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #d0d0d0;
    }
    QPushButton:pressed {
        background-color: #b0b0b0;
    }
    QPushButton:focus {
        outline: none;
        border: none;
    }

    QLabel:focus, QTreeWidget:focus, QTreeWidget::item:focus, QTreeView:focus {
        outline: none;
        border: none;
    }

    QTreeWidget {
        background-color: #ffffff;
        border: none;
    }

    QTreeWidget::item {
        border-radius: 4px;
        padding: 4px;
        margin: 2px;
        background-clip: padding;
    }

    QTreeWidget::item:selected {
        background: #d0d0d0;
        border: none;
    }
    QTreeWidget::item:selected:focus {
        outline: none;
        border: none;
    }

    QTreeView::branch {
        background-clip: padding;
        border-radius: 4px;
        margin: 2px;
    }

    QTreeView::branch:closed:has-children {
        background: none;
        image: url(images/arrow-right.png);
    }

    QTreeView::branch:open:has-children {
        background: none;
        image: url(images/arrow-down.png);
    }

    QSplitter::handle {
        background: none;
        border: none;
    }
    QSplitter::handle:horizontal {
        width: 1px;
        background: none;
    }
    QSplitter::handle:vertical {
        height: 1px;
        background: none;
    }
"""

light_scrollbar_style = """
QScrollBar:vertical {
    border: none;
    background: #f0f0f0; /* Background color of scrollbar track */
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #cccccc; /* Color of the scrollbar handle */
    border-radius: 5px; /* Rounded edges */
    min-height: 20px; /* Minimum handle height */
}

QScrollBar::handle:vertical:hover {
    background: #aaaaaa; /* Hover color */
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px; /* Hide up/down arrows */
    width: 0px; /* Hide up/down arrows */
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none; /* Transparent for the remaining track */
}
"""

light_mode_stylesheet += light_scrollbar_style

dim_mode_stylesheet = """
    QWidget {
        background-color: #4b4b4b;
        color: #e0e0e0;
        font-size: 14px;
        font-family: Arial;
    }

    QMainWindow {
        background-color: #4b4b4b;
        border: none;
    }

    QMenuBar {
        background-color: #4b4b4b; 
        border: none;
        padding: 0px;
        margin: 0px;
    }
    QMenuBar::item:selected {
        background: transparent;
    }
    QMenuBar::item:focus {
        outline: none;
        border: none;
    }

    #PanelArea {
        background-color: #565656;
        border: none;
        margin-right: 0px;
        padding: 0px;
    }

    #SidePanelTitle {
        font-size: 16px;
        font-weight: bold;
        color: #e0e0e0;
        padding-left: 10px;
        margin-bottom: 5px;
        background: transparent;
        border: none;
    }

    #NotebookArea {
        background-color: #616161;
        border: none;
        padding: 10px;
    }

    QScrollArea, QScrollArea > QWidget, QScrollArea > QViewport {
        background-color: #616161;
        border: none;
    }

    #MetricCell {
        background-color: #505050; 
        border: 1px solid #5a5a5a;
        border-radius: 8px;
        padding: 10px;
    }

    QPushButton {
        background-color: #6b6b6b;
        color: white;
        border: 2px solid #5e5e5e;
        border-radius: 5px;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #7b7b7b;
    }
    QPushButton:pressed {
        background-color: #5b5b5b;
    }
    QPushButton:focus {
        outline: none;
        border: none;
    }

    QLabel:focus, QTreeWidget:focus, QTreeWidget::item:focus, QTreeView:focus {
        outline: none;
        border: none;
    }

    QTreeWidget {
        background-color: #585858;
        border: none;
    }

    QTreeWidget::item {
        border-radius: 4px;
        padding: 4px;
        margin: 2px;
        background-clip: padding;
    }

    QTreeWidget::item:selected {
        background: #6e6e6e;
        border: none;
    }
    QTreeWidget::item:selected:focus {
        outline: none;
        border: none;
    }

    QTreeView::branch {
        background-clip: padding;
        border-radius: 4px;
        margin: 2px;
    }

    QTreeView::branch:closed:has-children {
        background: none;
        image: url(images/arrow-right.png);
    }

    QTreeView::branch:open:has-children {
        background: none;
        image: url(images/arrow-down.png);
    }

    QSplitter::handle {
        background: none;
        border: none;
    }
    QSplitter::handle:horizontal {
        width: 1px;
        background: none;
    }
    QSplitter::handle:vertical {
        height: 1px;
        background: none;
    }
"""

dim_scrollbar_style = """
QScrollBar:vertical {
    border: none;
    background: #4b4b4b; /* Background color of scrollbar track */
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #6b6b6b; /* Color of the scrollbar handle */
    border-radius: 5px; /* Rounded edges */
    min-height: 20px; /* Minimum handle height */
}

QScrollBar::handle:vertical:hover {
    background: #7b7b7b; /* Hover color */
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px; /* Hide up/down arrows */
    width: 0px; /* Hide up/down arrows */
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none; /* Transparent for the remaining track */
}
"""

dim_mode_stylesheet += dim_scrollbar_style