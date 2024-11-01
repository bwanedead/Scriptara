

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

    @property
    def percentage_frequencies(self):
        return self.main_controller.percentage_frequencies

    @property
    def z_scores(self):
        return self.main_controller.z_scores
    
    @property
    def file_reports(self):
        # Pass the file reports from the MainController
        return self.main_controller.file_reports
