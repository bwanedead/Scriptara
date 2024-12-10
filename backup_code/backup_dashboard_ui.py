# # dashboard_ui.py

# import os
# import logging
# import pandas as pd
# from PyQt5.QtWidgets import (
#     QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QFrame, QRadioButton, QButtonGroup, QCheckBox,
#     QTableWidget, QTabWidget, QTableWidget, QTableWidgetItem, 
# )
# from PyQt5.QtCore import Qt, pyqtSignal
# from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
# from matplotlib.figure import Figure


# class CheckableComboBox(QComboBox):
#     selection_changed = pyqtSignal()
    
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         # Use a standard item model to hold the items
#         self.setModel(QStandardItemModel(self))
#         # Connect the view's pressed signal to handle item selection
#         self.view().pressed.connect(self.handle_item_pressed)
#         # Make the combo box editable to display custom text
#         self.setEditable(True)
#         # Set the line edit to be read-only
#         self.lineEdit().setReadOnly(True)
#         # Placeholder text when no files are selected
#         self.lineEdit().setPlaceholderText('Select Files...')
#         # List to keep track of checked items
#         self.checked_items = []
#         # Tooltip to display selected files
#         self.setToolTip('')
#         # Dictionary to store colors for each item
#         self.colors = {}
    
#     def addItem(self, text, data=None):
#         # Create a standard item
#         item = QStandardItem(text)
#         # Set the item to be enabled and checkable
#         item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
#         # Initialize the check state to checked (all files selected by default)
#         item.setData(Qt.Checked, Qt.CheckStateRole)
#         # Store additional data if provided
#         if data is not None:
#             item.setData(data, Qt.UserRole)
#         # Assign a color to the item
#         color = QColor.fromHsv(len(self.colors) * 36 % 360, 255, 200)
#         self.colors[text] = color
#         item.setData(color, Qt.DecorationRole)  # Set the color decoration
#         # Add the item to the model
#         self.model().appendRow(item)
#         # Add the item to checked items
#         self.checked_items.append(text)
#         # Update the placeholder
#         self.update_placeholder()
    
#     def add_special_items(self):
#         # Add "Select All" option
#         select_all_item = QStandardItem("Select All")
#         select_all_item.setFlags(Qt.ItemIsEnabled)
#         self.model().insertRow(0, select_all_item)
#         # Add "Deselect All" option
#         deselect_all_item = QStandardItem("Deselect All")
#         deselect_all_item.setFlags(Qt.ItemIsEnabled)
#         self.model().insertRow(1, deselect_all_item)
    
#     def handle_item_pressed(self, index):
#         # Get the item that was pressed
#         item = self.model().itemFromIndex(index)
#         if item.text() == "Select All":
#             self.select_all()
#             return
#         elif item.text() == "Deselect All":
#             self.deselect_all()
#             return
#         if item.checkState() == Qt.Checked:
#             item.setCheckState(Qt.Unchecked)
#             # Remove the item from checked items
#             self.checked_items.remove(item.text())
#         else:
#             item.setCheckState(Qt.Checked)
#             # Add the item to checked items
#             self.checked_items.append(item.text())
#         # Update the placeholder and tooltip
#         self.update_placeholder()
#         # Emit signal to update the plot
#         self.selection_changed.emit()
    
#     def update_placeholder(self):
#         selected_count = len(self.checked_items)
#         if selected_count == 0:
#             self.lineEdit().setText('Select Files...')
#             self.setToolTip('')
#         elif selected_count == 1:
#             self.lineEdit().setText(self.checked_items[0])
#             self.setToolTip(self.checked_items[0])
#         else:
#             self.lineEdit().setText(f'{selected_count} files selected')
#             # Set tooltip with the list of selected files
#             self.setToolTip('\n'.join(self.checked_items))
    
#     def get_checked_items(self):
#         # Return the list of checked items
#         return self.checked_items
    
#     def select_all(self):
#         # Clear the list of checked items
#         self.checked_items.clear()
#         for index in range(2, self.model().rowCount()):  # Skip special items
#             item = self.model().item(index)
#             # Set each item's check state to checked
#             item.setCheckState(Qt.Checked)
#             # Add the item to checked items
#             self.checked_items.append(item.text())
#         # Update the placeholder and tooltip
#         self.update_placeholder()
#         # Emit signal to update the plot
#         self.selection_changed.emit()
    
