# PC interface for Hameg HM1007 & HM205-3
## Introduction
The aim of this project is to provide an easy way to read the data from a Hameg HM1007 & HM205-3 oscilloscope. On the one hand, this is done by using an Arduino Nano for interfacing with the oscilloscope via it's Hameg interface (a 26-pin connector on the back of the oscilloscope). The Arduino provides a serial connection for the PC, via which all data from the oscilloscope can be read out. On the other hand, this repository also includes a Python program for visualizing the received data and storing it in various formats.
> **Although the project has been extended to include support for the HM205-3 recently, the focus remains on the HM1007. Therefore, it's implementation is only limited and not all features have been adapted yet.**
## Serial interface
### Flashing the Arduino
Altough the code for the microcontroller was written in *PlatformIO* copying the content of `PlatformIO/src/main.cpp` into an instance of the *Arduino IDE* is also possible.

Due to the usage of the same processor for the Arduino Uno and Nano it is also possible to compile and upload the program to both of these two boards without any modification to the code. 

### Wiring Diagram
![Wiring Diagram](Pictures/Wiring_Diagram.png?raw=true "wiring diagram of arduino interface")
### Features
- Only transmits valid data (channel must be shown on oscilloscope's screen to be valid)
- Automatically detect whether oscilloscope is in XY or normal operation mode (HM1007 only)
- Reset Single-Shot trigger and transmit data when signal is fully captured (HM1007 only)


### How it works (HM1007)
The memory of the scope contains four 2048 byte long data blocks. One for each of the 4 channels (*CH1,CH2,REF1,REF2*) which regardless of the validness of the data must be read out entirely each time data is read from the oscilloscope.
#### normal operation mode
Sending a 'R' to the serial port opened by the Arduino starts the data read-out process, which is described in more detail below.

#### single-shot mode
When a 'S' is sent to the microcontroller it resets the Single-Shot trigger of the oscilloscope by pulling the *HBRESET* pin to Ground (0V) for a short period of time. Afterwards it waits for the oscilloscope to pull the *TE* pin to Ground to signalize the successful capture of the signal and starts the same read-out process as in normal operation mode.
#### the process of reading out the signal data
Although it's not necessary to know how the microcontroller gets all the data from the oscilloscope in order to use the program the process is nevertheless described below. 


> **All the following pin operations are handled by the Arduino itself and do not require any interaction from the user!**

| Step | Pin Operation                      | Info                                                    |
|------|------------------------------------|----------------------------------------------------     |
| 1    | Capture HB0 to HB7                 | read scope id                                           |
| 2    | Set SQR to HIGH                    | Request service from scope                              |
| 3    | Check TE until it´s pulled LOW     | scope indicates ready to transmit (HM1007 only)         |
| 4    | Check X-Y                          | If LOW -> scope in XY mode -> skip step 4 (HM007 only) |
| 5    | Capture HB0 to HB7                 | Datalines show baseline position shift (REF. -Pos)      |
| 6    | Pull CLRAC to LOW for a short time | Reset address counter                                   |
| 7    | Set CLKAC to High                  | count address counter up once                           |
| 8    | Set CLKAC to LOW                   | Falling edge of CLKAC does not do anything              |
| 9    | Capture HB0 to HB7                 | Datalines show data of byte 0                           |
| 10    | CLKAC to High, CLKAC to LOW       | Repeat step 7 to 9 for 8191 times                       |
| 11   | Set SQR back to LOW                | scope returns into normal operation mode                |
### Pictures
| | |
| --- | --- | 
|![Bottom of Circuit Board](Pictures/Hameg_Interface_circuit_board_top.png?raw=true "Top of circuit board") | ![Alt text](Pictures/Hameg_Interface_circuit_board_bottom.png?raw=true "Bottom of circuit board")|

![Alt text](Pictures/Hameg_Interface_with_cable.png?raw=true "Serial interface with case and cables")
## Python GUI

### Selecting a COM port or loading raw data files
First you need to select the serial port of the Arduino acting as the interface to the oscilloscope from the drop down menu. Alternative you can click *File -> Import Raw Data* to load the data from a previously saved raw log ).

![Python GUI](Pictures/Software/Empty_Interface.png?raw=true "python program with no data loaded")

### Set parameters of oscilloscope
The oscilloscope only transmits 2048 values between 0 and 255 for each of the four channels (two physical and two reference ones) as well as the reference position of these two channels to the interface.

This limitation of the HM-1007 requires us to manually set not only the *Time per division* (all channels share the same time base) but also the *Volts per division* (independent for each of the four channels).
A division is always the distance between either two vertical or two horizontal lines on the oscilloscope's screen.

The program allows you to select every position of the physical selector knobs found on the scope via a dropdown menu.
(The *time per division* selector only lets you select values where the oscilloscope is capable of operating in *Storage mode*.)

![Python GUI](Pictures/Software/Square_Wave_Loaded.png?raw=true "python program with with square signal")

Because the values received from the oscilloscope represent absolute values on its screen's vertical axis it is also necessary to select a horizontal line on the screen which represents 0V (Ground).<br/>
This is done by selecting a value between -4 and 4 in the dropdown list right of the volts/division select menu where 0 means 0V is at the line in the middle of the scope's screen.
Selecting -4 will be interpreted as the lowest line on the screen represents 0V and 4 means the top line is 0V.<br/>
This allows you to tune the horizontal position of 0V of your input signal (best done by pressing the GD button and then varying the Y-position dial of the channel) to any of the 9 available horizontal lines.
Doing so doesn't impact the amplitude of the signal(s) but results in correct absolute voltage values.   
### Fast Fourier transform
The interface is also capable of displaying the fast fourier transform (FFT) of the captured signal which can be handy to 
detect harmonic oscillations.

![Python GUI](Pictures/Software/Square_Wave_FFT.png?raw=true "python program with FFT analysis")