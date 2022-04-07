import os
import tkinter as tk
from tkinter import filedialog
import serial.tools.list_ports
import hameghm1007
from datetime import datetime
import webbrowser

import settings_gui
import scope_gui
import signalinfo_gui

ser = serial.Serial()


class App(tk.Frame):
    data = []
    dataframe = []
    fftframe = []
    comport = ''
    folderdir = ''

    def browse_button(self):
        """
        asks user where to store the oscilloscope data and stores location in self.folderdir
        :return: nothing
        """

        newfolder = filedialog.askdirectory()
        if newfolder != '':
            os.chdir(newfolder)
        # print(folderdir.get())
        self.folderdir.set(os.getcwd())
        return

    def load_raw_data_button(self):
        """
        loads serial data saved into a .txt file and updates scope on screen
        :return: True if successfully imported data
        """
        filedir = filedialog.askopenfilename(title="Select serial dump file",
                                             filetypes=(("Serial dump file", '*.txt'),))
        if filedir == '':
            return False
        print("Loaded", filedir)
        self.data = hameghm1007.readfromfile(filedir)
        # self.lasttimestamp = datetime.now()
        self.settingswindow.scopemodel.set(hameghm1007.oscilloscopemodel)
        self.update_fig()
        return True

    def update_fig(self, event=None):
        """
        :param event: needed because it`s executed when selection in combobox is made
        :return: nothing
        """
        self.calcnumpypandasfig()
        t_s = self.settingswindow.getsamplinginterval()
        if "CH1" in self.dataframe:
            self.X = self.fftframe.CH1.tolist()
            self.freqs = self.fftframe.freq.tolist()

            #self.X, self.freqs = hameghm1007.calc_fft(self.dataframe.CH1.tolist(), t_s)

        self.scopewindow.plot()
        return

    def on_select_com_port(self, event=None):
        """
        is executed whenever a serial port from the combobox is chosen
        Closes the connection to the old serialport and
        opens a serial connection on the new port
        :param event: needed because it`s executed when selection in combobox is made
        :return: nothing
        """
        # or get selection directly from combobox
        self.comport = self.settingswindow.comcb.get().split()[0]
        ser.close()
        ser.port = self.comport  # COM port of arduino
        ser.baudrate = 250000
        ser.open()
        hameghm1007.readmodelfromInterface(ser=ser)
        
        print("connected to" + hameghm1007.oscilloscopemodel+"on" + self.comport)
        return

    def on_select_time(self, event=None):
        """
        checks if the new selection of the time value is available in "µs" or just in "ms" and "s"
        :param event:
        :return: nothing
        """
        if self.settingswindow.timecb.current() > 3:  # time value is smaller than 5 -> µs are not possible
            if self.settingswindow.timeunitcb.current() == 2:  # reset selection if µs are selected
                self.settingswindow.timeunitcb.set('')
            self.settingswindow.timeunitcb['values'] = ['s', 'ms']
        else:  # µs are possible
            self.settingswindow.timeunitcb['values'] = ['s', 'ms', 'us']

        self.update_fig()
        return

    def calcnumpypandasfig(self):
        """
        Calculates a pandas dataframe out of the raw values received from the arduino.
        Uses the values from the selectors in the GUI to convert them into voltages.

        Afterwards a fast fourier transform will be calculated for each channel.

        Finally the signal infos on the screen will be updated.

        :return: nothing
        """
        self.dataframe = hameghm1007.createpandasframe(self.data, timeres=self.settingswindow.getsamplinginterval(),
                                                       ch1res=self.settingswindow.voltages[
                                                                  self.settingswindow.voltch1cb.current()] / 25,
                                                       ch2res=self.settingswindow.voltages[
                                                                  self.settingswindow.voltch2cb.current()] / 25,
                                                       ref1res=self.settingswindow.voltages[
                                                                   self.settingswindow.voltref1cb.current()] / 25,
                                                       ref2res=self.settingswindow.voltages[
                                                                   self.settingswindow.voltref2cb.current()] / 25,
                                                       ch1off=self.settingswindow.ch1rawoffset,
                                                       ch2off=self.settingswindow.ch2rawoffset,
                                                       ref1off=127 - 25 * (
                                                               self.settingswindow.voltref1offcb.current() - 4),
                                                       ref2off=127 - 25 * (
                                                               self.settingswindow.voltref2offcb.current() - 4))

        self.fftframe = hameghm1007.calc_fftdataframe(self.dataframe,self.settingswindow.getsamplinginterval()) # Calculate the FFT of all available channels
        self.signalinfoframe.update_infos() #Update signal infos on GUI
        return

    def savemanual(self):
        """
        is executed when "Save" Button in GUI is pressed
        gets new timestamp and exports data to file system
        :return:
        """
        self.lasttimestamp = datetime.now()
        self.savedata()
        return

    def savedata(self):
        """
        saves current data to files
        :param now: datetime timestamp (datetime.now())
        :return:
        """
        if len(self.data) == 0:
            print("No data -> not saving")
            return False

        hameghm1007.save(self.folderdir.get(), self.lasttimestamp, self.data, self.dataframe)
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
        if self.settingswindow.timeunitcb.current() == -1:
            print("No time unit selected")
            return False
        if self.settingswindow.timecb.current() == -1:
            print("no time value selected")
            return False
        self.lasttimestamp = datetime.now()
        self.data = hameghm1007.readfromoszi(ser=ser, mod=mode)
        # self.calcnumpypandasfig()
        self.update_fig()
        if (self.settingswindow.autosave.get() == 1):
            self.savedata()
        
        self.settingswindow.scopemodel.set(hameghm1007.oscilloscopemodel)
        return True

    def __init__(self, parent, *args, **kwargs):
        """
        init function
        """
        self.lasttimestamp = datetime.now()
        self.folderdir = tk.StringVar()
        self.folderdir.set(os.getcwd())

        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.menubar = tk.Menu(self.parent)
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

        self.help_menu = tk.Menu(self.menubar, tearoff=0
                                 )
        self.menubar.add_cascade(label="Help", menu=self.help_menu)

        self.help_menu.add_command(label='GitHub page', command=lambda: webbrowser.open_new(
            'https://github.com/eilmi/HAMEG-HM1007-serial-interface'))

        self.scopewindow = scope_gui.ScopeWindow(self)
        self.settingswindow = settings_gui.SettingsWindow(self)
        self.signalinfoframe = signalinfo_gui.SignalInfoFrame(self)

        self.folderlabel = tk.Label(self, textvariable=self.folderdir)
        self.folderlabel.grid(column=0, row=2, columnspan=2, sticky=tk.W)
        self.update_fig()
        self.grid()

        return
    
    def calcoffsets(self,ch):
        if (self.comport==''):
            print ("Please select COM port first")
        else:
            da = hameghm1007.readfromoszi(ser)

        return


def main():
    root = tk.Tk()
    root.geometry("820x500")
    root.minsize(820, 500)
    root.title("HAMEG Bus Interface")
    app = App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
