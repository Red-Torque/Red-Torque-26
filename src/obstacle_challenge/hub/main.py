"""
RT-X7 — Obstacle Challenge — SPIKE Prime Hub (Pybricks)

Execution layer: receives steering/throttle over UART from the Bridge
ESP32 and drives the propulsion motor(s) and steering servo accordingly.
Independently tracks laps using the built-in IMU (heading) and the LEGO
color sensor on the blue/orange boundary lines, so lap counting does not
depend on the Pi's vision pipeline.

Incoming packet (from Bridge ESP32, matches bridge_esp32.ino):
    S:<steer_deg>,T:<throttle_pct>\n
"""
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Direction, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase

# --- Devices ---
hub = PrimeHub()

steering_servo = Motor(Port.A)
drive_motor = Motor(Port.B, Direction.COUNTERCLOCKWISE)
line_color_sensor = ColorSensor(Port.C)

STEER_LIMIT_DEG = 45
STEER_MOTOR_DEG_PER_STEER_DEG = 2.2   # calibrate against the linkage geometry

MAX_MOTOR_SPEED = 1000    # deg/s, propulsion motor speed at throttle=100

# Lap detection: count boundary-line color transitions rather than a
# single color, since the run alternates blue/orange edges.
LAP_TRIGGER_COLORS = (Color.BLUE, Color.ORANGE)
lap_count = 0
_last_line_color = None
_line_debounce = StopWatch()
LINE_DEBOUNCE_MS = 300

buffer = ""


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def apply_steering(steer_deg):
    steer_deg = clamp(steer_deg, -STEER_LIMIT_DEG, STEER_LIMIT_DEG)
    target_motor_deg = steer_deg * STEER_MOTOR_DEG_PER_STEER_DEG
    steering_servo.track_target(target_motor_deg)


def apply_throttle(throttle_pct):
    throttle_pct = clamp(throttle_pct, -100, 100)
    speed = (throttle_pct / 100) * MAX_MOTOR_SPEED
    drive_motor.run(speed)


def update_lap_count():
    global lap_count, _last_line_color
    detected = line_color_sensor.color()
    if detected in LAP_TRIGGER_COLORS and detected != _last_line_color:
        if _line_debounce.time() > LINE_DEBOUNCE_MS:
            lap_count += 1
            _line_debounce.reset()
            hub.light.blink(Color.GREEN, [50, 50])
    if detected in LAP_TRIGGER_COLORS:
        _last_line_color = detected
    elif detected == Color.NONE:
        _last_line_color = None


def parse_and_apply(line):
    steer = None
    throttle = None
    for field in line.split(","):
        if field.startswith("S:"):
            try:
                steer = int(field[2:])
            except ValueError:
                pass
        elif field.startswith("T:"):
            try:
                throttle = int(field[2:])
            except ValueError:
                pass

    if steer is not None:
        apply_steering(steer)
    if throttle is not None:
        apply_throttle(throttle)


def main():
    global buffer
    hub.light.on(Color.WHITE)
    steering_servo.reset_angle(0)
    print("[hub] RT-X7 obstacle challenge ready")

    while True:
        # Non-blocking-ish read: Pybricks stdin is line buffered over the
        # REPL/UART link from the Bridge ESP32.
        try:
            chunk = stdin_read_available()
        except NameError:
            chunk = ""

        if chunk:
            buffer += chunk
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if line:
                    parse_and_apply(line)

        update_lap_count()
        wait(10)


def stdin_read_available():
    """
    Placeholder hook for the Hub's UART read.
    On real Pybricks firmware this reads from the wired UART port the
    Bridge ESP32 is connected to; swap in the appropriate Pybricks I/O
    call for the exact hub SDK build/firmware in use.
    """
    return ""


if __name__ == "__main__":
    main()
