"""
voice/commands.py - transcript -> action name.

Keep this a plain keyword table. Speech recognition is already the flaky
part of the pipeline; do not add a second uncertain layer on top of it.

Add a command:
  1. one row in PHRASES
  2. one branch in main.py's handle_voice()
"""

PHRASES = {
    "start":     ["start", "begin", "play", "let's go", "lets go", "rock"],
    "restart":   ["restart", "again", "retry", "reset", "new game"],
    "pause":     ["pause", "hold on", "wait", "stop"],
    "resume":    ["resume", "continue", "carry on"],
    "status":    ["status", "how am i doing", "health", "hp", "score"],
    "help":      ["help", "how do i play", "controls", "explain", "instructions"],
    "debug":     ["debug", "diagnostics", "show data"],
    "hologram":  ["hologram", "holo", "pyramid"],
    "keyboard":  ["keyboard", "manual mode", "backup mode"],
    "camera":    ["camera", "webcam", "hand mode", "gesture mode"],
    "quit":      ["quit", "exit", "shut down", "close the game"],
}


def match_command(text: str):
    """Longest phrase wins, so 'new game' beats 'game'."""
    text = (text or "").lower().strip()
    if not text:
        return None
    best_action, best_len = None, 0
    for action, phrases in PHRASES.items():
        for phrase in phrases:
            if phrase in text and len(phrase) > best_len:
                best_action, best_len = action, len(phrase)
    return best_action


# What Jarvis says back. Kept here so the personality is one file to edit.
REPLIES = {
    "start": "Amps are hot. Go.",
    "restart": "Resetting the stage.",
    "pause": "Paused.",
    "resume": "Back in.",
    "help": ("Left hand makes the chord shape. Fist for E, open palm for A, "
             "peace sign for D. Right hand strums up or down. Chain three "
             "chords for a combo."),
    "debug": "Diagnostics on screen.",
    "hologram": "Hologram window toggled.",
    "keyboard": "Switching to keyboard control.",
    "camera": "Switching to hand tracking.",
    "quit": "Shutting down. Nice set.",
}
