import serial
import time
import os
import csv
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
import serial.tools.list_ports
from  datetime import datetime
import hameghm1007

ser = serial.Serial()

class App:
    fname=''
    comport=''
    voltages=[5,2,1,0.5,0.2,0.1,0.05,0.02,0.01,0.005]
    times=[50,20,10,5,2,1,0.5,0.2,0.1]
    time_units=[1,1e-3,1e-6]
    voltage_names=['5V','2V','1V','.5V','.2V','.1V','50mV','20mV','10mV','5mV']

    def browse_button(self):
        # Allow user to select a directory and store it in global var
        # called folder_path
        self.fname = filedialog.askdirectory()
        print(self.fname)


    def serial_ports(self):    
        return serial.tools.list_ports.comports()

    def on_select_com_port(self,event=None):

        # or get selection directly from combobox
        self.comport=self.comcb.get().split()[0]
        print(self.comport)
        #print("comboboxes: ", self.cb.get())


    def on_select_time(self,event=None):
        if (self.timecb.current()>3):
            if (self.timeunitcb.current()==2):
                self.timeunitcb.set('')
            self.timeunitcb['values']=['s','ms']
        else:
            self.timeunitcb['values']=['s','ms','us']
    

    def updateserialports(self):
        self.comcb['values'] = self.serial_ports()

    def readfromoszi(self):
        if self.comport=='':
            print("Please select comport first")
            return
        if self.voltch1cb.current()==-1:
            print("Please set Voltage per Division first")
            return
        if self.timeunitcb.current()==-1:
            print("Please set time unit first")
            return
        if self.timecb.current()==-1:
            print("Please set time value first")
            return
        
        hameghm1007.readfromoszi(ser,self.comport,timeres=self.times[self.timecb.current()]*self.time_units[self.timeunitcb.current()]/200,ch1res=self.voltages[self.voltch1cb.current()]/25,ch2res=self.voltages[self.voltch2cb.current()]/25,ref1res=self.voltages[self.voltref1cb.current()]/25,ref2res=self.voltages[self.voltref2cb.current()]/25)
        return
    def __init__(self, master):
        root.title("HAMGEG HM1007 interface")
        root.geometry("300x200")

        #Combibox for selecting right serial port
        tk.Label(root,text="Serial port:").grid(column=0,row=0)
        self.comcb = ttk.Combobox(root, values=self.serial_ports(), postcommand= self.updateserialports,width=10)
        self.comcb.grid(row=0,column=1)
        self.comcb.bind('<<ComboboxSelected>>', self.on_select_com_port)
        
        #time selector
        tk.Label(root,text="Time per Division:").grid(column=0,row=1)
        self.timecb = ttk.Combobox(root, values=['50','20','10','5','2','1','.5','.2','.1'],width=5)
        self.timecb.bind('<<ComboboxSelected>>', self.on_select_time)
        self.timecb.grid(column=1,row=1)

        #time unit selector
        self.timeunitcb = ttk.Combobox(root, values=['s','ms','us'],width=5)
        self.timeunitcb.grid(column=2,row=1)

        #voltage selector CH1
        tk.Label(root,text="Volts per Division (CH1):").grid(column=0,row=2)
        self.voltch1cb = ttk.Combobox(root, values=self.voltage_names,width=5)
        self.voltch1cb.grid(column=1,row=2)

        #voltage selector CH2
        tk.Label(root,text="Volts per Division (CH2):").grid(column=0,row=3)
        self.voltch2cb = ttk.Combobox(root, values=self.voltage_names,width=5)
        self.voltch2cb.grid(column=1,row=3)

        #voltage selector REF1
        tk.Label(root,text="Volts per Division (REF1):").grid(column=0,row=4)
        self.voltref1cb = ttk.Combobox(root, values=self.voltage_names,width=5)
        self.voltref1cb.grid(column=1,row=4)

        #voltage selector REF2
        tk.Label(root,text="Volts per Division (REF2):").grid(column=0,row=5)
        self.voltref2cb = ttk.Combobox(root, values=self.voltage_names,width=5)
        self.voltref2cb.grid(column=1,row=5)

        #button to read from oscilloscope
        self.buttonreadsingle = tk.Button(root,text="Read",command=self.readfromoszi)
        self.buttonreadsingle.grid(column=0,row=6)

        self.buttonbrowsefolder = tk.Button(text="Browse", command=self.browse_button)
        self.buttonbrowsefolder.grid(column=1,row=6)

root = tk.Tk()
app = App(root)
root.mainloop()