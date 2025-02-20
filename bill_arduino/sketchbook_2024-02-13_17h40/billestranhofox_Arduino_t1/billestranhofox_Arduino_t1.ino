/*Pinagem do arduino
  Fonte: https://www.arduinoportugal.pt/ponte-h-l298n-aprenda-controlar-velocidade-um-motor-dc/

  Adaptção JS - Iniciada em 28/06/2024
*/

//Para BluetoothSerial
#include "BluetoothSerial.h"
BluetoothSerial SerialBT;
char command;
boolean state = 1;
int contador1 = 0;
int contador2 = 0;
int contador3 = 0;
int contador4 = 0;

//Para millis()
#define TEMPO_DEBOUNCE 50 //ms  10
int contador_acionamentos = 0;
unsigned long timestamp_ultimo_acionamento = 0;


//Encoder - para void wheelSpeedXX()
//const byte encoder0pinA = 32;//A pin -> the interrupt pin 32
//const byte encoder0pinB = 35;//B pin -> the digital pin 35
byte encoder0PinALastFL;
byte encoder0PinALastFR;
byte encoder0PinALastRL;
byte encoder0PinALastRR;
int durationFL;//the number of the pulses
int durationFR;//the number of the pulses
int durationRL;//the number of the pulses
int durationRR;//the number of the pulses

boolean Direction;//the rotation direction


//Motor Front
//Esquerda
int8_t FL_FORW = 26;              //IN3
int8_t FL_BACK = 25;              //IN4
int8_t FL_enablePin = 13;         //ENB
const byte FL_encoderPin1 = 32;   //Encoder Pin1 // - Interrupt pin
const byte FL_encoderPin2 = 35;   //Encoder Pin2 // - Digital pin
//Direita
int8_t FR_FORW = 19;              //INI1
int8_t FR_BACK = 18;              //INI2
int8_t FR_enablePin = 23;         //ENA
const byte FR_encoderPin1 = 4;    //Encoder Pin1 - Interrupt pin
const byte FR_encoderPin2 = 5;    //Encoder Pin2 - Digital pin


//Motor Rear
//Esquerda
int8_t RL_FORW = 17;              //IN3
int8_t RL_BACK = 16;              //IN4
int8_t RL_enablePin = 15;         //ENB
const byte RL_encoderPin1 = 21;   //Encoder Pin1 - Interrupt pin
const byte RL_encoderPin2 = 22;   //Encoder Pin2 - Digital pin
//Direita
int8_t RR_FORW = 12;              //INI1
int8_t RR_BACK = 27;              //INI2
int8_t RR_enablePin = 14;         //ENA
const byte RR_encoderPin1 = 34;   //Encoder Pin1 - Interrupt pin
const byte RR_encoderPin2 = 33;   //Encoder Pin2  - Digital pin

//variavel auxiliar
int Speed = 200; // = 200; // 0 - 255.

void setup() {
  //Define a porta do led como saida
  pinMode(2, OUTPUT);
  //Serial.begin(115200);
  Serial.begin(57600);
  //  EncoderInitFL();//Initialize the module Encoder  - void wheelSpeedFL()
  //  EncoderInitFR();//Initialize the module Encoder  - void wheelSpeedFL()
  EncoderInit();//Initialize the module Encoder  - void wheelSpeedFL()

  SerialBT.begin("billestranhofox");

  //Motor front
  //Esquerda
  pinMode(FL_FORW, OUTPUT);          //IN3
  pinMode(FL_BACK, OUTPUT);          //IN4
  pinMode(FL_enablePin, OUTPUT);     //ENB  //Velocidade B
  pinMode(FL_encoderPin1, OUTPUT);   //Encoder Pin1    - Interrupt pin
  //pinMode(FL_encoderPin2, OUTPUT);  //Encoder Pin2  - Digital pin - ver EncoderInitFL()

  //Direita
  pinMode(FR_FORW, OUTPUT);          //INI1
  pinMode(FR_BACK, OUTPUT);          //INI2
  pinMode(FR_enablePin, OUTPUT);     //ENA // Velocidade A
  pinMode(FR_encoderPin1, OUTPUT);   //Encoder Pin1 - Interrupt pin
  //pinMode(FR_encoderPin2, OUTPUT); //Encoder Pin2 - Digital pin - ver EncoderInitFL()

  //Motor Rear
  //Esquerda
  pinMode(RL_FORW, OUTPUT);          //IN3
  pinMode(RL_BACK, OUTPUT);          //IN4
  pinMode(RL_enablePin, OUTPUT);     //ENB  //Velocidade B
  pinMode(RL_encoderPin1, OUTPUT);   //Encoder Pin1 - Interrupt pin
  //pinMode(RL_encoderPin2, OUTPUT); //Encoder Pin2 - Digital pin - ver EncoderInitFL()
  //Direita
  pinMode(RR_FORW, OUTPUT);          //INI1
  pinMode(RR_BACK, OUTPUT);          //INI2
  pinMode(RR_enablePin, OUTPUT);     //ENA // Velocidade A
  pinMode(RR_encoderPin1, OUTPUT);   //Encoder Pin1 - Interrupt pin
  //pinMode(RR_encoderPin2, OUTPUT); //Encoder Pin2 - Digital pin - ver EncoderInitFL()

  Stop(); //Initialize with motors stoped.
}

