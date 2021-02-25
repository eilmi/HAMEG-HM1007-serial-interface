import tkinter as tk
from tkinter import ttk

import serial


class SettingsWindow(tk.Frame):
    """
    Left upper part of the main window
    includes all changeable parameters off the signal
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

        :return:
        """
        self.comcb['values'] = self.get_serial_port_list()



    def __init__(self, parent, *args, **kwargs):

        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.frame = tk.Frame(self.parent)

        self.saverawlog = tk.IntVar(value=1)
        self.savecsv = tk.IntVar(value=1)
        self.saveimg = tk.IntVar(value=1)
        self.autosave = tk.IntVar(value=1)

        # Combobox for selecting right serial port
        tk.Label(self.frame, text="Serial port:").grid(column=0, row=0)
        self.comcb = ttk.Combobox(self.frame, values=self.get_serial_port_list(), postcommand=self.updateserialports, width=10)
        self.comcb.grid(row=0, column=1)
        self.comcb.bind('<<ComboboxSelected>>', self.parent.on_select_com_port)

        # time selector
        tk.Label(self.frame, text="Time per Division:").grid(column=0, row=1)
        self.timecb = ttk.Combobox(self.frame, values=['50', '20', '10', '5', '2', '1', '.5', '.2', '.1'], width=5)
        self.timecb.bind('<<ComboboxSelected>>', self.parent.on_select_time)
        self.timecb.grid(column=1, row=1)
        self.timecb.current(0)

        # time unit selectorS
        self.timeunitcb = ttk.Combobox(self.frame, values=['s', 'ms', 'us'], width=5)
        self.timeunitcb.grid(column=2, row=1)
        self.timeunitcb.bind('<<ComboboxSelected>>', self.parent.update_fig)
        self.timeunitcb.current(1)

        # voltage selector CH1
        tk.Label(self.frame, text="Volts per Division (CH1):").grid(column=0, row=2)
        self.voltch1cb = ttk.Combobox(self.frame, values=self.voltage_names, width=5)
        self.voltch1cb.grid(column=1, row=2)
        self.voltch1cb.current(2)
        self.voltch1cb.bind('<<ComboboxSelected>>', self.parent.update_fig)

        # voltage selector CH2
        tk.Label(self.frame, text="Volts per Division (CH2):").grid(column=0, row=3)
        self.voltch2cb = ttk.Combobox(self.frame, values=self.voltage_names, width=5)
        self.voltch2cb.grid(column=1, row=3)
        self.voltch2cb.current(2)
        self.voltch2cb.bind('<<ComboboxSelected>>', self.parent.update_fig)

        # voltage selector REF1
        tk.Label(self.frame, text="Volts per Division (REF1):").grid(column=0, row=4)
        self.voltref1cb = ttk.Combobox(self.frame, values=self.voltage_names, width=5)
        self.voltref1cb.grid(column=1, row=4)
        self.voltref1cb.current(2)
        self.voltref1cb.bind('<<ComboboxSelected>>', self.parent.update_fig)

        # voltage selector REF2
        tk.Label(self.frame, text="Volts per Division (REF2):").grid(column=0, row=5)
        self.voltref2cb = ttk.Combobox(self.frame, values=self.voltage_names, width=5)
        self.voltref2cb.grid(column=1, row=5)
        self.voltref2cb.current(2)
        self.voltref2cb.bind('<<ComboboxSelected>>', self.parent.update_fig)

        # voltage offset CH1
        self.voltch1offcb = ttk.Combobox(self.frame, values=self.grid_names, width=5)
        self.voltch1offcb.grid(column=2, row=2)
        self.voltch1offcb.current(4)
        self.voltch1offcb.bind('<<ComboboxSelected>>', self.parent.update_fig)

        # voltage offset CH2
        self.voltch2offcb = ttk.Combobox(self.frame, values=self.grid_names, width=5)
        self.voltch2offcb.grid(column=2, row=3)
        self.voltch2offcb.current(4)
        self.voltch2offcb.bind('<<ComboboxSelected>>', self.parent.update_fig)

        # voltage offset REF1
        self.voltref1offcb = ttk.Combobox(self.frame, values=self.grid_names, width=5)
        self.voltref1offcb.grid(column=2, row=4)
        self.voltref1offcb.current(4)
        self.voltref1offcb.bind('<<ComboboxSelected>>', self.parent.update_fig)

        # voltage offset REF2
        self.voltref2offcb = ttk.Combobox(self.frame, values=self.grid_names, width=5)
        self.voltref2offcb.grid(column=2, row=5)
        self.voltref2offcb.current(4)
        self.voltref2offcb.bind('<<ComboboxSelected>>', self.parent.update_fig)

        # button to read from oscilloscope
        self.buttonreadsingle = tk.Button(self.frame, text="Read from scope", command=lambda: (self.parent.readfromoszi(mode='R')))
        self.buttonreadsingle.grid(column=0, row=6, columnspan=2, sticky=tk.W + tk.E)

        self.buttonreadsingleshot = tk.Button(self.frame, text="Reset Single-Shot + Read",
                                              command=lambda: (self.parent.readfromoszi(mode='S')))
        self.buttonreadsingleshot.grid(column=0, row=7, columnspan=2, sticky=tk.W + tk.E)

        tk.Label(self.frame, text="Things to save:").grid(column=0, row=8)
        self.saverawlogcb = tk.Checkbutton(self.frame,text="raw log", variable=self.saverawlog)
        self.saverawlogcb.grid(column=0, row=9)
        self.savecsvcb = tk.Checkbutton(self.frame,text="csv", variable=self.savecsv)
        self.savecsvcb.grid(column=1, row=9)
        self.saveimgcb = tk.Checkbutton(self.frame,text="png", variable=self.saveimg)
        self.saveimgcb.grid(column=2, row=9)

        self.savebutton = tk.Button(self.frame,text="Save", command=self.parent.savemanual)
        self.savebutton.grid(column=0, row=10)

        self.saveimgcb = tk.Checkbutton(self.frame,text="save automatically", variable=self.autosave)
        self.saveimgcb.grid(column=1, row=10)

        self.frame.grid(column=0,row=0,sticky=tk.N)
        return