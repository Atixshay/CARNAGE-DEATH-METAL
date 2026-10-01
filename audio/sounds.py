"""
audio/sounds.py - chord playback.

Two paths:
  * assets/sounds/<CHORD>.wav exists  -> use your real guitar sample
  * it does not                       -> synthesise a plucked chord with
                                         Karplus-Strong so the game makes
                                         noise on day one with no downloads

Every sample is built or loaded once at startup. Never touch the disk in
the game loop.
"""

import os
from typing import Dict

import numpy as np
import pygame

import config

SAMPLE_RATE = 44100
ASSET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sounds")


def _karplus_strong(freq: float, seconds: float, decay: float = 0.996) -> np.ndarray:
   
    n = int(SAMPLE_RATE * seconds)
    period = max(2, int(SAMPLE_RATE / freq))

    rng = np.random.default_rng(int(freq * 100))
    buf = rng.uniform(-1.0, 1.0, period)

    out = np.empty(n, dtype=np.float32)

    for i in range(n):
        out[i] = buf[i % period]

        nxt = (i + 1) % period
        buf[nxt] = decay * 0.5 * (
            buf[i % period] + buf[nxt]
        )

    return out

def _render_chord(freqs, seconds=1.8) -> np.ndarray:
    
    n = int(SAMPLE_RATE * seconds)
    mix = np.zeros(n, dtype=np.float32)

    # Build each string separately
    for i, f in enumerate(freqs):
        tone = _karplus_strong(
            f,
            seconds,
            decay=0.998
        )

        # Slightly different attack time for each string
        offset = int(SAMPLE_RATE * 0.008 * i)

        if offset < n:
            mix[offset:] += tone[:n - offset] * (0.75 ** i)

    # Normalize before distortion
    peak = np.max(np.abs(mix)) or 1.0
    mix /= peak

    # ---------------------------------------------------------
    # AMP DISTORTION
    # Soft clipping creates guitar-like harmonics.
    # ---------------------------------------------------------
    drive = 3.2
    mix = np.tanh(mix * drive)

    # ---------------------------------------------------------
    # ADD HARMONICS
    # Gives the chord more "electric guitar" character.
    # ---------------------------------------------------------
    harmonic2 = np.tanh(mix * 2.0) * 0.18
    harmonic3 = np.tanh(mix * 3.0) * 0.08

    mix = mix + harmonic2 + harmonic3

    # ---------------------------------------------------------
    # GUITAR ATTACK
    # Sharp initial hit, followed by sustain.
    # ---------------------------------------------------------
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE

    attack = 1.0 - np.exp(-t * 90.0)
    decay = np.exp(-t * 0.75)

    env = attack * decay
    mix *= env

    # ---------------------------------------------------------
    # CABINET-STYLE HIGH FREQUENCY ROLL-OFF
    # Simple smoothing filter.
    # ---------------------------------------------------------
    smooth = np.empty_like(mix)
    smooth[0] = mix[0]

    for i in range(1, n):
        smooth[i] = smooth[i - 1] * 0.15 + mix[i] * 0.85

    mix = smooth

    # Final normalization
    peak = np.max(np.abs(mix)) or 1.0

    return (mix / peak * 0.9).astype(np.float32)



def _blip(freq: float, seconds: float, kind: str = "sine") -> np.ndarray:
    t = np.linspace(0, seconds, int(SAMPLE_RATE * seconds), endpoint=False)
    if kind == "noise":
        wave = np.random.default_rng(7).uniform(-1, 1, t.shape)
    elif kind == "saw":
        wave = 2.0 * ((t * freq) % 1.0) - 1.0
    else:
        wave = np.sin(2 * np.pi * freq * t)
    env = np.exp(-6.0 * t / seconds)
    return (wave * env * 0.7).astype(np.float32)


