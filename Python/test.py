import serial
import os
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
import serial.tools.list_ports
import hameghm1007
from datetime import datetime, time
import time

ser = serial.Serial()

data = hameghm1007.readfromfile('test.txt')
ch1, ch2, ref1, ref2 = hameghm1007.createnumpyarrays(data)
dateframe = hameghm1007.createpandasframe(ch1, ch2, ref1, ref2)

fig = hameghm1007.makeplot(data, ch1, ch2, ref1, ref2,timeres=1,ch1res=1,ch2res=1,ref1res=1,ref2res=1)

hameghm1007.save(os.getcwd(),datetime.now(),data,dateframe,fig)

time.sleep(10)

print("Ende")