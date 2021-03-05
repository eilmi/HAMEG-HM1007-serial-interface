import tkinter as tk
from tkinter import ttk
import matplotlib.pylab as plt
import numpy as np
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class ScopeWindow(tk.Frame):
    """
    scope part of the main window
    consists mainly of a Canvas figure in which the matplotlib figure is shown
    """

    def toggleplot(self):
        """
        toggle between time plot and FFT
        :return: nothing
        """
        if (self.fft_in_plot.get() == 0):
            self.fft_in_plot.set(1)
            self.toggleplot['text'] = "show plot"
            #self.scopeframe.destroy()
            self.plot_fft()
        else:
            self.fft_in_plot.set(0)
            self.toggleplot['text'] = "show fft"
            self.plot_timeplot()
        plt.close('all')
        return

    def plot_fft(self, event=None):
        """
        plot FFT in Canvas figure
        :param event: event
        :return: nothing
        """
        try:
            f_s = 1/self.parent.settingswindow.getsamplinginterval()
            self.scopeax.clear()
            self.scopeax.stem(self.parent.freqs, np.abs(self.parent.X) * 2 / len(self.parent.data))
            # ax.stem(freqs, X)
            self.scopeax.set_xlabel('Frequency [Hz]')
            self.scopeax.set_ylabel('Frequency Domain (Spectrum) Magnitude')
            self.scopeax.set_xlim(-f_s / 2, f_s / 2)

            self.scope.draw_idle()
        except AttributeError:
            print("FFT not calculated -> skipped plotting")
        #print(self.parent.freqs[0])
        #print(len(self.parent.X))

        return

    def update_fft_x_lims(self, event=None):
        """
        replot FFT with new xlimit
        :param event:
        :return:
        """

        if (self.fft_in_plot.get() == 1):
            self.plot_fft()
            plt.close('all')
        return

    def plot_timeplot(self):
        """
        Plot the time plot in the Canvas figure
        :return: nothing
        """
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

        self.scopeax.set(xlabel='time [s]', ylabel='Volts')
        self.scopeax.grid()
        self.scope.draw_idle()

        return

    def plot(self):
        """
        plot Canvas figure
        :return:
        """
        if (self.fft_in_plot.get() == 0):
            self.plot_timeplot()
        else:
            self.plot_fft()
        plt.close('all')

    def __init__(self, parent, *args, **kwargs):
        """
        initialization of scope part of GUI
        :param parent: main window
        :param args: not used
        :param kwargs: not used
        """

        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.frame = tk.Frame(self.parent)
        self.scopeframe = tk.Frame(self.frame)
        self.fft_in_plot = tk.IntVar(value=0)

        self.scopefig = Figure(dpi=80)
        self.scopeax = self.scopefig.add_subplot(111)
        self.scope = FigureCanvasTkAgg(self.scopefig, master=self.scopeframe)
        self.toolbar = NavigationToolbar2Tk(self.scope, self.scopeframe)

        self.toolbar.update()
        self.scope.get_tk_widget().config(width=640 / 1.25, height=480 / 1.25)
        # self.scope
        self.scope.get_tk_widget().pack()
        self.scope.draw()

        self.scopeframe.grid(column=0, row=0, columnspan=3, sticky=tk.W + tk.E)

        #self.maxfftslider = tk.Scale(self.frame, from_=10, to=200, orient=tk.HORIZONTAL, command=self.update_fft_x_lims)
        #self.maxfftslider.grid(column=0, row=1)
        # self.maxfftslider.pack()

        self.toggleplot = tk.Button(self.frame, text="Show FFT", command=self.toggleplot)
        self.toggleplot.grid(column=1, row=1)
        # self.toggleplot.pack()

        self.frame.grid(column=1, row=0)
        return
