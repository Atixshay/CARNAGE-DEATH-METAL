import sys
import time

import pygame

import config
from audio.sounds import SoundBank
from game.loop import Game
from game.state import Phase
from gestures.recognizer import GestureRecognizer
from input.keyboard_source import KeyboardSource
from render.scene import Scene
from voice.commands import REPLIES


# ---------------------------------------------------------------- helpers
def make_webcam_source():
    from input.webcam_source import WebcamSource
    return WebcamSource()


def cam_to_surface(bgr):
    """OpenCV BGR ndarray -> pygame Surface, for the picture-in-picture."""
    if bgr is None:
        return None
    import numpy as np
    rgb = bgr[:, :, ::-1]
    return pygame.surfarray.make_surface(np.transpose(rgb, (1, 0, 2)))


def draw_landmarks(bgr, frame):
    """Cheap debug overlay drawn straight onto the preview image."""
    if bgr is None:
        return bgr
    import cv2
    h, w = bgr.shape[:2]
    for hand, colour in ((frame.left, (80, 200, 120)), (frame.right, (58, 134, 255))):
        if hand is None:
            continue
        for (x, y, _) in hand.landmarks:
            cv2.circle(bgr, (int(x * w), int(y * h)), 4, colour, -1)
    return bgr


# ---------------------------------------------------------------- main
def main() -> None:
    use_keyboard = "--keyboard" in sys.argv
    if "--no-voice" in sys.argv:
        config.ENABLE_VOICE = False

    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.display.set_caption(config.TITLE)
    screen = pygame.display.set_mode((config.WINDOW_W, config.WINDOW_H))
    clock = pygame.time.Clock()

    sounds = SoundBank()
    scene = Scene(screen)
    game = Game()
    recognizer = GestureRecognizer()

    # ---- input source ----------------------------------------------------
    source = None
    if not use_keyboard:
        try:
            source = make_webcam_source()
        except Exception as exc:
            print(f"[input] webcam unavailable ({exc}); falling back to keyboard")
    if source is None:
        source = KeyboardSource()

    # ---- voice -----------------------------------------------------------
    jarvis = None
    if config.ENABLE_VOICE:
        from voice.jarvis import Jarvis
        jarvis = Jarvis()
        jarvis.start()

    hologram = None
    debug = False
    running = True

    def swap_input():
        nonlocal source
        old = source
        try:
            source = KeyboardSource() if old.name == "webcam" else make_webcam_source()
        except Exception as exc:
            print(f"[input] swap failed: {exc}")
            return
        old.release()
        recognizer.reset()

    def handle_voice(cmd):
        nonlocal debug, hologram, running
        a = cmd.action
        if a == "start" and game.state.phase is not Phase.PLAYING:
            game.start()
        elif a == "restart":
            game.start()
        elif a == "status":
            jarvis.say(f"You are on {game.player.hp} health. "
                       f"Enemy on {game.enemy.hp}. Score {game.state.score}.")
            return
        elif a == "debug":
            debug = not debug
        elif a == "keyboard" and source.name != "keyboard":
            swap_input()
        elif a == "camera" and source.name != "webcam":
            swap_input()
        elif a == "hologram":
            toggle_hologram()
        elif a == "quit":
            running = False
        if a in REPLIES:
            jarvis.say(REPLIES[a])

    def toggle_hologram():
        nonlocal hologram
        if hologram is None:
            from render.hologram import HologramView
            hologram = HologramView()
            if not hologram.open():
                hologram = None
        else:
            hologram.close()
            hologram = None

    # ---- the loop --------------------------------------------------------
    while running:
        dt = clock.tick(config.FPS_CAP) / 1000.0

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                elif e.key == pygame.K_SPACE and game.state.phase is Phase.MENU:
                    game.start()
                elif e.key == pygame.K_r:
                    game.start()
                elif e.key == pygame.K_F1:
                    debug = not debug
                elif e.key == pygame.K_F2:
                    swap_input()
                elif e.key == pygame.K_h:
                    toggle_hologram()
                elif e.key == pygame.K_LEFTBRACKET:
                    config.STRUM_VELOCITY_THRESHOLD = max(
                        0.1, config.STRUM_VELOCITY_THRESHOLD - 0.05)
                elif e.key == pygame.K_RIGHTBRACKET:
                    config.STRUM_VELOCITY_THRESHOLD += 0.05
                elif isinstance(source, KeyboardSource):
                    source.handle_key(e.key)

        if jarvis is not None:
            cmd = jarvis.poll()
            if cmd:
                handle_voice(cmd)

        # ---- input -> events --------------------------------------------
        frame = source.read()
        events = source.poll_events()
        if source.name == "webcam":
            events += recognizer.process(frame)

        # ---- game --------------------------------------------------------
        game.update(dt, events)
        scene.handle_fx(game.state.drain(), sounds)

        # ---- draw --------------------------------------------------------
        cam_surface = None
        if source.name == "webcam" and frame is not None and frame.raw_image is not None:
            img = frame.raw_image.copy()
            if debug:
                img = draw_landmarks(img, frame)
            cam_surface = cam_to_surface(img)

        fps = getattr(source, "fps", clock.get_fps())
        scene.draw(game, recognizer if source.name == "webcam" else None,
                   fps, source.name, debug, frame, cam_surface, dt)

        if hologram is not None:
            hologram.draw(screen)

    source.release()
    if jarvis is not None:
        jarvis.stop()
    pygame.quit()


if __name__ == "__main__":
    main()
