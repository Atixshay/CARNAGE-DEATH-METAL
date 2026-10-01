"""
render/comic_fx.py - the comic-book layer: impact words, speed lines,
screen shake, halftone paper, panel borders.

All of it is procedural. No sprite files needed, though you can drop PNGs
into assets/sprites/ later and swap them in without touching anything else.
"""

import math
import random

import pygame

import config


class Shake:
    def __init__(self):
        self.amount = 0.0

    def kick(self, amount: float) -> None:
        self.amount = max(self.amount, amount)

    def tick(self, dt: float):
        self.amount = max(0.0, self.amount - dt * 60.0)
        if self.amount <= 0:
            return 0, 0
        return (
            random.randint(-int(self.amount), int(self.amount)),
            random.randint(-int(self.amount), int(self.amount)),
        )


class ImpactWord:
    """A POW! that punches in, wobbles, then flies off."""

    def __init__(self, text, pos, font, color=config.YELLOW, scale=1.0):
        self.text = text
        self.x, self.y = pos
        self.font = font
        self.color = color
        self.life = 0.0
        self.max_life = 0.75
        self.scale = scale
        self.angle = random.uniform(-14, 14)
        self.drift = random.uniform(-40, 40)

    @property
    def dead(self) -> bool:
        return self.life >= self.max_life

    def tick(self, dt: float) -> None:
        self.life += dt
        self.y -= dt * 60
        self.x += self.drift * dt

    def draw(self, surf) -> None:
        p = self.life / self.max_life
        pop = 1.0 + 0.9 * math.sin(min(1.0, p * 3.2) * math.pi * 0.5)
        size = max(0.1, self.scale * pop * (1.0 - 0.25 * p))
        alpha = int(255 * (1.0 - max(0.0, (p - 0.6) / 0.4)))

        base = self.font.render(self.text, True, self.color)
        outline = self.font.render(self.text, True, config.INK)

        # never let a long combo name run off the page
        max_w = config.WINDOW_W * 0.8
        if base.get_width() * size > max_w:
            size = max_w / base.get_width()

        w = int(base.get_width() * size)
        h = int(base.get_height() * size)
        if w <= 0 or h <= 0:
            return
        base = pygame.transform.smoothscale(base, (w, h))
        outline = pygame.transform.smoothscale(outline, (w + 8, h + 8))
        base = pygame.transform.rotate(base, self.angle)
        outline = pygame.transform.rotate(outline, self.angle)
        base.set_alpha(alpha)
        outline.set_alpha(alpha)

        surf.blit(outline, outline.get_rect(center=(self.x, self.y)))
        surf.blit(base, base.get_rect(center=(self.x, self.y)))


def make_halftone(size, dot=9, color=(226, 214, 184)):
    """A paper-texture surface of offset dots. Build once, blit forever."""
    w, h = size
    surf = pygame.Surface(size).convert()
    surf.fill(config.PAPER)
    for row, y in enumerate(range(0, h + dot, dot)):
        offset = (dot // 2) if row % 2 else 0
        for x in range(0, w + dot, dot):
            pygame.draw.circle(surf, color, (x + offset, y), max(1, dot // 4))
    return surf


def draw_speed_lines(surf, center, count=34, inner=260, outer=760, color=config.INK):
    cx, cy = center
    for i in range(count):
        a = (i / count) * math.tau + random.uniform(-0.04, 0.04)
        r1 = inner + random.uniform(-20, 40)
        r2 = outer
        pygame.draw.line(
            surf, color,
            (cx + math.cos(a) * r1, cy + math.sin(a) * r1),
            (cx + math.cos(a) * r2, cy + math.sin(a) * r2),
            random.randint(1, 4),
        )


def draw_panel(surf, rect, width=6, color=config.INK):
    pygame.draw.rect(surf, color, rect, width, border_radius=4)


def draw_starburst(surf, center, radius, color=config.RED, points=12, ink=config.INK):
    cx, cy = center
    pts = []
    for i in range(points * 2):
        r = radius if i % 2 == 0 else radius * 0.58
        a = (i / (points * 2)) * math.tau
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, ink, pts, 5)