void buzina() {
  Serial.print("Buzina On  ");
  delay(1000);
}


void encoderJS() { // Infornaçõe do encoder
  if ( (millis() - timestamp_ultimo_acionamento) >= TEMPO_DEBOUNCE )
  {
    wheelSpeedFL();
    Serial.print("Pulse FL: ");
    Serial.print(durationFL);
    durationFL = 0;

    wheelSpeedFR();
    Serial.print("  Pulse FR: ");
    Serial.print(durationFR);
    durationFR = 0;

    wheelSpeedRL();
    Serial.print("  Pulse RL: ");
    Serial.print(durationRL);
    durationRL = 0;

    wheelSpeedRR();
    Serial.print("  Pulse RR: ");
    Serial.println(durationRR);
    durationRR = 0;

    contador_acionamentos++;
    timestamp_ultimo_acionamento = millis();
  }

}

void Stop() {
  analogWrite(FL_enablePin, 0); // Para Motor Front Left
  analogWrite(FR_enablePin, 0); // Para Motor Front Right
  analogWrite(RL_enablePin, 0); // Para Motor Rear Left
  analogWrite(RR_enablePin, 0); // Para Motor Rear Right
}

void forward() {
  //Serial.print("Moving forward  ");
  encoderJS();
  //Motor front
  //Esquerda
  digitalWrite(FL_FORW, HIGH);
  digitalWrite(FL_BACK, LOW);
  analogWrite(FL_enablePin, Speed);
  //Direita
  digitalWrite(FR_FORW, HIGH);
  digitalWrite(FR_BACK, LOW);
  analogWrite(FR_enablePin, Speed);

  //Motor rear
  //Esquerda
  digitalWrite(RL_FORW, HIGH);
  digitalWrite(RL_BACK, LOW);
  analogWrite(RL_enablePin, Speed);
  //Direita
  digitalWrite(RR_FORW, HIGH);
  digitalWrite(RR_BACK, LOW);
  analogWrite(RR_enablePin, Speed);
}

void backward() {
  //Serial.print("Moving backward  ");
  encoderJS();
  //Motor front
  //Esquerda
  digitalWrite(FL_FORW, LOW);
  digitalWrite(FL_BACK, HIGH);
  analogWrite(FL_enablePin, Speed);
  //Direita
  digitalWrite(FR_FORW, LOW);
  digitalWrite(FR_BACK, HIGH);
  analogWrite(FR_enablePin, Speed);

  //Motor rear
  //Esquerda
  digitalWrite(RL_FORW, LOW);
  digitalWrite(RL_BACK, HIGH);
  analogWrite(RL_enablePin, Speed);
  //Direita
  digitalWrite(RR_FORW, LOW);
  digitalWrite(RR_BACK, HIGH);
  analogWrite(RR_enablePin, Speed);
}

void superleft() {
  //Serial.print("Moving superleft  ");
  encoderJS();
  //Motor front
  //Esquerda
  digitalWrite(FL_FORW, LOW);
  digitalWrite(FL_BACK, HIGH);
  analogWrite(FL_enablePin, Speed);
  //Direita
  digitalWrite(FR_FORW, HIGH);
  digitalWrite(FR_BACK, LOW);
  analogWrite(FR_enablePin, Speed);

  //Motor rear
  //Esquerda
  digitalWrite(RL_FORW, HIGH);
  digitalWrite(RL_BACK, LOW);
  analogWrite(RL_enablePin, Speed);
  //Direita
  digitalWrite(RR_FORW, LOW);
  digitalWrite(RR_BACK, HIGH);
  analogWrite(RR_enablePin, Speed);

}

