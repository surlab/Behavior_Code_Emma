//set desired frequency
int freq = 40 //Hz
const float cycle_time = 1000/freq //msec
const int on_time = 5 //msec 
const float off_time = cycle_time-on_time

// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin from medpc as input
  // pins on arduino as an output to laser
  pinMode(11, OUTPUT);
}

// the loop function runs over and over again forever
// read state on input pin
void loop() {
    {
  digitalWrite(11, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(on_time);                       // wait for 5 ms
  digitalWrite(11, LOW);    // turn the LED off by making the voltage LOW
  delay(off_time);                  // wait for 45 ms
  }
 }
