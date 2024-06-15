#include <Servo.h>

#define SERVO_INTERVAL  20 // Changing the servo position every 10ms (Speed of Servo)

Servo Servo1;
Servo Servo2;
Servo Servo3;
Servo Servo4;
Servo Servo5;
Servo Servo6;

int servoPin1 = 3;
int servoPin2 = 5;
int servoPin3 = 6;
int servoPin4 = 9;
int servoPin5 = 10;
int endEffector = 11;

int set_angle1 = 90, set_angle2 = 180, set_angle3 = 160, set_angle4 = 50, set_angle5 = 90, set_angle6 = 180;
int current_angle1 = 90, current_angle2 = 180, current_angle3 = 160, current_angle4 = 50, current_angle5 = 90, current_angle6 = 180;

unsigned long servo_timestamp = 0;
int done = 1; // To indicate whether the movement of the robotic arm is completed.

String params[6];

void setup()
{
  Servo1.attach(servoPin1);
  Servo2.attach(servoPin2);
  Servo3.attach(servoPin3);
  Servo4.attach(servoPin4);
  Servo5.attach(servoPin5);
  Servo6.attach(endEffector);
  Serial.begin(115200);
  while (!Serial){}
}

void loop() 
{
  String rxString = "";

  if (Serial.available() > 0) 
  {
    done = 0;
    while (Serial.available()) {
      // Delay to allow byte to arrive in input buffer/
      delay(2);

      // Read a single character from the buffer.
      char ch = Serial.read();

      rxString += ch;
    }

    int stringStart = 0;
    int arrayIndex = 0;

    for (int i = 0; i < rxString.length(); i++) {
      if (rxString.charAt(i) == ',') {

        params[arrayIndex] = "";

        params[arrayIndex] = rxString.substring(stringStart, i);

        stringStart = (i + 1);
        arrayIndex++;
      }
    }

    set_angle1 = params[0].toInt();
    set_angle2 = params[1].toInt();
    set_angle3 = params[2].toInt();
    set_angle4 = params[3].toInt();
    set_angle5 = params[4].toInt();
    set_angle6 = params[5].toInt();
  }

  // Smooth Movement of Robotic Arm
  if (millis() - servo_timestamp > SERVO_INTERVAL) {
    servo_timestamp += SERVO_INTERVAL;

    // Movement of Servo1
    if (set_angle1 > current_angle1) {
      current_angle1++;
    }
    else if (set_angle1 < current_angle1) {
      current_angle1--;
    }

    // Movement of Servo2
    if (set_angle2 > current_angle2) {
      current_angle2++;
    }
    else if (set_angle2 < current_angle2) {
      current_angle2--;
    }

    // Movement of Servo3
    if (set_angle3 > current_angle3) {
      current_angle3++;
    }
    else if (set_angle3 < current_angle3) {
      current_angle3--;
    }

    // Movement of Servo4
    if (set_angle4 > current_angle4) {
      current_angle4++;
    }
    else if (set_angle4 < current_angle4) {
      current_angle4--;
    }

    // Movement of Servo5
    if (set_angle5 > current_angle5) {
      current_angle5++;
    }
    else if (set_angle5 < current_angle5) {
      current_angle5--;
    }

    // Movement of End Effector
    if (set_angle6 > current_angle6) {
      current_angle6++;
    }
    else if (set_angle6 < current_angle6) {
      current_angle6--;
    }

    Servo1.write(current_angle1);
    Servo2.write(current_angle2);
    Servo3.write(current_angle3);
    Servo4.write(current_angle4);
    Servo5.write(current_angle5);
    Servo6.write(current_angle6);

    if (current_angle1 == set_angle1 && current_angle2 == set_angle2 && 
    current_angle3 == set_angle3 && current_angle4 == set_angle4 &&
    current_angle5 == set_angle5 && current_angle6 == set_angle6 && done == 0) {
      Serial.println('Done');
      done = 1;
    }
  }
}