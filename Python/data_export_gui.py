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

import settings_gui
import scope_gui

ser = serial.Serial()

class App(tk.Frame):
    data = []
    dataframe = []
    comport = ''
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
        self.calcnumpypandasfig()
        self.update_fig()
        return True

    def update_fig(self, event=None):
        """

        :param event: needed because it´s executed when selection in combobox is made
        :return: nothing
        """
        self.calcnumpypandasfig()
        t_s = self.settingswindow.times[self.settingswindow.timecb.current()] * self.settingswindow.time_units[
            self.settingswindow.timeunitcb.current()] / 200
        if (len(self.ch1) != 0):
            self.X, self.freqs = hameghm1007.calc_fft(self.ch1, t_s)


        self.scopewindow.plot()
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
        self.comport = self.settingswindow.comcb.get().split()[0]
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


    def calcnumpypandasfig(self):
        """

        :return: nothing
        """
        self.timearr, self.ch1, self.ch2, self.ref1, self.ref2 = hameghm1007.createnumpyarrays(self.data,
                                                                                               timeres=self.settingswindow.times[
                                                                                                           self.settingswindow.timecb.current()] *
                                                                                                       self.settingswindow.time_units[
                                                                                                           self.settingswindow.timeunitcb.current()] / 200,
                                                                                               ch1res=self.settingswindow.voltages[
                                                                                                          self.settingswindow.voltch1cb.current()] / 25,
                                                                                               ch2res=self.settingswindow.voltages[
                                                                                                          self.settingswindow.voltch2cb.current()] / 25,
                                                                                               ref1res=self.settingswindow.voltages[
                                                                                                           self.settingswindow.voltref1cb.current()] / 25,
                                                                                               ref2res=self.settingswindow.voltages[
                                                                                                           self.settingswindow.voltref2cb.current()] / 25,
                                                                                               ch1off=127 - 25 * (
                                                                                                           self.settingswindow.voltch1offcb.current() - 4),
                                                                                               ch2off=127 - 25 * (
                                                                                                           self.settingswindow.voltch2offcb.current() - 4),
                                                                                               ref1off=127 - 25 * (
                                                                                                       self.settingswindow.voltref1offcb.current() - 4),
                                                                                               ref2off=127 - 25 * (
                                                                                                       self.settingswindow.voltref2offcb.current() - 4))
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

        hameghm1007.save(self.folderdir.get(), self.lasttimestamp, self.data, self.dataframe, self.timeplotfig)
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

    def __init__(self, parent, *args, **kwargs):

        self.lasttimestamp = datetime.now()
        self.folderdir = tk.StringVar()
        self.folderdir.set(os.getcwd())
        self.saverawlog = tk.IntVar(value=1)
        self.savecsv = tk.IntVar(value=1)
        self.saveimg = tk.IntVar(value=1)
        self.autosave = tk.IntVar(value=1)

        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.menubar = tk.Menu(parent)
        parent.config(menu=self.menubar)

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

        self.scopewindow = scope_gui.ScopeWindow(self)
        self.settingswindow = settings_gui.SettingsWindow(self)
        #self.test = tk.Frame(ScopeWindow(self.parent))
        #self.scopewindow.grid(row=0,column=0)
        self.grid()

        #self.settingswindow.grid(row=0,column=0)
        #self.scopewindow.grid(row=0,column=1)


        self.calcnumpypandasfig()
        self.update_fig()

        return


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == '__main__':
    main()
