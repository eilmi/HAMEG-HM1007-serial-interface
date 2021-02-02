# Serial interface for Hameg HM1007
## Introduction
This repository contains all the needed code to get the data from a HAMEG HM1007 oscilloscope. The core of this interface is an Arduino Nano which is used to communicate with the oscilloscope via it's HO79-4 interface.
## Flashing the Arduino
Alttough the code for the microcontroller was written in *PlatformIO* copying the content of `PlatformIO/src/main.cpp` into an instance of the *Arduino IDE* is also possible.

Due to the usage of the same processor for the Arduino Uno and Nano it is also possible to compile and upload the program to both of these two boards without any modification to the code. 

## Wiring Diagram
TODO 
## Features
- Automatically detect whether oscilloscope is in XY or normal operation mode
- Reset Single-Shot Trigger and transmit data when signal is fully captured
- Only transmits valid data (channel must be shown on oscilloscope's screen to be valid)

## How it works
The memory of the scope contains four 2048 byte long data blocks for each of the 4 channels (*CH1,CH2,REF1,REF2*) which regardless of the validness of the data must be read out entirely each time data is read from the oscilloscope.
### normal operation mode
Sending a 'R' to the serial port opened by the Arduino starts the data read-out process, which is described in more detail below.

### single-shot mode
When a 'S' is sent to the microcontroller it resets the Single-Shot trigger of the oscilloscope by pulling the *HBRESET* pin to Ground (0V) for a short period of time. Afterwards it waits for the oscilloscope to pull the *TE* pin to Ground to signalize the successful capture of the signal and starts the same read-out process as in normal operation mode.

### the process of reading out the signal data
Although it's not necessary to know how the microcontroller gets all the data from the oscilloscope in order to use the program the process is nevertheless described below. 


> **All the following pin operations are handled by the Arduino itself and do not require any interaction from the user!**

TODO

## Create a CSV file with the provided Python code
TODO