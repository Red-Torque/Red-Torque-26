"""
High-level state machine for the obstacle challenge run.

States:
    WALL_FOLLOW   — default: PID wall-following using left/right TF-Luna.
    AVOID_PILLAR  — a red/green pillar has been detected close enough to
                    require an avoidance maneuver (pass left of red,
                    right of green, per WRO Future Engineers convention).
    PARKING       — final-lap parking maneuver, using the rear TF-LC02.
    STOPPED       — end of run / fault condition.
"""
from enum import Enum
import config


class State(Enum):
    WALL_FOLLOW = "WALL_FOLLOW"
    AVOID_PILLAR = "AVOID_PILLAR"
    PARKING = "PARKING"
    STOPPED = "STOPPED"


class StateMachine:
    def __init__(self):
        self.state = State.WALL_FOLLOW
        self._avoid_side = None  # "left" or "right" while avoiding

    def update(self, sensor_reading, rear_mm, frame_result):
        pillar = frame_result.get("pillar")
        front_mm = sensor_reading.get("front", 9999)

        if self.state == State.PARKING:
            # once committed to parking, stay there until fully stopped
            if rear_mm > config.PARKING_TRIGGER_DISTANCE * 3:
                return
            if rear_mm <= 20:
                self.state = State.STOPPED
            return

        if pillar is not None and front_mm < config.PILLAR_TRIGGER_DISTANCE:
            self.state = State.AVOID_PILLAR
            self._avoid_side = "left" if pillar == "red" else "right"
            return

        if self.state == State.AVOID_PILLAR and pillar is None:
            # cleared the obstacle — resume normal wall following
            self.state = State.WALL_FOLLOW
            self._avoid_side = None
            return

        if self.state != State.AVOID_PILLAR:
            self.state = State.WALL_FOLLOW

    def avoidance_steer(self, frame_result):
        offset = frame_result.get("offset", 0)
        # steer away from the pillar's side, proportional to how centered it is
        direction = -1 if self._avoid_side == "left" else 1
        magnitude = min(abs(offset) * 0.15 + 15, config.MAX_STEER)
        return direction * magnitude

    def parking_command(self, rear_mm):
        if rear_mm <= 20:
            return 0, 0
        # slow, straight reverse into the parking bay
        return 0, -config.AVOID_THROTTLE // 2

    def sensor_cluster_angle(self, steer):
        """
        Angle sent to the Sensor ESP32's cluster servo so the left/right/
        front sensors stay aimed correctly through a turn, rather than
        just being discounted in software while off-axis.
        """
        angle = steer * config.CLUSTER_SERVO_GAIN
        return max(-config.CLUSTER_SERVO_LIMIT, min(config.CLUSTER_SERVO_LIMIT, angle))

    def trigger_parking(self):
        self.state = State.PARKING
