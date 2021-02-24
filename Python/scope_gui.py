import tkinter as tk
from tkinter import ttk
import matplotlib.pylab as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class ScopeWindow(tk.Frame):

    def toggleplot(self):
        if (self.fft_in_plot.get()==0):
            self.fft_in_plot.set(1)
            self.toggleplot['text']="show plot"
            self.plot_fft()
        else:
            self.fft_in_plot.set(0)
            self.toggleplot['text'] = "show fft"
            self.plot_timeplot()
        plt.close('all')
        return
    def plot_fft(self,event=None):
        f_s = 1/(self.parent.settingswindow.times[self.parent.settingswindow.timecb.current()] * self.parent.settingswindow.time_units[
            self.parent.settingswindow.timeunitcb.current()] / 200)
        self.scopeax.clear()
        self.scopeax.stem(self.parent.freqs, np.abs(self.parent.X) * 2 / len(self.parent.data))
        # ax.stem(freqs, X)
        self.scopeax.set_xlabel('Frequency [Hz]')
        self.scopeax.set_ylabel('Frequency Domain (Spectrum) Magnitude')
        self.scopeax.set_xlim(-10, f_s / self.maxfftslider.get())

        self.scope.draw_idle()

        return

    def update_fft_x_lims(self,event=None):

        if (self.fft_in_plot.get()==1):
            self.plot_fft()
            plt.close('all')
        return
    def plot_timeplot(self):
        self.scopeax.clear()

        if "XY-Plot" in self.parent.data:
            self.scopeax.plot(self.parent.ch2, self.parent.ch1)
        else:
            if (np.size(self.parent.ch1) == 2048):
                self.scopeax.plot(self.parent.timearr, self.parent.ch1)
            if (np.size(self.parent.ch2) == 2048):
                self.scopeax.plot(self.parent.timearr, self.parent.ch2)
            if (np.size(self.parent.ref1) == 2048):
                self.scopeax.plot(self.timearr, self.parent.parent.ref1)
            if (np.size(self.parent.ref2) == 2048):
                self.scopeax.plot(self.parent.timearr, self.parent.ref2)
            # ax.plot(ch2_data,timearray)
            # ax.plot(ref1_data,timearray)
            # ax.plot(ref2_data,timearray)

        self.scopeax.set(xlabel='time [s]', ylabel='Volts',
                         title='Data from Hameg HM1007')
        self.scopeax.grid()
        self.scope.draw_idle()

        return

    def plot(self):
        if (self.fft_in_plot.get() == 0):
            self.plot_timeplot()
        else:
            self.plot_fft()
        plt.close('all')

    def __init__(self, parent, *args, **kwargs):

        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.frame = tk.Frame(self.parent)

        self.fft_in_plot = tk.IntVar(value=0)
        self.scopefig = Figure(dpi=80)
        self.scopeax = self.scopefig.add_subplot(111)
        self.scope = FigureCanvasTkAgg(self.scopefig, master=self.frame)
        self.scope.get_tk_widget().config(width=640 / 1.25, height=480 / 1.25)
        self.scope.get_tk_widget().grid(column=0, row=0,columnspan=3, sticky=tk.W + tk.E)
        self.scope.draw()

        self.maxfftslider = tk.Scale(self.frame, from_=10, to=200, orient=tk.HORIZONTAL, command=self.update_fft_x_lims)
        self.maxfftslider.grid(column=0, row=1)

        self.toggleplot = tk.Button(self.frame,text="Show FFT", command=self.toggleplot)
        self.toggleplot.grid(column=1, row=1)

        self.frame.grid(column=1,row=0)
        return