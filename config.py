

# ---------------------------------------------------------------- window
WINDOW_W, WINDOW_H = 1280, 720
FPS_CAP = 60
TITLE = "CARNAGE:DEATH METAL"

# ---------------------------------------------------------------- camera
CAM_INDEX = 0
CAM_WIDTH, CAM_HEIGHT = 640, 480
MIRROR_CAMERA = True          # selfie view; almost always what you want
SHOW_CAM_PREVIEW = True       # picture-in-picture of the webcam feed
CAM_PREVIEW_SCALE = 0.42

# ---------------------------------------------------------------- mediapipe
MIN_DETECTION_CONF = 0.7
MIN_TRACKING_CONF = 0.5
MODEL_COMPLEXITY = 0          # 0 = fastest. Raise to 1 only if you have FPS to spare

# ---------------------------------------------------------------- gestures
CHORD_HOLD_FRAMES = 3         # frames a chord shape must persist before it counts
FINGER_EXT_MARGIN = 0.02      # tolerance when deciding "is this finger extended"

STRUM_VELOCITY_THRESHOLD = 0.9   # normalised screen-heights per second
STRUM_COOLDOWN_MS = 50         # one physical strum must not fire twice
STRUM_SMOOTHING = 0.55           # 0 = no smoothing, 0.9 = very smooth / laggy

# ---------------------------------------------------------------- chords
# gesture name -> chord name shown on screen
CHORD_MAP = {
    "FIST":  "E",
    "OPEN":  "A",
    "PEACE": "D",
    "HORNS": "G",
    "THUMB": "C",
}

# chord -> midi-ish note frequencies used by the built-in synth
CHORD_FREQS = {
    "E": [82.41, 123.47, 164.81, 207.65, 246.94, 329.63],
    "A": [110.00, 164.81, 220.00, 277.18, 329.63],
    "D": [146.83, 220.00, 293.66, 369.99],
    "G": [98.00, 123.47, 146.83, 196.00, 246.94, 392.00],
    "C": [130.81, 164.81, 196.00, 261.63, 329.63],
}

# ---------------------------------------------------------------- combat
PLAYER_HP = 500
ENEMY_HP = 1000

DAMAGE = {"E": 15, "A": 10, "D": 12, "G": 13, "C": 11}
UPSTRUM_MULTIPLIER = 0.8      # up-strums are lighter, down-strums are the power move
STRENGTH_BONUS = 0.6          # damage *= 1 + strength * STRENGTH_BONUS

ENEMY_ATTACK_INTERVAL_S = 2.0
ENEMY_TELEGRAPH_S = 0.5       # wind-up before the hit lands
ENEMY_DAMAGE = 10

# ---------------------------------------------------------------- combos
COMBO_WINDOW_MS = 2500
COMBOS = {
    ("E", "E", "A"): ("POWER SLIDE", 45),
    ("D", "D", "G"): ("SONIC BOOM", 50),
    ("A", "D", "E"): ("THUNDER RIFF", 60),
    ("C", "G", "C"): ("HARMONY BLAST", 40),
}

# ---------------------------------------------------------------- feel
HIT_SHAKE = 14
COMBO_SHAKE = 34
IMPACT_WORDS = ["POW!", "SLAM!", "BAM!", "C'MONN!!", "OWW!"]

# ---------------------------------------------------------------- colours
INK = (18, 16, 24)
PAPER = (247, 240, 214)
RED = (222, 52, 58)
YELLOW = (255, 201, 41)
BLUE = (58, 134, 255)
GREEN = (80, 200, 120)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- toggles
ENABLE_VOICE = True           # Jarvis assistant thread
ENABLE_HOLOGRAM = False       # second window, 4-way mirrored
VOICE_WAKE_WORD = "jarvis"
