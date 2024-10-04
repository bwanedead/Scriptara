# styles.py

dark_mode_stylesheet = """
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
        font-size: 14px;
        font-family: Arial;
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
    QListWidget {
        background-color: #333333;
        border: 1px solid #3e3e3e;
    }
    QMenuBar {
        background-color: #3e3e3e;
        color: white;
    }
    QMenuBar::item:selected {
        background-color: #555555;
    }
"""

light_mode_stylesheet = """
    QWidget {
        background-color: #f0f0f0;
        color: #000000;
        font-size: 14px;
        font-family: Arial;
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
    QListWidget {
        background-color: #ffffff;
        border: 1px solid #cccccc;
    }
    QMenuBar {
        background-color: #ffffff;
        color: black;
    }
    QMenuBar::item:selected {
        background-color: #cccccc;
    }
"""

