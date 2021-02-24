import serial
import os
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
import serial.tools.list_ports
import hameghm1007
from datetime import datetime
import webbrowser
from scipy import fftpack
import numpy as np
from matplotlib.figure import Figure
import matplotlib.pylab as plt
from matplotlib import tight_layout
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

ser = serial.Serial()


def get_serial_port_list():
    """
    Get list of available serial ports
    :return: list of available serial ports
    """
    return serial.tools.list_ports.comports()


class App():
    data = []
    dataframe = []
    comport = ''
    voltages = [5, 2, 1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005]
    times = [50, 20, 10, 5, 2, 1, 0.5, 0.2, 0.1]
    time_units = [1, 1e-3, 1e-6]
    voltage_names = ['5V', '2V', '1V', '.5V', '.2V', '.1V', '50mV', '20mV', '10mV', '5mV']
    grid_names = ['+4', '+3', '+2', '+1', '0', '-1', '-2', '-3', '-4']
    folderdir = ''

    def browse_button(self):
        """
        asks user where to store the oscilloscope data and stores location in self.folderdir
        :return: nothing
        """
        # Allow user to select a directory and store it in global var
        # called folder_path
        newfolder = filedialog.askdirectory()
        if newfolder != '':
            os.chdir(newfolder)
        # print(folderdir.get())
        self.folderdir.set(os.getcwd())
        return

    def load_raw_data_button(self):
        """
        loads serial data saved into a .txt file and updates scope on screen
        :return: True if successfully loaded data
        """
        filedir = filedialog.askopenfilename(title="Select serial dump file",
                                             filetypes=(("Serial dump file", '*.txt'),))
        if filedir == '':
            return False
        print("Loaded", filedir)
        self.data = hameghm1007.readfromfile(filedir)
        self.lasttimestamp = datetime.now()
        # self.calcnumpypandasfig()
        self.update_fig()
        return True

    def update_fig(self, event=None):
        """

        :param event: needed because it´s executed when selection in combobox is made
        :return: nothing
        """
        self.calcnumpypandasfig()
        t_s = self.times[self.timecb.current()] * self.time_units[
            self.timeunitcb.current()] / 200
        if (len(self.ch1) != 0):
            self.X, self.freqs = hameghm1007.calc_fft(self.ch1, t_s)


        if (self.fft_in_plot.get()==0):
            self.plot_timeplot()
        else:
            self.plot_fft()
        plt.close('all')

        return

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
        f_s = 1/(self.times[self.timecb.current()] * self.time_units[
            self.timeunitcb.current()] / 200)
        self.te.set_xlim(-40,f_s/self.maxfftslider.get())

        self.scopeax.clear()
        self.scopeax.stem(self.freqs, np.abs(self.X) * 2 / len(self.data))
        # ax.stem(freqs, X)
        self.scopeax.set_xlabel('Frequency [Hz]')
        self.scopeax.set_ylabel('Frequency Domain (Spectrum) Magnitude')
        self.scopeax.set_xlim(-10, f_s / self.maxfftslider.get())
        #self.scopefig.set_dpi(80)
        #self.scope.get_tk_widget().grid(column=3, row=0, rowspan=11, sticky=tk.W + tk.E)
        #self.scope.
        self.scope.draw_idle()
        #self.scopefig.show()

        return

    t =0
    def plot_timeplot(self):
        self.scopeax.clear()

        if "XY-Plot" in self.data:
            self.scopeax.plot(self.ch2, self.ch1)
        else:
            if (np.size(self.ch1) == 2048):
                self.scopeax.plot(self.timearr, self.ch1)
            if (np.size(self.ch2) == 2048):
                self.scopeax.plot(self.timearr, self.ch2)
            if (np.size(self.ref1) == 2048):
                self.scopeax.plot(self.timearr, self.ref1)
            if (np.size(self.ref2) == 2048):
                self.scopeax.plot(self.timearr, self.ref2)
            # ax.plot(ch2_data,timearray)
            # ax.plot(ref1_data,timearray)
            # ax.plot(ref2_data,timearray)

        self.scopeax.set(xlabel='time [s]', ylabel='Volts',
               title='Data from Hameg HM1007')
        self.scopeax.grid()
        self.scope.draw_idle()


        return
    t=0
    def update_fft_x_lims(self,event=None):

        if (self.fft_in_plot.get()==1):
            self.plot_fft()
            plt.close('all')
        return


    def on_select_com_port(self, event=None):
        """
        is executed whenever a serial port from the combobox is chosen
        Closes the connection to the old serialport and
        opens a serial connection on the new port
        :param event: needed because it´s executed when selection in combobox is made
        :return: nothing
        """
        # or get selection directly from combobox
        self.comport = self.comcb.get().split()[0]
        ser.close()
        ser.port = self.comport  # COM port of arduino
        ser.baudrate = 250000
        ser.open()
        print("connected to" + self.comport)
        return

    def on_select_time(self, event=None):
        """
        checks if the new selection of the time value is available in "µs" or just in "ms" and "s"
        :param event:
        :return: nothing
        """
        if self.timecb.current() > 3:  # time value is smaller than 5 -> µs are not possible
            if self.timeunitcb.current() == 2:  # reset selection if µs are selected
                self.timeunitcb.set('')
            self.timeunitcb['values'] = ['s', 'ms']
        else:  # µs are possible
            self.timeunitcb['values'] = ['s', 'ms', 'us']

        self.update_fig()
        return

    def updateserialports(self):
        self.comcb['values'] = get_serial_port_list()

    def calcnumpypandasfig(self):
        """

        :return: nothing
        """
        self.timearr, self.ch1, self.ch2, self.ref1, self.ref2 = hameghm1007.createnumpyarrays(self.data,
                                                                                               timeres=self.times[
                                                                                                           self.timecb.current()] *
                                                                                                       self.time_units[
                                                                                                           self.timeunitcb.current()] / 200,
                                                                                               ch1res=self.voltages[
                                                                                                          self.voltch1cb.current()] / 25,
                                                                                               ch2res=self.voltages[
                                                                                                          self.voltch2cb.current()] / 25,
                                                                                               ref1res=self.voltages[
                                                                                                           self.voltref1cb.current()] / 25,
                                                                                               ref2res=self.voltages[
                                                                                                           self.voltref2cb.current()] / 25,
                                                                                               ch1off=127 - 25 * (
                                                                                                           self.voltch1offcb.current() - 4),
                                                                                               ch2off=127 - 25 * (
                                                                                                           self.voltch2offcb.current() - 4))
        self.dataframe = hameghm1007.createpandasframe(self.timearr, self.ch1, self.ch2, self.ref1, self.ref2)
        self.timeplotfig,self.timeplotax = hameghm1007.makeplot(self.data, self.ch1, self.ch2, self.ref1, self.ref2, self.timearr)

    def savedata(self):
        """
        saves current data to files
        :param now: datetime timestamp (datetime.now())
        :return:
        """
        if len(self.data) == 0:
            print("No data -> not saving")
            return False

        hameghm1007.save(self.folderdir.get(), self.lasttimestamp, self.data, self.dataframe, self.fig)
        print("data saved")
        return True

    def readfromoszi(self, mode='R'):
        """

        :param mode: 'R' for normal data readout and 'S' for singleshotmode
        :return: True is data is successfully read from oscilloscope
        """
        if self.comport == '':
            print("No COM port selected")
            return False
        if self.timeunitcb.current() == -1:
            print("No time unit selected")
            return False
        if self.timecb.current() == -1:
            print("no time value selected")
            return False
        self.lasttimestamp = datetime.now()
        self.data = hameghm1007.readfromoszi(ser=ser, mod=mode)
        # self.calcnumpypandasfig()
        self.update_fig()
        self.savedata()

        return True

    def __init__(self, master):

        #self.timeplotfig, self.timeplotax = plt.subplots()
        self.timeplotfig = Figure(dpi=100)
        self.timeplotax = self.timeplotfig.add_subplot(111)
        self.pll, self.te=plt.subplots()
        #self.scopefig,self.scopeax = plt.subplots()
        self.scopefig = Figure(dpi=100)
        self.scopeax = self.scopefig.add_subplot(111)
        self.lasttimestamp = datetime.now()
        self.folderdir = tk.StringVar()
        self.folderdir.set(os.getcwd())
        self.saverawlog = tk.IntVar(value=1)
        self.savecsv = tk.IntVar(value=1)
        self.fft_in_plot = tk.IntVar(value=0)
        self.saveimg = tk.IntVar(value=1)
        self.autosave = tk.IntVar(value=1)

        root.title("HAMEG HM1007 interface")
        root.geometry("780x450")
        root.minsize(780, 450)
        tk.Grid.columnconfigure(root, 3, weight=1)


        self.scope = FigureCanvasTkAgg(self.scopefig, master=root)
        self.scope.get_tk_widget().config(width=640 / 1.25, height=480 / 1.25)
        self.scope.get_tk_widget().grid(column=3, row=0, rowspan=11, sticky=tk.W + tk.E)
        self.scope.draw()


        self.menubar = tk.Menu(root)
        root.config(menu=self.menubar)

        # File Menu
        self.file_menu = tk.Menu(
            self.menubar,
            tearoff=0
        )
        self.file_menu.add_command(label='Import Raw Data', command=self.load_raw_data_button)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Select export folder', command=self.browse_button)
        self.menubar.add_cascade(
            label="File",
            menu=self.file_menu
        )
        # Help Menu

        self.help_menu = tk.Menu(
            self.menubar,
            tearoff=0
        )
        self.menubar.add_cascade(
            label="Help",
            menu=self.help_menu
        )

        self.help_menu.add_command(label='GitHub page', command=lambda: webbrowser.open_new(
            'https://github.com/eilmi/HAMEG-HM1007-serial-interface'))

        # Combobox for selecting right serial port
        tk.Label(root, text="Serial port:").grid(column=0, row=0)
        self.comcb = ttk.Combobox(root, values=get_serial_port_list(), postcommand=self.updateserialports, width=10)
        self.comcb.grid(row=0, column=1)
        self.comcb.bind('<<ComboboxSelected>>', self.on_select_com_port)

        # time selector
        tk.Label(root, text="Time per Division:").grid(column=0, row=1)
        self.timecb = ttk.Combobox(root, values=['50', '20', '10', '5', '2', '1', '.5', '.2', '.1'], width=5)
        self.timecb.bind('<<ComboboxSelected>>', self.on_select_time)
        self.timecb.grid(column=1, row=1)
        self.timecb.current(0)

        # time unit selectorS
        self.timeunitcb = ttk.Combobox(root, values=['s', 'ms', 'us'], width=5)
        self.timeunitcb.grid(column=2, row=1)
        self.timeunitcb.bind('<<ComboboxSelected>>', self.update_fig)
        self.timeunitcb.current(1)

        # voltage selector CH1
        tk.Label(root, text="Volts per Division (CH1):").grid(column=0, row=2)
        self.voltch1cb = ttk.Combobox(root, values=self.voltage_names, width=5)
        self.voltch1cb.grid(column=1, row=2)
        self.voltch1cb.bind('<<ComboboxSelected>>', self.update_fig)

        # voltage selector CH2
        tk.Label(root, text="Volts per Division (CH2):").grid(column=0, row=3)
        self.voltch2cb = ttk.Combobox(root, values=self.voltage_names, width=5)
        self.voltch2cb.grid(column=1, row=3)
        self.voltch2cb.bind('<<ComboboxSelected>>', self.update_fig)

        # voltage selector REF1
        tk.Label(root, text="Volts per Division (REF1):").grid(column=0, row=4)
        self.voltref1cb = ttk.Combobox(root, values=self.voltage_names, width=5)
        self.voltref1cb.grid(column=1, row=4)
        self.voltref1cb.bind('<<ComboboxSelected>>', self.update_fig)

        # voltage selector REF2
        tk.Label(root, text="Volts per Division (REF2):").grid(column=0, row=5)
        self.voltref2cb = ttk.Combobox(root, values=self.voltage_names, width=5)
        self.voltref2cb.grid(column=1, row=5)
        self.voltref2cb.bind('<<ComboboxSelected>>', self.update_fig)

        # voltage offset CH1
        self.voltch1offcb = ttk.Combobox(root, values=self.grid_names, width=5)
        self.voltch1offcb.grid(column=2, row=2)
        self.voltch1offcb.current(4)
        self.voltch1offcb.bind('<<ComboboxSelected>>', self.update_fig)

        # voltage offset CH2
        self.voltch2offcb = ttk.Combobox(root, values=self.grid_names, width=5)
        self.voltch2offcb.grid(column=2, row=3)
        self.voltch2offcb.current(4)
        self.voltch2offcb.bind('<<ComboboxSelected>>', self.update_fig)

        # voltage offset REF1
        self.voltref1offcb = ttk.Combobox(root, values=self.grid_names, width=5)
        self.voltref1offcb.grid(column=2, row=4)
        self.voltref1offcb.current(4)
        self.voltref1offcb.bind('<<ComboboxSelected>>', self.update_fig)

        # voltage offset REF2
        self.voltref2offcb = ttk.Combobox(root, values=self.grid_names, width=5)
        self.voltref2offcb.grid(column=2, row=5)
        self.voltref2offcb.current(4)
        self.voltref2offcb.bind('<<ComboboxSelected>>', self.update_fig)

        # button to read from oscilloscope
        self.buttonreadsingle = tk.Button(root, text="Read from scope", command=lambda: (self.readfromoszi(mode='R')))
        self.buttonreadsingle.grid(column=0, row=6, columnspan=2, sticky=tk.W + tk.E)

        self.buttonreadsingleshot = tk.Button(root, text="Reset Single-Shot + Read",
                                              command=lambda: (self.readfromoszi(mode='S')))
        self.buttonreadsingleshot.grid(column=0, row=7, columnspan=2, sticky=tk.W + tk.E)

        self.folderlabel = tk.Label(root, textvariable=self.folderdir, width=30)
        self.folderlabel.grid(column=0, row=11, columnspan=4, sticky=tk.E + tk.W)

        self.toggleplot = tk.Button(text="Show FFT", command=self.toggleplot)
        self.toggleplot.grid(column=1, row=10)

        tk.Label(root, text="Things to save:").grid(column=0, row=8)
        self.saverawlogcb = tk.Checkbutton(text="raw log", variable=self.saverawlog)
        self.saverawlogcb.grid(column=0, row=9)
        self.savecsvcb = tk.Checkbutton(text="csv", variable=self.savecsv)
        self.savecsvcb.grid(column=1, row=9)
        self.saveimgcb = tk.Checkbutton(text="png", variable=self.saveimg)
        self.saveimgcb.grid(column=2, row=9)

        self.savebutton = tk.Button(text="Save", command=self.savedata)
        self.savebutton.grid(column=0, row=10)

        self.maxfftslider= tk.Scale(root, from_=10, to=200,orient=tk.HORIZONTAL,command=self.update_fft_x_lims)
        self.maxfftslider.grid(column=3,row=12)

        self.calcnumpypandasfig()
        self.update_fig()


        return


root = tk.Tk()
app = App(root)
root.mainloop()
