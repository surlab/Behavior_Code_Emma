const long BAUD = 115200;
const int SOLENOID_PIN = 9; // Pin for solenoid
const int SOLENOID_LED = 12; // Reporter LED for solenoid activation
int set_sol_duration = 30; // Default duration for solenoid to stay open (in milliseconds)

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
    String command = Serial.readStringUntil('\n'); // Read the command until newline
    command.trim(); // Remove any extra whitespace

    if (command == "C") {
      // Open solenoid
      digitalWrite(SOLENOID_PIN, HIGH);
      digitalWrite(SOLENOID_LED, HIGH);
      sol_start_time = millis();
      sol_open = true;
      Serial.println("Solenoid Activated");
    } 
    else if (command.startsWith("SET_SOL_DURATION=")) {
      // Extract the duration from the command and set the new solenoid duration
      set_sol_duration = command.substring(17).toInt(); // Get the integer value after the command
      Serial.print("Solenoid duration updated to: ");
      Serial.print(set_sol_duration);
      Serial.println(" ms");
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
