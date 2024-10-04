

from ui.dashboard_ui import DashboardWindow

class DashboardController:
    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.view = DashboardWindow(self)

    def show(self):
        self.view.show()

    @property
    def imported_files(self):
        return self.main_controller.imported_files

    @property
    def word_frequencies(self):
        return self.main_controller.word_frequencies
