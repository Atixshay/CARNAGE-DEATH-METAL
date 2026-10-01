import pygame

import config


class HologramView:
    def __init__(self, size=720):
        self.size = size
        self.surface = pygame.Surface((size, size))
        self.window = None

    def open(self):
        # A second OS window needs pygame 2.4+ (pygame-ce has it).
        try:
            from pygame._sdl2.video import Window, Renderer, Texture
            self.window = Window("HOLOGRAM", size=(self.size, self.size))
            self.renderer = Renderer(self.window)
            self._Texture = Texture
            return True
        except Exception as exc:
            print(f"[hologram] second window unavailable: {exc}")
            return False

    def draw(self, source: pygame.Surface):
        """source = a square surface with the subject on black."""
        if self.window is None:
            return
        s = self.size
        quarter = pygame.transform.smoothscale(source, (s // 2, s // 2))

        self.surface.fill((0, 0, 0))
        # bottom (upright), top (180), left (90), right (270)
        placements = [
            (pygame.transform.rotate(quarter, 0),   (s // 4, s // 2)),
            (pygame.transform.rotate(quarter, 180), (s // 4, 0)),
            (pygame.transform.rotate(quarter, 90),  (0, s // 4)),
            (pygame.transform.rotate(quarter, 270), (s // 2, s // 4)),
        ]
        for img, pos in placements:
            self.surface.blit(img, pos)

        tex = self._Texture.from_surface(self.renderer, self.surface)
        self.renderer.clear()
        tex.draw()
        self.renderer.present()

    def close(self):
        if self.window is not None:
            self.window.destroy()
            self.window = None
