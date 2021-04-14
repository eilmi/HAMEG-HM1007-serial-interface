# Serial interface for Hameg HM1007
## Introduction
This repository contains all the needed code to get the data from a HAMEG HM1007 oscilloscope. The core of this interface is an Arduino Nano which is used to communicate with the oscilloscope via it's HO79-4 interface.

## Serial interface
### Flashing the Arduino
Altough the code for the microcontroller was written in *PlatformIO* copying the content of `PlatformIO/src/main.cpp` into an instance of the *Arduino IDE* is also possible.

Due to the usage of the same processor for the Arduino Uno and Nano it is also possible to compile and upload the program to both of these two boards without any modification to the code. 

### Wiring Diagram
TODO (can also be found in the sourcecode of the C code `PlatformIO/src/main.cpp` )
### Features
- Automatically detect whether oscilloscope is in XY or normal operation mode
- Reset Single-Shot Trigger and transmit data when signal is fully captured
- Only transmits valid data (channel must be shown on oscilloscope's screen to be valid)

### How it works
The memory of the scope contains four 2048 byte long data blocks. One for each of the 4 channels (*CH1,CH2,REF1,REF2*) which regardless of the validness of the data must be read out entirely each time data is read from the oscilloscope.
#### normal operation mode
Sending a 'R' to the serial port opened by the Arduino starts the data read-out process, which is described in more detail below.

#### single-shot mode
When a 'S' is sent to the microcontroller it resets the Single-Shot trigger of the oscilloscope by pulling the *HBRESET* pin to Ground (0V) for a short period of time. Afterwards it waits for the oscilloscope to pull the *TE* pin to Ground to signalize the successful capture of the signal and starts the same read-out process as in normal operation mode.
#### the process of reading out the signal data
Although it's not necessary to know how the microcontroller gets all the data from the oscilloscope in order to use the program the process is nevertheless described below. 


> **All the following pin operations are handled by the Arduino itself and do not require any interaction from the user!**

| Step | Pin Operation                      | Info                                               |
|------|------------------------------------|----------------------------------------------------|
| 1    | Set SQR to HIGH                    | Request service from scope                         |
| 2    | Check TE until it´s pulled LOW     | HM1007 indicates ready to transmit                 |
| 3    | Check X-Y                          | If LOW -> scope in X-Y mode -> skip step 4         |
| 4    | Capture HB0 to HB7                 | Datalines show baseline position shift (REF. -Pos) |
| 5    | Pull CLRAC to LOW for a short time | Reset address counter                              |
| 6    | Set CLKAC to High                  | count address counter up once                      |
| 7    | Set CLKAC to LOW                   | Falling edge of CLKAC does not do anything         |
| 8    | Capture HB0 to HB7                 | Datalines show data of byte 0                      |
| 9    | CLKAC to High, CLKAC to LOW        | Repeat step 6 to 8 for 8191 times                  |
| 10   | Set SQR back to LOW                | HM1007 returns into normal operation mode          |
### Pictures
| | |
| --- | --- | 
|![Bottom of Circuit Board](Pictures/Hameg_Interface_circuit_board_top.png?raw=true "Top of circuit board") | ![Alt text](Pictures/Hameg_Interface_circuit_board_bottom.png?raw=true "Bottom of circuit board")|

![Alt text](Pictures/Hameg_Interface_with_cable.png?raw=true "Serial interface with case and cables")
## Python GUI
This repository also includes a python program which can be used, to not only visualize the data from the scope, but also store it in a variety of formats.
> **This section of this README is still under development!**

### How to use the program
First you need to select the serial port of the Arduino acting as the interface to the oscilloscope from the drop down menu. Alternative you can click *File -> Import Raw Data* to load the data from a previously saved raw log  
![Python GUI](Pictures/Software/Empty_Interface.png?raw=true "python program with no data loaded")

### Ploting the signal(s)
![Python GUI](Pictures/Software/Square_Wave_Loaded.png?raw=true "python program with no data loaded")

### Fast Fourier transform
![Python GUI](Pictures/Software/Square_Wave_FFT.png?raw=true "python program with no data loaded")