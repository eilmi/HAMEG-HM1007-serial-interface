/*
This program gets all of the available data from a HAMEG HM1007 oszilloskop and transmits it over serial 

written by Philipp Eilmsteiner, 27.01.2021
*/

/*
PIN-Definition (for Arduino NANO)
A0 (PC0) <-> HB0 (data Bit 0 (LSB)) (3)
A1 (PC1) <-> HB1 (data Bit 1) (4)
A2 (PC2) <-> HB2 (data Bit 2) (5)
A3 (PC3) <-> HB3 (data Bit 3) (6)
A4 (PC4) <-> HB4 (data Bit 4) (7)
A5 (PC5) <-> HB5 (data Bit 5) (8)
A6 (PC6) <-> not connected (reserved for XPLOT) (13)
A7 (PC7) <-> not connected (reserved for YPLOT) (15)

D2 (PD2) <-> HB6 (data Bit 6) (9)
D3 (PD3) <-> HB7 (data Bit 7 (MSB)) (10)
D5 (PD5) <-> DATAVAL (data valid) (17)
D6 (PD6) <-> XY-Plot (16)
D7 (PD7) <-> TE (transmit enable) (22)
D8 (PB0) <-> CLRAC (Reset address counter) (18)
D9 (PB1) <-> CLKAC (clock input of address counter) (19)
D10 (PB2) <-> SRQ (service request) (20)
D11 (PB3) <-> not connected (reserved for HBWR) (21)
D12 (PB4) <-> HBRESET (reset single shot) (23)
*/


#include <Arduino.h>

const char* Channelnames[]={"CH1","CH2","REF1","REF2"};

void readfromoszi(){
  // ------------------------ Initialize Oszilloskop ------------------------------
  PORTB|=0b100; // SET SRQ to HIGH to signal Oszilloskop that we want data from it (blanks screen of Oszilloskop)
  delay(10);
  while((PIND&(1<<7))); //Wait until oszilloskop pull`s TE pin low to signal it is ready

  if (PIND&(1<<6)){ //Check if XY-Plot is enabled
    int value = (PINC&0b111111)|(PIND&(0b1100))<<4; //get reference-position
    Serial.println("Ref. Pos:");Serial.println(value);
  }
  else{
    Serial.println("XY-Plot");
  }
  PORTB=PORTB&(~1<<0); //falling edge to reset the address counter of oszilloskop
  delay(10);
  PORTB|=1<<0; //set reset pin to HIGH again (it´s normal state)

  // ------------- Read all 4 buffers -------------------
  bool isvalid;
  for (int x=0;x<=3;x++){
    Serial.println(Channelnames[x]);
    for (int i=0;i<=2047;i++){

      isvalid=!(PIND&(1<<5)); //get info if data in next address is valid or not
      PORTB|=1<<1; //generate rising edge for counting one adress further
      _delay_us(80);
      PORTB=PORTB&(~(1<<1)); //falling edge for counter - does not do anything

      int value = (PINC&0b111111)|((PIND&(0b1100))<<4); //reading the data from the bus
      if (isvalid) //check if oszilloskop signaled that the data is valid on previous address
        Serial.println(value);
    
      _delay_us(40);
    }
  }
  PORTB=PORTB& ~(0b100); //set SRQ to LOW to return Oszilloskop into normal operation mode 
  Serial.println("END");
}

void setup() {
  DDRC=0x0; //Set whole port register C as input
  PORTC=0x0; //disable pull-up for all inputs of port register C
  DDRB=0b00111; //set first 3 pins of port register B as output
  PORTB=1<<0; //SET CLRAC (Reset address counter) to HIGH (5V)
  DDRD=0b00000; //Set whole port register D as input
  PORTD=0b00000; //disable all pull-up resistors of port register D

  Serial.begin(250000);
  delay(10);
}

void readsingleshoot(){
  DDRB|=1<<4; //SET PB4 (HBRESET) to OUTPUT (0V) -> Pulls pin to LOW
  delay(10);
  DDRB=DDRB&(~(1<<4)); //SET PB4 (HBRESET) back to INPUT -> oszilloskop pulls it back to 5V
  delay(5);
  while((PIND&(1<<7))); //Wait for oszilloskope to pull TE low to signal signal was successfully captured
  readfromoszi();
}

void loop() {
  if (Serial.available()>0){
    int receive = Serial.read();
    if (receive=='R')
      readfromoszi();
    if (receive=='S'){
      readsingleshoot();
    }
  }
}