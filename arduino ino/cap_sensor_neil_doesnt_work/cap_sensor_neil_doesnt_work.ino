//
// hello.txtx2.RP2040.ino
//    RP2040 XIAO two-channel transmit-receive step-response hello-world
//    overclock at 250 MHz
//
// Neil Gershenfeld 7/10/23
//

#define digitalWriteFast(pin,val) (val ? sio_hw->gpio_set = (1 << pin) : sio_hw->gpio_clr = (1 << pin))
#define digitalReadFast(pin) ((1 << pin) & sio_hw->gpio_in)

#define Rx1 7 // receive 1 pin (D5)
#define Tx1 0 // transmit 1 pin (D6)
#define Rx2 29 // receive 2 pin (D3)
#define Tx2 6 // transmit 2 pin (D4)
#define settle 20 // settle time
#define samples 2000 // number of samples to accumulate

void setup() {
   Serial.begin(115200);
   }

void loop() {
   }

void setup1() {
   pinMode(Tx1,OUTPUT);
   pinMode(Tx2,OUTPUT);
   }

void loop1() {
   int32_t up1,down1,up2,down2;
   up1 = down1 = up2 = down2 = 0;
   for (int i = 0; i < samples; ++i) {
      digitalWriteFast(Tx1,HIGH); // charge up
      up1 += analogRead(Rx1); // read
      delayMicroseconds(settle); //settle
      digitalWriteFast(Tx1,LOW); // charge down
      down1 += analogRead(Rx1); // read
      delayMicroseconds(settle); // settle
      digitalWriteFast(Tx2,HIGH); // charge up
      up2 += analogRead(Rx2); // read
      delayMicroseconds(settle); //settle
      digitalWriteFast(Tx2,LOW); // charge down
      down2 += analogRead(Rx2); // read
      delayMicroseconds(settle); // settle
      }
   Serial.print(up1-down1); // send difference
   Serial.print(',');
   Serial.println(up2-down2); // send difference
   Serial.flush(); // finish communicating before measuring
   }