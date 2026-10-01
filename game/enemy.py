

from dataclasses import dataclass

import config


@dataclass
class Enemy:
    hp: int = config.ENEMY_HP
    max_hp: int = config.ENEMY_HP
    timer: float = 0.0
    telegraphing: bool = False
    hurt_timer: float = 0.0
    name: str = "CARNAGE"

    def reset(self) -> None:
        self.hp = self.max_hp
        self.timer = 0.0
        self.telegraphing = False
        self.hurt_timer = 0.0

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)
        self.hurt_timer = 0.25

    def tick(self, dt: float, state) -> int:
        """Advance the attack cycle. Returns damage dealt to the player (0 or more)."""
        self.hurt_timer = max(0.0, self.hurt_timer - dt)
        self.timer += dt

        wind_up_at = config.ENEMY_ATTACK_INTERVAL_S - config.ENEMY_TELEGRAPH_S

        if not self.telegraphing and self.timer >= wind_up_at:
            self.telegraphing = True
            state.emit("telegraph")

        if self.timer >= config.ENEMY_ATTACK_INTERVAL_S:
            self.timer = 0.0
            self.telegraphing = False
            return config.ENEMY_DAMAGE

        return 0

    @property
    def alive(self) -> bool:
        return self.hp > 0

    @property
    def hp_ratio(self) -> float:
        return self.hp / self.max_hp if self.max_hp else 0.0
