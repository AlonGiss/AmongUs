import pygame

FONT = None

class Button:
    def __init__(self, screen, size, text='', color_back='BLACK', color_for='WHITE', image=None):
        pygame.init()
        self.screen = screen
        self.dist = (size[0],size[1])
        self.rect = pygame.Rect(size)
        self.color_back = color_back
        self.color_for = color_for
        self.text = text
        self.font = pygame.font.SysFont(FONT, 36)

        # Optional image
        self.image = image  # Should be a loaded pygame.Surface, not a path string

    def draw(self):
        if self.image:
            # Scale and blit image to fit button rect
            scaled_img = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
            self.screen.blit(scaled_img, self.rect.topleft)
        else:
            # Draw colored rect and text
            pygame.draw.rect(self.screen, self.color_back, self.rect)
            if self.text:
                surface_text = self.font.render(self.text, True, self.color_for)
                text_rect = surface_text.get_rect(center=self.rect.center)
                self.screen.blit(surface_text, text_rect)

    def is_button_pressed(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    return True
        return False  # Make sure it always returns something

    def set_rect(self, size):
        self.rect = pygame.Rect(size)

    def set_image(self, image_surface):
        self.image = image_surface
