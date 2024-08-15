const long BAUD = 115200;
const int SOLENOID_PIN = 9; // Pin for solenoid
const int SOLENOID_LED = 12; // Reporter LED for solenoid activation
const int set_sol_duration = 30; // Duration for solenoid to stay open (in milliseconds)

// For controlling solenoid
bool sol_open = false;
unsigned long sol_start_time = 0;

void setup() {
  pinMode(SOLENOID_PIN, OUTPUT);
  pinMode(SOLENOID_LED, OUTPUT);
  digitalWrite(SOLENOID_PIN, LOW);
  digitalWrite(SOLENOID_LED, LOW);
  // Initialize serial communication
  Serial.begin(BAUD);
  Serial.println("Arduino Ready");
}

void loop() {
  if (Serial.available() > 0 && !sol_open) { // Check for new command only if solenoid is not open
    char command = Serial.read();
    if (command == 'C') {
      // Open solenoid
      digitalWrite(SOLENOID_PIN, HIGH);
      digitalWrite(SOLENOID_LED, HIGH);
      sol_start_time = millis();
      sol_open = true;
      Serial.println("Solenoid Activated");
    }
  }

  if (sol_open) {
    // Check if solenoid should be closed
    if (millis() - sol_start_time > set_sol_duration) {
      // Turn off solenoid
      digitalWrite(SOLENOID_PIN, LOW);
      digitalWrite(SOLENOID_LED, LOW);
      sol_open = false;
      Serial.println("Solenoid Deactivated");
    }
  }
}