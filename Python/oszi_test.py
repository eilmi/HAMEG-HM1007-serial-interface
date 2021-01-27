import serial
import time
import os
import csv
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ser = serial.Serial()
ser.port = 'COM7'
ser.baudrate=250000

ser.open()
time.sleep(2)


print("connected to: " + ser.portstr)
count=1

ser.write(b'R') 
data=[]
while 1:
    inp = ser.readline()
    inp = inp.rstrip().decode()
    if inp=="END":
        break
    else:
        data.append(inp)


#data = ser.readlines()

ser.close()

#for i in range(len(data)):
#    data[i]=data[i].rstrip().decode()

begin_CH1=data.index("CH1")
begin_CH2=data.index("CH2")
begin_Ref1=data.index("REF1")
begin_Ref2=data.index("REF2")

ch1_data=np.array(data[begin_CH1+1:begin_CH2]).astype(np.int)
ch2_data=np.array(data[begin_CH2+1:begin_Ref1]).astype(np.int)
ref1_data=np.array(data[begin_Ref1+1:begin_Ref2]).astype(np.int)
ref2_data=np.array(data[begin_Ref2+1:]).astype(np.int)

with open('rawdata.txt', 'w') as f:
    for item in data:
        f.write("%s\n" % item)


if (np.size(ch2_data)==2048):
    if (np.size(ref1_data)==2048):
        combined_data=np.vstack((ch1_data,ch2_data,ref1_data,ref2_data)).T
        testframe=pd.DataFrame(combined_data,columns=['CH1', 'CH2', 'REF1','REF2'])
    else:
        combined_data=np.vstack((ch1_data,ch2_data)).T
        testframe=pd.DataFrame(combined_data,columns=['CH1', 'CH2'])
else:
    if (np.size(ref1_data)==2048):
        combined_data=np.vstack((ch1_data,ref1_data)).T
        testframe=pd.DataFrame(combined_data,columns=['CH1', 'REF1'])
    else:
        combined_data=np.vstack((ch1_data,)).T
        testframe=pd.DataFrame(combined_data,columns=['CH1'])



testframe.to_csv('pandas_dataframe.csv',index=False,header=True)


fig, ax = plt.subplots()
ax.plot(ch1_data)
ax.plot(ch2_data)
ax.plot(ref1_data)
ax.plot(ref2_data)

# XY-Plot
#ax.plot(ch2_data,ch1_data)

ax.set(xlabel='time', ylabel='Volts',
       title='Data from Hameg HM1007')
ax.grid()
ax.set_xlim(0, 2047)
ax.set_ylim(0,255)
fig.savefig("test.png")
plt.show()