#     def deselect_all(self):
#         for index in range(2, self.model().rowCount()):  # Skip special items
#             item = self.model().item(index)
#             # Set each item's check state to unchecked
#             item.setCheckState(Qt.Unchecked)
#         # Clear the list of checked items
#         self.checked_items.clear()
#         # Update the placeholder and tooltip
#         self.update_placeholder()
#         # Emit signal to update the plot
#         self.selection_changed.emit()

# class DashboardWindow(QMainWindow):
#     def __init__(self, controller):
#         super().__init__()
#         self.controller = controller
#         # Dictionary to keep track of line objects for highlighting
#         self.line_objects = {}
#         # Variables for panning
#         self.panning = False
#         self.pan_start = None
#         self.init_ui()
    
#     def init_ui(self):
#         self.setWindowTitle('Frequency Curves Dashboard')
#         self.setGeometry(150, 150, 1000, 600)

#         # Central widget
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)

#         # Main layout is horizontal to have a sidebar and chart area
#         main_layout = QHBoxLayout(central_widget)

#         # Left sidebar for controls
#         sidebar_layout = QVBoxLayout()
#         sidebar_layout.setContentsMargins(5, 5, 5, 5)
#         sidebar_layout.setSpacing(10)
#         self.sidebar_layout = sidebar_layout  # Store as an instance attribute

#         # Initialize the custom checkable combo box
#         self.combo_box = CheckableComboBox()
#         self.combo_box.add_special_items()  # Add special items ("Select All" and "Deselect All")
#         self.file_list = list(self.controller.imported_files)  # Get the list of imported files from the controller
#         for file in self.file_list:
#             basename = os.path.basename(file)
#             self.combo_box.addItem(basename, data=file)

#         # Connect signals
#         self.combo_box.selection_changed.connect(self.update_plot)
#         self.combo_box.view().entered.connect(self.on_combo_hover)

#         # Add widgets to the sidebar
#         sidebar_layout.addWidget(QLabel("Select Files:"))
#         sidebar_layout.addWidget(self.combo_box)

#         # Add the similarity metric dropdown
#         metric_layout = QVBoxLayout()
#         metric_layout.addWidget(QLabel("Similarity Metric:"))

#         self.metric_combo = QComboBox()
#         metrics = ['Jaccard Index', 'Dice Coefficient', 'Overlap Coefficient',
#                 'Cosine Similarity', 'KL Divergence', 'JS Divergence', 'Bhattacharyya Distance',
#                 'BO Score BOn1', 'BO Score BOn2']
#         self.metric_combo.addItems(metrics)
#         self.metric_combo.currentTextChanged.connect(self.update_similarity_plot)
#         metric_layout.addWidget(self.metric_combo)
#         sidebar_layout.addLayout(metric_layout)

#         # Visualization Type Selection
#         vis_layout = QVBoxLayout()
#         vis_layout.addWidget(QLabel("Visualization Type:"))

#         # Create the radio buttons for selecting the visualization type
#         self.radio_loglog = QRadioButton("Frequency")
#         self.radio_percentage = QRadioButton("Percentage Frequency")
#         self.radio_zscore = QRadioButton("Z-Score")
#         self.radio_loglog.setChecked(True)  # Set Frequency as the default view

#         # Button group to manage radio buttons
#         self.vis_group = QButtonGroup()
#         self.vis_group.addButton(self.radio_loglog)
#         self.vis_group.addButton(self.radio_percentage)
#         self.vis_group.addButton(self.radio_zscore)

#         # Connect radio buttons to the update_plot method
#         self.radio_loglog.toggled.connect(self.update_plot)
#         self.radio_percentage.toggled.connect(self.update_plot)
#         self.radio_zscore.toggled.connect(self.update_plot)

#         # Add the radio buttons to the visualization layout
#         vis_layout.addWidget(self.radio_loglog)
#         vis_layout.addWidget(self.radio_percentage)
#         vis_layout.addWidget(self.radio_zscore)

#         # Axis Scaling Options
#         vis_layout.addWidget(QLabel("Axis Scaling:"))
#         self.checkbox_log_x = QCheckBox("Logarithmic X-Axis")
#         self.checkbox_log_y = QCheckBox("Logarithmic Y-Axis")
#         self.checkbox_log_x.setChecked(False)
#         self.checkbox_log_y.setChecked(False)

