const long BAUD = 115200;
const int solenoidPin = 9; // Pin for solenoid
const int solenoidLED = 12; // Reporter LED for solenoid activation
const unsigned long duration = 60000; // Total duration of 60 seconds
const unsigned long valve_open = 500; //msec, time valve is open should be calibrated.
const unsigned long interval = 2500-valve_open; // Interval of 2.5 seconds

void setup()
{
  Serial.begin(BAUD);
  pinMode(solenoidPin, OUTPUT);
  pinMode(solenoidLED, OUTPUT);
  digitalWrite(solenoidPin, LOW);
  digitalWrite(solenoidLED, LOW);
}

void loop()
{
  if (Serial.available() > 0)
  {
    char command = Serial.read();
    if (command == 'S')
    {
      unsigned long startTime = millis();
      while (millis() - startTime < duration)
      {
        digitalWrite(solenoidPin, HIGH);
        delay(valve_open);
        digitalWrite(solenoidPin, LOW);
        digitalWrite(solenoidLED, HIGH);
        delay(interval / 2); // Activate for half of the interval (1.25 seconds)
        digitalWrite(solenoidLED, LOW);
        delay(interval / 2); // Deactivate for half of the interval (1.25 seconds)
      }
      Serial.println("Completed");
    }
  }
}
