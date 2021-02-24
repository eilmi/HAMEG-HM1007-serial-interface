from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import ttk
import tkinter as tk


class MainApplication(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        notes = ttk.Notebook(self)
        notes.grid(column=0, row=0, sticky='nsew')
        notes.rowconfigure(0, weight=1)
        self.page = ttk.Frame(notes)
        notes.add(self.page, text='Picture')
        self.plotter()
        input_frame = ttk.Frame(self)
        input_frame.grid(column=1, row=0, sticky='nsew')

        button = ttk.Button(input_frame, text='Plot', command=self.new_draw)
        button.grid(column=0, row=4, columnspan=2, sticky='ew')

    def plotter(self):
        self.figure = Figure(dpi=100)
        self.plot_canvas = FigureCanvasTkAgg(self.figure, self.page)
        self.axes = self.figure.add_subplot(111)
        self.plot_canvas.get_tk_widget().grid(column=0, row=0, sticky='nsew')
    t=0
    def new_draw(self):
        self.t=self.t+1
        self.axes.clear()
        x_list = [x for x in range(0, self.t)]
        y_list = [x^3 for x in x_list]
        self.axes.plot(x_list, y_list, color='y')
        self.plot_canvas.draw_idle()

MainApplication().mainloop()