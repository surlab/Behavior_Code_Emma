
const int SOLENOID_PIN = 3; //D10

//Capacitive sensing setup
const int CAP_SEND_1 = 0; //D6
const int CAP_RECEIVE_1 = 7; //D5
const int CAP_SEND_2 = 6; //D4
const int CAP_RECEIVE_2 = 29; //D3
const int CAP_LED_1 = 26; //D0
const int CAP_LED_2 = 27; //D1

void setup() {
  // Initialize the serial monitor
  Serial.begin(9600);

  pinMode(CAP_SEND_1, OUTPUT);    // Set the send pin as OUTPUT
  pinMode(CAP_RECEIVE_1, INPUT);  // Set the receive pin as INPUT

  pinMode(CAP_LED_1, OUTPUT);
  pinMode(CAP_LED_2, OUTPUT);
}

void loop() {
  long touchValue = measureCapacitance();
  Serial.println(touchValue); // Print the measured value
  delay(50);                  // Short delay for stability
}

long measureCapacitance() {
  // Step 1: Discharge the capacitor
  pinMode(CAP_RECEIVE_1, OUTPUT); // Temporarily set receivePin to OUTPUT
  digitalWrite(CAP_RECEIVE_1, LOW); // Discharge the receive pin
  delayMicroseconds(10);         // Ensure it fully discharges
  pinMode(CAP_RECEIVE_1, INPUT);    // Set back to INPUT to measure

  // Step 2: Send a pulse to charge the capacitor
  digitalWrite(CAP_SEND_1, HIGH); // Send pulse
  delayMicroseconds(10);       // Short pulse
  digitalWrite(CAP_SEND_1, LOW);  // Stop charging

  // Step 3: Measure discharge time
  long startTime = micros();
  while (digitalRead(CAP_RECEIVE_1) == LOW) {
    // Wait for the pin to go HIGH (capacitor charges)
    if (micros() - startTime > 30000) {
      // Timeout for safety, in case of no response
      return -1;
    }
  }
  long endTime = micros();

  // Calculate the time taken to charge
  return endTime - startTime;
}



// listen for digital input from nidaq 
// open solenoid using timer method

// listen for signal at button pin 
// open solenoid using timer method

//do we need serial communication actually? maybe not? 

//two capacitive sensors use library/code from rig! 
//program led to turn on when sensor on 

// connect power and solenoid appropriately 