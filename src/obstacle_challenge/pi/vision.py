"""
Pillar (obstacle) color detection using the Pi Camera Module 3 Wide.

Detects red vs green pillars via HSV thresholding, returns the pillar
color and its horizontal offset from frame-center (used by the state
machine to decide which side to pass on).

NOTE: HSV thresholds below are a reasonable starting point tuned under
indoor workshop lighting. Re-check and adjust under venue lighting
before competition runs (see Systems Thinking > Testing notes), and
lock exposure/white balance so thresholds don't drift mid-run.
"""
import cv2
import numpy as np

try:
    from picamera2 import Picamera2
    _HAS_PICAMERA2 = True
except ImportError:
    _HAS_PICAMERA2 = False

# HSV ranges — retune under venue lighting.
RED_LOWER_1 = np.array([0, 120, 70])
RED_UPPER_1 = np.array([10, 255, 255])
RED_LOWER_2 = np.array([170, 120, 70])
RED_UPPER_2 = np.array([180, 255, 255])
GREEN_LOWER = np.array([40, 70, 70])
GREEN_UPPER = np.array([85, 255, 255])

MIN_CONTOUR_AREA = 400


class PillarVision:
    def __init__(self, resolution=(640, 480)):
        self.resolution = resolution
        self._picam = None
        if _HAS_PICAMERA2:
            self._picam = Picamera2()
            cfg = self._picam.create_preview_configuration(
                main={"size": resolution, "format": "RGB888"}
            )
            self._picam.configure(cfg)
            # Lock exposure/white balance once tuned, to avoid drift mid-run.
            self._picam.set_controls({"AeEnable": False, "AwbEnable": False})
            self._picam.start()

    def _grab_frame(self):
        if self._picam is not None:
            return self._picam.capture_array()
        return None

    def process_latest(self):
        frame = self._grab_frame()
        if frame is None:
            return {"pillar": None, "offset": 0}

        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

        red_mask = cv2.inRange(hsv, RED_LOWER_1, RED_UPPER_1) | \
            cv2.inRange(hsv, RED_LOWER_2, RED_UPPER_2)
        green_mask = cv2.inRange(hsv, GREEN_LOWER, GREEN_UPPER)

        red_result = self._largest_blob(red_mask)
        green_result = self._largest_blob(green_mask)

        frame_center_x = frame.shape[1] / 2

        if red_result and (not green_result or red_result[0] > green_result[0]):
            cx, area = red_result
            return {"pillar": "red", "offset": cx - frame_center_x, "area": area}
        elif green_result:
            cx, area = green_result
            return {"pillar": "green", "offset": cx - frame_center_x, "area": area}

        return {"pillar": None, "offset": 0}

    @staticmethod
    def _largest_blob(mask):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        if area < MIN_CONTOUR_AREA:
            return None
        M = cv2.moments(largest)
        if M["m00"] == 0:
            return None
        cx = M["m10"] / M["m00"]
        return (cx, area)

    def close(self):
        if self._picam is not None:
            self._picam.stop()