#         # Connect checkboxes to the update_plot method
#         self.checkbox_log_x.stateChanged.connect(self.update_plot)
#         self.checkbox_log_y.stateChanged.connect(self.update_plot)

#         vis_layout.addWidget(self.checkbox_log_x)
#         vis_layout.addWidget(self.checkbox_log_y)

#         # Add BO Score Visualization Options
#         vis_type_layout = QVBoxLayout()
#         vis_type_layout.addWidget(QLabel("BO Score Visualization:"))

#         self.bo_vis_bar = QRadioButton("Bar Chart")
#         self.bo_vis_wordcloud = QRadioButton("Word Cloud")
#         self.bo_vis_bar.setChecked(True)

#         # Button group to manage BO Score visualization radio buttons
#         self.bo_vis_group = QButtonGroup()
#         self.bo_vis_group.addButton(self.bo_vis_bar)
#         self.bo_vis_group.addButton(self.bo_vis_wordcloud)

#         # Connect radio buttons to the update_similarity_plot method
#         self.bo_vis_bar.toggled.connect(self.update_similarity_plot)
#         self.bo_vis_wordcloud.toggled.connect(self.update_similarity_plot)

#         vis_type_layout.addWidget(self.bo_vis_bar)
#         vis_type_layout.addWidget(self.bo_vis_wordcloud)

#         # Add visualization layouts to the sidebar
#         sidebar_layout.addLayout(vis_layout)
#         sidebar_layout.addLayout(vis_type_layout)
#         sidebar_layout.addStretch()  # Push everything up

#         # Add a frame to the sidebar for styling (optional)
#         sidebar_frame = QFrame()
#         sidebar_frame.setLayout(sidebar_layout)
#         sidebar_frame.setFrameShape(QFrame.StyledPanel)
#         sidebar_frame.setFixedWidth(250)  # Set the width of the sidebar

#         # Chart area
#         chart_layout = QVBoxLayout()

#         # Create a tab widget to switch between visualization and data table
#         self.tab_widget = QTabWidget()

#         # Visualization tab
#         visualization_widget = QWidget()
#         visualization_layout = QVBoxLayout(visualization_widget)
#         self.similarity_figure = Figure()
#         self.similarity_canvas = FigureCanvas(self.similarity_figure)
#         visualization_layout.addWidget(self.similarity_canvas)
#         visualization_widget.setLayout(visualization_layout)
#         self.tab_widget.addTab(visualization_widget, "Visualization")

#         # Data Table tab
#         data_table_widget = QWidget()
#         data_table_layout = QVBoxLayout(data_table_widget)
#         self.bo_scores_table = QTableWidget()
#         data_table_layout.addWidget(self.bo_scores_table)
#         data_table_widget.setLayout(data_table_layout)
#         self.tab_widget.addTab(data_table_widget, "BO Scores Table")

#         # Add the tab widget to the chart layout
#         chart_layout.addWidget(self.tab_widget)

#         # Add the Matplotlib navigation toolbar
#         self.toolbar = NavigationToolbar(self.similarity_canvas, self)
#         chart_layout.addWidget(self.toolbar)

#         # Add layouts to the main layout
#         main_layout.addWidget(sidebar_frame)
#         main_layout.addLayout(chart_layout)

#         # Initial plot
#         self.update_plot()


#     def update_plot(self):
#         logging.info("Updating the plot with selected files.")

#         # Get the list of selected files
#         selected_files = []
#         for index in range(2, self.combo_box.model().rowCount()):  # Skip special items
#             item = self.combo_box.model().item(index)
#             if item.checkState() == Qt.Checked:
#                 file = self.file_list[index - 2]  # Adjust index for special items
#                 selected_files.append(file)

#         logging.debug(f"Selected files for plotting: {selected_files}")

#         self.figure.clear()
#         ax = self.figure.add_subplot(111)
#         ax.set_xlabel('Rank')
#         ax.set_title('Word Frequency Curves')

#         # Clear previous line references
#         self.line_objects.clear()

#         # Loop through the selected files to plot data
#         for file in selected_files:
#             basename = os.path.basename(file)
#             color = self.combo_box.colors.get(basename, None)
#             line_color = None
#             if color:
#                 rgb = color.getRgbF()
#                 line_color = (rgb[0], rgb[1], rgb[2])

#             logging.debug(f"Processing file: {basename}")

