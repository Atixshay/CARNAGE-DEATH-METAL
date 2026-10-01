from typing import List, Optional

import config
from gestures import chords
from gestures.strum import StrumDetector
from input.base import ChordEvent, InputFrame


class GestureRecognizer:
    def __init__(self):
        self.strum = StrumDetector()
        self.stable_chord = "NONE"
        self._candidate = "NONE"
        self._streak = 0
        self.last_strength = 0.0

    def reset(self) -> None:
        self.strum.reset()
        self.stable_chord = "NONE"
        self._candidate = "NONE"
        self._streak = 0

    def process(self, frame: Optional[InputFrame]) -> List[ChordEvent]:
        if frame is None:
            return []

        # ---- left hand: chord, with a hold requirement -------------------
        raw = chords.classify(frame.left)
        if raw == self._candidate:
            self._streak += 1
        else:
            self._candidate = raw
            self._streak = 1
        if self._streak >= config.CHORD_HOLD_FRAMES:
            self.stable_chord = raw

        # ---- right hand: strum ------------------------------------------
        direction, strength = self.strum.update(frame.right, frame.timestamp)
        self.last_strength = strength

        if direction is None or self.stable_chord == "NONE":
            return []

        return [
            ChordEvent(
                chord=self.stable_chord,
                strum=direction,
                strength=strength,
                timestamp=frame.timestamp,
            )
        ]
