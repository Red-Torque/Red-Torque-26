"""
Sends steering/throttle/cluster-servo commands from the Pi to the
Bridge ESP32, which relays them verbatim to the SPIKE Prime Hub.

Wire protocol (newline-delimited, matches bridge_esp32.ino and hub main.py):
    S:<steer_deg>,T:<throttle_pct>,C:<cluster_servo_deg>\n
"""
import serial


class BridgeLink:
    def __init__(self, port, baud=115200, timeout=0.05):
        self._ser = serial.Serial(port, baud, timeout=timeout)

    def send(self, steer: float, throttle: float, servo_cluster: float = 0):
        msg = f"S:{int(steer)},T:{int(throttle)},C:{int(servo_cluster)}\n"
        self._ser.write(msg.encode("utf-8"))

    def close(self):
        self._ser.close()
