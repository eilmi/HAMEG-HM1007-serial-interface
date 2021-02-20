import serial
import time
import os
import csv
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
import hameghm1007

ser = serial.Serial()
ser.port = 'COM7' # COM port of arduino
ser.baudrate=250000


ser.open()
time.sleep(2) # is needed because the arduino resets itself each time a serial connection is established


print("connected to: " + ser.portstr)

ser.write(b'R') 
#ser.write(b'S') #Reset Single-Shot trigger before reading data from oscilloscope 

data=[]
while 1:
    inp = ser.readline()
    inp = inp.rstrip().decode()
    if inp=="END":
        break
    else:
        data.append(inp)

ser.close()# close serial 

#get starting position of all 4 2048 byte long data blocks
begin_CH1=data.index("CH1")
begin_CH2=data.index("CH2")
begin_Ref1=data.index("REF1")
begin_Ref2=data.index("REF2")

#convert before created data array into 4 numpy arrays each containing one channel of oscilloscope
ch1_data=np.array(data[begin_CH1+1:begin_CH2]).astype(np.int)
ch2_data=np.array(data[begin_CH2+1:begin_Ref1]).astype(np.int)
ref1_data=np.array(data[begin_Ref1+1:begin_Ref2]).astype(np.int)
ref2_data=np.array(data[begin_Ref2+1:]).astype(np.int)

#save raw serial output of arduino to text file
now = datetime.now()
filename =now.strftime("HM1007_raw-%Y_%m_%d-%H_%M_%S.txt")

with open(filename, 'w') as f:
    for item in data:
        f.write("%s\n" % item)


# Create pandas dataframe only with valid data
if (np.size(ch2_data)==2048): # CH2 data valid
    if (np.size(ref1_data)==2048): #REF data valid
        combined_data=np.vstack((ch1_data,ch2_data,ref1_data,ref2_data)).T
        testframe=pd.DataFrame(combined_data,columns=['CH1', 'CH2', 'REF1','REF2'])
    else: #REF data invalid
        combined_data=np.vstack((ch1_data,ch2_data)).T
        testframe=pd.DataFrame(combined_data,columns=['CH1', 'CH2'])
else: #CH2 data invalid
    if (np.size(ref1_data)==2048): #REF data valid
        combined_data=np.vstack((ch1_data,ref1_data)).T
        testframe=pd.DataFrame(combined_data,columns=['CH1', 'REF1'])
    else: 
        combined_data=np.vstack((ch1_data,)).T #REF data invalid
        testframe=pd.DataFrame(combined_data,columns=['CH1'])


# Save pandas dataframe to csv file
filename =now.strftime("HM1007_data-%Y_%m_%d-%H_%M_%S.csv")
testframe.to_csv(filename,index=False,header=True)

# Plot data with matplotlib
fig, ax = plt.subplots()

if "XY-Plot" in data:
    ax.plot(ch2_data,ch1_data)
else:
    ax.plot(ch1_data)
    ax.plot(ch2_data)
    ax.plot(ref1_data)
    ax.plot(ref2_data)

ax.set(xlabel='time', ylabel='value',
       title='Data from Hameg HM1007')
ax.grid()
ax.set_xlim(0, 2047)
ax.set_ylim(0,255)
filename =now.strftime("HM1007_plot-%Y_%m_%d-%H_%M_%S.png")
fig.savefig(filename)
plt.show()