#             # Retrieve the appropriate data based on the selected radio button
#             if self.radio_loglog.isChecked():
#                 y_data = self.controller.word_frequencies.get(file, [])
#                 y_label = 'Frequency'
#             elif self.radio_percentage.isChecked():
#                 y_data = self.controller.percentage_frequencies.get(file, [])
#                 y_label = 'Percentage Frequency'
#             elif self.radio_zscore.isChecked():
#                 y_data = self.controller.z_scores.get(file, [])
#                 y_label = 'Z-Score'
#             else:
#                 logging.warning(f"No valid visualization type selected for {basename}.")
#                 continue  # Skip to the next file

#             logging.debug(f"{basename} - {y_label} data (first 10 points): {y_data[:10]}")

#             # Plot the data if available
#             if y_data:
#                 ranks = range(1, len(y_data) + 1)
#                 line, = ax.plot(ranks, y_data, label=basename, color=line_color)
#                 self.line_objects[basename] = line

#         # Set axis labels
#         ax.set_ylabel(y_label)

#         # Apply axis scaling based on checkbox states
#         if self.checkbox_log_x.isChecked():
#             ax.set_xscale('log')
#         else:
#             ax.set_xscale('linear')

#         if self.checkbox_log_y.isChecked():
#             ax.set_yscale('log')
#         else:
#             ax.set_yscale('linear')

#         # Add grid lines for better readability
#         ax.grid(True, which='both', linestyle='--', linewidth=0.5)

#         # Display a message if no files are selected
#         if not selected_files:
#             logging.warning("No files selected for plotting.")
#             ax.text(0.5, 0.5, 'No files selected', transform=ax.transAxes,
#                     ha='center', va='center')

#         # Redraw the main plot canvas
#         self.canvas.draw()
#         logging.info("Plot updated successfully.")

#         # Update the similarity plot (new addition)
#         self.update_similarity_plot()

#     def update_similarity_plot(self):
#         metric = self.metric_combo.currentText()
#         similarity_results = self.controller.similarity_results.get(metric, {})

#         if not similarity_results:
#             logging.warning(f"No results for metric {metric}")
#             self.similarity_figure.clear()  # Clear the figure if no results are available
#             self.similarity_canvas.draw()
#             return

#         if metric.startswith('BO Score'):
#             # Populate the table with BO Scores
#             self.display_bo_scores_table(similarity_results, metric)
#             # Switch to the Data Table tab
#             self.tab_widget.setCurrentIndex(1)

#             # Handle BO Score visualization type
#             if self.bo_vis_bar.isChecked():
#                 self.plot_bo_scores(similarity_results, metric)  # Bar chart visualization
#             elif self.bo_vis_wordcloud.isChecked():
#                 self.plot_bo_scores_wordcloud(similarity_results, metric)  # Word cloud visualization
#             elif self.bo_vis_scatter.isChecked():  # Added scatter plot logic
#                 self.plot_bo_scores_scatter(similarity_results, metric)  # Scatter plot visualization
#         else:
#             # Prepare data for heatmap for non-BO Score metrics
#             texts = list(self.controller.file_reports.keys())
#             import pandas as pd
#             similarity_matrix = pd.DataFrame(index=texts, columns=texts, dtype=float)

#             for (text1, text2), value in similarity_results.items():
#                 similarity_matrix.at[text1, text2] = value
#                 similarity_matrix.at[text2, text1] = value  # Assuming symmetry

#             # Plot heatmap
#             self.similarity_figure.clear()
#             ax = self.similarity_figure.add_subplot(111)
#             cax = ax.matshow(similarity_matrix.values.astype(float), interpolation='nearest', cmap='viridis')
#             self.similarity_figure.colorbar(cax)

#             # Configure axes
#             ax.set_xticks(range(len(texts)))
#             ax.set_yticks(range(len(texts)))
#             ax.set_xticklabels([os.path.basename(t) for t in texts], rotation=90)
#             ax.set_yticklabels([os.path.basename(t) for t in texts])
#             ax.set_title(f'{metric} Heatmap')

#             # Render the updated plot
#             self.similarity_canvas.draw()
#             self.tab_widget.setCurrentIndex(0)  # Switch to the Visualization tab



#     def display_bo_scores_table(self, bo_scores, metric):
#         # Filter out words with zero BO Scores
#         filtered_bo_scores = {word: score for word, score in bo_scores.items() if score > 0}

