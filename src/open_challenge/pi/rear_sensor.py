"""
Reads the rear TF-LC02 directly over USB (native TF-LC02 UART frame format),
used only for the late-run parking state.

TF-LC02 frame (9 bytes): 0x59 0x59 DIST_L DIST_H STRENGTH_L STRENGTH_H
MODE_L MODE_H CHECKSUM
(distance in cm per the TF-LC02 datasheet; converted to mm here for
consistency with the rest of the stack).
"""
import threading
import serial

FRAME_HEADER = b"\x59\x59"
FRAME_LEN = 9


class RearSensor:
    def __init__(self, port, baud=115200, timeout=0.05):
        self._ser = serial.Serial(port, baud, timeout=timeout)
        self._lock = threading.Lock()
        self._latest_mm = 9999
        self._running = True
        self._buf = bytearray()
        self._thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._thread.start()

    def _reader_loop(self):
        while self._running:
            try:
                chunk = self._ser.read(64)
                if not chunk:
                    continue
                self._buf.extend(chunk)
                self._drain_frames()
            except Exception:
                continue

    def _drain_frames(self):
        while True:
            idx = self._buf.find(FRAME_HEADER)
            if idx < 0 or len(self._buf) - idx < FRAME_LEN:
                if idx > 0:
                    del self._buf[:idx]
                return
            frame = self._buf[idx:idx + FRAME_LEN]
            if self._checksum_ok(frame):
                dist_cm = frame[2] | (frame[3] << 8)
                with self._lock:
                    self._latest_mm = dist_cm * 10
            del self._buf[:idx + FRAME_LEN]

    @staticmethod
    def _checksum_ok(frame):
        return (sum(frame[:8]) & 0xFF) == frame[8]

    def read_latest(self):
        with self._lock:
            return self._latest_mm

    def close(self):
        self._running = False
        self._thread.join(timeout=0.5)
        self._ser.close()
