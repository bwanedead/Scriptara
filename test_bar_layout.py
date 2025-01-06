import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QToolButton
from pyqtgraph import PlotWidget, BarGraphItem
from PyQt5.QtCore import Qt

class DummyVisualization:
    def get_data(self):
        # Mock data for testing
        return (
            [(f"Item {i}", i) for i in range(1, 11)],  # BOn1 data
            [(f"Item {i}", i * 2) for i in range(1, 11)]  # BOn2 data
        )

class BOScoreBarLayout:
    """
    A simplified version of your BOScoreBarLayout for testing.
    """
    def __init__(self, vis):
        self.vis = vis
        self.plot_widget = None
        self.show_bon1 = True
        self.show_bon2 = False

    def generate_layout(self):
        layout_widget = QWidget()
        layout = QVBoxLayout(layout_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Title
        title_label = QLabel("BO Score Bar Chart")
        title_label.setStyleSheet("color: #fff; font-size:16px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Controls for toggling visibility
        controls_layout = QHBoxLayout()

        # Toggle BOn1 button
        bon1_btn = QToolButton()
        bon1_btn.setText("Toggle BOn1")
        bon1_btn.setCheckable(True)
        bon1_btn.setChecked(self.show_bon1)
        bon1_btn.toggled.connect(self.on_bon1_toggle)
        controls_layout.addWidget(bon1_btn)

        # Toggle BOn2 button
        bon2_btn = QToolButton()
        bon2_btn.setText("Toggle BOn2")
        bon2_btn.setCheckable(True)
        bon2_btn.setChecked(self.show_bon2)
        bon2_btn.toggled.connect(self.on_bon2_toggle)
        controls_layout.addWidget(bon2_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Create the PlotWidget
        self.plot_widget = PlotWidget()
        self.plot_widget.setBackground('k')
        self.plot_widget.getPlotItem().setLabel("bottom", "Rank")
        self.plot_widget.getPlotItem().setLabel("left", "BO Score")
        layout.addWidget(self.plot_widget)

        # Draw bars initially
        self.update_plot()

        return layout_widget

    def update_plot(self):
        print(f"[DEBUG] update_plot called. show_bon1={self.show_bon1}, show_bon2={self.show_bon2}")
        bon1_data, bon2_data = self.vis.get_data()

        self.plot_widget.clear()
        plot_item = self.plot_widget.getPlotItem()

        # Plot BOn1 bars in red if enabled
        if self.show_bon1 and bon1_data:
            x_vals = [i + 1 for i in range(len(bon1_data))]
            y_vals = [score for (_, score) in bon1_data]
            bar_item = BarGraphItem(x=x_vals, height=y_vals, width=0.3, brush='r')
            plot_item.addItem(bar_item)

        # Plot BOn2 bars in green if enabled
        if self.show_bon2 and bon2_data:
            x_vals2 = [i + 1 + 0.4 for i in range(len(bon2_data))]
            y_vals2 = [score for (_, score) in bon2_data]
            bar_item2 = BarGraphItem(x=x_vals2, height=y_vals2, width=0.3, brush='g')
            plot_item.addItem(bar_item2)

    def on_bon1_toggle(self, checked):
        print(f"[DEBUG] on_bon1_toggle called with checked={checked}")
        self.show_bon1 = checked
        self.update_plot()

    def on_bon2_toggle(self, checked):
        print(f"[DEBUG] on_bon2_toggle called with checked={checked}")
        self.show_bon2 = checked
        self.update_plot()

# Test the bar layout standalone
def test_boscore_bar_layout():
    app = QApplication(sys.argv)

    vis = DummyVisualization()
    layout_obj = BOScoreBarLayout(vis)
    layout_widget = layout_obj.generate_layout()

    window = QMainWindow()
    window.setCentralWidget(layout_widget)
    window.resize(800, 600)
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    test_boscore_bar_layout()
