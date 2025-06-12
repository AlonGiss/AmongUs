import pygame
from Button import  Button
ZOOM = 4
SIZE_MAP = (1000,700)

class SecurityCameraSystem:
    def __init__(self, screen, map_surface):
        self.screen = screen
        self.map = map_surface
        self.camera_zones = [(563,375),(206,282),(443,111),(854,273)]
        self.active_camera = None
        self.in_camera_mode = False
        self.font = pygame.font.SysFont(None, 24)
        self.indx= 0
        self.change = Button(self.screen,(700,500,100,100),'Change')

    def show_camera(self,events = None):
        zoom = ZOOM
        cam_w, cam_h = SIZE_MAP[0] // zoom, SIZE_MAP[1] // zoom
        cam_x = max(0, min(self.camera_zones[self.indx][0] - cam_w // 2, self.map.get_width() - cam_w))
        cam_y = max(0, min(self.camera_zones[self.indx][1] - cam_h // 2, self.map.get_height() - cam_h))
        print(f'{cam_x} cam_y: {cam_y}\n\n\n')
        camera_rect = pygame.Rect(cam_x, cam_y, cam_w, cam_h)
        view = self.map.subsurface(camera_rect)
        view_scaled = pygame.transform.scale(view, (SIZE_MAP[0], SIZE_MAP[1]))
        self.screen.blit(view_scaled, (0, 0))
        self.change.draw()
        if events and self.change.is_button_pressed(events):
            self.camera_mode_change()

    def camera_mode_change(self):
        self.indx = (self.indx +1) % len(self.camera_zones)
        print(self.camera_zones[self.indx])
        self.show_camera()

