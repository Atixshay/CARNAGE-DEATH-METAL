import random
from typing import Optional, Tuple

import config


def base_damage(chord: str, strum: str, strength: float) -> int:
    dmg = config.DAMAGE.get(chord, 8)
    if strum == "UP":
        dmg *= config.UPSTRUM_MULTIPLIER
    dmg *= 1.0 + strength * config.STRENGTH_BONUS
    return max(1, int(round(dmg)))


def detect_combo(recent: Tuple[str, ...]) -> Optional[Tuple[str, int]]:
    """Does the tail of the recent-chord list match a combo? Longest first."""
    for pattern in sorted(config.COMBOS, key=len, reverse=True):
        n = len(pattern)
        if len(recent) >= n and tuple(recent[-n:]) == pattern:
            return config.COMBOS[pattern]
    return None


def impact_word() -> str:
    return random.choice(config.IMPACT_WORDS)


def resolve(event, player, enemy, state) -> None:
    """The one function that applies a strum to the world."""
    player.push_chord(event.chord, event.timestamp)

    combo = detect_combo(player.recent_chords())
    if combo:
        name, dmg = combo
        enemy.take_damage(dmg)
        state.score += dmg * 3
        player.combo_buffer.clear()
        state.emit("combo", name=name, damage=dmg, chord=event.chord)
        return

    dmg = base_damage(event.chord, event.strum, event.strength)
    enemy.take_damage(dmg)
    state.score += dmg
    state.emit(
        "hit",
        chord=event.chord,
        strum=event.strum,
        damage=dmg,
        word=impact_word(),
        strength=event.strength,
    )
