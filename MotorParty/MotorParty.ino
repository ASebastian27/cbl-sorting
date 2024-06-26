#include <AFMotor.h>
#include <Servo.h> 

// DC hobby servo
Servo servo1;        // arm servo
Servo servo2;        // dispenser servo
AF_DCMotor motor(4); // big conveyor motor
AF_DCMotor motor2(3); // small conveyor motor

void setup() {
  Serial.begin(9600); // set up Serial library at 9600 bps
  servo1.attach(10);  // attach servo1 to port 10
  servo1.write(0);    // move servo1 to init pos
  
  //motor.setSpeed(200);// set motor speed
  motor.run(RELEASE); // release motor
  delay(1000); 
  
  //motor2.setSpeed(200);
  motor2.run(RELEASE);
  delay(1000);        // delay to warm up

  servo2.attach(9);   // attach second servo to port 9
}

void moveSmallConveyor() {
  motor2.run(FORWARD);
  // Move small conveyor
  uint8_t i;
  motor2.setSpeed(254);
  delay(5000);
  motor2.setSpeed(0);
  motor2.run(RELEASE);
}

void moveBigConveyor() {
  motor.run(FORWARD);
  // Move BIG conveyor
  uint8_t i;
  for (i=0; i<255; i++) { // start conveyor w PID
    motor.setSpeed(i);  
    delay(10);
  }
  delay(5000);        // keep conveyor on for 5 sec
  motor.setSpeed(0);  // turn motor off
  motor.run(RELEASE); // stop main conveyor
}

void punch() {
  // Dispense arm
  servo2.write(140); // extend arm at max speed
  delay(500);        // for 600ms
  
  servo2.write(40);   // retract arm at max speed
  delay(500);        // for 800ms
  
  servo2.write(90);  // do nothing
  delay(1000);       // for 1s
}

void dispense() {

  moveSmallConveyor();
  punch();
  moveBigConveyor();
  
  delay(1000);         // do nothing for 1s
  servoMoveTo(0);     // reset servo
}

int sleep = 1000;

void servoMoveTo(int deg) {
  servo1.write(deg);
  delay(sleep);
  // Serial.print(deg);
}

void letFree() {
  servoMoveTo(0);
}

void loop() {
  if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n');
    if (message == "65") {
      Serial.print("Moving to RED pos\n");
      servoMoveTo(40);
      punch();
      moveBigConveyor();
      letFree();
    } else if (message == "135") {
      Serial.print("Moving to BLUE pos\n");
      servoMoveTo(110);
      punch();
      moveBigConveyor();
      letFree();
    } else if (message == "0") {
      Serial.print("Moving to GREEN pos\n");
      servoMoveTo(0);
      punch();
      moveBigConveyor();
      letFree();
    } else if (message == "free") {
      Serial.print("Freeing\n");
      letFree();
    } else if (message == "load") {
      moveSmallConveyor();
    } else if (message == "punch") {
      punch();
    } else if (message == "big") {
      moveBigConveyor();
    }
  }
}
