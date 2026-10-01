"""
input/webcam_source.py - MediaPipe Hands implementation of InputSource.

Runs capture + inference on a background thread so the game loop never
stalls waiting for the camera. The loop always gets the newest frame.
"""

import threading
import time
from typing import Optional

import config
from input.base import Hand, InputFrame, InputSource


class WebcamSource(InputSource):
    name = "webcam"

    def __init__(self):
        import cv2
        import mediapipe as mp

        self.cv2 = cv2
        self.cap = cv2.VideoCapture(config.CAM_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAM_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAM_HEIGHT)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not self.cap.isOpened():
            raise RuntimeError(
                "Could not open the webcam. Close Zoom/Teams/other camera apps, "
                "or change CAM_INDEX in config.py (try 1 or 2)."
            )

        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=config.MODEL_COMPLEXITY,
            min_detection_confidence=config.MIN_DETECTION_CONF,
            min_tracking_confidence=config.MIN_TRACKING_CONF,
        )

        self._latest: Optional[InputFrame] = None
        self._lock = threading.Lock()
        self._running = True
        self.fps = 0.0
        self._t = threading.Thread(target=self._worker, daemon=True)
        self._t.start()

    # ------------------------------------------------------------------ thread
    def _worker(self):
        cv2 = self.cv2
        last = time.perf_counter()
        while self._running:
            ok, bgr = self.cap.read()
            if not ok:
                time.sleep(0.01)
                continue

            if config.MIRROR_CAMERA:
                bgr = cv2.flip(bgr, 1)

            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False
            result = self.hands.process(rgb)

            left = right = None
            if result.multi_hand_landmarks:
                pairs = zip(result.multi_hand_landmarks, result.multi_handedness)
                for lm, handed in pairs:
                    label = handed.classification[0].label   # "Left" / "Right"
                    score = handed.classification[0].score
                    # MediaPipe labels assume a NON-mirrored image. We flipped
                    # the frame for the selfie view, so flip the label back.
                    if config.MIRROR_CAMERA:
                        label = "Right" if label == "Left" else "Left"
                    pts = [(p.x, p.y, p.z) for p in lm.landmark]
                    hand = Hand(landmarks=pts, handedness=label, confidence=score)
                    if label == "Left":
                        left = hand
                    else:
                        right = hand

            frame = InputFrame(
                timestamp=time.perf_counter(),
                left=left,
                right=right,
                raw_image=bgr,
            )
            with self._lock:
                self._latest = frame

            now = time.perf_counter()
            dt = now - last
            last = now
            if dt > 0:
                self.fps = 0.9 * self.fps + 0.1 * (1.0 / dt)

    # ------------------------------------------------------------------ api
    def read(self) -> Optional[InputFrame]:
        with self._lock:
            return self._latest

    def release(self) -> None:
        self._running = False
        time.sleep(0.05)
        try:
            self.cap.release()
            self.hands.close()
        except Exception:
            pass
