import pygame

import config
from gestures import chords as chord_utils


def comic_bar(surf, rect, ratio, fill, label, font, flip=False):
    x, y, w, h = rect
    pygame.draw.rect(surf, config.PAPER, (x, y, w, h), border_radius=6)
    inner_w = int((w - 8) * max(0.0, min(1.0, ratio)))
    if inner_w > 0:
        ix = x + 4 if not flip else x + w - 4 - inner_w
        pygame.draw.rect(surf, fill, (ix, y + 4, inner_w, h - 8), border_radius=4)
    pygame.draw.rect(surf, config.INK, (x, y, w, h), 5, border_radius=6)
    txt = font.render(label, True, config.INK)
    surf.blit(txt, (x + 6, y - txt.get_height() - 2))


def draw(surf, game, recognizer, fonts, fps, source_name, debug=False, frame=None):
    W = config.WINDOW_W
    p, e = game.player, game.enemy

    comic_bar(surf, (40, 60, 420, 40), p.hp / p.max_hp, config.GREEN,
              f"YOU  {p.hp}", fonts["small"])
    comic_bar(surf, (W - 460, 60, 420, 40), e.hp_ratio, config.RED,
              f"{e.name}  {e.hp}", fonts["small"], flip=True)

    # current chord, centre top
    chord = recognizer.stable_chord if recognizer else "NONE"
    label = chord if chord != "NONE" else "--"
    col = config.BLUE if chord != "NONE" else (150, 145, 135)
    big = fonts["chord"].render(label, True, col)
    ink = fonts["chord"].render(label, True, config.INK)
    cx = W // 2
    surf.blit(ink, ink.get_rect(center=(cx + 3, 93)))
    surf.blit(big, big.get_rect(center=(cx, 90)))
    cap = fonts["small"].render("CHORD", True, config.INK)
    surf.blit(cap, cap.get_rect(center=(cx, 40)))

    # combo trail
    trail = " > ".join(c for c, _ in p.combo_buffer[-4:])
    if trail:
        t = fonts["small"].render(trail, True, config.INK)
        surf.blit(t, t.get_rect(center=(cx, 138)))

    # score
    sc = fonts["med"].render(f"SCORE {game.state.score}", True, config.INK)
    surf.blit(sc, sc.get_rect(midtop=(cx, config.WINDOW_H - 96)))

    # status line
    status = fonts["tiny"].render(
        f"{fps:5.1f} FPS   input: {source_name}   F1 debug   F2 swap input   R restart   ESC quit",
        True, (90, 85, 78),
    )
    surf.blit(status, (28, config.WINDOW_H - 40))

    if debug:
        _debug(surf, fonts, recognizer, frame)


def _debug(surf, fonts, recognizer, frame):
    lines = []
    if frame is not None:
        lines.append(f"left hand:  {'yes' if frame.left else 'no'}")
        lines.append(f"right hand: {'yes' if frame.right else 'no'}")
        lines.append(f"fingers:    {chord_utils.describe(frame.left)}")
    if recognizer is not None:
        lines.append(f"velocity:   {recognizer.strum.velocity:+.2f}")
        lines.append(f"threshold:  {config.STRUM_VELOCITY_THRESHOLD:.2f}  ([ / ] to tune)")
        lines.append(f"armed:      {recognizer.strum.armed}")
        lines.append(f"stable:     {recognizer.stable_chord}")

    pad = 10
    box = pygame.Surface((330, 24 * len(lines) + pad * 2), pygame.SRCALPHA)
    box.fill((18, 16, 24, 215))
    surf.blit(box, (16, 180))
    for i, line in enumerate(lines):
        surf.blit(fonts["tiny"].render(line, True, config.PAPER),
                  (16 + pad, 180 + pad + i * 24))
