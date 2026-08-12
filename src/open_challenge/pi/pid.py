"""
Small hand-rolled PID controller.

Tuned iteratively on a taped-out mock track (see README > Navigation &
Obstacle Management): P first until reliable oscillation, then D to
damp it, then a small I term to correct steady-state wall-drift.
"""


class PID:
    def __init__(self, kp, ki, kd, output_limits=(-100, 100)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.min_out, self.max_out = output_limits
        self._integral = 0.0
        self._prev_error = 0.0
        self._prev_valid = False

    def update(self, error, dt):
        self._integral += error * dt
        # simple anti-windup: clamp the accumulated integral term
        max_i = (self.max_out - self.min_out)
        self._integral = max(-max_i, min(max_i, self._integral))

        derivative = 0.0
        if self._prev_valid and dt > 0:
            derivative = (error - self._prev_error) / dt

        output = (self.kp * error) + (self.ki * self._integral) + (self.kd * derivative)
        output = max(self.min_out, min(self.max_out, output))

        self._prev_error = error
        self._prev_valid = True
        return output

    def reset(self):
        self._integral = 0.0
        self._prev_error = 0.0
        self._prev_valid = False
