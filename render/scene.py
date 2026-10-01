"""
render/scene.py - draws one whole frame from GameState.

Owns the fonts, the background, the effect list and the webcam preview.
Reads the game; never changes it.
"""

import math
import random

import pygame

import config
from render import comic_fx, hud
from game.state import Phase


class Scene:
    def __init__(self, screen):
        self.screen = screen
        self.shake = comic_fx.Shake()
        self.effects = []
        self.flash = 0.0
        self.fonts = self._load_fonts()
        self.bg = self._load_background()
        self.enemy_sprite = self._load_enemy_sprite()
        self.speed_lines_timer = 0.0

    # ------------------------------------------------------------------ setup
    def _load_fonts(self):
        def pick(size, bold=True):
            for name in ("bangers", "impact", "arialblack", "dejavusans"):
                path = pygame.font.match_font(name, bold=bold)
                if path:
                    return pygame.font.Font(path, size)
            return pygame.font.Font(None, size)

        return {
            "tiny": pick(18),
            "small": pick(24),
            "med": pick(36),
            "big": pick(64),
            "chord": pick(96),
            "huge": pick(120),
        }

    def _load_enemy_sprite(self):
        import os
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            "assets", "sprites", "enemy.png")
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            return img
        return None

    # ------------------------------------------------------------------ fx
    def handle_fx(self, events, sounds):
        cx, cy = config.WINDOW_W // 2, config.WINDOW_H // 2 - 20
        for ev in events:
            if ev.kind == "hit":
                self.shake.kick(config.HIT_SHAKE * (0.7 + ev.data.get("strength", 0)))
                self.effects.append(comic_fx.ImpactWord(
                    ev.data.get("word", "POW!"),
                    (cx + random.randint(-140, 140), cy + random.randint(-90, 40)),
                    self.fonts["big"], config.YELLOW,
                    1.0 + ev.data.get("strength", 0) * 0.5,
                ))
                sounds.play_chord(ev.data["chord"], 0.6 + ev.data.get("strength", 0) * 0.4)

            elif ev.kind == "combo":
                self.shake.kick(config.COMBO_SHAKE)
                self.flash = 0.35
                self.speed_lines_timer = 0.45
                self.effects.append(comic_fx.ImpactWord(
                    ev.data["name"], (cx, cy - 40),
                    self.fonts["big"], config.RED, 1.15,
                ))
                sounds.play_chord(ev.data["chord"], 1.0)
                sounds.play("combo", 0.9)

            elif ev.kind == "player_hurt":
                self.shake.kick(config.HIT_SHAKE * 1.2)
                self.flash = 0.25
                self.effects.append(comic_fx.ImpactWord(
                    f"-{ev.data['damage']}", (240, config.WINDOW_H - 200),
                    self.fonts["big"], config.RED,
                ))
                sounds.play("hurt", 0.8)

            elif ev.kind == "telegraph":
                sounds.play("telegraph", 0.5)

            elif ev.kind == "win":
                sounds.play("win")
            elif ev.kind == "lose":
                sounds.play("lose")

    # ------------------------------------------------------------------ draw
    def draw(self, game, recognizer, fps, source_name, debug=False,
             frame=None, cam_surface=None, dt=0.016):
        s = self.screen
        ox, oy = self.shake.tick(dt)
        self.flash = max(0.0, self.flash - dt * 3)
        self.speed_lines_timer = max(0.0, self.speed_lines_timer - dt)

        s.blit(self.bg, (ox, oy))

        cx, cy = config.WINDOW_W // 2, config.WINDOW_H // 2 - 10

        if self.speed_lines_timer > 0:
            comic_fx.draw_speed_lines(s, (cx + ox, cy + oy))

        if game.state.phase is Phase.PLAYING:
            self._draw_enemy(s, game, cx + ox, cy + oy)
            if cam_surface is not None and config.SHOW_CAM_PREVIEW:
                self._draw_cam(s, cam_surface)
            hud.draw(s, game, recognizer, self.fonts, fps, source_name, debug, frame)
        else:
            self._draw_card(s, game)

        for fx in list(self.effects):
            fx.tick(dt)
            fx.draw(s)
            if fx.dead:
                self.effects.remove(fx)

        if self.flash > 0:
            veil = pygame.Surface((config.WINDOW_W, config.WINDOW_H), pygame.SRCALPHA)
            veil.fill((255, 255, 255, int(200 * self.flash)))
            s.blit(veil, (0, 0))

        comic_fx.draw_panel(s, (10, 10, config.WINDOW_W - 20, config.WINDOW_H - 20), 8)
        pygame.display.flip()

    def _draw_enemy(self, s, game, cx, cy):
        e = game.enemy
        # Villain idle animation
        bob = math.sin(game.state.elapsed * 3.5) * 18
        sway = math.sin(game.state.elapsed * 2.2) * 4
        size = 380
        # Pulse harder while preparing an attack
        if e.telegraphing:
            size += int(35 * abs(math.sin(game.state.elapsed * 12)))

        # Shake when hit
        if e.hurt_timer > 0:
            cx += random.randint(-12, 12)
            cy += random.randint(-6, 6)
        if e.telegraphing:
            size += int(28 * math.sin(game.state.elapsed * 26))
        if e.hurt_timer > 0:
            cx += random.randint(-9, 9)

        colour = config.RED if e.telegraphing else (118, 92, 168)
        if e.hurt_timer > 0:
            colour = config.WHITE

        if self.enemy_sprite is not None:
            scale = size / self.enemy_sprite.get_width()
            new_w = int(self.enemy_sprite.get_width() * scale)
            new_h = int(self.enemy_sprite.get_height() * scale)
            img = pygame.transform.smoothscale(
                self.enemy_sprite,
                (new_w, new_h)
            )
            rect = img.get_rect(center=(cx + sway, cy + bob))
            s.blit(img, rect)
        else:
            comic_fx.draw_starburst(s, (cx, cy + bob), size // 2, colour)
            # face
            for dx in (-52, 52):
                pygame.draw.circle(s, config.PAPER, (cx + dx, cy + bob - 28), 26)
                pygame.draw.circle(s, config.INK, (cx + dx, cy + bob - 28), 26, 5)
                pygame.draw.circle(s, config.INK, (cx + dx, cy + bob - 24), 11)
            mouth = pygame.Rect(0, 0, 120, 46 if e.telegraphing else 22)
            mouth.center = (cx, cy + bob + 52)
            pygame.draw.ellipse(s, config.INK, mouth)

        if e.telegraphing:
            warn = self.fonts["med"].render("INCOMING!", True, config.RED)
            s.blit(warn, warn.get_rect(center=(cx, cy - 210 + bob)))

    def _draw_cam(self, s, cam_surface):
        w = int(config.CAM_WIDTH * config.CAM_PREVIEW_SCALE)
        h = int(config.CAM_HEIGHT * config.CAM_PREVIEW_SCALE)
        small = pygame.transform.smoothscale(cam_surface, (w, h))
        x, y = config.WINDOW_W - w - 34, config.WINDOW_H - h - 34
        s.blit(small, (x, y))
        comic_fx.draw_panel(s, (x - 4, y - 4, w + 8, h + 8), 5)

    def _draw_card(self, s, game):
        phase = game.state.phase
        cx, cy = config.WINDOW_W // 2, config.WINDOW_H // 2

        if phase is Phase.MENU:
            title, sub, colour = config.TITLE, "PRESS SPACE TO PLAY", config.BLUE
            lines = [
                "LEFT HAND  = chord shape     fist E   open A   peace D   horns G   thumb C",
                "RIGHT HAND = strum           swing down or up to fire",
                "COMBOS     = E E A   D D G   A D E   C G C",
                "",
                "F2 switches to keyboard control if the camera struggles.",
            ]
        elif phase is Phase.WIN:
            title, sub, colour = "YOU SHRED!", f"SCORE {game.state.score}", config.GREEN
            lines = ["PRESS R TO PLAY AGAIN"]
        else:
            title, sub, colour = "WIPED OUT", f"SCORE {game.state.score}", config.RED
            lines = ["PRESS R TO TRY AGAIN"]

        comic_fx.draw_starburst(s, (cx, cy - 60), 260, colour, 16)
        t = self.fonts["huge"].render(title, True, config.PAPER)
        ti = self.fonts["huge"].render(title, True, config.INK)
        s.blit(ti, ti.get_rect(center=(cx + 4, cy - 56)))
        s.blit(t, t.get_rect(center=(cx, cy - 60)))

        st = self.fonts["med"].render(sub, True, config.INK)
        s.blit(st, st.get_rect(center=(cx, cy + 110)))

        for i, line in enumerate(lines):
            if not line:
                continue
            ln = self.fonts["small"].render(line, True, config.INK)
            s.blit(ln, ln.get_rect(center=(cx, cy + 170 + i * 30)))
    def _load_background(self):
        import os

        path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "assets",
            "backgrounds",
            "arena.png"
        )

        if os.path.exists(path):
            img = pygame.image.load(path).convert()
            return pygame.transform.smoothscale(
                img,
                (config.WINDOW_W, config.WINDOW_H)
            )

        return comic_fx.make_halftone(
            (config.WINDOW_W, config.WINDOW_H)
        )
