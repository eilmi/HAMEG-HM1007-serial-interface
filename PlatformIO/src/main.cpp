/*
This program gets all of the available data from a HAMEG HM1007 or HM205-3 oscilloscope and transmits it over serial 

written by Philipp Eilmsteiner, 03.07.2021
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
#define DATALINES ((PINC&0b111111)|(PIND&(0b1100))<<4)

#define ID_HM1007 2
#define ID_HM205_3 1

const char* Channelnames[]={"CH1","CH2","REF1","REF2"};
int chcount = 2;
int valcount=1024;
char model = 0;


void sendModel(){
  int oid = DATALINES;
  switch (oid){
    case ID_HM1007:
      Serial.println("HM1007");
      chcount=4;
      valcount=2048;
      model = ID_HM1007;
      break;

    case ID_HM205_3:
      Serial.println("HM205-3");
      chcount=2;
      valcount=2048;
      model = ID_HM205_3;
      break;

    default:
    //modelname="unknown";
    Serial.println("unknown");
    chcount=2;
    break;
  }
}

void readfromoszi(){

  // ------------------------ Read oscilloscope ID ---------------------------------
  sendModel();

  // ------------------------ Initialize oscilloscope ------------------------------
  PORTB|=0b100; // SET SRQ to HIGH to signal oscilloscope that we want data from it (blanks screen of oscilloscope)
  _delay_us(100);
  if (model==ID_HM1007)
    while((PIND&(1<<7))); //Wait until oscilloscope pull`s TE pin low to signal it is ready
  else
    _delay_us(40);

  if (model==ID_HM1007){
    if (PIND&(1<<6)){ //Check if XY-Plot is enabled
      int value = DATALINES; //get reference-position
      Serial.println("Ref. Pos:");Serial.println(value);
    }
    else{
      Serial.println("XY-Plot");
    }
  }
  PORTB&=(~1<<0); //falling edge to reset the address counter of oscilloscope
  _delay_us(50);
  PORTB|=1<<0; //set reset pin to HIGH again (it´s normal state)

  // ------------- Read all 4 buffers -------------------
  bool isvalid;
  char prevch=0;
  for (int x=0;x<chcount;x++){
    if (model==ID_HM1007){
      Serial.println(Channelnames[x]);
      }
    for (int i=0;i<valcount;i++){
      isvalid=!(PIND&(1<<5)); //get info if data in next address is valid or not
      PORTB|=1<<1; //generate rising edge for counting one address further
      _delay_us(40);
      PORTB&=(~(1<<1)); //falling edge for counter - does not do anything
      _delay_us(40);

      if (i==0 && model==ID_HM205_3){
        if (PIND&(1<<5)){ //check whether CH1 or CH2 is being transmitted by the oscilloscope
          if (prevch!=1) //check if CH1 was transmitted previously
            Serial.println("CH1"); //if not send "CH1" over serial
          else  
            break; //abort if channel has already been sent
          prevch=1;
          }
        else{ //CH2 is transmitted
          if (prevch!=2)
            Serial.println("CH2");
          else
            break; //abort if channel has already been sent
          prevch=2;
          }
      }
      
      if (isvalid || model==ID_HM205_3){ //check if oscilloscope signaled that the data is valid on previous address
        //int value = DATALINES; //reading the data from the bus
        Serial.println((int)DATALINES);
      }
    
      _delay_us(20);
    }
  }
  PORTB&=~(0b100); //set SRQ to LOW to return oscilloscope into normal operation mode 
  Serial.println("END");
}

void readsingleshoot(){
  DDRB|=1<<4; //SET PB4 (HBRESET) to OUTPUT (0V) -> Pulls pin to LOW
  _delay_ms(10);
  DDRB=DDRB&(~(1<<4)); //SET PB4 (HBRESET) back to INPUT -> oscilloscope pulls it back to 5V
  _delay_ms(5);
  while((PIND&(1<<7))); //Wait for oscilloscope to pull TE low to signal signal was successfully captured
  readfromoszi();
}

void sendid(){
  Serial.println(DATALINES);
}

void setup() {
  DDRC=0x0; //Set whole port register C as input
  PORTC=0x0; //disable pull-up for all inputs of port register C
  DDRB=0b00111; //set first 3 pins of port register B as output
  PORTB=1<<0; //SET CLRAC (Reset address counter) to HIGH (5V)
  DDRD=0b00000; //Set whole port register D as input
  PORTD=0b00000; //disable all pull-up resistors of port register D

  Serial.begin(250000);
  _delay_ms(10);
}


void loop() {
  if (Serial.available()>0){
    int receive = Serial.read();
    if (receive=='R')
      readfromoszi();

    if (receive=='S'){
      readsingleshoot();
    }
    if (receive=='i')
      sendid();
    if (receive=='m')
      sendModel();
  }
}