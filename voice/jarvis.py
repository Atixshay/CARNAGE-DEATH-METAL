

import queue
import threading
import time
from dataclasses import dataclass
from typing import Optional

import config
from voice.commands import match_command


@dataclass
class VoiceCommand:
    action: str          # "start", "restart", "pause", "status", "hologram", ...
    said: str            # the raw transcript, for the on-screen caption
    args: dict = None


class Jarvis:
    def __init__(self):
        self.queue: "queue.Queue[VoiceCommand]" = queue.Queue()
        self.say_queue: "queue.Queue[str]" = queue.Queue()
        self.available = False
        self.status = "off"
        self.last_heard = ""
        self._running = True
        self._sr = None
        self._recognizer = True
        self._mic = True

    # ------------------------------------------------------------------ boot
    def start(self) -> bool:
        if not config.ENABLE_VOICE:
            self.status = "disabled in config"
            return False
        try:
            import speech_recognition as sr
            self._sr = sr
            self._recognizer = sr.Recognizer()
            self._recognizer.dynamic_energy_threshold = True
            self._recognizer.pause_threshold = 0.6
            self._mic = sr.Microphone()
            with self._mic as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.8)
        except Exception as exc:
            self.status = f"voice off ({type(exc).__name__})"
            print(f"[jarvis] disabled: {exc}")
            return False

        self.available = True
        self._running = True
        self.status = "listening"
        threading.Thread(target=self._listen_loop, daemon=True).start()
        threading.Thread(target=self._speak_loop, daemon=True).start()
        self.say("Jarvis online. Say jarvis start to begin.")
        return True

    def stop(self) -> None:
        self._running = False

    # ------------------------------------------------------------------ ears
    def _listen_loop(self) -> None:
        sr = self._sr
        while self._running:
            try:
                with self._mic as source:
                    audio = self._recognizer.listen(
                        source, timeout=4, phrase_time_limit=4
                    )
                text = self._recognizer.recognize_google(audio).lower()
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except Exception as exc:
                # network hiccup, mic unplugged, whatever. Back off, keep going.
                self.status = f"retrying ({type(exc).__name__})"
                time.sleep(1.0)
                continue

            self.last_heard = text
            self.status = "listening"

            wake = config.VOICE_WAKE_WORD
            if wake in text:
                text = text.split(wake, 1)[1].strip() or text

            action = match_command(text)
            if action:
                self.queue.put(VoiceCommand(action=action, said=text))

    # ------------------------------------------------------------------ mouth
    def _speak_loop(self) -> None:
        try:
            import pyttsx3
        except Exception:
            return
        while self._running:
            try:
                phrase = self.say_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", 178)
                voices = engine.getProperty("voices")
                if voices:
                    engine.setProperty("voice", voices[0].id)
                engine.say(phrase)
                engine.runAndWait()
                engine.stop()
            except Exception as exc:
                print(f"[jarvis] tts failed: {exc}")

    # ------------------------------------------------------------------ api
    def say(self, phrase: str) -> None:
        if self.available:
            self.say_queue.put(phrase)

    def poll(self) -> Optional[VoiceCommand]:
        try:
            return self.queue.get_nowait()
        except queue.Empty:
            return None
