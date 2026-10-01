"""
game/loop.py - the pure game tick.

Takes dt and a list of ChordEvents. Draws nothing, plays nothing, knows
nothing about cameras. This is what makes the VR swap a one-line change,
and what lets you unit-test the whole game with fake events.
"""

from typing import List

import config
from game import combat
from game.enemy import Enemy
from game.player import Player
from game.state import GameState, Phase


class Game:
    def __init__(self):
        self.state = GameState()
        self.player = Player()
        self.enemy = Enemy()

    # ------------------------------------------------------------------ api
    def start(self) -> None:
        self.player.reset()
        self.enemy.reset()
        self.state.phase = Phase.PLAYING
        self.state.score = 0
        self.state.elapsed = 0.0

    def update(self, dt: float, events: List) -> None:
        if self.state.phase is not Phase.PLAYING:
            return

        self.state.elapsed += dt
        self.player.tick(dt)

        for ev in events:
            combat.resolve(ev, self.player, self.enemy, self.state)

        incoming = self.enemy.tick(dt, self.state)
        if incoming:
            self.player.take_damage(incoming)
            self.state.emit("player_hurt", damage=incoming)

        if not self.enemy.alive:
            # time bonus: finishing fast is worth points
            self.state.score += max(0, int(2000 - self.state.elapsed * 30))
            self.state.phase = Phase.WIN
            self.state.emit("win")
        elif not self.player.alive:
            self.state.phase = Phase.LOSE
            self.state.emit("lose")
