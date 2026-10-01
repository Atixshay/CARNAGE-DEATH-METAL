from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List


class Phase(Enum):
    MENU = auto()
    PLAYING = auto()
    WIN = auto()
    LOSE = auto()


@dataclass
class FxEvent:
    """Something the renderer and the audio layer should react to.

    game/ never draws or plays anything itself it only says what happened. :)
    """
    kind: str                       # "hit", "combo", "player_hurt", "miss", "telegraph"
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GameState:
    phase: Phase = Phase.MENU
    fx: List[FxEvent] = field(default_factory=list)
    score: int = 0
    elapsed: float = 0.0

    def emit(self, kind: str, **data) -> None:
        self.fx.append(FxEvent(kind, data))

    def drain(self) -> List[FxEvent]:
        out, self.fx = self.fx, []
        return out
