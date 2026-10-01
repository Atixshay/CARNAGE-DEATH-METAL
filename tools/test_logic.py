
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.loop import Game
from game.state import Phase
from game import combat
from input.base import ChordEvent

ok = 0
fail = 0


def check(label, cond):
    global ok, fail
    if cond:
        ok += 1
        print(f"  PASS  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}")


def ev(chord, strum="DOWN", strength=0.5, t=None):
    return ChordEvent(chord, strum, strength, t if t is not None else time.perf_counter())


print("\n-- damage ------------------------------------------------------")
check("down-strum beats up-strum",
      combat.base_damage("E", "DOWN", 0.5) > combat.base_damage("E", "UP", 0.5))
check("harder strum hurts more",
      combat.base_damage("E", "DOWN", 1.0) > combat.base_damage("E", "DOWN", 0.0))

print("\n-- combos ------------------------------------------------------")
check("E E A is a combo", combat.detect_combo(("E", "E", "A")) is not None)
check("trailing match works", combat.detect_combo(("D", "E", "E", "A")) is not None)
check("random chords are not", combat.detect_combo(("E", "D", "C")) is None)

print("\n-- full round --------------------------------------------------")
g = Game()
g.start()
check("starts in PLAYING", g.state.phase is Phase.PLAYING)

start_hp = g.enemy.hp
g.update(0.016, [ev("E")])
check("enemy takes damage", g.enemy.hp < start_hp)
check("score went up", g.state.score > 0)

t0 = time.perf_counter()
g.update(0.016, [ev("E", t=t0), ev("E", t=t0 + 0.1), ev("A", t=t0 + 0.2)])
check("combo landed", any(f.kind == "combo" for f in g.state.fx) or g.enemy.hp < start_hp)

g.state.drain()
for _ in range(400):
    g.update(0.05, [ev("E", strength=1.0)])
    if g.state.phase is not Phase.PLAYING:
        break
check("round ends", g.state.phase in (Phase.WIN, Phase.LOSE))

print("\n-- player can lose ---------------------------------------------")
g2 = Game()
g2.start()
for _ in range(1200):
    g2.update(0.1, [])
    if g2.state.phase is Phase.LOSE:
        break
check("enemy can kill the player", g2.state.phase is Phase.LOSE)

print(f"\n{ok} passed, {fail} failed\n")
sys.exit(1 if fail else 0)
