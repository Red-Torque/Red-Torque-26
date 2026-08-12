"""
Central config for the Pi-side open challenge stack.
Same sensor hardware as the obstacle challenge (2x TF-Luna + front/rear
TF-LC02), but no camera/vision — Open Challenge has no pillars, just
walls to follow and laps to complete.
"""

# --- Serial links ---
SENSOR_ESP32_PORT = "/dev/ttyUSB0"   # Sensor ESP32 -> Pi (left/right TF-Luna, front TF-LC02)
SENSOR_ESP32_BAUD = 115200

BRIDGE_ESP32_PORT = "/dev/ttyUSB1"   # Pi -> Bridge ESP32 -> Hub
BRIDGE_ESP32_BAUD = 115200

REAR_LIDAR_PORT = "/dev/ttyACM0"     # Rear TF-LC02, direct USB to Pi
REAR_LIDAR_BAUD = 115200

# --- PID (wall following) ---
WALL_KP = 0.9
WALL_KI = 0.02
WALL_KD = 0.15
MAX_STEER = 45          # degrees, matches steering servo mechanical limit

# --- Driving ---
CRUISE_THROTTLE = 60      # Open Challenge has no obstacles, so can run faster
LOOP_PERIOD = 0.02         # 50 Hz control loop

# --- Sensor cluster servo ---
CLUSTER_SERVO_GAIN = 0.6   # fraction of steering angle the cluster servo follows
CLUSTER_SERVO_LIMIT = 40

# --- Laps ---
TARGET_LAPS = 3