#         # Convert the BO Scores to a DataFrame
#         df = pd.DataFrame({
#             'Word': list(filtered_bo_scores.keys()),
#             'BO Score': list(filtered_bo_scores.values())
#         })

#         # Sort the DataFrame
#         df.sort_values(by='BO Score', ascending=False, inplace=True)

#         # Update the table widget
#         self.bo_scores_table.clear()
#         self.bo_scores_table.setRowCount(len(df))
#         self.bo_scores_table.setColumnCount(2)
#         self.bo_scores_table.setHorizontalHeaderLabels(['Word', 'BO Score'])

#         for row, (_, data) in enumerate(df.iterrows()):
#             word_item = QTableWidgetItem(data['Word'])
#             score_item = QTableWidgetItem(f"{data['BO Score']:.4f}")

#             self.bo_scores_table.setItem(row, 0, word_item)
#             self.bo_scores_table.setItem(row, 1, score_item)

#         # Resize columns to fit content
#         self.bo_scores_table.resizeColumnsToContents()

    
    
#     def plot_bo_scores(self, bo_scores, metric):
#         import pandas as pd
#         import logging

#         # Initialize logger
#         logger = logging.getLogger(__name__)
#         logger.setLevel(logging.DEBUG)

#         try:
#             logger.info("Starting to plot BO Scores...")

#             # Convert the BO Scores to a DataFrame
#             df = pd.DataFrame({
#                 'Word': list(bo_scores.keys()),
#                 'BO_Score': list(bo_scores.values())
#             })

#             # Sort the DataFrame by BO Score in descending order
#             df.sort_values(by='BO_Score', ascending=False, inplace=True)
#             logger.debug(f"Total words to display: {len(df)}")

#             # Use the entire DataFrame
#             df_all = df

#             # Adjust the figure size dynamically based on the number of words
#             num_words = len(df_all)
#             figure_height = max(6, num_words * 0.2)  # 0.2 inches per word, minimum height of 6 inches
#             logger.debug(f"Calculated figure height: {figure_height}")

#             # Clear the previous figure and set the new size
#             self.similarity_figure.clear()
#             self.similarity_figure.set_size_inches(8, figure_height)  # Fixed width for better readability
#             ax = self.similarity_figure.add_subplot(111)

#             # Plot bar chart for all words
#             ax.barh(df_all['Word'][::-1], df_all['BO_Score'][::-1], color='skyblue')
#             ax.set_xlabel('BO Score')
#             ax.set_ylabel('Word')
#             ax.set_title(f'All Words by {metric}')
#             logger.info("Bar chart successfully created.")

#             # Dynamically adjust the canvas and ensure the chart fits in the scrollable area
#             self.similarity_canvas.draw()
#             logger.info("Chart successfully rendered on canvas.")

#         except Exception as e:
#             logger.error(f"Error while plotting BO Scores: {e}")
#             raise

#     def plot_bo_scores_scatter(self, bo_scores, metric):
        
#         # Filter out words with zero BO Scores
#         filtered_bo_scores = {word: score for word, score in bo_scores.items() if score > 0}

#         # Convert the BO Scores to a DataFrame
#         df = pd.DataFrame({
#             'Word': list(filtered_bo_scores.keys()),
#             'BO_Score': list(filtered_bo_scores.values())
#         })

#         # Sort the DataFrame by BO Score in descending order
#         df.sort_values(by='BO_Score', ascending=False, inplace=True)
#         df.reset_index(drop=True, inplace=True)
#         df['Rank'] = df.index + 1

#         # Clear the previous figure
#         self.similarity_figure.clear()
#         ax = self.similarity_figure.add_subplot(111)

#         # Plot scatter plot
#         ax.scatter(df['Rank'], df['BO_Score'], s=10, color='blue')
#         ax.set_xlabel('Word Rank')
#         ax.set_ylabel('BO Score')
#         ax.set_title(f'BO Score Distribution ({metric})')

#         # Optionally set logarithmic scales
#         ax.set_xscale('log')
#         ax.set_yscale('log')

#         # Draw the updated canvas
#         self.similarity_canvas.draw()


#     def plot_bo_scores_wordcloud(self, bo_scores, metric):
#         """
#         Plots the BO Scores as a word cloud.

