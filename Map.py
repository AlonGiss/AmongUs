import pygame
from Button import Button



class Map:
    def __init__(self,screen,player):
        self.screen = screen
        self.player = player
        self.map_img = pygame.image.load('assets/map/map_icon.png')
        self.map_img = pygame.transform.scale(self.map_img,(1000,700))
        self.exit_button = Button(self.screen,(200, 510, 83, 82),image=pygame.image.load(r'assets/Images/Tasks/close.PNG'))
        self.amongus_player = pygame.image.load('assets/map/amongus_icon.png')
        self.amongus_player = pygame.transform.scale(self.amongus_player,(20,20))

    def show_map(self):
        self.screen.blit(self.map_img,(0,0))
        self.exit_button.draw()
        self.screen.blit(self.amongus_player,(self.player.x,self.player.y))


