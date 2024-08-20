#include <CapacitiveSensor.h>
/*
okay the code is working great now. however, i need to add something. 
if more than 10 seconds passes since last solenoid opening,
 reset the sensor2_activity[3] to all true to allow new solenoid openings 
*/
// Configuration and initial setup
const long BAUD = 115200;
bool arduino_doing_things = false;

// Define the send and receive pins for the capacitive sensors
const int SENSOR_SEND_1 = 2;
const int SENSOR_RECEIVE_1 = 4;
const int SENSOR_SEND_2 = 5;
const int SENSOR_RECEIVE_2 = 7;

// Solenoid and LED pins
const int SOLENOID_PIN = 9;
const int SOLENOID_LED = 10;

// Create a CapacitiveSensor object
CapacitiveSensor capSensor_1 = CapacitiveSensor(SENSOR_SEND_1, SENSOR_RECEIVE_1);
CapacitiveSensor capSensor_2 = CapacitiveSensor(SENSOR_SEND_2, SENSOR_RECEIVE_2);
//how are prev_center and thresh_center determined? and should they be set independently (probably yes)
int prev_center_1 = 0;
const int threshold_center_1 = 20;
int prev_center_2 = 0;
const int threshold_center_2 = 20;

// Initialize sensor values
long sensorValue_1 = 0;
long sensorValue_2 = 0;

// LED and output pins
const int OUT_TO_LED_1 = 12;
const int OUT_TO_LED_2 = 13;
const int OUT_TO_UNO_1 = 3;
const int OUT_TO_UNO_2 = 6;

// Touch sensing variables
bool touch_active = false;
unsigned long touch_start_time = 0;
unsigned long touch_duration = 0;
const int set_touch_duration = 1500;

// Solenoid control variables
bool sol_open = false;
unsigned long sol_start_time = 0;
unsigned long sol_duration = 0;
const int set_sol_duration = 35;

// For tracking sensor 2 activity during the last three solenoid openings
bool sensor2_activity[3] = {true, true, true};  // Initially set to true to allow the first trial
int activity_index = 0;

// For checking solenoid pin status
int pinState = 0;

void setup() {
  pinMode(OUT_TO_LED_1, OUTPUT);
  pinMode(OUT_TO_LED_2, OUTPUT);
  pinMode(OUT_TO_UNO_1, OUTPUT);
  pinMode(OUT_TO_UNO_2, OUTPUT);
  pinMode(SOLENOID_PIN, OUTPUT);
  pinMode(SOLENOID_LED, OUTPUT);
  digitalWrite(SOLENOID_PIN, LOW);
  digitalWrite(SOLENOID_LED, LOW);

  Serial.begin(BAUD);

  capSensor_1.set_CS_AutocaL_Millis(0xFFFFFFFF);
  capSensor_2.set_CS_AutocaL_Millis(0xFFFFFFFF);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 'S') {
      arduino_doing_things = true;
      Serial.println("Arduino doing things, Arduino started");
      Serial.println("touch duration: " + String(set_touch_duration) + "ms");
      Serial.println("solenoid open for " + String(set_sol_duration) + "ms");
    } else if (command == 'X') {
      arduino_doing_things = false;
      Serial.println("Arduino not doing things, Arduino stopped");
    }
  }

  if (arduino_doing_things) {
    sensorValue_1 = capSensor_1.capacitiveSensor(30);
    sensorValue_2 = capSensor_2.capacitiveSensor(30);

    sensorValue_1 = 0.9 * prev_center_1 + 0.1 * sensorValue_1;
    prev_center_1 = 0;
    sensorValue_2 = 0.9 * prev_center_2 + 0.1 * sensorValue_2;
    prev_center_2 = 0;

    Serial.print("bar: ");
    Serial.println(sensorValue_1);
    Serial.print("lick: ");
    Serial.println(sensorValue_2);

    if (sensorValue_1 > threshold_center_1) {
      digitalWrite(OUT_TO_LED_1, HIGH);
      digitalWrite(OUT_TO_UNO_1, HIGH);
    } else {
      digitalWrite(OUT_TO_LED_1, LOW);
      digitalWrite(OUT_TO_UNO_1, LOW);
    }
    if (sensorValue_2 > threshold_center_2) {
      digitalWrite(OUT_TO_LED_2, HIGH);
      digitalWrite(OUT_TO_UNO_2, HIGH);
      // Update sensor2_activity if a touch is detected
      sensor2_activity[activity_index] = true;
    } else {
      digitalWrite(OUT_TO_LED_2, LOW);
      digitalWrite(OUT_TO_UNO_2, LOW);
    }

    if (sensorValue_1 > threshold_center_1 && !sol_open) {
      if (!touch_active) {
        touch_active = true;
        touch_start_time = millis();
      }
      touch_duration = millis() - touch_start_time;
      if (touch_duration > set_touch_duration) {
        // Check if any of the last three sensor 2 activities detected a touch
        bool allow_solenoid_opening = false;
        for (int i = 0; i < 3; i++) {
          if (sensor2_activity[i]) {
            allow_solenoid_opening = true;
            break;
          }
        }

        if (allow_solenoid_opening) {
          digitalWrite(SOLENOID_PIN, HIGH);
          sol_start_time = millis();
          sol_open = true;
          Serial.println("Solenoid Activated");

          // Reset the sensor2_activity for the current index to false
          sensor2_activity[activity_index] = false;

          // Reset touch sensor(1/bar) timer
          touch_start_time = millis();
          touch_duration = 0;
        } else {
          Serial.println("Solenoid Blocked: No touch detected at sensor 2 in the last 3 solenoid activations.");
        }
      }
    } else {
      if (touch_active) {
        touch_active = false;
        touch_duration = 0;
      }
    }

    pinState = digitalRead(SOLENOID_PIN);
    Serial.println(pinState);

    sol_duration = millis() - sol_start_time;
    if ((sol_open) && (sol_duration > set_sol_duration)) {
      digitalWrite(SOLENOID_PIN, LOW);
      sol_open = false;
      sol_start_time = millis();
      sol_duration = 0;

      // Move to the next activity_index for the next cycle
      activity_index = (activity_index + 1) % 3;
    }

    delay(1);
  }
}

