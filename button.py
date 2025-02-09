import pygame

class Button():
    def __init__(self, x, y, image, scale=1.1):
        self.original_image = image
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.scale = scale
        self.hovered = False

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if not self.hovered:
                self.image = pygame.transform.scale(self.original_image, (int(self.rect.width * self.scale), int(self.rect.height * self.scale)))
                self.rect = self.image.get_rect(center=self.rect.center)
                self.hovered = True
            if pygame.mouse.get_pressed()[0]:
                action = True
        else:
            self.image = self.original_image
            self.rect = self.image.get_rect(center=self.rect.center)
            self.hovered = False

        surface.blit(self.image, self.rect)
        return action
