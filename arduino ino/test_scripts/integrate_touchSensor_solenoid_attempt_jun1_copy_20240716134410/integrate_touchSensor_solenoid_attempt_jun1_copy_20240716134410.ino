const long BAUD = 115200;
const int solenoidPin = 7; // Pin for solenoid
const int solenoidLED = 6; // Reporter LED for solenoid activation
const int touchLED = 10; // Reporter LED for touch activation
const int touchPins[] = {3, 4}; // Pins for capacitive touch sensor
const int numTouchPins = 2;
const int measure_int = 50; //msec, how frequently it reads touch sensor
bool touchDetected = false;

// Variables to track touch state and duration
bool touchActive[numTouchPins] = {false, false};
unsigned long touchStartTime[numTouchPins] = {0, 0};
unsigned long touchDuration[numTouchPins] = {0, 0};

void setup() {
  Serial.begin(BAUD);
  pinMode(touchLED, OUTPUT);
  pinMode(solenoidPin, OUTPUT);
  pinMode(solenoidLED, OUTPUT);
  digitalWrite(touchLED, LOW);
  digitalWrite(solenoidPin, LOW);
  digitalWrite(solenoidLED, LOW);
  for (int i = 0; i < numTouchPins; i++) {
    pinMode(touchPins[i], INPUT);
  }
}

void loop() {
  while(true){ // infinite loop to check touch sensor every 
    // Check touch sensors and print their values
    for (int i = 0; i < numTouchPins; i++) {
      int touchValue = digitalRead(touchPins[i]);
      Serial.print("Pin ");
      Serial.print(touchPins[i]);
      Serial.print(" state: ");
      Serial.println(touchValue);
      if (touchValue == 0) {
        touchDetected = true;
        if (!touchActive[i]){//indicates touch just started (bc touchValue was read as touch, but its currently recorded as not active touch)
          touchActive[i]=true;
          touchStartTime[i]=millis();
        }
        //where to put so it doesnt spaz??
        touchDuration[i]=millis()-touchStartTime[i];
        //NEED TO TAKE tHIS OUT OF THE FOREVER LOOP??? but also still have an ability to reset the touchDuration
        if (touchDuration[0]>1000){//if pin 3 sense touch for at least 1000 msec, open solenoid. 
            digitalWrite(solenoidPin, HIGH); // Activate solenoid
            digitalWrite(solenoidLED, HIGH);
            delay(50); //solenoid valve open time
            digitalWrite(solenoidPin, LOW); // Deactivate solenoid
            delay(50); // extend LED to make solenoid activation more obvious
            digitalWrite(solenoidLED, LOW);
            Serial.println("Solenoid Activated");
            touchDuration[0]=0;
            touchStartTime[0]=millis(); //this should prevent the constant opening
        }
      } else {
        touchDetected = false;
        if(touchActive[i]){//indicates touch just ended
          touchActive[i]=false;
          touchDuration[i]=0;
        }
      }
    }
    // Control the touch LED based on touch detection
    if (touchDetected) { //this is currently agnostic to input at pin 3 or 4 (ie LED will turn on if pin 3 OR 4 sense touch)
      digitalWrite(touchLED, HIGH); // Turn on the LED if any touch is detected
    } else {
      digitalWrite(touchLED, LOW); // Turn off the LED if no touch is detected
    }
    delay(measure_int);
  } 


}
