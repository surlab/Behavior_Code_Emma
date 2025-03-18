#include <CapacitiveSensor.h>

// Configuration and initial setup
const long BAUD = 115200;
bool arduino_doing_things = false;
bool opto_trigger_active = false;

// LED and output pins
const int OUT_TO_LED_1 = 10;
const int OUT_TO_LED_2 = 11;

// Solenoid and LED pins
const int SOLENOID_PIN = 5;
const int SOLENOID_LED = 13;

// opto trigger pin 
const int TRIGGER_OPTO = 4;

// Define the send and receive pins for the capacitive sensors
const int SENSOR_SEND_1 = 6;
const int SENSOR_RECEIVE_1 = 7;
const int SENSOR_SEND_2 = 8;
const int SENSOR_RECEIVE_2 = 9;

// Create a CapacitiveSensor object
CapacitiveSensor capSensor_1 = CapacitiveSensor(SENSOR_SEND_1, SENSOR_RECEIVE_1);
CapacitiveSensor capSensor_2 = CapacitiveSensor(SENSOR_SEND_2, SENSOR_RECEIVE_2);

int prev_center_1 = 0;
const int threshold_center_1 = 10;
int prev_center_2 = 0;
const int threshold_center_2 = 15;

// Initialize sensor values
long sensorValue_1 = 0;
long sensorValue_2 = 0;

// Touch sensing variables
bool touch_active = false;
unsigned long touch_start_time = 0;
unsigned long touch_duration = 0;
const int set_touch_duration = 3000;

// Solenoid control variables
bool sol_open = false;
unsigned long sol_start_time = 0;
unsigned long sol_duration = 0;
const int set_sol_duration = 55; //msec

//opto control variables
const int chance_opto = 30; //percent chance of opto trial
bool opto_t_on = false;
unsigned long opto_t_start = 0;
unsigned long opto_t_dur = 0;
const int opto_trigger_duration = 10;//msec

// For checking solenoid pin status
int pinState = 0;

void setup() {
  pinMode(OUT_TO_LED_1, OUTPUT);
  pinMode(OUT_TO_LED_2, OUTPUT);
  pinMode(SOLENOID_PIN, OUTPUT);
  pinMode(SOLENOID_LED, OUTPUT);
  pinMode(TRIGGER_OPTO, OUTPUT);
  digitalWrite(SOLENOID_PIN, LOW);
  digitalWrite(SOLENOID_LED, LOW);
  digitalWrite(TRIGGER_OPTO, LOW);
 
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
    } else if (command == 'O') {
      arduino_doing_things = true;
      opto_trigger_active = true;
      Serial.println("Arduino doing OPTO things, Arduino started. \n primary arduino uno will send trigger signal to secondary nano. \n nano controls opto duration, frequency, duty cycle, etc. ");
      Serial.println("touch duration: " + String(set_touch_duration) + "ms");
      Serial.println("solenoid open for " + String(set_sol_duration) + "ms");
    } else if (command == 'X') {
      arduino_doing_things = false;
      opto_trigger_active = false;
      Serial.println("Arduino not doing things, Arduino stopped");
      digitalWrite(OUT_TO_LED_1, LOW);
      digitalWrite(OUT_TO_LED_2, LOW);
      digitalWrite(SOLENOID_PIN, LOW);
      digitalWrite(SOLENOID_LED, LOW);
      digitalWrite(TRIGGER_OPTO, LOW);
    }
  }

  if (arduino_doing_things) {
    sensorValue_1 = capSensor_1.capacitiveSensor(30);
    sensorValue_2 = capSensor_2.capacitiveSensor(30);

    sensorValue_1 = 0.9 * prev_center_1 + 0.1 * sensorValue_1;
    //prev_center_1 = sensorValue_1;
    sensorValue_2 = 0.9 * prev_center_2 + 0.1 * sensorValue_2;
    //prev_center_2 = sensorValue_2;

    Serial.print("bar: ");
    Serial.println(sensorValue_1);
    Serial.print("lick: ");
    Serial.println(sensorValue_2);

    if (sensorValue_1 > threshold_center_1) {
      digitalWrite(OUT_TO_LED_1, HIGH);
    } else {
      digitalWrite(OUT_TO_LED_1, LOW);
    }

    if (sensorValue_2 > threshold_center_2) {
      digitalWrite(OUT_TO_LED_2, HIGH);
    } else {
      digitalWrite(OUT_TO_LED_2, LOW);
    }

    if (sensorValue_1 > threshold_center_1 && !sol_open) {
      if (!touch_active) {
        touch_active = true;
        touch_start_time = millis();
      }
      touch_duration = millis() - touch_start_time;
      if (touch_duration > set_touch_duration && !sol_open) {
        //if opto session,30% chance to send opto trigger signal to micro
        if (opto_trigger_active && (random(100) < chance_opto)) {
          digitalWrite(TRIGGER_OPTO, HIGH);
          opto_t_start = millis();
          opto_t_on = true;
          Serial.println("Opto trigger signal sent to micro");
        }

        //open solenoid (after opto trigger in case there is any delay)
        digitalWrite(SOLENOID_PIN, HIGH);
        digitalWrite(SOLENOID_LED, HIGH);
        sol_start_time = millis();
        sol_open = true;
        Serial.println("Solenoid Activated");

        // Reset touch sensor(1/bar) timer
        touch_start_time = millis();
        touch_duration = 0;
      }
    } else {
      if (touch_active) {
        touch_active = false;
        touch_duration = 0;
      }
    }

    pinState = digitalRead(SOLENOID_PIN);
    Serial.print("Solenoid pin state: ");
    Serial.println(pinState);

    sol_duration = millis() - sol_start_time;
    if ((sol_open) && (sol_duration > set_sol_duration)) {
      digitalWrite(SOLENOID_PIN, LOW);
      digitalWrite(SOLENOID_LED,LOW);
      sol_open = false;
      sol_start_time = millis(); //not necessary
    }

    //turn off opto trigger after opto_trigger_duration
    opto_t_dur = millis() - opto_t_start;
    if (opto_t_on && (opto_t_dur > opto_trigger_duration)) {
      digitalWrite(TRIGGER_OPTO, LOW);
      opto_t_on = false; // end trigger signal
      opto_t_start = millis();//not necessary
    }

    delay(1);
  }
}

