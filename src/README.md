# Source Code — RT-X7

This tree matches the structure documented in the main repository README.

```
src/
├── open_challenge/
│   └── hub/                # Pybricks — standalone gyro-straight + lap counting
└── obstacle_challenge/
    ├── pi/                 # Raspberry Pi — vision, PID, state machine
    ├── sensor_esp32/        # Sensor ESP32 — TF-Luna x2, front TF-LC02, cluster servo
    ├── bridge_esp32/        # Bridge ESP32 — Pi <-> Hub UART relay
    └── hub/                 # Pybricks — motor/steering execution + lap counting
```

## Status

This is a first working scaffold, generated to match the architecture
described in the main README — wire it up, flash it, and tune the
constants (PID gains, servo mapping, HSV thresholds, pin numbers) against
your actual hardware before relying on it at competition. Treat the pin
assignments in each file as placeholders to confirm against your wiring,
not as verified fact.

## Flashing order (see also the Reproducibility section of the main README)

1. Hub: copy the relevant `hub/main.py` onto the SPIKE Prime Hub via the
   Pybricks IDE/extension.
2. Sensor ESP32: open `sensor_esp32/sensor_esp32.ino` in Arduino IDE/PlatformIO,
   set board to your ESP32 dev board, flash.
3. Bridge ESP32: same, with `bridge_esp32/bridge_esp32.ino`.
4. Pi: `pip install -r obstacle_challenge/pi/requirements.txt`, adjust the
   serial ports in `obstacle_challenge/pi/config.py`, then run
   `python3 obstacle_challenge/pi/main.py`.

## Bench-test each piece in isolation before integrating

- Sensor ESP32: watch the `L:...,R:...,F:...` stream in a serial monitor
  against known distances.
- Bridge ESP32: send a test `S:..,T:..,C:..\n` line from a serial monitor
  and confirm it reaches the Hub in the stripped `S:..,T:..\n` form.
- Hub: jog the steering servo and drive motor manually before trusting
  the UART-driven path.
- Pi vision: run `vision.py` standalone against sample red/green pillar
  images/frames and check the reported offsets before wiring it into
  the state machine.
