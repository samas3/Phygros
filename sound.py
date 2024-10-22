import pygame
pygame.mixer.init()
hitsong0 = pygame.mixer.Sound('src/HitSong0.ogg')
hitsong1 = pygame.mixer.Sound('src/HitSong1.ogg')
hitsong2 = pygame.mixer.Sound('src/HitSong2.ogg')
sounds = [hitsong0, hitsong1, hitsong2]
def play(id, options={}):
    if 'nosound' in options:
        return
    sounds[id].play()