//set pins
const int LED = 13;
const int OPTO = 3;

//set desired frequency
int freq = 1; //Hz
const float cycle_time = 1000/freq; //msec
const int on_time = 5; //msec 
const float off_time = cycle_time-on_time;

// the setup function runs once when you press reset or power the board
void setup() {
  // pins on arduino as an output to laser
  pinMode(LED, OUTPUT);
  pinMode(OPTO,OUTPUT);
}

//runs for infinity
void loop() {
    {
  digitalWrite(LED, HIGH);   // turn the LED on (HIGH is the voltage level)
  digitalWrite(OPTO,HIGH);
  delay(on_time);                       // wait for 5 ms
  digitalWrite(LED, LOW);    // turn the LED off by making the voltage LOW
  digitalWrite(OPTO,LOW);
  delay(off_time);                  // wait for 45 ms
  }
 }
