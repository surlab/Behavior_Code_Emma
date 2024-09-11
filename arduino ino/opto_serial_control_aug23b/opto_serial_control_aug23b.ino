// Configuration and initial setup
const long BAUD = 115200;
bool stim_on = false;

//set pins
const int LED = 13;
const int OPTO = 3;

//set desired frequency
int freq = 40; //Hz
const float cycle_time = 1000.0/freq; //msec
const int on_time = 5; //msec 
const float off_time = cycle_time-on_time;

void setup() {
  // put your setup code here, to run once:
  pinMode(LED, OUTPUT);
  pinMode(OPTO,OUTPUT);
  digitalWrite(LED,LOW);
  digitalWrite(OPTO,LOW);
  //initialize serial communication
  Serial.begin(BAUD);
}

void loop() {
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

  if (stim_on) {
    digitalWrite(LED, HIGH);   // turn the LED on (HIGH is the voltage level)
    digitalWrite(OPTO,HIGH);
    delay(on_time);                       
    digitalWrite(LED, LOW);    // turn the LED off by making the voltage LOW
    digitalWrite(OPTO,LOW);
    delay(off_time);                
  }

}
