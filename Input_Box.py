import pygame

FONT = r'assets\Fonts\AmongUsFont.ttf'

class InputBox:
    def __init__(self, x, y, w, h, font=FONT, text=''):
        pygame.font.init()
        self.password = False
        if font and font == 'PASSWORD':
            font = FONT
            self.password = True
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = pygame.Color('gray')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.text = text
        self.font = pygame.font.Font(FONT,32)
        self.txt_surface = self.font.render(self.text, True, pygame.Color('blue'))
        self.active = False

    def handle_event(self, event,max_char=6):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                pass  # Let Menu handle RETURN
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isprintable() and len(self.text) < max_char:
                self.text += event.unicode
            if self.password:
                self.txt_surface = self.font.render((len(self.text)*'*'), True, pygame.Color('blue'))
            else:
                self.txt_surface = self.font.render(self.text, True, pygame.Color('blue'))

    def draw(self, screen):

        if self.password:
            self.txt_surface = self.font.render((len(self.text) * '*'), True, pygame.Color('blue'))
        else:
            self.txt_surface = self.font.render(self.text, True, pygame.Color('blue'))

        # Resize box if needed
        self.rect.w = max(300, self.txt_surface.get_width() + 10)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def get_text(self):
        return self.text
