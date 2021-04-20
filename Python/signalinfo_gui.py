import tkinter as tk
import matplotlib.pylab as plt
import numpy as np
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class SignalInfoFrame(tk.Frame):
    """
    signal info subframe of the main window
    """

    def __init__(self, parent, *args, **kwargs):
        """
        initialization of signal info part of GUI
        :param parent: main window
        :param args: not used
        :param kwargs: not used
        """

        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.frame = tk.Frame(self.parent)

        #variables
        self.channelselframe = tk.Frame(self.frame)
        self.channelselector = tk.IntVar()
        self.signalfreq = tk.StringVar()
        self.signaldcoffset = tk.StringVar()
        self.signalperiod = tk.StringVar()
        self.signaldutycycle = tk.StringVar()
        self.values = {"CH1": "0", "CH2": "1", "REF1": "2", "REF2": "3"}
        self.rbt=[]

        tk.Label(self.frame,font=("Arial", 18), text="Signal information:").grid(column=0, row=0,columnspan=2)

        for (text, value) in self.values.items():
            rb = tk.Radiobutton(self.channelselframe, text=text, variable=self.channelselector,
                        value=value,command=self.update_infos)
            rb.grid(row=1, column=int(value))
            self.rbt.append(rb)

        self.channelselframe.grid(column=0,columnspan=2, row=1)

        tk.Label(self.frame,text="frequency:").grid(column=0,columnspan=1,row=2)
        tk.Label(self.frame,text="period time:").grid(column=0,columnspan=1,row=3)
        tk.Label(self.frame,text="DC-offset:").grid(column=0,columnspan=1,row=4)
        tk.Label(self.frame,text="duty-cycle:").grid(column=0,row=5)

        tk.Label(self.frame,textvariable=self.signalfreq).grid(column=1,row=2)
        tk.Label(self.frame,textvariable=self.signaldcoffset).grid(column=1,row=4)
        tk.Label(self.frame,textvariable=self.signalperiod).grid(column=1,row=3)
        tk.Label(self.frame,textvariable=self.signaldutycycle).grid(column=1,row=5)

        self.frame.grid(column=0,row=1,sticky=tk.N)

        return

    def calc_duty_cycle(self,signal):
        """
        Calculates the duty cycle of a signal between all found zero crossings

        To ensure all zero crossing are detected, this function shifts the signal in such a way
        that the maximum and the minimum of it is spread evenly around 0

        :param signal: signal of which the duty cycle should be determined
        :return: array of all calculated duty cycles
        """
        signal = signal - (np.min(signal) + (np.max(signal) - np.min(signal)) / 2)
        zero_crossings = np.where(np.diff(np.signbit(signal)))[0]
        #print(zero_crossings)
        duty_cycles = []
        for i in range(0, len(zero_crossings) - 2):
            middle1 = zero_crossings[i] + int((zero_crossings[i + 1] - zero_crossings[i]) / 2)
            # middle2=zero_crossings[i+1]+int((zero_crossings[i+2]-zero_crossings[i+1])/2)
            dc = (zero_crossings[i + 1] - zero_crossings[i]) / (zero_crossings[i + 2] - zero_crossings[i])
            if (signal[middle1] < 0):
                dc = 1 - dc
            duty_cycles.append(dc)
        return duty_cycles

    def addprefix(self,number,unit,printprec):
        """
        Returns a String consisting of the given value converted into a prefix + SI conform format + given unit
        for example 0.030 will be converted into 30m + unit
        :param number: value which should be converted
        :param unit: suffix will be added to the string
        :param printprec: number of decimal places
        :return:
        """
        a_number = np.abs(number)
        if a_number<1e-6:
            return str(round(number*1e9,printprec))+'n'+unit
        elif a_number<1e-3:
            return str(round(number*1e6,printprec))+'µ'+unit
        elif a_number<1:
            return str(round(number*1e3,printprec))+'m'+unit
        elif a_number<1e3:
            return str(round(number,printprec))+unit
        elif a_number<1e6:
            return str(round(number*1e-3,printprec))+'k'+unit
        elif a_number<1e9:
            return str(round(number*1e-6,printprec))+'M'+unit
        else:
            return "false"

    def update_infos(self):
        """
        update the values of the signal info subframe
        :return:
        """
        # Check which channels are present in the loaded data
        self.rbt[0]["state"] = tk.NORMAL if "CH1" in self.parent.dataframe else tk.DISABLED
        self.rbt[1]["state"] = tk.NORMAL if "CH2" in self.parent.dataframe else tk.DISABLED
        self.rbt[2]["state"] = tk.NORMAL if "REF1" in self.parent.dataframe else tk.DISABLED
        self.rbt[3]["state"] = tk.NORMAL if "REF2" in self.parent.dataframe else tk.DISABLED

        channelname=(list(self.values.items())[self.channelselector.get()][0]) # get name of selected channel
        if channelname in self.parent.fftframe: #check if data for this channel is available
            self.signaldcoffset.set(self.addprefix(np.real(self.parent.fftframe[channelname][0]),"V",3)) # get DC-offset out of FFT
            #Look for biggest peak in FFT and get the frequency of it
            freqency = self.parent.fftframe["freq"][1+np.abs(self.parent.fftframe[channelname][1:1024]).argmax()]
            self.signalfreq.set(self.addprefix(np.abs(freqency),"Hz",3))
            self.signalperiod.set(self.addprefix(1/np.abs(freqency),"s",3))

            #Calculate Duty Cycles
            signal = self.parent.dataframe[channelname]
            duty_cycles = self.calc_duty_cycle(signal)

            self.signaldutycycle.set(str(np.mean(duty_cycles)*100)+"%")
            #print(np.abs(freqency),self.addprefix(np.abs(freqency),"Hz",3))



        return
