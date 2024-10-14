import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
tap_img = pygame.image.load("Tap.png").convert_alpha()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    screen.fill((255, 255, 255))
    alpha = int(255 * (1 - (pygame.time.get_ticks() % 10000) / 10000))
    font = pygame.font.Font(None, 36)
    text = font.render("Alpha: " + str(alpha), True, (0, 0, 0))
    screen.blit(text, (10, 10))
    #将图片透明度设置为alpha
    tap_img.set_alpha(alpha)
    screen.blit(tap_img, (100, 100))
    pygame.display.flip()
    clock.tick(60)