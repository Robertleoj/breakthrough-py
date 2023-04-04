from math import floor
from pathlib import Path
from random import random, randint
import pygame

class Player:
    def __init__(self, fname, nframes, nattacks):
        path = Path(fname) / 'Idle.png'
        attack_path = Path(fname) / 'Attack_1.png'
        self.image = pygame.image.load(path) # 5 frames
        self.attack_image = pygame.image.load(attack_path) # 5 frames
        self.sprites = []
        self.attack_sprites = []
        width, height = self.image.get_size()
        sw = width // nframes
        self.width = sw
        self.height = height
        for i in range(nframes):
            self.sprites.append(self.image.subsurface(i*sw, 0, sw, height))
        width, height = self.attack_image.get_size()
        sw = width // nattacks
        self.attack_width = sw
        self.attack_height = height
        for i in range(nattacks):
            self.attack_sprites.append(self.attack_image.subsurface(i*sw, 0, sw, height))

        self.animation_idx = random() * len(self.sprites)
        self.animation_speed = 0.05
        self.attack_animation_idx = random() * len(self.attack_sprites)
        self.attack_animation_speed = 0.3

    def draw(self, screen, x, y):
        x = x - self.width // 2
        y = y - self.height //2 - 20
        sprite = self.sprites[floor(self.animation_idx)]
        screen.blit(sprite, (x, y))
        self.animation_idx += self.animation_speed
        if self.animation_idx >= len(self.sprites):
            self.animation_idx = 0

    def draw_attack(self, screen, x, y):
        x = x - self.attack_width // 2
        y = y - self.attack_height //2 - 20
        sprite = self.attack_sprites[floor(self.attack_animation_idx)]
        screen.blit(sprite, (x, y))
        self.attack_animation_idx += self.attack_animation_speed
        if self.attack_animation_idx >= len(self.attack_sprites):
            self.attack_animation_idx = 0
