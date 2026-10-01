from typing import Optional, Tuple

import config
from input.base import Hand, WRIST, MIDDLE_MCP


class StrumDetector:
    def __init__(self):
        self.last_y: Optional[float] = None
        self.last_t: Optional[float] = None
        self.velocity = 0.0
        self.last_fire_t = -999.0
        self.armed = True

    def reset(self) -> None:
        self.last_y = None
        self.last_t = None
        self.velocity = 0.0
        self.last_fire_t = -999.0
        self.armed = True

    def update(self, hand: Optional[Hand], t: float) -> Tuple[Optional[str], float]:
        """Returns (direction or None, strength 0..1)."""
        if hand is None:
            self.last_y = None
            self.last_t = None
            self.velocity *= 0.5
            return None, 0.0

        # Palm centre is steadier than the wrist point alone.
        y = (hand.landmarks[WRIST][1] + hand.landmarks[MIDDLE_MCP][1]) / 2.0

        if self.last_y is None or self.last_t is None:
            self.last_y, self.last_t = y, t
            return None, 0.0

        dt = t - self.last_t
        if dt <= 0:
            return None, 0.0

        raw_v = (y - self.last_y) / dt          # +y is downward in image space
        self.last_y, self.last_t = y, t

        a = config.STRUM_SMOOTHING
        self.velocity = a * self.velocity + (1.0 - a) * raw_v

        thr = config.STRUM_VELOCITY_THRESHOLD
        cooldown_s = config.STRUM_COOLDOWN_MS / 1000.0

        if abs(self.velocity) < thr * 0.35:     # hand has slowed: re-arm
            self.armed = True

        if not self.armed or (t - self.last_fire_t) < cooldown_s:
            return None, 0.0

        if self.velocity > thr:
            self.armed = False
            self.last_fire_t = t
            return "DOWN", min(1.0, abs(self.velocity) / (thr * 3.0))

        if self.velocity < -thr:
            self.armed = False
            self.last_fire_t = t
            return "UP", min(1.0, abs(self.velocity) / (thr * 3.0))

        return None, 0.0
