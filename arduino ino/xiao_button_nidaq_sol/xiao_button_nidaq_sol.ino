/*
this script reads for button press or digital nidaq signal to open solenoid.
update serial to communicate cap sensor data when we have a working version. 
*/
const long BAUD = 115200;

const int BUTTON = 4; //D9
const int NIDAQ = 28; //D2
const int LED_1 = 26; //D0 //would be for cap sensor if working
const int LED_2 = 27; //D1

const int SOLENOID_PIN = 3; //D10
int sol_duration = 30; //msec. dur for solenoid valve to open
bool sol_open = false;
unsigned long sol_start_time = 0;

void setup() {
  pinMode(LED_1, OUTPUT);
  pinMode(LED_2, OUTPUT);
  pinMode(BUTTON,INPUT_PULLDOWN);
  pinMode(NIDAQ, INPUT_PULLDOWN);
  
  pinMode(SOLENOID_PIN, OUTPUT);
  digitalWrite(SOLENOID_PIN, LOW);

  Serial.begin(BAUD);
}

void loop() {
  //start with if pin (connected to bnc == HIGH) then the button becomes an else if (){}
  if (digitalRead(NIDAQ)==HIGH && !sol_open){
    //open solenoid and turn on LED_1
    digitalWrite(LED_1, HIGH);
    digitalWrite(SOLENOID_PIN, HIGH);
    sol_start_time = millis();
    sol_open = true;
    Serial.println("Solenoid Activated");
  }
  else if (digitalRead(BUTTON)==HIGH && !sol_open){
    //open solenoid and turn on LED_1
    digitalWrite(LED_1, HIGH);
    digitalWrite(SOLENOID_PIN, HIGH);
    sol_start_time = millis();
    sol_open = true;
    Serial.println("Solenoid Activated");
  }
  if (sol_open) {
    // Check if solenoid should be closed
    if (millis() - sol_start_time > sol_duration) {
      // Turn off solenoid
      digitalWrite(SOLENOID_PIN, LOW);
      digitalWrite(LED_1, LOW);
      sol_open = false;
      Serial.println("Solenoid Deactivated");
    }
  }
}
