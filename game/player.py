

from dataclasses import dataclass, field
from typing import List, Tuple

import config


@dataclass
class Player:
    hp: int = config.PLAYER_HP
    max_hp: int = config.PLAYER_HP
    combo_buffer: List[Tuple[str, float]] = field(default_factory=list)
    hurt_timer: float = 0.0

    def reset(self) -> None:
        self.hp = self.max_hp
        self.combo_buffer.clear()
        self.hurt_timer = 0.0

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)
        self.hurt_timer = 0.4

    def push_chord(self, chord: str, t: float) -> None:
        self.combo_buffer.append((chord, t))
        window = config.COMBO_WINDOW_MS / 1000.0
        self.combo_buffer = [(c, ts) for c, ts in self.combo_buffer if t - ts <= window]
        if len(self.combo_buffer) > 6:
            self.combo_buffer = self.combo_buffer[-6:]

    def recent_chords(self) -> Tuple[str, ...]:
        return tuple(c for c, _ in self.combo_buffer)

    def tick(self, dt: float) -> None:
        self.hurt_timer = max(0.0, self.hurt_timer - dt)

    @property
    def alive(self) -> bool:
        return self.hp > 0
