import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
import time
from scipy import fftpack

oscilloscopemodel = ''
horizontalresolution = None

def __storescopemodel(serialdata):
    """
    reads serial data received from the microcontroller and stores received oscilloscope type
    :return: 
    """
    global oscilloscopemodel
    global horizontalresolution
    if serialdata[0]=="HM-1007":
        oscilloscopemodel="HM-1007"
        horizontalresolution=2048
    elif serialdata[0]=="HM-205":
        oscilloscopemodel="HM-205"
        horizontalresolution=1024
    else:
        oscilloscopemodel="unknown"
        horizontalresolution=2048
        
    return

def readfromfile(filename,setModel=True):
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
    if setModel:
        __storescopemodel(line)
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
        ser.write(b'S') #Reset Single-Shot trigger before reading data from oscilloscope

    data = []
    while 1:
        inp = ser.readline()
        inp = inp.rstrip().decode()
        if inp == "END":
            break
        else:
            data.append(inp)
    __storescopemodel(data)
    return data

def readmodelfromInterface(ser=None):
    """
    """
    print("Writing m to interface")
    ser.write(b'm')
    __storescopemodel([ser.readline().rstrip().decode()])
    return


#def createpandasframe(data, timeres=1, ch1off=0, ch1res=1, ch2off=0, ch2res=1,
#                      ref1off=0, ref1res=1, ref2off=0, ref2res=1):
def createpandasframe(data, timeres=1, resolutions=[],offsets=[]):
    """
    Generates the pandas dataframe out of the raw serial input stream.
    :param data: raw serial values
    :param timeres: sampling rate (in seconds) of the channels
    :param ch1off: offset of CH1 in bits (raw value)
    :param ch1res: resolution of CH1 in V/bit
    :param ch2off: offset of CH2 in bits (raw value)
    :param ch2res: resolution of CH2 in V/bit
    :param ref1off:  
    :param ref1res:
    :param ref2off:
    :param ref2res:
    :return:
    """
    # get starting position of all 4 2048 or 1024 byte long data blocks
    try:
        begin_CH1 = data.index("CH1")
        begin_CH2 = data.index("CH2")
        begin_Ref1 = data.index("REF1")
        begin_Ref2 = data.index("REF2")
    except ValueError:
        print("invalid serial data - couldnt create numpy arrays")
        return []

    # convert before created data array into 4 numpy arrays each containing one channel of oscilloscope
    time_data = np.arange(horizontalresolution) * timeres
    ch1_data = (np.array(data[begin_CH1 + 1:begin_CH2]).astype(np.int) - offsets[0]) * resolutions[0]
    ch2_data = (np.array(data[begin_CH2 + 1:begin_Ref1]).astype(np.int) - offsets[1]) * resolutions[1]
    ref1_data = (np.array(data[begin_Ref1 + 1:begin_Ref2]).astype(np.int) - offsets[2]) * resolutions[2]
    ref2_data = (np.array(data[begin_Ref2 + 1:]).astype(np.int) - offsets[3])* resolutions[3]

    #create pandas dataframe with all valid data
    pandasframe = pd.DataFrame()
    if np.size(ch1_data) == horizontalresolution and np.size(ch2_data) == horizontalresolution:
        if np.size(ref1_data) == horizontalresolution:
            combined_data = np.vstack((time_data, ch1_data, ch2_data, ref1_data, ref2_data)).T
            pandasframe = pd.DataFrame(combined_data, columns=['time', 'CH1', 'CH2', 'REF1', 'REF2'])
        else:
            combined_data = np.vstack((time_data, ch1_data, ch2_data)).T
            pandasframe = pd.DataFrame(combined_data, columns=['time', 'CH1', 'CH2'])


    elif (np.size(ch1_data) == horizontalresolution and np.size(ch2_data) != horizontalresolution):
        if np.size(ref1_data) == horizontalresolution:
            combined_data = np.vstack((time_data, ch1_data, ref1_data)).T
            pandasframe = pd.DataFrame(combined_data, columns=['time', 'CH1', 'REF1'])
        else:
            combined_data = np.vstack((time_data, ch1_data)).T
            pandasframe = pd.DataFrame(combined_data, columns=['time', 'CH1'])
    elif (np.size(ch1_data) != horizontalresolution and np.size(ch2_data) == horizontalresolution):
        if (np.size(ref2_data) == horizontalresolution):
            combined_data = np.vstack((time_data, ch2_data, ref2_data)).T
            pandasframe = pd.DataFrame(combined_data, columns=['time', 'CH2', 'REF2'])
        else:
            combined_data = np.vstack((time_data, ch2_data,)).T
            pandasframe = pd.DataFrame(combined_data, columns=['time', 'CH2'])

    return pandasframe


def makeplot(data, dataframe):
    """
    generate and returns a matplotlib figure containing all available channels

    :param data: only needed to check if data is XY-Plot
    :param dataframe: contains the data of all available channels
    :return: matplotlib figure
    """
    fig, ax = plt.subplots()

    if "XY-Plot" in data:
        ax.plot(dataframe.CH2.tolist(), dataframe.CH1.tolist())
    else:
        if "CH1" in dataframe:
            ax.plot(dataframe["time"], dataframe["CH1"])
        if "CH2" in dataframe:
            ax.plot(dataframe["time"], dataframe["CH2"])
        if "REF1" in dataframe:
            ax.plot(dataframe["time"], dataframe["REF1"])
        if "REF2" in dataframe:
            ax.plot(dataframe["time"], dataframe["REF2"])

    ax.set(xlabel='time [s]', ylabel='Volts',
           title='Data from Hameg HM1007')
    ax.grid()

    # plt.show()
    return fig,ax


def save(directory, now, data, dataframe):
    """
    creates a new folder in the given directory and saves the data in various forms
    generates a CSV file and a PNG picture while also saving the raw serial message from the Interface (Arduino)

    :return: True when everything could be saved
    """
    fig, ax = makeplot(data, dataframe)
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


def __calc_fft(data, time_interval):
    """
    internal function used to calculate the fft

    :param data: data on which the fft should be performed
    :param time_interval: time interval between two data points
    """
    f_s = 1 / time_interval

    try:
        X = fftpack.fft(data)
        X[0] = X[0] / 2
        freqs = fftpack.fftfreq(len(data)) * f_s

    except ValueError:
        print("No data for FFT")
        return False
    except TypeError:
        print("No data for FFT")
        return False

    return X,freqs

def calc_fftdataframe(dataframe,samplinginterval):
    """
    Calculate the fast fourier transform of all channels stored in the dataframe

    :param dataframe: Pandas dataframe containing signal information
    :param samplinginterval: interval between two signal samples
    :return:
    """
    fftframe = pd.DataFrame()

    for column in dataframe: # calculate fft for each channel in dataframe (CH1,CH2,REF1,REF2)
        if column=="time":
            continue
        X, freqs = __calc_fft(dataframe[column].tolist(),samplinginterval)
        X = X * 2 / len(dataframe[column].tolist())
        if "freq" not in fftframe:
            fftframe['freq'] = freqs
        fftframe[column] = X

    return fftframe


