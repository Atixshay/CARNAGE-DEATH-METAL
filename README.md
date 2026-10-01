# CARNAGE: DEATH METAL

Gesture-controlled guitar combat. Your webcam watches your hands: the **left hand**
makes a chord shape, the **right hand** strums. Chord + strum = a guitar sound and
an attack on the enemy. Comic-book presentation, combo system, optional Jarvis
voice assistant, optional hologram output.


---

## Run it

```
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

pip install -r requirements.txt
python main.py
```

No camera, or the camera is misbehaving:

```
python main.py --keyboard      # 1-5 pick the chord, UP/DOWN arrows strum
python main.py --no-voice      # skip the microphone entirely
```

No audio files are needed. Chords are synthesised at startup with Karplus-Strong,
so the game makes guitar noises out of the box. Drop `assets/sounds/E.wav` (and
`A`, `D`, `G`, `C`) in to replace them with real samples — the code picks them up
automatically.

Check the game logic without a window, camera or speakers:

```
python tools/test_logic.py
```

---

## Controls

| Left hand | Chord |
| --- | --- |
| Fist | E |
| Open palm | A |
| Peace sign | D |
| Rock horns | G |
| Thumbs up | C |

**Right hand:** swing down = down-strum (full damage), swing up = up-strum (80%).
Strum harder for more damage.

**Combos** (three chords within 2.5 s): `E E A` Power Slide · `D D G` Sonic Boom ·
`A D E` Thunder Riff · `C G C` Harmony Blast.

| Key | Does |
| --- | --- |
| SPACE | Start |
| R | Restart |
| F1 | Debug overlay: landmarks, finger states, live strum velocity |
| F2 | Swap between webcam and keyboard input |
| H | Toggle the hologram window |
| `[` `]` | Lower / raise the strum threshold **while playing** |
| ESC | Quit |

`[` and `]` are the expo-day lifesaver. If the hall's lighting makes strums fire
too easily or not at all, tune it live with F1 open and watch the velocity number.

---

## Voice assistant (Jarvis)

Say **"jarvis start"**, **"jarvis status"**, **"jarvis help"**, **"jarvis restart"**,
**"jarvis keyboard"**, **"jarvis hologram"**, **"jarvis quit"**.

Adapted from the stack used by
[kishanrajput23/Jarvis-Desktop-Voice-Assistant](https://github.com/kishanrajput23/Jarvis-Desktop-Voice-Assistant)
(SpeechRecognition + PyAudio + pyttsx3), restructured for a game: that project is a
blocking listen→act→listen loop, which would freeze a 60 FPS game. Here, listening
and speaking each run on their own daemon thread and hand `VoiceCommand` objects to
the game through a queue, drained once per frame.

If `speech_recognition`, `pyaudio` or `pyttsx3` is missing or the mic fails, voice
turns itself off and the game runs normally. Add a command in two places:
`voice/commands.py` (the phrase) and `main.py` `handle_voice()` (the effect).

Note: `recognize_google` needs internet. 

---

## Architecture

The whole design rests on one rule: **the game never knows where input came from.**

```
Camera ─► HandTracker ─► InputFrame ─► GestureRecognizer ─► ChordEvent ─► Game ─► Render
VR (later) ────────────────┘                                    │              └─► Audio
Keyboard ───────────────────────────────────────────────────────┘
```

Everything left of `ChordEvent` is replaceable. Everything right of it never changes.
`input/vr_source.py` is a stub with the same two methods — filling it in is the
entire VR port.

```
main.py              entry point: build, loop, nothing else
config.py            EVERY tunable number
input/base.py        THE CONTRACT: Hand, InputFrame, ChordEvent, InputSource
input/webcam_source.py   MediaPipe on a background thread
input/keyboard_source.py the safety net + how Person B works without a camera
input/vr_source.py       the plug point
gestures/chords.py       finger states -> chord, with 1-finger tolerance
gestures/strum.py        smoothed wrist velocity -> DOWN/UP, cooldown + re-arm
gestures/recognizer.py   combines both, owns the stability buffer
game/                    pure logic. Imports nothing from input/ or render/
render/                  comic FX, HUD, scene, hologram
audio/sounds.py          synthesised or sampled chords
voice/                   Jarvis
tools/test_logic.py      headless tests
```

Three rules that keep it honest:

1. `game/` never imports from `input/` or `render/`. If you need `import mediapipe`
   inside `game/`, the design has broken.
2. Every tunable number lives in `config.py`.
3. `main.py` stays short: pick a source, build the game, run the loop.

---

## Hologram (optional)

Press H. A second window renders the scene four times, each rotated 90°, on black.
Cut four trapezoids of clear acrylic (base 60 mm, top 10 mm, height 36 mm for a
phone; scale up for a tablet), tape them into a truncated pyramid, stand it on the
screen, kill the room lights.

---

## If something breaks

| Symptom | Fix |
| --- | --- |
| "Could not open the webcam" | Close Zoom/Teams/Meet. Or set `CAM_INDEX = 1` in `config.py` |
| Hands not detected | Light your hands from the front. This is 90% of all tracking problems |
| Strums fire constantly | Raise the threshold with `]`, or raise `STRUM_SMOOTHING` |
| Strums never fire | Lower it with `[`. Watch the velocity number with F1 |
| Chords flicker between two | Raise `CHORD_HOLD_FRAMES` to 5 |
| Under 15 FPS | `CAM_WIDTH, CAM_HEIGHT = 480, 360` and `MODEL_COMPLEXITY = 0` |
| MediaPipe won't install | You are on Python 3.12+. Use 3.11 |
| Everything is on fire mid-demo | F2. Keyboard mode. Keep talking |
