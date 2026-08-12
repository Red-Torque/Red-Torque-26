#!/usr/bin/env python3
"""
RT-X7 — Open Challenge — Raspberry Pi main entry point.

Same sensor stack as the obstacle challenge (left/right TF-Luna + front
TF-LC02 via the Sensor ESP32, rear TF-LC02 direct over USB), but no
vision/pillar logic — Open Challenge is pure wall-following + lap
completion, so the Pi just runs the PID loop and lets the Hub's own
color-sensor lap counter (see open_challenge/hub) decide when the run
ends.

Note: the Hub can also run the open challenge fully standalone off its
IMU (see open_challenge/hub/main.py) if you choose not to wire up the
Pi/ESP32 sensor stack for this event. This Pi-driven version is for
teams that want LiDAR-based wall following instead of (or in addition
to) IMU-only heading control.
"""
import time
import signal
import sys

from sensor_link import SensorLink
from rear_sensor import RearSensor
from pid import PID
from bridge_link import BridgeLink
import config


def main():
    print("[main] RT-X7 open challenge — starting up")

    sensors = SensorLink(port=config.SENSOR_ESP32_PORT, baud=config.SENSOR_ESP32_BAUD)
    rear = RearSensor(port=config.REAR_LIDAR_PORT, baud=config.REAR_LIDAR_BAUD)
    bridge = BridgeLink(port=config.BRIDGE_ESP32_PORT, baud=config.BRIDGE_ESP32_BAUD)

    wall_pid = PID(kp=config.WALL_KP, ki=config.WALL_KI, kd=config.WALL_KD,
                    output_limits=(-config.MAX_STEER, config.MAX_STEER))

    def shutdown(*_):
        print("\n[main] shutting down — sending neutral command")
        try:
            bridge.send(steer=0, throttle=0, servo_cluster=0)
        except Exception:
            pass
        sensors.close()
        rear.close()
        bridge.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    last_time = time.time()

    try:
        while True:
            now = time.time()
            dt = max(now - last_time, 1e-3)
            last_time = now

            reading = sensors.read_latest()   # {'left':..,'right':..,'front':..}
            _rear_mm = rear.read_latest()      # kept for parity/logging; unused in Open

            error = (reading.get("right", 0) - reading.get("left", 0))
            steer = wall_pid.update(error, dt)
            throttle = config.CRUISE_THROTTLE

            cluster_angle = steer * config.CLUSTER_SERVO_GAIN
            cluster_angle = max(-config.CLUSTER_SERVO_LIMIT,
                                 min(config.CLUSTER_SERVO_LIMIT, cluster_angle))

            bridge.send(steer=steer, throttle=throttle, servo_cluster=cluster_angle)

            time.sleep(config.LOOP_PERIOD)

    except Exception as exc:
        print(f"[main] fatal error: {exc}")
        shutdown()


if __name__ == "__main__":
    main()
