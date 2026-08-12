"""
RT-X7 — Open Challenge — SPIKE Prime Hub (Pybricks)

Open Challenge has no pillars, so no camera/vision is needed — but this
file only covers the *standalone* way to run it: the Hub drives the
whole run by itself using its built-in IMU for straight-line heading
correction and the color sensor for lap counting.

If you'd rather use the LiDAR sensor stack (2x TF-Luna + front/rear
TF-LC02) for wall-following instead of pure IMU heading-hold, see
../pi, ../sensor_esp32 and ../bridge_esp32 — this same Hub file still
receives S:/T: over UART from the Bridge ESP32 either way, it just
isn't required to if running standalone.

Behavior:
  - Drive straight, using the IMU heading to correct steering drift.
  - Track laps via boundary-line color transitions.
  - Stop automatically after the required number of laps.
"""
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Direction, Color
from pybricks.tools import wait, StopWatch

hub = PrimeHub()

steering_servo = Motor(Port.A)
drive_motor = Motor(Port.B, Direction.COUNTERCLOCKWISE)
line_color_sensor = ColorSensor(Port.C)

STEER_LIMIT_DEG = 45
STEER_MOTOR_DEG_PER_STEER_DEG = 2.2

CRUISE_SPEED = 700          # deg/s propulsion speed during straight run
HEADING_KP = 2.5            # steering correction per degree of heading error

TARGET_LAPS = 3
LAP_TRIGGER_COLORS = (Color.BLUE, Color.ORANGE)
LINE_DEBOUNCE_MS = 300

lap_count = 0
_last_line_color = None
_line_debounce = StopWatch()


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def apply_steering(steer_deg):
    steer_deg = clamp(steer_deg, -STEER_LIMIT_DEG, STEER_LIMIT_DEG)
    steering_servo.track_target(steer_deg * STEER_MOTOR_DEG_PER_STEER_DEG)


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


def stop_all():
    drive_motor.stop()
    apply_steering(0)


def main():
    hub.light.on(Color.WHITE)
    steering_servo.reset_angle(0)
    hub.imu.reset_heading(0)
    print("[hub] RT-X7 open challenge ready")

    drive_motor.run(CRUISE_SPEED)

    while lap_count < TARGET_LAPS:
        heading_error = hub.imu.heading()
        steer = -HEADING_KP * heading_error
        apply_steering(steer)

        update_lap_count()
        wait(10)

    stop_all()
    hub.light.on(Color.RED)
    print("[hub] run complete — laps:", lap_count)


if __name__ == "__main__":
    main()
