from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import collections


class LiveGraph(FigureCanvas):
    def __init__(self, title="Live Data", y_label="Value", color="#e74c3c", max_points=30):
        self.fig = Figure(figsize=(4, 2), tight_layout=True)
        self.fig.patch.set_facecolor('#ffffff')
        super().__init__(self.fig)

        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#f7f9fc')
        self.ax.set_title(title, fontsize=10, pad=4)
        self.ax.set_ylabel(y_label, fontsize=8)
        self.ax.tick_params(labelsize=7)

        self.data = collections.deque([0] * max_points, maxlen=max_points)
        self.color = color
        self.line, = self.ax.plot(list(self.data), color=color, linewidth=2)
        self.ax.set_ylim(40, 140)
        self.ax.grid(True, alpha=0.3)

    def update_point(self, value: float):
        self.data.append(value)
        self.line.set_ydata(list(self.data))
        self.draw()
