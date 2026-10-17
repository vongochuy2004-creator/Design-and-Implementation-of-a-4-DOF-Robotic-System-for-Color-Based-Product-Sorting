#include <AccelStepper.h>
#include <SoftwareSerial.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Pin definitions
const int pulsePin  = 3;
const int dirPin    = 4;
const int enaPin    = 5;
const int sensorPin = 2;

// SoftwareSerial của MASTER
SoftwareSerial masterSerial(10, 11);  // RX, TX

// LCD
LiquidCrystal_I2C lcd(0x27, 16, 2);

// AccelStepper
AccelStepper stepper(AccelStepper::DRIVER, pulsePin, dirPin);

// Trạng thái
bool runEnable = false;
bool detected = false;
bool lastDetected = false;
bool lastRunEnable = false;

// Buffer nhận lệnh
String inputBuffer = "";

// ------------------------------
void setup() {
  Serial.begin(9600);
  masterSerial.begin(19200);

  pinMode(enaPin, OUTPUT);
  pinMode(sensorPin, INPUT);
  digitalWrite(enaPin, LOW);    // enable driver

  stepper.setMaxSpeed(1000);
  stepper.setAcceleration(200);

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print(" SYSTEM READY ");
  lcd.setCursor(0, 1);
  lcd.print(" WAIT FOR CMD ");
  delay(800);
  lcd.clear();
}

// ------------------------------
void updateLCD(const String &l1, const String &l2) {
  lcd.setCursor(0, 0);
  lcd.print("                ");
  lcd.setCursor(0, 0);
  lcd.print(l1);

  lcd.setCursor(0, 1);
  lcd.print("                ");
  lcd.setCursor(0, 1);
  lcd.print(l2);
}

// ------------------------------
void processCommand(String cmd) {
  if (cmd == "C0") {
    runEnable = true;
  }
  if (cmd == "C1") {
    runEnable = false;
  }
}

// ------------------------------
void loop() {

  /* ======================================
     1. Nhận lệnh từ MASTER
     ====================================== */
  while (masterSerial.available()) {
    char c = masterSerial.read();

    if (c == '\n') {
      processCommand(inputBuffer);
      inputBuffer = "";
    } else {
      inputBuffer += c;
    }
  }

  /* ======================================
     2. Đọc cảm biến
     ====================================== */
  detected = (digitalRead(sensorPin) == LOW);

  // Khi cảm biến đổi trạng thái
  if (detected != lastDetected) {
    if (detected) {
      runEnable = false;
      masterSerial.println("D");
      updateLCD("SENSOR TRIGGER", "CONVEYOR STOP");
    } else {
      updateLCD("NO OBJECT", "READY TO RUN");
    }
    lastDetected = detected;
  }

  /* ======================================
     3. Điều khiển STEP MOTOR
     ====================================== */
  if (runEnable && !detected) {

    if (!lastRunEnable) {
      updateLCD("RUNNING...", "CONVEYOR ACTIVE");
    }
    lastRunEnable = true;

    digitalWrite(enaPin, LOW);
    stepper.setSpeed(300);
    stepper.runSpeed();

  }
  else {

    if (lastRunEnable && !detected) {
      updateLCD("STOPPED", "IDLE");
    }
    lastRunEnable = false;

    digitalWrite(enaPin, HIGH);  // tắt driver → dừng ngay

  }
}
