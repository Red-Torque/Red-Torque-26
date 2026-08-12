"""
Central config for the Pi-side obstacle challenge stack.
Tune these on the bench / mock track before competition runs.
"""

# --- Serial links ---
SENSOR_ESP32_PORT = "/dev/ttyUSB0"   # Sensor ESP32 -> Pi (left/right TF-Luna, front TF-LC02)
SENSOR_ESP32_BAUD = 115200

BRIDGE_ESP32_PORT = "/dev/ttyUSB1"   # Pi -> Bridge ESP32 -> Hub
BRIDGE_ESP32_BAUD = 115200

REAR_LIDAR_PORT = "/dev/ttyACM0"     # Rear TF-LC02, direct USB to Pi
REAR_LIDAR_BAUD = 115200

# --- Camera ---
CAMERA_RESOLUTION = (640, 480)

# --- PID (wall following) ---
WALL_KP = 0.9
WALL_KI = 0.02
WALL_KD = 0.15
MAX_STEER = 45          # degrees, matches steering servo mechanical limit

# --- Driving ---
CRUISE_THROTTLE = 55     # 0-100 scale sent to Hub
AVOID_THROTTLE = 40
LOOP_PERIOD = 0.02        # 50 Hz control loop

# --- Obstacle thresholds (mm) ---
PILLAR_TRIGGER_DISTANCE = 500
PARKING_TRIGGER_DISTANCE = 300

# --- Sensor cluster servo ---
CLUSTER_SERVO_GAIN = 0.6   # fraction of steering angle the cluster servo follows
CLUSTER_SERVO_LIMIT = 40
