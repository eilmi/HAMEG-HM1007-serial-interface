clear all;
close all;

nooffset = import_csv_func("HM1007_export-2021_02_25-07_41_05\HM1007_data-2021_02_25-07_41_05.csv");
offset = import_csv_func("HM1007_export-2021_02_25-07_37_34\HM1007_data-2021_02_25-07_37_34.csv");


data = offset;
plot (offset.time,offset.CH1)

T = data.time(2)-data.time(1);             % Sampling period
Fs = 1/T;            % Sampling frequency    
L = 2048;             % Length of signal
t = (0:L-1)*T;        % Time vector

Y = fft(data.CH1);
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);

f = Fs*(0:(L/2))/L;
stem(f,P1) 
title('Single-Sided Amplitude Spectrum of X(t)')
xlabel('f (Hz)')
ylabel('|P1(f)|')


                
