import serial
import os
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
import serial.tools.list_ports
import hameghm1007

ser = serial.Serial()


def serial_ports():
    return serial.tools.list_ports.comports()


class App:
    comport = ''
    voltages = [5, 2, 1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005]
    times = [50, 20, 10, 5, 2, 1, 0.5, 0.2, 0.1]
    time_units = [1, 1e-3, 1e-6]
    voltage_names = ['5V', '2V', '1V', '.5V', '.2V', '.1V', '50mV', '20mV', '10mV', '5mV']
    grid_names = ['+4', '+3', '+2', '+1', '0', '-1', '-2', '-3', '-4']


    def browse_button(self):
        # Allow user to select a directory and store it in global var
        # called folder_path
        newfolder = filedialog.askdirectory()
        if (newfolder != ''):
            os.chdir(newfolder)
        # print(folderdir.get())
        self.folderdir.set(os.getcwd())

    def on_select_com_port(self, event=None):

        # or get selection directly from combobox
        self.comport = self.comcb.get().split()[0]
        ser.close()
        ser.port = self.comport  # COM port of arduino
        ser.baudrate = 250000
        ser.open()
        print("connected to"+self.comport)

    def on_select_time(self, event=None):
        if self.timecb.current() > 3:
            if self.timeunitcb.current() == 2:
                self.timeunitcb.set('')
            self.timeunitcb['values'] = ['s', 'ms']
        else:
            self.timeunitcb['values'] = ['s', 'ms', 'us']

    def updateserialports(self):
        self.comcb['values'] = serial_ports()

    def readfromoszi(self, mode='r'):
        if self.comport == '':
            print("Please select comport first")
            return
        if self.voltch1cb.current() == -1:
            print("Please set Voltage per Division first")
            return
        if self.timeunitcb.current() == -1:
            print("Please set time unit first")
            return
        if self.timecb.current() == -1:
            print("Please set time value first")
            return

        hameghm1007.readfromoszi(ser=ser, mod=mode, directory=self.folderdir,
                                 timeres=self.times[self.timecb.current()] * self.time_units[
                                     self.timeunitcb.current()] / 200,
                                 ch1res=self.voltages[self.voltch1cb.current()] / 25,
                                 ch2res=self.voltages[self.voltch2cb.current()] / 25,
                                 ref1res=self.voltages[self.voltref1cb.current()] / 25,
                                 ref2res=self.voltages[self.voltref2cb.current()] / 25,
                                 ch1off=127 - 25 * (self.voltch1offcb.current() - 4),
                                 ch2off=127 - 25 * (self.voltch2offcb.current() - 4))
        return

    def __init__(self, master):
        root.title("HAMEG HM1007 interface")
        root.geometry("400x250")
        self.folderdir = tk.StringVar()
        self.folderdir.set(os.getcwd())
        self.saverawlog = tk.IntVar(value=1)
        self.savecsv = tk.IntVar(value=1)
        self.saveimg = tk.IntVar(value=1)

        # Combobox for selecting right serial port
        tk.Label(root, text="Serial port:").grid(column=0, row=0)
        self.comcb = ttk.Combobox(root, values=serial_ports(), postcommand=self.updateserialports, width=10)
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
        self.timeunitcb.current(1)

        # voltage selector CH1
        tk.Label(root, text="Volts per Division (CH1):").grid(column=0, row=2)
        self.voltch1cb = ttk.Combobox(root, values=self.voltage_names, width=5)
        self.voltch1cb.grid(column=1, row=2)

        # voltage selector CH2
        tk.Label(root, text="Volts per Division (CH2):").grid(column=0, row=3)
        self.voltch2cb = ttk.Combobox(root, values=self.voltage_names, width=5)
        self.voltch2cb.grid(column=1, row=3)

        # voltage selector REF1
        tk.Label(root, text="Volts per Division (REF1):").grid(column=0, row=4)
        self.voltref1cb = ttk.Combobox(root, values=self.voltage_names, width=5)
        self.voltref1cb.grid(column=1, row=4)

        # voltage selector REF2
        tk.Label(root, text="Volts per Division (REF2):").grid(column=0, row=5)
        self.voltref2cb = ttk.Combobox(root, values=self.voltage_names, width=5)
        self.voltref2cb.grid(column=1, row=5)

        # voltage offset CH1
        self.voltch1offcb = ttk.Combobox(root, values=self.grid_names, width=5)
        self.voltch1offcb.grid(column=2, row=2)
        self.voltch1offcb.current(4)

        # voltage offset CH2
        self.voltch2offcb = ttk.Combobox(root, values=self.grid_names, width=5)
        self.voltch2offcb.grid(column=2, row=3)
        self.voltch2offcb.current(4)

        # voltage offset REF1
        self.voltref1offcb = ttk.Combobox(root, values=self.grid_names, width=5)
        self.voltref1offcb.grid(column=2, row=4)
        self.voltref1offcb.current(4)

        # voltage offset REF2
        self.voltref2offcb = ttk.Combobox(root, values=self.grid_names, width=5)
        self.voltref2offcb.grid(column=2, row=5)
        self.voltref2offcb.current(4)

        # button to read from oscilloscope
        self.buttonreadsingle = tk.Button(root, text="Read from scope", command=lambda: (self.readfromoszi(mode='R')))
        self.buttonreadsingle.grid(column=0, row=6, columnspan=2, sticky=tk.W + tk.E)

        self.folderlabel = tk.Label(root, textvariable=self.folderdir, width=30)
        self.folderlabel.grid(column=0, row=7, columnspan=3, sticky=tk.W + tk.E)

        self.buttonbrowsefolder = tk.Button(text="Browse", command=self.browse_button)
        self.buttonbrowsefolder.grid(column=3, row=7)

        tk.Label(root, text="Things to save:").grid(column=0, row=8)
        self.saverawlogcb = tk.Checkbutton(text="raw log",variable=self.saverawlog)
        self.saverawlogcb.grid(column=0,row=9)
        self.savecsvcb = tk.Checkbutton(text="csv",variable=self.savecsv)
        self.savecsvcb.grid(column=1,row=9)
        self.saveimgcb = tk.Checkbutton(text="png",variable=self.saveimg)
        self.saveimgcb.grid(column=2,row=9)


root = tk.Tk()
app = App(root)
root.mainloop()
