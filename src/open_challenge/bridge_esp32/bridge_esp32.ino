/*
 * RT-X7 — Bridge ESP32 firmware (shared for Open + Obstacle Challenge)
 *
 * Pure relay: forwards the Pi's steering/throttle/cluster-servo decisions
 * to the LEGO SPIKE Prime Hub over UART. Deliberately has no logic of its
 * own beyond framing/validation — keeps the Pi <-> Hub link simple and
 * makes the Hub-side parser trivial (see README > Software Architecture).
 *
 * Pi -> Bridge (USB/UART, Serial):
 *   S:<steer_deg>,T:<throttle_pct>,C:<cluster_servo_deg>\n
 *
 * Bridge -> Hub (UART, Serial1, matches hub main.py's stdin parser):
 *   S:<steer_deg>,T:<throttle_pct>\n
 *
 * (The cluster-servo field is consumed by the Sensor ESP32, not the Hub,
 * so it is stripped here rather than relayed.)
 */

#define HUB_RX 16   // ESP32 RX <- Hub TX
#define HUB_TX 17   // ESP32 TX -> Hub RX

HardwareSerial HubSerial(1);
String inputBuffer;

void setup() {
  Serial.begin(115200);                 // link to Raspberry Pi
  HubSerial.begin(115200, SERIAL_8N1, HUB_RX, HUB_TX);
  Serial.println("[bridge_esp32] ready");
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      relayToHub(inputBuffer);
      inputBuffer = "";
    } else {
      inputBuffer += c;
    }
  }
}

void relayToHub(const String &line) {
  int steer = extractField(line, "S:");
  int throttle = extractField(line, "T:");

  if (steer == INVALID_FIELD || throttle == INVALID_FIELD) {
    return;  // malformed packet — drop rather than send a stale/garbage command
  }

  HubSerial.print("S:");
  HubSerial.print(steer);
  HubSerial.print(",T:");
  HubSerial.println(throttle);
}

const int INVALID_FIELD = -32768;

int extractField(const String &line, const char *key) {
  int idx = line.indexOf(key);
  if (idx < 0) return INVALID_FIELD;
  int start = idx + strlen(key);
  int end = line.indexOf(',', start);
  String value = (end < 0) ? line.substring(start) : line.substring(start, end);
  if (value.length() == 0) return INVALID_FIELD;
  return value.toInt();
}
