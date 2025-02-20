
// JS
//18/08/2024


//Front left
#define FLForwardPin  26   //Verde
#define FLBackwardPin 25   //Amarelo
#define FLEnablePin   13    //Laranja
#define FLEncoderPinA 32   //Pin1 (A) Azul
#define FLEncoderPinB 35   //Pin2 (B) laranja

//Front right
#define FRForwardPin  19   //Lilás
#define FRBackwardPin 18   //Azul
#define FREnablePin   23   //Branco
#define FREncoderPinA  4   //Pin1 (A) Azul
#define FREncoderPinB  5   //Pin2 (B) Laranja

//Rear left
#define RLForwardPin  17   //Verde
#define RLBackwardPin 16   //Amarelo
#define RLEnablePin   15   //Laranja
#define RLEncoderPinA 21   //Pin1 (A) Azul
#define RLEncoderPinB 22   //Pin2 (B) Laranja

//Rear right
#define RRForwardPin  12  //Lilás
#define RRBackwardPin 27  //Azul
#define RREnablePin   14  //Branco
#define RREncoderPinA 34  //Pin1 (A) Azul
#define RREncoderPinB 33  //Pin2 (B) Laranja

volatile long FLEncodervalue = 0;
volatile long FREncodervalue = 0;
volatile long RLEncodervalue = 0;
volatile long RREncodervalue = 0;
int contador = 0;

void setup() {
  //Define a porta do led como saida
  pinMode(2, OUTPUT);
  //Front left
  pinMode(FLForwardPin, OUTPUT);
  pinMode(FLBackwardPin, OUTPUT);
  pinMode(FLEnablePin, OUTPUT);
  pinMode(FLEncoderPinA, INPUT);
  pinMode(FLEncoderPinB, INPUT);
  attachInterrupt(digitalPinToInterrupt(FLEncoderPinA), FLupdateEncoder, RISING);
  //Front right
  pinMode(FRForwardPin, OUTPUT);
  pinMode(FRBackwardPin, OUTPUT);
  pinMode(FREnablePin, OUTPUT);
  pinMode(FREncoderPinA, INPUT);
  pinMode(FREncoderPinB, INPUT);
  attachInterrupt(digitalPinToInterrupt(FREncoderPinA), FRupdateEncoder, RISING);

  //Rear left
  pinMode(RLForwardPin, OUTPUT);
  pinMode(RLBackwardPin, OUTPUT);
  pinMode(RLEnablePin, OUTPUT);
  pinMode(RLEncoderPinA, INPUT);
  pinMode(RLEncoderPinB, INPUT);
  attachInterrupt(digitalPinToInterrupt(RLEncoderPinA), RLupdateEncoder, RISING);

  //Rear right
  pinMode(RRForwardPin, OUTPUT);
  pinMode(RRBackwardPin, OUTPUT);
  pinMode(RREnablePin, OUTPUT);
  pinMode(RREncoderPinA, INPUT);
  pinMode(RREncoderPinB, INPUT);
  attachInterrupt(digitalPinToInterrupt(RREncoderPinA), RRupdateEncoder, RISING);

  Serial.begin(9600);
  pare();
}

void loop() {
  //Acende o led
  digitalWrite(2, HIGH);
  pare();

  //frente();
  //digitalWrite(ForwardPin, HIGH);
  //digitalWrite(BackwardPin, LOW);
  //analogWrite(EnablePin, 255);
  //pare();

  contador = contador + 1;
  if (contador <= 20) {
    frente();
    //re();
   
  }
  else {
    pare();
  }



  //Rotate the motor using your hands for one revolution and note down the encoder value printed on serial monitor.
  Serial.print("Front left:    ");
  Serial.print(FLEncodervalue);
  Serial.print("     Front right:    ");
  Serial.print(FREncodervalue);
  Serial.print("     Rear left:    ");
  Serial.print(RLEncodervalue);
  Serial.print("     Rear right:    ");
  Serial.println(RREncodervalue);

}

void pare() {
  //digitalWrite(ForwardPin, HIGH);
  //digitalWrite(BackwardPin, LOW);
  //Front left
  analogWrite(FLEnablePin, 0);
  //Front right
  analogWrite(FREnablePin, 0);
  //Rear left
  analogWrite(RLEnablePin, 0);
  //Rear right
  analogWrite(RREnablePin, 0);
}

void frente() {
  //Front left
  digitalWrite(FLForwardPin, HIGH);
  digitalWrite(FLBackwardPin, LOW);
  analogWrite(FLEnablePin, 255);
  //Front right
  digitalWrite(FRForwardPin, HIGH);
  digitalWrite(FRBackwardPin, LOW);
  analogWrite(FREnablePin, 255);
  //Rear left
  digitalWrite(RLForwardPin, HIGH);
  digitalWrite(RLBackwardPin, LOW);
  analogWrite(RLEnablePin, 255);
  //Rear right
  digitalWrite(RRForwardPin, HIGH);
  digitalWrite(RRBackwardPin, LOW);
  analogWrite(RREnablePin, 255);
}

void re() {
  //Front left
  digitalWrite(FLForwardPin, LOW);
  digitalWrite(FLBackwardPin, HIGH);
  analogWrite(FLEnablePin, 255);
  //Front right
  digitalWrite(FRForwardPin, LOW);
  digitalWrite(FRBackwardPin, HIGH);
  analogWrite(FREnablePin, 255);
  //Rear left
  digitalWrite(RLForwardPin, LOW);
  digitalWrite(RLBackwardPin, HIGH);
  analogWrite(RLEnablePin, 255);
  //Rear right
  digitalWrite(RRForwardPin, LOW);
  digitalWrite(RRBackwardPin, HIGH);
  analogWrite(RREnablePin, 255);
}

//Front left
void FLupdateEncoder()
{
  if (digitalRead(FLEncoderPinA) > digitalRead(FLEncoderPinB))
    FLEncodervalue++;
  else
    FLEncodervalue--;
}

//Front right
void FRupdateEncoder()
{
  if (digitalRead(FREncoderPinA) > digitalRead(FREncoderPinB))
    FREncodervalue++;
  else
    FREncodervalue--;
}

//Rear left
void RLupdateEncoder()
{
  if (digitalRead(RLEncoderPinA) > digitalRead(RLEncoderPinB))
    RLEncodervalue++;
  else
    RLEncodervalue--;
}


//Rear right
void RRupdateEncoder()
{
  if (digitalRead(RREncoderPinA) > digitalRead(RREncoderPinB))
    RREncodervalue++;
  else
    RREncodervalue--;
}
