# 🔧 Red Torque – WRO 2026 Component Breakdown

---

##  Core Processing System

![Raspberry Pi](https://upload.wikimedia.org/wikipedia/commons/5/51/Raspberry_Pi_5.jpg)

* **Raspberry Pi 5**
  Handles computer vision and decision-making using Python and OpenCV.

* **ESP32**
  Executes real-time control for motors and steering.

* **USB Serial Communication**
  Enables fast data transfer between Pi and ESP32.

---

##  Vision System

![Pi Camera](https://upload.wikimedia.org/wikipedia/commons/3/3b/Raspberry_Pi_Camera_Module_V2.jpg)

* **Pi Camera Module v2**
  Used to detect red and green cubes.

* Provides input for navigation decisions.

---

##  Mechanical System (LEGO)

![LEGO Chassis](https://upload.wikimedia.org/wikipedia/commons/6/6d/Lego_Technic.jpg)

* Built using **LEGO Technic**
* Modular, lightweight, and precise
* Implements **Ackermann steering geometry**

---

##  Drive System

![Motor](https://upload.wikimedia.org/wikipedia/commons/3/3a/DC_Motor.jpg)

* **DC Motors** → Movement
* **Motor Driver** → Speed & direction control
* **Servo Motor** → Steering control

---

##  Power System

![Battery](https://upload.wikimedia.org/wikipedia/commons/3/3c/18650_Li-ion_cell.jpg)

* Li-ion Battery Pack
* BMS for safety
* Buck converter for voltage regulation

---

## 📡 Sensor System

![IMU](https://upload.wikimedia.org/wikipedia/commons/5/5e/MPU-6050.jpg)

* **IMU (MPU6050)** → Orientation tracking
* **Ultrasonic Sensors** → Distance measurement
* **Camera** → Primary perception sensor

---

##  Software System

* Python (Raspberry Pi)
* OpenCV (vision processing)
* Serial communication protocol
* ESP32 firmware (motor control)

---

##  System Architecture

```
Pi Camera → Raspberry Pi 5 → Vision + Decision
                      ↓
                 USB Serial
                      ↓
                   ESP32
                      ↓
            Motor + Steering Control
```

---

##  Team: Red Torque

WRO Future Engineers 2026

