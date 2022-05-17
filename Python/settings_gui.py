import tkinter as tk
from tkinter import ttk

import serial
import numpy as np


class SettingsWindow(tk.Frame):
    """
    Left upper part of the main window
    includes all changeable parameters of the signal
    """
    voltages = [5, 2, 1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005]
    times = [50, 20, 10, 5, 2, 1, 0.5, 0.2, 0.1]
    time_units = [1, 1e-3, 1e-6]
    voltage_names = ['5V', '2V', '1V', '.5V', '.2V', '.1V', '50mV', '20mV', '10mV', '5mV']
    grid_names = ['+4', '+3', '+2', '+1', '0', '-1', '-2', '-3', '-4']

    def get_serial_port_list(self):
        """
        Get list of available serial ports
        :return: list of available serial ports
        """
        return serial.tools.list_ports.comports()

    def updateserialports(self):
        """
        update entries of combobox for selecting available serial ports
        :return: none
        """
        self.comcb['values'] = self.get_serial_port_list()

    def getsamplinginterval(self):
        """
        calculate sampling time interval based on selected time per division
        :return: sampling interval
        """

        return self.times[self.timecb.current()] * self.time_units[self.timeunitcb.current()] / 200


    def getoffsetarray(self):
        """
        :return: array of all raw (bit) offset values for all four channels
        """
        return [self.ch1rawoffset,self.ch2rawoffset,self.ref1rawoffset,self.ref2rawoffset]

    def getresolutionarray(self):
        """
        :return: array of all the resolutions of the four channels in Volt per Bit
        """
        return [self.voltages[self.voltch1cb.current()] / 25,
                self.voltages[self.voltch2cb.current()] / 25,
                self.voltages[self.voltref1cb.current()] / 25,
                self.voltages[self.voltref2cb.current()] / 25]


    def updatescopemodel(self,scopemodel):
        """
        :param scopemodel: String of current scope model
        :return: none
        """
        #print(scopemodel)
        self.scopemodel.set(scopemodel)

        te = tk.ACTIVE if scopemodel=="HM1007" else tk.DISABLED
        self.voltref1cb["state"] = te
        self.voltref1offcb["state"] = te
        self.voltref2cb["state"] = te
        self.voltref2offcb["state"] = te
        self.getoffsetref1btn["state"] = te
        self.getoffsetref2btn["state"] = te
        self.buttonreadsingleshot["state"] = te
        #print("updated")
        return


    def updaterawoffsetsandfig(self,event=None):
        """
        Updates the raw offset values corresponding to the values chosen in the dropdown menus and redraws the figure
        """
        self.ch1rawoffset=127 - 25 * (self.voltch1offcb.current() - 4)
        self.ch2rawoffset=127 - 25 * (self.voltch2offcb.current() - 4)
        self.ref1rawoffset=127 - 25 * (self.voltref1offcb.current() - 4)
        self.ref2rawoffset=127 - 25 * (self.voltref2offcb.current() - 4)
        self.parent.update_fig()
        return

    def readinoffsets(self,ch):
        """
        TODO
        read in the data from the oscilloscope and use it to determine the current DC offset
        """

        da=self.parent.getrawdata()

        try:
            begin_CH1 = da.index("CH1")
            begin_CH2 = da.index("CH2")
            begin_Ref1 = da.index("REF1")
            begin_Ref2 = da.index("REF2")
        except AttributeError:
            print("invalid serial data - coudn`t set offset")
            return
        
        if ch=="CH1":
            arr = np.array(da[begin_CH1 + 1:begin_CH2]).astype(np.int)
            if len(arr)==2048 or len(arr)==1024:
                self.ch1rawoffset=np.mean(arr,dtype=np.int)
                self.voltch1offcb.set("")

        if ch=="CH2":
            arr = np.array(da[begin_CH2 + 1:begin_Ref1]).astype(np.int)
            if len(arr)==2048 or len(arr)==1024:
                self.ch2rawoffset=np.mean(arr,dtype=np.int)
                self.voltch2offcb.set("")

        if ch=="REF1":
            arr = np.array(da[begin_Ref1 + 1:begin_Ref2]).astype(np.int)
            if len(arr)==2048 or len(arr)==1024:
                self.ref1rawoffset=np.mean(arr,dtype=int)
                self.voltref1offcb.set("")

        if ch=="REF2":
            arr = np.array(da[begin_Ref2 + 1:]).astype(np.int)
            if len(arr)==2048 or len(arr)==1024:
                self.ref2rawoffset=np.mean(arr,dtype=int)
                self.voltref2offcb.set("")

        self.parent.update_fig()
        return

    def __onselecttime__(self,event=None):
        """
        TODO: move to settings_gui.py
        checks if the new selection of the time value is available in "µs" or just in "ms" and "s"
        :param event:
        :return: nothing
        """
        sm = self.scopemodel.get()
        if sm=="HM1007":
            if self.timecb.current() > 3:  # time value is smaller than 5 -> µs are not possible
                if self.timeunitcb.current() == 2:  # reset selection if µs are selected
                    self.timeunitcb.set('')
                self.timeunitcb['values'] = ['s', 'ms']
            else:  # µs are possible
                self.timeunitcb['values'] = ['s', 'ms', 'us']
        elif sm=="HM205-3":
            if self.timecb.current() > 2: #time value is smaller than 10 -> µs aren't possible
                if self.timeunitcb.current() == 2:  # reset selection if µs are selected
                    self.timeunitcb.set('')
                self.timeunitcb['values'] = ['s', 'ms']
            
            elif self.timecb.current() < 3: # time value is bigger than 5 -> s are not possible
                if self.timeunitcb.current() == 0:  # reset selection if µs are selected
                    self.timeunitcb.set('')
                self.timeunitcb['values'] = ['','ms','us']
            else:
                self.timeunitcb['values'] = ['s', 'ms', 'us'] 
        self.parent.update_fig()

        return

    def __init__(self, parent, *args, **kwargs):
        """
        initialization of setting part of main GUI
        :param parent: main window
        :param args: not used
        :param kwargs: not used
        """

        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.frame = tk.Frame(self.parent)

        self.scopemodel = tk.StringVar()
        self.saverawlog = tk.IntVar(value=1)
        self.savecsv = tk.IntVar(value=1)
        self.saveimg = tk.IntVar(value=1)
        self.autosave = tk.IntVar(value=1)
        self.ch1rawoffset=127
        self.ch2rawoffset=127
        self.ref1rawoffset=127
        self.ref2rawoffset=127

        # Combobox for selecting right serial port
        tk.Label(self.frame, text="Serial port:").grid(column=0, row=0)
        self.comcb = ttk.Combobox(self.frame, values=self.get_serial_port_list(), postcommand=self.updateserialports, width=10)
        self.comcb.grid(row=0, column=1)
        self.comcb.bind('<<ComboboxSelected>>', self.parent.on_select_com_port)

        #
        tk.Label(self.frame, text="scope model:").grid(column=0, row=1)
        tk.Label(self.frame,textvariable=self.scopemodel).grid(column=1,row=1)

        # time selector
        tk.Label(self.frame, text="Time per Division:").grid(column=0, row=2)
        self.timecb = ttk.Combobox(self.frame, values=['50', '20', '10', '5', '2', '1', '.5', '.2', '.1'], width=5)
        self.timecb.bind('<<ComboboxSelected>>', self.__onselecttime__)
        self.timecb.grid(column=1, row=2)
        self.timecb.current(0)

        # time unit selectors
        self.timeunitcb = ttk.Combobox(self.frame, values=['s', 'ms', 'us'], width=5)
        self.timeunitcb.grid(column=2, row=2)
        self.timeunitcb.bind('<<ComboboxSelected>>', self.parent.update_fig)
        self.timeunitcb.current(1)

        # voltage selector CH1
        tk.Label(self.frame, text="Volts per Division (CH1):").grid(column=0, row=3)
        self.voltch1cb = ttk.Combobox(self.frame, values=self.voltage_names, width=5)
        self.voltch1cb.grid(column=1, row=3)
        self.voltch1cb.current(2)
        self.voltch1cb.bind('<<ComboboxSelected>>', self.parent.update_fig)

        # voltage selector CH2
        tk.Label(self.frame, text="Volts per Division (CH2):").grid(column=0, row=4)
        self.voltch2cb = ttk.Combobox(self.frame, values=self.voltage_names, width=5)
        self.voltch2cb.grid(column=1, row=4)
        self.voltch2cb.current(2)
        self.voltch2cb.bind('<<ComboboxSelected>>', self.parent.update_fig)

        # voltage selector REF1
        tk.Label(self.frame, text="Volts per Division (REF1):").grid(column=0, row=5)
        self.voltref1cb = ttk.Combobox(self.frame, values=self.voltage_names, width=5)
        self.voltref1cb.grid(column=1, row=5)
        self.voltref1cb.current(2)
        self.voltref1cb.bind('<<ComboboxSelected>>', self.parent.update_fig)

        # voltage selector REF2
        tk.Label(self.frame, text="Volts per Division (REF2):").grid(column=0, row=6)
        self.voltref2cb = ttk.Combobox(self.frame, values=self.voltage_names, width=5)
        self.voltref2cb.grid(column=1, row=6)
        self.voltref2cb.current(2)
        self.voltref2cb.bind('<<ComboboxSelected>>', self.parent.update_fig)

        # voltage offset CH1
        self.voltch1offcb = ttk.Combobox(self.frame, values=self.grid_names, width=5)
        self.voltch1offcb.grid(column=2, row=3)
        self.voltch1offcb.current(4)
        self.voltch1offcb.bind('<<ComboboxSelected>>', self.updaterawoffsetsandfig)

        # voltage offset CH2
        self.voltch2offcb = ttk.Combobox(self.frame, values=self.grid_names, width=5)
        self.voltch2offcb.grid(column=2, row=4)
        self.voltch2offcb.current(4)
        self.voltch2offcb.bind('<<ComboboxSelected>>', self.updaterawoffsetsandfig)

        # voltage offset REF1
        self.voltref1offcb = ttk.Combobox(self.frame, values=self.grid_names, width=5)
        self.voltref1offcb.grid(column=2, row=5)
        self.voltref1offcb.current(4)
        self.voltref1offcb.bind('<<ComboboxSelected>>', self.updaterawoffsetsandfig)

        # voltage offset REF2
        self.voltref2offcb = ttk.Combobox(self.frame, values=self.grid_names, width=5)
        self.voltref2offcb.grid(column=2, row=6)
        self.voltref2offcb.current(4)
        self.voltref2offcb.bind('<<ComboboxSelected>>', self.updaterawoffsetsandfig)


        # get voltage offset buttons
        self.getoffsetch1btn = tk.Button(self.frame,text="get", command=lambda: (self.readinoffsets(ch='CH1')))
        self.getoffsetch1btn.grid(column=3,row=3)

        self.getoffsetch2btn = tk.Button(self.frame,text="get", command=lambda: (self.readinoffsets(ch='CH2')))
        self.getoffsetch2btn.grid(column=3,row=4)

        self.getoffsetref1btn = tk.Button(self.frame,text="get", command=lambda: (self.readinoffsets(ch='REF1')))
        self.getoffsetref1btn.grid(column=3,row=5)

        self.getoffsetref2btn = tk.Button(self.frame,text="get", command=lambda: (self.readinoffsets(ch='REF2')))
        self.getoffsetref2btn.grid(column=3,row=6)


        # button to read from oscilloscope
        self.buttonreadsingle = tk.Button(self.frame, text="Read from scope", command=lambda: (self.parent.readfromoszi(mode='R')))
        self.buttonreadsingle.grid(column=0, row=7, columnspan=2, sticky=tk.W + tk.E)

        self.buttonreadsingleshot = tk.Button(self.frame, text="Reset Single-Shot + Read",
                                              command=lambda: (self.parent.readfromoszi(mode='S')))
        self.buttonreadsingleshot.grid(column=0, row=8, columnspan=2, sticky=tk.W + tk.E)

        tk.Label(self.frame, text="Things to save:").grid(column=0, row=9)
        self.saverawlogcb = tk.Checkbutton(self.frame,text="raw log", variable=self.saverawlog)
        self.saverawlogcb.grid(column=1, row=11)
        self.savecsvcb = tk.Checkbutton(self.frame,text="csv", variable=self.savecsv)
        self.savecsvcb.grid(column=1, row=10)
        self.saveimgcb = tk.Checkbutton(self.frame,text="png", variable=self.saveimg)
        self.saveimgcb.grid(column=2, row=10)

        self.savebutton = tk.Button(self.frame,text="Save", command=self.parent.savemanual)
        self.savebutton.grid(column=0, row=11)

        self.saveimgcb = tk.Checkbutton(self.frame,text="save automatically", variable=self.autosave)
        self.saveimgcb.grid(column=0, row=10)

        self.frame.grid(column=0,row=0,sticky=tk.N)
        return