//void left() {
void right() {
  //Serial.print("Moving left  ");
  encoderJS();
  //Motor front
  //Esquerda
  digitalWrite(FL_FORW, LOW);
  digitalWrite(FL_BACK, HIGH);
  analogWrite(FL_enablePin, Speed);
  //Direita
  digitalWrite(FR_FORW, HIGH);
  digitalWrite(FR_BACK, LOW);
  analogWrite(FR_enablePin, Speed);

  //Motor rear
  //Esquerda
  digitalWrite(RL_FORW, LOW);
  digitalWrite(RL_BACK, HIGH);
  analogWrite(RL_enablePin, Speed);
  //Direita
  digitalWrite(RR_FORW, HIGH);
  digitalWrite(RR_BACK, LOW);
  analogWrite(RR_enablePin, Speed);

}

void superright() {
  //Serial.print("Moving superright  ");
  encoderJS();
  //Motor front
  //Esquerda
  digitalWrite(FL_FORW, HIGH);
  digitalWrite(FL_BACK, LOW);
  analogWrite(FL_enablePin, Speed);
  //Direita
  digitalWrite(FR_FORW, LOW);
  digitalWrite(FR_BACK, HIGH);
  analogWrite(FR_enablePin, Speed);

  //Motor rear
  //Esquerda
  digitalWrite(RL_FORW, LOW);
  digitalWrite(RL_BACK, HIGH);
  analogWrite(RL_enablePin, Speed);
  //Direita
  digitalWrite(RR_FORW, HIGH);
  digitalWrite(RR_BACK, LOW);
  analogWrite(RR_enablePin, Speed);

}

//void right() {
void left() {
  //Serial.print("Moving right  ");
  encoderJS();
  //Motor front
  //Esquerda
  digitalWrite(FL_FORW, HIGH);
  digitalWrite(FL_BACK, LOW);
  analogWrite(FL_enablePin, Speed);
  //Direita
  digitalWrite(FR_FORW, LOW);
  digitalWrite(FR_BACK, HIGH);
  analogWrite(FR_enablePin, Speed);

  //Motor rear
  //Esquerda
  digitalWrite(RL_FORW, HIGH);
  digitalWrite(RL_BACK, LOW);
  analogWrite(RL_enablePin, Speed);
  //Direita
  digitalWrite(RR_FORW, LOW);
  digitalWrite(RR_BACK, HIGH);
  analogWrite(RR_enablePin, Speed);

}

//void forwardleft() {
void forwardright() {
  //Serial.print("Moving forwardleft  ");
  encoderJS();
  //Motor front
  //Esquerda
  digitalWrite(FL_FORW, HIGH);
  digitalWrite(FL_BACK, LOW);
  analogWrite(FL_enablePin, 0);
  //Direita
  digitalWrite(FR_FORW, HIGH);
  digitalWrite(FR_BACK, LOW);
  analogWrite(FR_enablePin, Speed);

  //Motor rear
  //Esquerda
  digitalWrite(RL_FORW, HIGH);
  digitalWrite(RL_BACK, LOW);
  analogWrite(RL_enablePin, 0);
  //Direita
  digitalWrite(RR_FORW, HIGH);
  digitalWrite(RR_BACK, LOW);
  analogWrite(RR_enablePin, Speed);

}


//void forwardright() {
void forwardleft() {
  //Serial.print("Moving forwardright  ");
  encoderJS();
  //Motor front
  //Esquerda
  digitalWrite(FL_FORW, HIGH);
  digitalWrite(FL_BACK, LOW);
  analogWrite(FL_enablePin, Speed);
  //Direita
  digitalWrite(FR_FORW, HIGH);
  digitalWrite(FR_BACK, LOW);
  analogWrite(FR_enablePin, 0);

  //Motor rear
  //Esquerda
  digitalWrite(RL_FORW, HIGH);
  digitalWrite(RL_BACK, LOW);
  analogWrite(RL_enablePin, Speed);
  //Direita
  digitalWrite(RR_FORW, HIGH);
  digitalWrite(RR_BACK, LOW);
  analogWrite(RR_enablePin, 0);
}


//void backleft() {
void backright() {
  //Serial.print("Moving backleft  ");
  encoderJS();
  //Motor front
  //Esquerda
  digitalWrite(FL_FORW, LOW);
  digitalWrite(FL_BACK, HIGH);
  analogWrite(FL_enablePin, Speed);
  //Direita
  digitalWrite(FR_FORW, LOW);
  digitalWrite(FR_BACK, HIGH);
  analogWrite(FR_enablePin, 0);

  //Motor rear
  //Esquerda
  digitalWrite(RL_FORW, LOW);
  digitalWrite(RL_BACK, HIGH);
  analogWrite(RL_enablePin, Speed);
  //Direita
  digitalWrite(RR_FORW, LOW);
  digitalWrite(RR_BACK, HIGH);
  analogWrite(RR_enablePin, 0);
}


