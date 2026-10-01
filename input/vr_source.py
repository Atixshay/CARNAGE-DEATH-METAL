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
