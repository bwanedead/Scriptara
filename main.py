import sys
import logging
from PyQt5.QtWidgets import QApplication
from ui.interface import MainWindow
from controller.main_controller import MainController

# Set logging to display debug messages
logging.basicConfig(level=logging.DEBUG)

def main():
    try:
        logging.info("Starting application...")
        app = QApplication(sys.argv)

        window = MainWindow()
        controller = MainController(window)

        window.show()
        logging.info("Application is running.")
        
        sys.exit(app.exec_())

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
