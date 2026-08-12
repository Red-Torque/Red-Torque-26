"""
Reads the streamed sensor packet from the Sensor ESP32.

Wire protocol (newline-delimited, sent by sensor_esp32.ino):
    L:<left_mm>,R:<right_mm>,F:<front_mm>\n

Runs a background thread so the last-known reading is always available
without blocking the main control loop on serial I/O.
"""
import threading
import serial


class SensorLink:
    def __init__(self, port, baud=115200, timeout=0.05):
        self._ser = serial.Serial(port, baud, timeout=timeout)
        self._lock = threading.Lock()
        self._latest = {"left": 9999, "right": 9999, "front": 9999}
        self._running = True
        self._thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._thread.start()

    def _reader_loop(self):
        while self._running:
            try:
                line = self._ser.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                parsed = self._parse(line)
                if parsed:
                    with self._lock:
                        self._latest.update(parsed)
            except Exception:
                continue

    @staticmethod
    def _parse(line):
        try:
            parts = line.split(",")
            out = {}
            for p in parts:
                key, _, val = p.partition(":")
                if key == "L":
                    out["left"] = int(val)
                elif key == "R":
                    out["right"] = int(val)
                elif key == "F":
                    out["front"] = int(val)
            return out if out else None
        except (ValueError, IndexError):
            return None

    def read_latest(self):
        with self._lock:
            return dict(self._latest)

    def close(self):
        self._running = False
        self._thread.join(timeout=0.5)
        self._ser.close()
