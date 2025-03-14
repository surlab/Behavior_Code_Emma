// Configuration and initial setup
//update button in and trig read pin condition! 
//update duration
//update to start 1.5 sec sequence of 40 Hz flicker with 5 ms on time at each set of flicker
//troubleshoot led
//check power.
const long BAUD = 115200;

//set pins
const int BUTTON = 2;
const int LED = 3;
const int OPTO_PIN = 5;
const int TRIG_PIN = 10;

//set duration, timer variables 
bool stim_on = false;
unsigned long stim_start = 0;
unsigned long total_stim_dur = 1500; //msec

//set desired frequency
int freq = 40; //Hz
const float cycle_time = 1000.0/freq; //msec
const int on_time = 5; //msec 
const float off_time = cycle_time-on_time;

void setup() {
  pinMode(LED, OUTPUT);
  pinMode(OPTO_PIN,OUTPUT);
  pinMode(BUTTON, INPUT_PULLDOWN);
  pinMode(TRIG_PIN, INPUT_PULLDOWN);
  digitalWrite(LED,LOW);
  digitalWrite(OPTO_PIN,LOW);
  Serial.begin(BAUD);
  Serial.println("Off time: " +String(off_time/2));
}

void loop() {
  Serial.println("button read: " + String(digitalRead(BUTTON)));
  Serial.println("trig read: " + String(digitalRead(TRIG_PIN)));
  if (((digitalRead(TRIG_PIN) == HIGH ) || (digitalRead(BUTTON == HIGH)) && !stim_on){
    Serial.println("opto triggered");
    stim_on = true;
    stim_start = millis();
    while(millis()-stim_start<total_stim_dur){
      digitalWrite(OPTO_PIN,HIGH);
      digitalWrite(LED,HIGH);
      delay(on_time);
      digitalWrite(OPTO_PIN,LOW);
      digitalWrite(LED,LOW);
      delay(off_time/2);
      //split delay for opto in half to allow LED to stay on longer for visual :)
      delay(off_time/2);
    }
    stim_on = false;
    digitalWrite(OPTO_PIN,LOW);
    digitalWrite(LED,LOW);
  }
}

/*
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 'S') {
      stim_on = true;
      Serial.println("Opto stim started");
      Serial.println("frequency: " + String(freq) + "Hz");
      Serial.println("LED_on_time " + String(on_time) + "ms");
    } else if ((command == 'X')&&stim_on){
      stim_on = false;
      Serial.println("Opto stim stopped");
    } else if (command == 'X') {
      stim_on = false;
      Serial.println("No opto stim");
    }
  }
*/ 

