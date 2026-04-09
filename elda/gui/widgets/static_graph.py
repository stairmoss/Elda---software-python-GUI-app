from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout

class StaticGraph(QWidget):
    def __init__(self, title="Historical Trends", y_label="Count", color="#8e44ad"):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Setup Figure
        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        # Initial Plot Styling
        self.figure.patch.set_facecolor('none')
        self.ax.set_facecolor('#f7f9fc')
        self.ax.set_title(title, fontsize=10, color='#2c3e50')
        self.ax.set_ylabel(y_label, fontsize=8)
        self.ax.grid(True, linestyle='--', alpha=0.3, axis='y')
        
        self.color = color
        
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)
        
    def plot_bar(self, data_dict):
        """Plots a bar chart from a dictionary {Label: Value}"""
        self.ax.clear()
        
        labels = list(data_dict.keys())
        values = list(data_dict.values())
        
        # Bars
        bars = self.ax.bar(labels, values, color=self.color, width=0.5)
        
        # Re-apply styling after clear
        self.ax.set_facecolor('#f7f9fc')
        self.ax.set_title("Medical Event Frequency (Last 7 Days)", fontsize=10, color='#2c3e50')
        self.ax.grid(True, linestyle='--', alpha=0.3, axis='y')
        
        self.canvas.draw()
