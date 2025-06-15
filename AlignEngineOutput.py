import math,pygame
import time
from Button import  Button

FONT = r'assets\Fonts\AmongUsFont.ttf'
IMG_ADRS = r'assets\Images\Tasks\AlignEngineOutput'
TASK_SIZE = (500,500)

class AlignEngineOutput:
    def __init__(self,screen):
        self.screen = screen
        exit_button_img = pygame.image.load(r'assets\Images\Tasks\close.PNG')
        self.exit_button = Button(screen,(215,430,65,65),'Exit','BLUE','White',exit_button_img)
        self.timer = 0
        self.start = 0
    def start_task_AlignEngineOutput(self):
        # Load your task screen and lever images
        task_img, liver_img, move_img = self.load_assets_align_engine_output()
        screen_size = self.screen.get_size()
        task_img_dest = (0, 0)
        move_img_dest = (30, task_img.get_size()[1] // 2 - 87)

        # Generate smooth points along the arc
        arc_points = self.generate_arc_points(task_img, liver_img, min_y=30, max_y=task_img.get_height() - 30)

        # Initial lever position at the midpoint of the arc
        lever_index = len(arc_points) // 2
        liver_img_dest = [arc_points[lever_index][0] - liver_img.get_width() // 2,
                              arc_points[lever_index][1] - liver_img.get_height() // 2 - 100]
        dragging = False
        while True:
            events = pygame.event.get()
            if self.exit_button.is_button_pressed(events):
                return False

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                dragging = self.is_liver_moved(event, liver_img_dest, liver_img, dragging, arc_points)

            self.screen.blit(task_img, task_img_dest)
            rotated_move, move_rect = self.rotate_engine(move_img, move_img_dest, liver_img_dest, liver_img,arc_points)

            self.screen.blit(rotated_move, move_rect.topleft)
            self.screen.blit(liver_img, liver_img_dest)
            self.exit_button.draw()
            pygame.display.update()
            if move_rect.x == 29 and move_rect.y == 161:
                self.timer +=  pygame.time.get_ticks() - self.start
                if self.timer > 5000:
                    break
            else:
                self.start = pygame.time.get_ticks()

        self.show_text('WELL DONE', TASK_SIZE[0] // 2 - 150, 100, 'GREEN', 50)
        pygame.display.update()
        time.sleep(3)
        return True

    def load_assets_align_engine_output(self):
        task_img = pygame.image.load(IMG_ADRS + r'\engineAlign_base.png')
        liver_img = pygame.image.load(IMG_ADRS + r'\engine_liver.png')
        move_img = pygame.image.load(IMG_ADRS + r'\engineAlign_base4.png')
        return task_img, liver_img, move_img

    def is_liver_moved(self, event, liver_img_dest, liver_img, dragging, arc_points):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            liver_rect = pygame.Rect(liver_img_dest, liver_img.get_size())
            if liver_rect.collidepoint(mouse_pos):
                dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False

        elif event.type == pygame.MOUSEMOTION and dragging:
            mouse_x, mouse_y = event.pos

            # Find the closest point on the arc to the current mouse position
            closest_point = min(arc_points, key=lambda p: (p[0] - mouse_x) ** 2 + (p[1] - mouse_y) ** 2)

             # Set lever position centered at the closest point on the arc
            liver_img_dest[0] = closest_point[0] - liver_img.get_width() // 2
            liver_img_dest[1] = closest_point[1] - liver_img.get_height() // 2

        return dragging

    def rotate_engine(self, move_img, move_img_dest, liver_img_dest, liver_img, arc_points):
        """
        Rotates the engine (move_img) to align with the direction of the lever along the arc.
        """
        # Find center of the current liver position
        liver_center = (
            liver_img_dest[0] + liver_img.get_width() // 2,
            liver_img_dest[1] + liver_img.get_height() // 2
        )

         # Find the closest arc index to the liver
        closest_index = min(
            range(len(arc_points)),
            key=lambda i: (arc_points[i][0] - liver_center[0]) ** 2 + (arc_points[i][1] - liver_center[1]) ** 2
        )

        # Compute angle between current and next arc point
        if closest_index < len(arc_points) - 1:
            p1 = arc_points[closest_index]
            p2 = arc_points[closest_index + 1]
        else:
            p1 = arc_points[closest_index - 1]
            p2 = arc_points[closest_index]

        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        angle = -1 * (math.degrees(math.atan2(-dy, dx)) + 90)  # Negate dy due to Pygame's inverted Y

        # Rotate the image
        rotated_move = pygame.transform.rotate(move_img, angle)

        # Center the rotated image around move_img_dest
        move_rect = rotated_move.get_rect(center=(
            move_img_dest[0] + move_img.get_width() // 2,
            move_img_dest[1] + move_img.get_height() // 2
        ))

        return rotated_move, move_rect

    def show_text(self, text, x, y, color='WHITE', size=25):
        font = pygame.font.SysFont(None, size)
        super_texto = font.render(text, True, color)
        self.screen.blit(super_texto, (x, y))

    def generate_arc_points(self,task_img, img, min_y=0, max_y=9999):
        """
        Generates a list of (x, y) points along a circular arc and restricts them within a Y range.
        """
        center = [int(task_img.get_width() + 400), (task_img.get_height() // 2)]
        radius = 500
        start_deg = 270
        end_deg = 90
        resolution = 100

        start_rad = math.radians(start_deg)
        end_rad = math.radians(end_deg)

        # Generate arc points
        points = [
            (
                center[0] + radius * math.cos(theta),
                center[1] + radius * math.sin(theta)
            )
            for theta in [start_rad + i * (end_rad - start_rad) / resolution for i in range(resolution + 1)]
        ]

        # Filter based on Y range
        filtered_points = [p for p in points if min_y <= p[1] <= max_y]
        return filtered_points

