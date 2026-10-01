"""
input/vr_source.py - the VR plug point. Deliberately unimplemented.

This file is the proof of the architecture and it is worth showing at the
expo. A VR headset already reports 21+ joints per hand. To switch the game
to VR you fill in read() so it returns the same InputFrame, and change one
line in main.py. Nothing in gestures/, game/, render/ or audio/ is touched.

Reference paths if you ever build it:
  - Meta Quest: OpenXR XR_EXT_hand_tracking -> 26 joints per hand
  - Ultraleap / Leap Motion: LeapC python bindings -> 21 joints, same layout
Map their joint order onto the MediaPipe indices in input/base.py and you
are done.
"""

from typing import Optional

from input.base import InputFrame, InputSource


class VRSource(InputSource):
    name = "vr"

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "VR hand tracking is a planned extension. The interface is ready: "
            "implement read() to return an InputFrame and the rest of the game "
            "works unchanged."
        )

    def read(self) -> Optional[InputFrame]:
        raise NotImplementedError

    def release(self) -> None:
        pass
