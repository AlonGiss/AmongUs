

from Button import Button
import pygame

from Tasks import Tasks


class Imposter:
    def __init__(self,screen):
        image = pygame.image.load(r'assets\Images\UI\kill_icon.png')
        self.kill_button = Button(screen,(880,600,83,82),'kill',image=image)
        self.vents_button = Button(screen,(750,510,83,82),'Vents')
        self.vent_points = [
            (665, 180),
            (758, 84),
            (911, 255),
            (911, 336),
            (773, 336),
            (773, 546),
            (629, 429),
            (374, 384),
            (254, 525),
            (137, 351),
            (116, 249),
            (311, 351),
            (254, 105),
            (356, 282)
        ]
        self.current_vent_index = None
        self.vent_radius = 40
        self.couldown = 7000
        self.last_kill = pygame.time.get_ticks()

    def kill(self,events):
        if self.kill_button.is_button_pressed(events) and pygame.time.get_ticks() - self.last_kill > self.couldown:
            self.last_kill = pygame.time.get_ticks()
            return True

    def show_button(self):
        if pygame.time.get_ticks() - self.last_kill > self.couldown:
            self.kill_button.image = pygame.image.load(r'assets\Images\UI\kill_icon.png')
            self.kill_button.draw()
        else:
            self.kill_button.image = pygame.image.load(r'assets\Images\UI\kill_icon_dim.png')
            self.kill_button.draw()

    def near_vent(self, x, y):
        for i, (vx, vy) in enumerate(self.vent_points):
            if ((x - vx) ** 2 + (y - vy) ** 2) ** 0.5 < self.vent_radius:
                self.vents_button.draw()
                return i
        return None

    def try_vent_jump(self, player,events):
        vent_idx = self.near_vent(player.x, player.y)
        if vent_idx is not None and self.vents_button.is_button_pressed(events):
            self.current_vent_index = (vent_idx + 1) % len(self.vent_points)
            new_x, new_y = self.vent_points[self.current_vent_index]
            player.set_X_Y(new_x, new_y)
            print(f"jumped: {self.current_vent_index}")
            return True
        return False




TASK_RADIUS = 10

class Crewmate:
    def __init__(self,screen,player):
        self.player = player
        self.screen = screen
        self.tasks_completed = []
        self.total_tasks = Tasks(self.screen,3)
        self.task_positions = self.total_tasks.tasks_postions
        self.mission = Button(screen, (880, 600, 83, 82), 'Mision')

    def check_near_task(self,):
        """
        task_positions: list of (x, y, task_name)
        returns task_name if within range
        """
        for tx, ty, name in self.task_positions:
            if self._distance(self.player.x, self.player.y, tx, ty) < TASK_RADIUS and name not in self.tasks_completed:
                print(name)
                return name
        return None

    def do_task(self, task_name):
        try:
            if self.total_tasks.do_task_by_name(task_name):
                self.tasks_completed.append(task_name)
                print(f'Task {task_name} completed!')
                return True
            return False
        except Exception as err:
            print(f'ERA: {err}')

    def has_finished_all_tasks(self):
        return self.total_tasks.tasks_finished

    def _distance(self, x1, y1, x2, y2):
        return ((x1 - x2)**2 + (y1 - y2)**2) ** 0.5

    def button_presed(self,events):
        if self.mission.is_button_pressed(events):
            return True

    def show_button(self):
        self.mission.draw()