//void backright() {
void backleft() {
  //Serial.print("Moving backright  ");
  encoderJS();
  //Motor front
  //Esquerda
  digitalWrite(FL_FORW, LOW);
  digitalWrite(FL_BACK, HIGH);
  analogWrite(FL_enablePin, 0);
  //Direita
  digitalWrite(FR_FORW, LOW);
  digitalWrite(FR_BACK, HIGH);
  analogWrite(FR_enablePin, Speed);

  //Motor rear
  //Esquerda
  digitalWrite(RL_FORW, LOW);
  digitalWrite(RL_BACK, HIGH);
  analogWrite(RL_enablePin, 0);
  //Direita
  digitalWrite(RR_FORW, LOW);
  digitalWrite(RR_BACK, HIGH);
  analogWrite(RR_enablePin, Speed);
}


/*
  void testandoencoder() {
  //Testando Encoder - Motor Front Left
  contador1 = contador1 + analogRead(FL_encoderPin1);
  Serial.print("FL: ");
  Serial.print(contador1);
  //delay(1);

  //Testando Encoder - Motor Front Right
  contador2 = contador2 + analogRead(FR_encoderPin1);
  Serial.print("   FR: ");
  Serial.print(contador2);
  //delay(1);

  //Testando Encoder - Motor Rear Left
  contador3 = contador3 + analogRead(RL_encoderPin1);
  Serial.print("   RL: ");
  Serial.print(contador3);
  //delay(1);

  //Testando Encoder - Motor Rear Right
  contador4 = contador4 + analogRead(RR_encoderPin1);
  Serial.print("   RR: ");
  Serial.println(contador4);
  //delay(1);
  }
*/


void EncoderInit()
{
  //Direction = true;  //default -> Forward
  Direction = false;  // -> Reward
  pinMode(FL_encoderPin2, INPUT);
  pinMode(FR_encoderPin2, INPUT);
  pinMode(RL_encoderPin2, INPUT);
  pinMode(RR_encoderPin2, INPUT);

  attachInterrupt(6, wheelSpeedFL, CHANGE);//int.0 6 Ok
  attachInterrupt(7, wheelSpeedFR, CHANGE);//int.0 7 Ok
  attachInterrupt(8, wheelSpeedRL, CHANGE);//int.0 8 Ok
  attachInterrupt(9, wheelSpeedRR, CHANGE);//int.0 9 Ok

}

//void testandoencodercominterrupacaoFL() {
void wheelSpeedFL() {
  /*
    Pay attention to the interrupt pin,please check which microcontroller you use.
    http://arduino.cc/en/Reference/AttachInterrupt
  */
  //The sample code for driving one way motor encoder

  int Lstate = digitalRead(FL_encoderPin1);
  //int Lstate = digitalRead(FR_encoderPin1);
  //int Lstate = digitalRead(RL_encoderPin1);
  //int Lstate = digitalRead(RR_encoderPin1);

  if ((encoder0PinALastFL == LOW) && Lstate == HIGH)
  {
    int val = digitalRead(FL_encoderPin2);
    //int val = digitalRead(FR_encoderPin2);
    //int val = digitalRead(RL_encoderPin2);
    //int val = digitalRead(RR_encoderPin2);

    if (val == LOW && Direction)
    {
      Direction = false; //Reverse
    }
    else if (val == HIGH && !Direction)
    {
      Direction = true;  //Forward
    }
  }
  encoder0PinALastFL = Lstate;
  if (!Direction)  durationFL++;
  else  durationFL--;
}

//void testandoencodercominterrupacaoFR() {
void wheelSpeedFR() {
  /*
    Pay attention to the interrupt pin,please check which microcontroller you use.
    http://arduino.cc/en/Reference/AttachInterrupt
  */
  //The sample code for driving one way motor encoder

  //int Lstate = digitalRead(FL_encoderPin1);
  int Lstate = digitalRead(FR_encoderPin1);
  //int Lstate = digitalRead(RL_encoderPin1);
  //int Lstate = digitalRead(RR_encoderPin1);

  if ((encoder0PinALastFR == LOW) && Lstate == HIGH)
  {
    //int val = digitalRead(FL_encoderPin2);
    int val = digitalRead(FR_encoderPin2);
    //int val = digitalRead(RL_encoderPin2);
    //int val = digitalRead(RR_encoderPin2);

    if (val == LOW && Direction)
    {
      Direction = false; //Reverse
    }
    else if (val == HIGH && !Direction)
    {
      Direction = true;  //Forward
    }
  }
  encoder0PinALastFR = Lstate;
  if (!Direction)  durationFR++;
  else  durationFR--;
}


