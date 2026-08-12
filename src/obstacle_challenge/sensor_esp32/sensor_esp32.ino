/*
 * RT-X7 — Obstacle Challenge — Sensor ESP32 firmware
 *
 * Reads:
 *   - Left TF-Luna  (I2C, Wire  bus, addr TFLUNA_ADDR)
 *   - Right TF-Luna (I2C, Wire1 bus, addr TFLUNA_ADDR)
 *   - Front TF-LC02 (UART, HardwareSerial2)
 *
 * Drives:
 *   - Sensor-cluster servo, which physically rotates the left/right/front
 *     sensor cluster in sync with steering, so the sensors stay aimed
 *     correctly through a turn instead of just being discounted in
 *     software (see README > Systems Thinking).
 *
 * Streams to the Raspberry Pi over UART (Serial):
 *   L:<left_mm>,R:<right_mm>,F:<front_mm>\n
 *
 * Accepts cluster-servo angle commands from the Pi over the same link:
 *   C:<angle_deg>\n
 *
 * NOTE ON I2C ADDRESSING: both TF-Luna units ship with the same default
 * I2C address. Runtime address-change commands reported success but did
 * NOT persist on real hardware, so this firmware avoids that entirely by
 * putting each TF-Luna on its own independent I2C bus (Wire + Wire1)
 * rather than trying to share one bus with reassigned addresses.
 */

#include <Wire.h>
#include <ESP32Servo.h>

// ---- Pin map ----
#define I2C0_SDA 21
#define I2C0_SCL 22
#define I2C1_SDA 18
#define I2C1_SCL 19

#define FRONT_LIDAR_RX 16   // ESP32 RX2 <- TF-LC02 TX
#define FRONT_LIDAR_TX 17   // ESP32 TX2 -> TF-LC02 RX (3.3V ONLY)

#define CLUSTER_SERVO_PIN 25

#define TFLUNA_ADDR 0x10

HardwareSerial FrontLidarSerial(2);
Servo clusterServo;

int leftDistanceMm = 9999;
int rightDistanceMm = 9999;
int frontDistanceMm = 9999;

const uint8_t FRONT_FRAME_HEADER[2] = {0x59, 0x59};
uint8_t frontFrameBuf[9];
uint8_t frontFrameIdx = 0;

unsigned long lastStreamMs = 0;
const unsigned long STREAM_PERIOD_MS = 20;   // 50 Hz to match Pi control loop

void setup() {
  Serial.begin(115200);              // link to Raspberry Pi
  FrontLidarSerial.begin(115200, SERIAL_8N1, FRONT_LIDAR_RX, FRONT_LIDAR_TX);

  Wire.begin(I2C0_SDA, I2C0_SCL);     // left TF-Luna bus
  Wire1.begin(I2C1_SDA, I2C1_SCL);    // right TF-Luna bus

  clusterServo.setPeriodHertz(50);
  clusterServo.attach(CLUSTER_SERVO_PIN, 500, 2400);
  clusterServo.write(90);             // centered

  Serial.println("[sensor_esp32] ready");
}

void loop() {
  readTFLuna(Wire, leftDistanceMm);
  readTFLuna(Wire1, rightDistanceMm);
  readFrontLidar();
  handleIncomingCommands();

  unsigned long now = millis();
  if (now - lastStreamMs >= STREAM_PERIOD_MS) {
    lastStreamMs = now;
    streamToPi();
  }
}

// TF-Luna I2C read: distance is registers 0x00 (low) / 0x01 (high), in cm.
void readTFLuna(TwoWire &bus, int &outMm) {
  bus.beginTransmission(TFLUNA_ADDR);
  bus.write(0x00);
  if (bus.endTransmission(false) != 0) {
    return;   // keep last known reading on comms error
  }
  bus.requestFrom(TFLUNA_ADDR, 2);
  if (bus.available() < 2) return;
  uint8_t lo = bus.read();
  uint8_t hi = bus.read();
  int distCm = (hi << 8) | lo;
  outMm = distCm * 10;
}

// TF-LC02 UART frame: 0x59 0x59 DIST_L DIST_H STRENGTH_L STRENGTH_H MODE_L MODE_H CHECKSUM
void readFrontLidar() {
  while (FrontLidarSerial.available()) {
    uint8_t b = FrontLidarSerial.read();

    if (frontFrameIdx < 2) {
      if (b == FRONT_FRAME_HEADER[frontFrameIdx]) {
        frontFrameBuf[frontFrameIdx++] = b;
      } else {
        frontFrameIdx = 0;
      }
      continue;
    }

    frontFrameBuf[frontFrameIdx++] = b;

    if (frontFrameIdx >= 9) {
      uint8_t checksum = 0;
      for (int i = 0; i < 8; i++) checksum += frontFrameBuf[i];
      if (checksum == frontFrameBuf[8]) {
        int distCm = frontFrameBuf[2] | (frontFrameBuf[3] << 8);
        frontDistanceMm = distCm * 10;
      }
      frontFrameIdx = 0;
    }
  }
}

// Accepts "C:<angle>\n" from the Pi to steer the cluster servo.
void handleIncomingCommands() {
  static String buf;
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      applyClusterCommand(buf);
      buf = "";
    } else {
      buf += c;
    }
  }
}

void applyClusterCommand(const String &line) {
  int idx = line.indexOf("C:");
  if (idx < 0) return;
  int angleDeg = line.substring(idx + 2).toInt();
  // angleDeg is steering-relative (-40..40); map to servo center 90.
  int servoAngle = constrain(90 + angleDeg, 40, 140);
  clusterServo.write(servoAngle);
}

void streamToPi() {
  Serial.print("L:");
  Serial.print(leftDistanceMm);
  Serial.print(",R:");
  Serial.print(rightDistanceMm);
  Serial.print(",F:");
  Serial.println(frontDistanceMm);
}