#         Parameters:
#             bo_scores (dict): Dictionary of BO Scores with words as keys and scores as values.
#             metric (str): The selected metric (e.g., "BO Score BOn1").
#         """
#         from wordcloud import WordCloud

#         self.similarity_figure.clear()
#         ax = self.similarity_figure.add_subplot(111)

#         # Create a word cloud
#         wordcloud = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(bo_scores)

#         # Display the word cloud
#         ax.imshow(wordcloud, interpolation="bilinear")
#         ax.axis("off")  # Hide axes
#         ax.set_title(f'Word Cloud for {metric}')
#         self.similarity_canvas.draw()

#     # Event handlers for panning and zooming
#     def on_mouse_press(self, event):
#         ax = event.inaxes
#         if event.button == 1 and ax:
#             xlim = ax.get_xlim()
#             ylim = ax.get_ylim()

#             # Check if the mouse is near the x or y axis
#             mouse_near_x_axis = abs(event.ydata - ylim[0]) < 0.03 * (ylim[1] - ylim[0])
#             mouse_near_y_axis = abs(event.xdata - xlim[0]) < 0.03 * (xlim[1] - xlim[0])

#             if mouse_near_x_axis or mouse_near_y_axis:
#                 self.panning = False  # Disable panning when dragging an axis
#             else:
#                 # Enable panning inside the chart area
#                 self.panning = True
#                 self.pan_start = (event.xdata, event.ydata)
#                 self.xlim_start = ax.get_xlim()
#                 self.ylim_start = ax.get_ylim()


#     def on_mouse_release(self, event):
#         if event.button == 1:
#             self.panning = False
#             self.pan_start = None

#     def on_mouse_move(self, event):
#         ax = event.inaxes
#         if ax is None or event.xdata is None or event.ydata is None:
#             return

#         xlim = ax.get_xlim()
#         ylim = ax.get_ylim()

#         # Define drag zones near the axis (but outside the plot)
#         mouse_near_x_axis = abs(event.y - self.canvas.geometry().height()) < 20  # Near x-axis
#         mouse_near_y_axis = abs(event.x) < 20  # Near y-axis

#         scrub_sensitivity = 0.001  # Adjust sensitivity for finer control

#         # Panning inside the plot
#         if self.panning and event.xdata and event.ydata:
#             dx = self.pan_start[0] - event.xdata
#             dy = self.pan_start[1] - event.ydata
#             ax.set_xlim(self.xlim_start[0] + dx, self.xlim_start[1] + dx)
#             ax.set_ylim(self.ylim_start[0] + dy, self.ylim_start[1] + dy)
#             self.canvas.draw()

#         # Scrubbing the x-axis only
#         elif mouse_near_x_axis and event.button == 1:
#             dx = (event.xdata - self.pan_start[0]) * scrub_sensitivity
#             new_xlim = [max(0, xlim[0] + dx), max(0, xlim[1] + dx)]
#             ax.set_xlim(new_xlim)
#             self.canvas.draw()

#         # Scrubbing the y-axis only
#         elif mouse_near_y_axis and event.button == 1:
#             dy = (event.ydata - self.pan_start[1]) * scrub_sensitivity
#             new_ylim = [max(0, ylim[0] + dy), max(0, ylim[1] + dy)]
#             ax.set_ylim(new_ylim)
#             self.canvas.draw()




#     def on_scroll(self, event):
#         ax = event.inaxes
#         if ax is None or event.xdata is None or event.ydata is None:
#             return

#         # Reverse the scale factor for more intuitive scrolling
#         scale_factor = 1.2 if event.button == 'down' else 0.8  # Changed directions
#         xdata = event.xdata
#         ydata = event.ydata
#         xlim = ax.get_xlim()
#         ylim = ax.get_ylim()

#         # Compute new limits
#         new_xlim = [xdata - (xdata - xlim[0]) * scale_factor,
#                     xdata + (xlim[1] - xdata) * scale_factor]
#         new_ylim = [ydata - (ydata - ylim[0]) * scale_factor,
#                     ydata + (ylim[1] - ydata) * scale_factor]
#         ax.set_xlim(new_xlim)
#         ax.set_ylim(new_ylim)
#         self.canvas.draw()

#     def on_combo_hover(self, index):
#         # ... existing code ...
#         pass

#     def highlight_line(self, file_name):
#         # ... existing code ...
#         pass

    