//void testandoencodercominterrupacaoRL() {
void wheelSpeedRL() {
  /*
    Pay attention to the interrupt pin,please check which microcontroller you use.
    http://arduino.cc/en/Reference/AttachInterrupt
  */
  //The sample code for driving one way motor encoder

  //int Lstate = digitalRead(FL_encoderPin1);
  //int Lstate = digitalRead(FR_encoderPin1);
  int Lstate = digitalRead(RL_encoderPin1);
  //int Lstate = digitalRead(RR_encoderPin1);

  if ((encoder0PinALastRL == LOW) && Lstate == HIGH)
  {
    // int val = digitalRead(FL_encoderPin2);
    //int val = digitalRead(FR_encoderPin2);
    int val = digitalRead(RL_encoderPin2);
    //int val = digitalRead(RR_encoderPin2);

    if (val == LOW && Direction)
    {
      Direction = false; //Reverse
    }
    else if (val == HIGH && !Direction)
    {
      Direction = true;  //Forward
    }
  }
  encoder0PinALastRL = Lstate;
  if (!Direction)  durationRL++;
  else  durationRL--;
}


//void testandoencodercominterrupacaoRR() {
void wheelSpeedRR() {
  /*
    Pay attention to the interrupt pin,please check which microcontroller you use.
    http://arduino.cc/en/Reference/AttachInterrupt
  */
  //The sample code for driving one way motor encoder

  //int Lstate = digitalRead(FL_encoderPin1);
  //int Lstate = digitalRead(FR_encoderPin1);
  //int Lstate = digitalRead(RL_encoderPin1);
  int Lstate = digitalRead(RR_encoderPin1);

  if ((encoder0PinALastRR == LOW) && Lstate == HIGH)
  {
    //int val = digitalRead(FL_encoderPin2);
    //int val = digitalRead(FR_encoderPin2);
    //int val = digitalRead(RL_encoderPin2);
    int val = digitalRead(RR_encoderPin2);

    if (val == LOW && Direction)
    {
      Direction = false; //Reverse
    }
    else if (val == HIGH && !Direction)
    {
      Direction = true;  //Forward
    }
  }
  encoder0PinALastRR = Lstate;
  if (!Direction)  durationRR++;
  else  durationRR--;
}

void loop() {
  if (SerialBT.available()) {
    command = SerialBT.read();
    //Serial.print("Comando pressionado: ");
    //Serial.println(command);
    //Acende o led
    digitalWrite(2, HIGH);
    delay(10); //JS
    if (command == 'X') {
      state = 1;
    } else if (command == 'x') {
      state = 0;
    }
  }
  switch (command) {
    case 'V': // teste JS
      buzina();
      break;
    case 'F':
      forward();
      break;
    case 'S':
      Stop(); // Stop motors.
      break;
    case 'B':
      backward();
      break;
    case 'L':
      //left();
      if (command == 'L' && state == 1) {
        superleft ();
      } else if (command == 'L' && state == 0) {
        left ();
      }
      break;
    case 'R':
      //right();
      if (command == 'R' && state == 1) {
        superright  ();
      } else if (command == 'R' && state == 0) {
        right ();
      }
      break;
    case 'G':
      forwardleft();
      break;
    case 'I':
      forwardright();
      break;
    case 'H':
      backleft();
      break;
    case 'J':
      backright();
      break;
    case '0':
      Speed = 100;
      break;
    case '1':
      Speed = 140;
      break;
    case '2':
      Speed = 153;
      break;
    case '3':
      Speed = 165;
      break;
    case '4':
      Speed = 178;
      break;
    case '5':
      Speed = 191;
      break;
    case '6':
      Speed = 204;
      break;
    case '7':
      Speed = 216;
      break;
    case '8':
      Speed = 229;
      break;
    case '9':
      Speed = 242;
      break;
    case 'q':
      Speed = 255;
      break;
  }

  /* JS - decobri para que serve essa função
    Speedsec = Turnradius;
    if (brkonoff == 1) {
      brakeOn();
    } else {
      brakeOff();
    }
  */


}
