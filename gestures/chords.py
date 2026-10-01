"""
gestures/chords.py - left hand pose -> chord name.

Deliberately simple: work out which fingers are extended, then look the
pattern up in a table. No machine learning, no training data, no surprises
on expo day. Add a chord by adding one row to PATTERNS.
"""

import math
from typing import Optional

import config
from input.base import (
    Hand, WRIST,
    THUMB_TIP, THUMB_IP, THUMB_MCP,
    INDEX_TIP, INDEX_PIP,
    MIDDLE_TIP, MIDDLE_PIP,
    RING_TIP, RING_PIP,
    PINKY_TIP, PINKY_PIP,
)

# (thumb, index, middle, ring, pinky) -> gesture name
PATTERNS = {
    (False, False, False, False, False): "FIST",
    (True,  True,  True,  True,  True):  "OPEN",
    (False, True,  True,  True,  True):  "OPEN",   # thumb tucked, still open
    (False, True,  True,  False, False): "PEACE",
    (True,  True,  True,  False, False): "PEACE",
    (False, True,  False, False, True):  "HORNS",
    (True,  True,  False, False, True):  "HORNS",
    (True,  False, False, False, False): "THUMB",
}


def _dist(a, b) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def finger_states(hand: Hand):
    """Return (thumb, index, middle, ring, pinky) booleans: extended?

    Works in normalised image space. For the four fingers we compare the tip
    against the middle joint relative to the wrist - that stays correct even
    when the hand is tilted. The thumb is checked sideways instead.
    """
    lm = hand.landmarks
    wrist = lm[WRIST]
    m = config.FINGER_EXT_MARGIN

    def extended(tip_i, pip_i) -> bool:
        return _dist(lm[tip_i], wrist) > _dist(lm[pip_i], wrist) + m

    index = extended(INDEX_TIP, INDEX_PIP)
    middle = extended(MIDDLE_TIP, MIDDLE_PIP)
    ring = extended(RING_TIP, RING_PIP)
    pinky = extended(PINKY_TIP, PINKY_PIP)

    # Thumb: extended when the tip is further from the hand's centre line
    # than its own lower joint.
    thumb = _dist(lm[THUMB_TIP], lm[PINKY_PIP]) > _dist(lm[THUMB_IP], lm[PINKY_PIP]) + m

    return (thumb, index, middle, ring, pinky)


def classify(hand: Optional[Hand]) -> str:
    """Left hand -> chord name from config.CHORD_MAP, or 'NONE'."""
    if hand is None:
        return "NONE"
    pattern = finger_states(hand)
    gesture = PATTERNS.get(pattern)
    if gesture is None:
        # Nearest match: tolerate one wrong finger so a slightly sloppy
        # shape still plays. This is what makes it feel good to strangers.
        best, best_score = None, 99
        for pat, name in PATTERNS.items():
            score = sum(1 for a, b in zip(pat, pattern) if a != b)
            if score < best_score:
                best, best_score = name, score
        gesture = best if best_score <= 1 else None
    if gesture is None:
        return "NONE"
    return config.CHORD_MAP.get(gesture, "NONE")


def describe(hand: Optional[Hand]) -> str:
    """Debug string for the overlay, e.g. 'T- I+ M+ R- P-'."""
    if hand is None:
        return "no left hand"
    names = "TIMRP"
    return " ".join(
        f"{n}{'+' if s else '-'}" for n, s in zip(names, finger_states(hand))
    )
