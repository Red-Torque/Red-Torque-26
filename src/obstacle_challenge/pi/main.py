#!/usr/bin/env python3
"""
RT-X7 — Obstacle Challenge — Raspberry Pi main entry point.

Responsibilities on the Pi:
  - Read left/right TF-Luna + front TF-LC02 distances streamed from the Sensor ESP32 (UART/USB).
  - Read the rear TF-LC02 directly (separate USB serial port).
  - Run vision (Pi Camera Module 3 Wide) for red/green pillar (obstacle) detection.
  - Run the PID wall-following / obstacle-avoidance logic.
  - Run the overall state machine (driving / avoiding / parking).
  - Send steering + throttle commands to the Bridge ESP32 over UART, which
    relays them to the SPIKE Prime Hub.

This file wires the smaller modules together; each module can also be
bench-tested in isolation (see Reproducibility section of the README).
"""
import time
import signal
import sys

from sensor_link import SensorLink
from rear_sensor import RearSensor
from vision import PillarVision
from pid import PID
from state_machine import StateMachine, State
from bridge_link import BridgeLink
import config


def main():
    print("[main] RT-X7 obstacle challenge — starting up")

    sensors = SensorLink(port=config.SENSOR_ESP32_PORT, baud=config.SENSOR_ESP32_BAUD)
    rear = RearSensor(port=config.REAR_LIDAR_PORT, baud=config.REAR_LIDAR_BAUD)
    vision = PillarVision(resolution=config.CAMERA_RESOLUTION)
    bridge = BridgeLink(port=config.BRIDGE_ESP32_PORT, baud=config.BRIDGE_ESP32_BAUD)

    wall_pid = PID(kp=config.WALL_KP, ki=config.WALL_KI, kd=config.WALL_KD,
                    output_limits=(-config.MAX_STEER, config.MAX_STEER))

    sm = StateMachine()

    def shutdown(*_):
        print("\n[main] shutting down — sending neutral command")
        try:
            bridge.send(steer=0, throttle=0, servo_cluster=0)
        except Exception:
            pass
        sensors.close()
        rear.close()
        bridge.close()
        vision.close()
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
            rear_mm = rear.read_latest()
            frame_result = vision.process_latest()  # {'pillar': 'red'/'green'/None, 'offset': px}

            sm.update(reading, rear_mm, frame_result)

            if sm.state == State.WALL_FOLLOW:
                error = (reading.get("right", 0) - reading.get("left", 0))
                steer = wall_pid.update(error, dt)
                throttle = config.CRUISE_THROTTLE

            elif sm.state == State.AVOID_PILLAR:
                steer = sm.avoidance_steer(frame_result)
                throttle = config.AVOID_THROTTLE

            elif sm.state == State.PARKING:
                steer, throttle = sm.parking_command(rear_mm)

            elif sm.state == State.STOPPED:
                steer, throttle = 0, 0

            else:
                steer, throttle = 0, 0

            cluster_angle = sm.sensor_cluster_angle(steer)

            bridge.send(steer=steer, throttle=throttle, servo_cluster=cluster_angle)

            time.sleep(config.LOOP_PERIOD)

    except Exception as exc:
        print(f"[main] fatal error: {exc}")
        shutdown()


if __name__ == "__main__":
    main()