def _to_sound(mono: np.ndarray) -> pygame.mixer.Sound:
    data = np.clip(mono, -1.0, 1.0)
    stereo = np.repeat((data * 32767).astype(np.int16)[:, None], 2, axis=1)
    return pygame.sndarray.make_sound(np.ascontiguousarray(stereo))

def _render_drum_loop(bpm=110, bars=2) -> np.ndarray:
    """Generate a simple low-volume rock drum loop."""
    beats_per_bar = 4
    total_beats = beats_per_bar * bars
    beat_time = 60.0 / bpm

    n = int(SAMPLE_RATE * total_beats * beat_time)
    mix = np.zeros(n, dtype=np.float32)

    def add_sound(sound, start_time, volume):
        start = int(start_time * SAMPLE_RATE)
        end = min(start + len(sound), n)

        if start < n:
            mix[start:end] += sound[:end - start] * volume

    # Drum sounds
    kick = _blip(75, 0.16, "sine")
    snare = _blip(180, 0.12, "noise")
    hat = _blip(7000, 0.045, "noise")

    for beat in range(total_beats):
        t = beat * beat_time

        # Kick on 1 and 3
        if beat % 4 in (0, 2):
            add_sound(kick, t, 0.65)

        # Snare on 2 and 4
        if beat % 4 in (1, 3):
            add_sound(snare, t, 0.38)

        # Eighth-note hi-hats
        add_sound(hat, t, 0.16)
        add_sound(hat, t + beat_time * 0.5, 0.11)

    # Keep the background drum quiet
    peak = np.max(np.abs(mix)) or 1.0
    return (mix / peak * 0.32).astype(np.float32)

class SoundBank:
    def __init__(self):
        self.chords: Dict[str, pygame.mixer.Sound] = {}
        self.sfx: Dict[str, pygame.mixer.Sound] = {}
        self.enabled = True

        try:
            self._build()

            # Start background drums
            self.sfx["drums"].set_volume(0.25)
            self.sfx["drums"].play(loops=-1)

        except Exception as exc:
            print(f"[audio] disabled: {exc}")
            self.enabled = False

    def _build(self) -> None:
        for chord, freqs in config.CHORD_FREQS.items():
            path = os.path.join(ASSET_DIR, f"{chord}.mp3")

            if os.path.exists(path):
                self.chords[chord] = pygame.mixer.Sound(path)
            else:
                self.chords[chord] = _to_sound(
                    _render_chord(freqs)
                )

        self.sfx["hurt"] = _to_sound(
            _blip(140, 0.25, "saw")
        )

        self.sfx["combo"] = _to_sound(
            np.concatenate([
                _blip(f, 0.12, "saw")
                for f in (440, 660, 880, 1320)
            ])
        )

        self.sfx["win"] = _to_sound(
            np.concatenate([
                _blip(f, 0.18)
                for f in (523, 659, 784, 1047)
            ])
        )

        self.sfx["lose"] = _to_sound(
            np.concatenate([
                _blip(f, 0.22, "saw")
                for f in (330, 262, 196, 147)
            ])
        )

        self.sfx["telegraph"] = _to_sound(
            _blip(90, 0.35, "noise")
        )

        self.sfx["drums"] = _to_sound(
            _render_drum_loop(110, 2)
        )

        # Pick up any .wav files in assets/sounds/
        if os.path.isdir(ASSET_DIR):
            for fn in os.listdir(ASSET_DIR):
                key = os.path.splitext(fn)[0]

                if fn.endswith(".wav") and key not in self.chords:
                    self.sfx[key] = pygame.mixer.Sound(
                        os.path.join(ASSET_DIR, fn)
                    )

    def play_chord(self, chord: str, volume: float = 1.0) -> None:
        if not self.enabled:
            return

        snd = self.chords.get(chord)

        if snd:
            snd.set_volume(max(0.25, min(1.0, volume)))
            snd.play()

    def play(self, key: str, volume: float = 1.0) -> None:
        if not self.enabled:
            return

        snd = self.sfx.get(key)

        if snd:
            snd.set_volume(volume)
            snd.play()
