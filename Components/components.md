# 🔧 Red Torque – WRO 2026 Component Breakdown

---

##  Core Processing System

![Raspberry Pi](https://robocraze.com/cdn/shop/files/Official_Raspberry_Pi_5_Model_B_1GB_RAM_1000x.png?v=1772000804)

* **Raspberry Pi 5**
  Handles computer vision and decision-making using Python and OpenCV.

![ESP-32](https://m.media-amazon.com/images/I/61HY2hJYbxL._SL1500_.jpg)

* **ESP32**
  Executes real-time control for motors and steering.

* **USB Serial Communication**
  Enables fast data transfer between Pi and ESP32.

---

##  Vision System

![Pi Camera](https://thepihut.com/cdn/shop/files/raspberry-pi-camera-module-3-raspberry-pi-sc0874-43251879215299_1000x.jpg?v=1727496119)

* **Pi Camera Module v3 wide**
  Used to detect red and green cubes.

* Provides input for navigation decisions.

---

##  Mechanical System (LEGO)

![LEGO Chassis]((https://makerbazar.in/cdn/shop/products/MakerbazarLEGO_EducationSPIKE_PrimeSet1.png?v=1676351298&width=700))

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

