#include <CapacitiveSensor.h>
//maybe i should add lines to prevent solenoid from opening when sensor 2 is active (mouse holding spout)
const long BAUD = 115200;
bool arduino_doing_things = false;
// Define the send and receive pins for the capacitive sensors
//BAR_1 = SENSOR_VALUE_1
const int SENSOR_SEND_1 = 2;
const int SENSOR_RECEIVE_1 = 4;
//LICK_2 = SENSOR_VALUE_2
const int SENSOR_SEND_2 = 5;
const int SENSOR_RECEIVE_2 = 7;
//solenoid
const int SOLENOID_PIN = 9;
const int SOLENOID_LED = 10;
// Create a CapacitiveSensor object
CapacitiveSensor capSensor_1 = CapacitiveSensor(SENSOR_SEND_1, SENSOR_RECEIVE_1);
CapacitiveSensor capSensor_2 = CapacitiveSensor(SENSOR_SEND_2, SENSOR_RECEIVE_2);
// initialize sensor values
long sensorValue_1 = 0;
long sensorValue_2 = 0;
//only one LED rn
const int OUT_TO_LED_1 = 12;
const int OUT_TO_LED_2 = 13;
//digital output to analog input on uno
const int OUT_TO_UNO_1 = 3;
const int OUT_TO_UNO_2 = 6;
//how are prev_center and thresh_center determined? and should they be set independently (probably yes)
int prev_center_1 = 0;
const int threshold_center_1 = 20;
int prev_center_2 = 0;
const int threshold_center_2 = 20;

//for bar touch sensing
bool touch_active = false;
unsigned long touch_start_time = 0;
unsigned long touch_duration = 0;
int set_touch_duration = 1000;
//for opening solenoid
bool sol_open = false;
unsigned long sol_start_time = 0;
unsigned long sol_duration = 0;
int set_sol_duration = 20;
//for solenoid pin status check
int pinState = 0;
void setup() {
  // Initialize the OUT_CENTER pin as an output
  pinMode(OUT_TO_LED_1, OUTPUT);
  pinMode(OUT_TO_LED_2, OUTPUT);
  pinMode(OUT_TO_UNO_1, OUTPUT);
  pinMode(OUT_TO_UNO_2, OUTPUT);
  pinMode(SOLENOID_PIN, OUTPUT);
  pinMode(SOLENOID_LED, OUTPUT);
  digitalWrite(SOLENOID_PIN, LOW);
  digitalWrite(SOLENOID_LED, LOW);
  // Initialize serial communication
  Serial.begin(BAUD);

  // Optional: set the capacitive sensor to use a higher resolution measurement
  capSensor_1.set_CS_AutocaL_Millis(0xFFFFFFFF);
  capSensor_2.set_CS_AutocaL_Millis(0xFFFFFFFF);
}

void loop() {
  //check for start, stop commands from python 
  //set state as arduino_doing_things (run it) or not (dont run script)
  if (Serial.available()>0){
    //char command = Serial.read(); //original, can use when only sending letter commands. 
    String command = Serial.readStringUntil('\n');  // Read the command until a newline character
    command.trim();  // Remove any extra whitespace
    if (command == 'S'){
      arduino_doing_things = true;
      Serial.println("Arduino doing things, Arduino started");
      Serial.println("default touch duration: " + String(set_touch_duration) + "ms");
      Serial.println("default solenoid open for " + String(set_sol_duration) + "ms");
    } else if (command == 'X'){
      arduino_doing_things = false;
      Serial.println("Arduino not doing things, Arduino stopped");
    } else if (command.startsWith("SET_TOUCH=")){ //takes string starting from position 10 on
      set_touch_duration = command.substring(10).toInt();
      Serial.println("Touch duration updated to " + String(set_touch_duration) + " ms"); 
    } else if (command.startsWith("SET_SOL=")){ //takes string starting from position 8 on
      set_sol_duration = command.substring(8).toInt();
      Serial.println("Solenoid open duration updated to " + String(set_sol_duration) + " ms");
    }
  }

  if(arduino_doing_things){
    // Perform the capacitive sensing (30 samples) //why 30 and at what rate??
    sensorValue_1 = capSensor_1.capacitiveSensor(30);
    sensorValue_2 = capSensor_2.capacitiveSensor(30);
    // Low pass filter
    sensorValue_1 = 0.9 * prev_center_1 + 0.1 * sensorValue_1;
    prev_center_1 = 0;
    sensorValue_2 = 0.9 * prev_center_2 + 0.1 * sensorValue_2;
    prev_center_2 = 0;
    //print to serial monitor
    Serial.print("bar: ");    
    Serial.println(sensorValue_1);
    Serial.print("lick: ");
    Serial.println(sensorValue_2);

    //REPORTER LED. check if sensor>threshold. 
    //light up LED if signal detected for sensor 1 or 2.
    //send analog input to UNO for solenoid control (sep arduino necessary because of delay statements)
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
      } else {
        digitalWrite(OUT_TO_LED_2, LOW);
        digitalWrite(OUT_TO_UNO_2, LOW);
      }//END REPORTER LED.
  //break *
      //BAR(SENSOR_1)DETECTION
      if (sensorValue_1 > threshold_center_1){
        if (!touch_active){ //one time measurement of touch_start_time per event
          touch_active=true;
          touch_start_time=millis();
        }
        //only measure touch_duration during active touch
        touch_duration = millis()-touch_start_time;
        if (touch_duration>set_touch_duration){
          //open solenoid
          digitalWrite(SOLENOID_PIN,HIGH);
          sol_start_time = millis();
          sol_open = true;
          Serial.println("Solenoid Activated");
          //reset touch sensor(1/bar) timer
          touch_start_time = millis();//necessary
          touch_duration=0;//not necessary (touch duration redefined each iteration of loop)
        }
      } else{
        if (touch_active){
          touch_active=false;
          touch_duration=0;
        }
      } 
      //for checking solenoid pin state, delete later
      pinState = digitalRead(SOLENOID_PIN);
      Serial.println (pinState);
      sol_duration = millis()-sol_start_time;
      if ((sol_open)&&(sol_duration>set_sol_duration)){
        //turn off solenoid pin/led
        digitalWrite(SOLENOID_PIN,LOW);
        sol_open=false;
        //reset solenoid timer
        sol_start_time = millis();
        sol_duration=0;
      }
      //breal *
      // Short delay before the next loop iteration
      delay(5);
  }
}