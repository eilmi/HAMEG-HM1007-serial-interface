import serial
import time
import os
import csv
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
import time


def readfromfile(filename):
    """
    read the data normally received from the oscilloscope out of a text file
    these text files are be default created when scope data is saved
    :param filename: name of the to be loaded file
    :return: oscilloscope data list
    """
    line = []
    with open(filename) as fp:
        for l in fp:
            line.append(l.strip())
    fp.close()
    return line


def readfromoszi(ser=None, mod='R'):
    """
    :param ser: already connected serial object
    :param mod: whether 'R' for normal data gathering or 'S' for single-shot reset and data gathering
    :return: oscilloscope data list
    """
    print("getting data from: " + ser.portstr)
    if (mod == 'R'):
        ser.write(b'R')
    elif (mod == 'S'):
        ser.write(b'S')
        # ser.write(b'S') #Reset Single-Shot trigger before reading data from oscilloscope

    data = []
    while 1:
        inp = ser.readline()
        inp = inp.rstrip().decode()
        if inp == "END":
            break
        else:
            data.append(inp)
    return data


def createnumpyarrays(data, timeres=1, ch1off=0, ch1res=1, ch2off=0, ch2res=1,
                      ref1off=0, ref1res=1, ref2off=0, ref2res=1):
    # get starting position of all 4 2048 byte long data blocks
    try:
        begin_CH1 = data.index("CH1")
        begin_CH2 = data.index("CH2")
        begin_Ref1 = data.index("REF1")
        begin_Ref2 = data.index("REF2")
    except ValueError:
        print("invalid serial data - couldnt create numpy arrays")
        return [], [], [], [], []

    # convert before created data array into 4 numpy arrays each containing one channel of oscilloscope
    time_data = np.arange(2048) * timeres
    ch1_data = (np.array(data[begin_CH1 + 1:begin_CH2]).astype(np.int) - ch1off) * ch1res
    # ch1_data = np.array(data[begin_CH1 + 1:begin_CH2]).astype(np.int)
    # ch2_data = np.array(data[begin_CH2 + 1:begin_Ref1]).astype(np.int)
    ch2_data = (np.array(data[begin_CH2 + 1:begin_Ref1]).astype(np.int) - ch2off) * ch2res
    ref1_data = np.array(data[begin_Ref1 + 1:begin_Ref2]).astype(np.int)
    ref2_data = np.array(data[begin_Ref2 + 1:]).astype(np.int)

    return time_data, ch1_data, ch2_data, ref1_data, ref2_data


def createpandasframe(time_data, ch1_data, ch2_data, ref1_data, ref2_data):
    # Create pandas dataframe only with valid data
    testframe = pd.DataFrame()
    if np.size(ch1_data) == 2048 and np.size(ch2_data) == 2048:
        if np.size(ref1_data) == 2048:
            combined_data = np.vstack((time_data, ch1_data, ch2_data, ref1_data, ref2_data)).T
            testframe = pd.DataFrame(combined_data, columns=['time', 'CH1', 'CH2', 'REF1', 'REF2'])
        else:
            combined_data = np.vstack((time_data, ch1_data, ch2_data)).T
            testframe = pd.DataFrame(combined_data, columns=['time', 'CH1', 'CH2'])


    elif (np.size(ch1_data) == 2048 and np.size(ch2_data) != 2048):
        if np.size(ref1_data) == 2048:
            combined_data = np.vstack((time_data, ch1_data, ref1_data)).T
            testframe = pd.DataFrame(combined_data, columns=['time', 'CH1', 'REF1'])
        else:
            combined_data = np.vstack((time_data, ch1_data)).T
            testframe = pd.DataFrame(combined_data, columns=['time', 'CH1'])
    elif (np.size(ch1_data) != 2048 and np.size(ch2_data) == 2048):
        if (np.size(ref2_data) == 2048):
            combined_data = np.vstack((time_data, ch2_data, ref2_data)).T
            testframe = pd.DataFrame(combined_data, columns=['time', 'CH2', 'REF2'])
        else:
            combined_data = np.vstack((time_data, ch2_data,)).T
            testframe = pd.DataFrame(combined_data, columns=['time', 'CH2'])

    return testframe


def makeplot(data, ch1_data, ch2_data, ref1_data, ref2_data, timearray):
    fig, ax = plt.subplots()

    if "XY-Plot" in data:
        ax.plot(ch2_data, ch1_data)
    else:
        if (np.size(ch1_data) == 2048):
            ax.plot(timearray, ch1_data)
        if (np.size(ch2_data) == 2048):
            ax.plot(timearray, ch2_data)
        if (np.size(ref1_data) == 2048):
            ax.plot(timearray, ref1_data)
        if (np.size(ref2_data) == 2048):
            ax.plot(timearray, ref2_data)
        # ax.plot(ch2_data,timearray)
        # ax.plot(ref1_data,timearray)
        # ax.plot(ref2_data,timearray)

    ax.set(xlabel='time [s]', ylabel='Volts',
           title='Data from Hameg HM1007')
    ax.grid()

    # plt.show()
    return fig


def save(directory, now, data, dataframe, fig):
    di = directory + now.strftime("\HM1007_export-%Y_%m_%d-%H_%M_%S")
    try:
        os.mkdir(di)
        os.chdir(di)
    except:
        print("Error creating folder occurred")
        return False

    filename = now.strftime("HM1007_raw-%Y_%m_%d-%H_%M_%S.txt")

    with open(filename, 'w') as f:
        for item in data:
            f.write("%s\n" % item)
    f.close()

    # Save pandas dataframe to csv file
    filename = now.strftime("HM1007_data-%Y_%m_%d-%H_%M_%S.csv")
    dataframe.to_csv(filename, index=False, header=True, float_format='%11.6f')

    filename = now.strftime("HM1007_plot-%Y_%m_%d-%H_%M_%S.png")
    fig.savefig(filename)
    return True
