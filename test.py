import pygame
pygame.init()
screen = pygame.display.set_mode((600, 480))
clock = pygame.time.Clock()
run = True

class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.surface.Surface((60, 60))
        self.rect = self.image.get_rect(center=pos)
        self.state = 0

    def update(self):
        self.state += 1
        self.image.fill((0, 0, 0))
        pygame.draw.circle(self.image, (200, 5 * self.state, 0), self.image.get_rect().center, self.state)
        if self.state > 30:
            self.kill()

class Ball(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.surface.Surface((40, 40))
        self.image.fill((60, 60, 200))
        self.rect = self.image.get_rect(center=pos)
        self.dir = 3

    def update(self):
        if not screen.get_rect().contains(self.rect):
            self.dir *= -1
        self.image.fill((self.rect.x % 255, 60, 200))
        self.rect.move_ip(self.dir, 0)

sprites = pygame.sprite.Group(Ball((200, 200)), Ball((100, 300)))
while run:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run = False 
        if e.type == pygame.MOUSEBUTTONDOWN:
            sprites.add(Explosion(e.pos))

    screen.fill((0, 0, 0))
    sprites.draw(screen)
    sprites.update()
    pygame.display.flip()
    clock.tick(60)