"""
input/keyboard_source.py - THE SAFETY NET.

Two jobs:
  1. Person B builds and tests the whole game with no camera at all.
  2. At the expo, if the lighting kills tracking, press F2 and keep demoing.

Keys:  1..5 pick the chord,  DOWN arrow = down-strum,  UP arrow = up-strum.
"""

import time
from typing import List, Optional

import config
from input.base import ChordEvent, InputFrame, InputSource


class KeyboardSource(InputSource):
    name = "keyboard"

    def __init__(self):
        import pygame
        self.pygame = pygame
        self.chords = list(config.CHORD_MAP.values())   # ["E","A","D","G","C"]
        self.current = self.chords[0]
        self._queue: List[ChordEvent] = []

    def handle_key(self, key) -> None:
        pg = self.pygame
        number_keys = [pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5]
        if key in number_keys:
            idx = number_keys.index(key)
            if idx < len(self.chords):
                self.current = self.chords[idx]
        elif key == pg.K_DOWN:
            self._emit("DOWN")
        elif key == pg.K_UP:
            self._emit("UP")

    def _emit(self, direction: str) -> None:
        self._queue.append(
            ChordEvent(
                chord=self.current,
                strum=direction,
                strength=0.75,
                timestamp=time.perf_counter(),
            )
        )

    def read(self) -> Optional[InputFrame]:
        # No hands to report; the recogniser is bypassed for this source.
        return InputFrame(timestamp=time.perf_counter())

    def poll_events(self) -> List[ChordEvent]:
        out, self._queue = self._queue, []
        return out

    def release(self) -> None:
        pass
