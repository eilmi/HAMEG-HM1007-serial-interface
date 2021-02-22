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


class App:
    data = []
    dataframe = []
    comport = ''
    voltages = [5, 2, 1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005]
    times = [50, 20, 10, 5, 2, 1, 0.5, 0.2, 0.1]
    time_units = [1, 1e-3, 1e-6]
    voltage_names = ['5V', '2V', '1V', '.5V', '.2V', '.1V', '50mV', '20mV', '10mV', '5mV']
    grid_names = ['+4', '+3', '+2', '+1', '0', '-1', '-2', '-3', '-4']
    folderdir=''
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
        filedir = filedialog.askopenfilename(title="Select serial dump file", filetypes=(("Serial dump file", '*.txt'),))
        print(filedir)
        if filedir == '':
            return False
        print("Loaded", filedir)
        self.data = hameghm1007.readfromfile(filedir)
        self.lasttimestamp = datetime.now()
        #self.calcnumpypandasfig()
        self.update_fig()
        return True

    def update_fig(self,event=None):
        """

        :param event: needed because it´s executed when selection in combobox is made
        :return: nothing
        """
        self.calcnumpypandasfig()
        test = self.fig
        test.set_dpi(80.0)
        self.output= FigureCanvasTkAgg(test,master=root)
        self.output.get_tk_widget().config(width=640/1.25, height=480/1.25)
        self.output.get_tk_widget().grid(column=3,row=0,rowspan=7,sticky=tk.W+tk.E)
        self.output.draw()
        plt.close('all')

        return

    def plot_fft(self):
        t_s=self.times[self.timecb.current()] * self.time_units[
            self.timeunitcb.current()] / 200
        f_s=1/t_s
        x=self.ch1
        X = fftpack.fft(x)
        freqs = fftpack.fftfreq(len(x)) * f_s

        fig, ax = plt.subplots()

        ax.stem(freqs, np.abs(X))
        ax.set_xlabel('Frequency in Hertz [Hz]')
        ax.set_ylabel('Frequency Domain (Spectrum) Magnitude')
        ax.set_xlim(0, f_s / 50)
        ax.set_ylim(-5, 110)

        plt.show()

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
        if self.timecb.current() > 3: #time value is smaller than 5 -> µs are not possible
            if self.timeunitcb.current() == 2: # reset selection if µs are selected
                self.timeunitcb.set('')
            self.timeunitcb['values'] = ['s', 'ms']
        else: # µs are possible
            self.timeunitcb['values'] = ['s', 'ms', 'us']

        self.update_fig()
        return

    def updateserialports(self):
        self.comcb['values'] = get_serial_port_list()

    def calcnumpypandasfig(self):
        """

        :return: nothing
        """
        self.timearr,self.ch1, self.ch2, self.ref1, self.ref2 = hameghm1007.createnumpyarrays(self.data,timeres=self.times[self.timecb.current()] * self.time_units[
                                            self.timeunitcb.current()] / 200,
                                        ch1res=self.voltages[self.voltch1cb.current()] / 25,
                                        ch2res=self.voltages[self.voltch2cb.current()] / 25,
                                        ref1res=self.voltages[self.voltref1cb.current()] / 25,
                                        ref2res=self.voltages[self.voltref2cb.current()] / 25,
                                        ch1off=127 - 25 * (self.voltch1offcb.current() - 4),
                                        ch2off=127 - 25 * (self.voltch2offcb.current() - 4))
        self.dataframe = hameghm1007.createpandasframe(self.timearr,self.ch1, self.ch2, self.ref1, self.ref2)
        self.fig = hameghm1007.makeplot(self.data, self.ch1, self.ch2, self.ref1, self.ref2,self.timearr)

    def savedata(self):
        """
        saves current data to files
        :param now: datetime timestamp (datetime.now())
        :return:
        """
        hameghm1007.save(self.folderdir.get(),self.lasttimestamp,self.data,self.dataframe,self.fig)
        print("Data saved")
        return

    def readfromoszi(self, mode='R'):
        """

        :param mode: 'R' for normal data readout and 'S' for singleshotmode
        :return: True is data is successfully read from oscilloscope
        """
        if self.comport == '':
            print("Please select comport first")
            return False
        if self.voltch1cb.current() == -1:
            print("Please set Voltage per Division first")
            return False
        if self.timeunitcb.current() == -1:
            print("Please set time unit first")
            return False
        if self.timecb.current() == -1:
            print("Please set time value first")
            return False
        self.lasttimestamp =datetime.now()
        self.data = hameghm1007.readfromoszi(ser=ser, mod=mode)
        #self.calcnumpypandasfig()
        self.update_fig()
        self.savedata()

        return True

    def __init__(self, master):
        self.lasttimestamp =datetime.now()
        self.folderdir = tk.StringVar()
        self.folderdir.set(os.getcwd())
        self.saverawlog = tk.IntVar(value=1)
        self.savecsv = tk.IntVar(value=1)
        self.saveimg = tk.IntVar(value=1)
        self.autosave = tk.IntVar(value=1)

        root.title("HAMEG HM1007 interface")
        root.geometry("800x500")
        tk.Grid.columnconfigure(root, 3, weight=1)
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

        self.help_menu.add_command(label='GitHub page',command=lambda: webbrowser.open_new('https://github.com/eilmi/HAMEG-HM1007-serial-interface'))

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

        # time unit selector
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

        self.folderlabel = tk.Label(root, textvariable=self.folderdir, width=30)
        self.folderlabel.grid(column=0, row=10, columnspan=3, sticky=tk.W + tk.E)

        self.fftbutton = tk.Button(text="Show FFT", command=self.plot_fft)
        self.fftbutton.grid(column=3, row=7)

        self.savebutton = tk.Button(text="Save", command=self.savedata)
        self.savebutton.grid(column=0, row=7)

        tk.Label(root, text="Things to save:").grid(column=0, row=8)
        self.saverawlogcb = tk.Checkbutton(text="raw log", variable=self.saverawlog)
        self.saverawlogcb.grid(column=0, row=9)
        self.savecsvcb = tk.Checkbutton(text="csv", variable=self.savecsv)
        self.savecsvcb.grid(column=1, row=9)
        self.saveimgcb = tk.Checkbutton(text="png", variable=self.saveimg)
        self.saveimgcb.grid(column=2, row=9)

        self.update_fig()

        return


root = tk.Tk()
app = App(root)
root.mainloop()
