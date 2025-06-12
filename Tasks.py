import threading
from EmptyGarbage import EmptyGarbage
import pygame
import random
from ClearAsteroids import ClearAsteroids
from AlignEngineOutput import AlignEngineOutput
from FixWiring import FixWiring

FONT = None
IMG_ADRS = r'assets\Images\Tasks'
TASK_SIZE = (500,500)
TASKS = [
    #"Turn On The Lights",
    #"Stabilize The Ship's Navigation",
    #"Reboot The Wifi",
    "Empty The Garbage",
    "Fix The Electricity Wires",
    #"Divert Power To Reactor",
    "Align Engine Output",
    #"Fuel Lower Engine",
    "Clear the Asteroids"
]



class Tasks:
    def __init__(self,screen,num_of_tasks):
        self.screen = screen
        self.num_of_tasks = num_of_tasks
        self.tasks_finished = False
        self.task_array = {}
        self.turn_on_the_lights_mission_status = False
        self.clear_asteroids_mission_status = False
        self.turn_on_the_lights_task_title = "Turn On The Lights"
        self.turn_on_the_lights_task_title_visibility_status = False
        self.stabilize_nav_task_title = "Stabilize The Ship's Navigation"
        self.stabilize_nav_task_title_visibility_status = False
        self.reboot_the_wifi_task_title = "Reboot The Wifi"
        self.reboot_the_wifi_task_title_visibility_status = False
        self.empty_the_garbage_task_title = "Empty The Garbage"
        self.empty_the_garbage_task_title_visibility_status = False
        self.fix_electircity_wires_task_title = "Fix The Electricity Wires"
        self.fix_electircity_wires_task_title_visibility_status = False
        self.divert_power_to_reactor_task_title = "Divert Power To Reactor"
        self.divert_power_to_reactor_task_title_visibility_status = False
        self.align_engine_output_task_title = "Align Engine Output"
        self.align_engine_output_title_visibility_status = False
        self.fuel_engine_task_title = "Fuel Lower Engine"
        self.fuel_engine_task_title_visibility_status = False
        self.clear_asteroids_task_title = "Clear the Asteroids"
        self.clear_asteroids_task_title_visibility_status = False

        self.tasks_postions = [(629,339,'Fix The Electricity Wires'),(584,618,"Empty The Garbage"),(770,144,"Clear the Asteroids"),(170,192,"Align Engine Output")]

        for i in range(self.num_of_tasks):
            task = TASKS[random.randint(0,len(TASKS)-1)]
            TASKS.remove(task)
            self.task_array[task] = self.create_task_instance_by_name(task)


    def show_tasks(self):
        inner_bg_rect = pygame.Rect(20,50, 200, 100)
        pygame.draw.rect(self.screen, (100, 100, 100,50), inner_bg_rect)
        y = 60
        for task in self.task_array.keys():
            self.show_text(task,30,y,'Black')
            y += 30

    def show_text(self,text,x,y,color='WHITE'):
        font = pygame.font.SysFont(FONT, 25)
        super_texto = font.render(text, True, color)
        self.screen.blit(super_texto, (x,y))

    def FixWiring(self):
        task = self.task_array["Fix The Electricity Wires"]
        if task.start_task_Fix_Wiring():
            self.task_array.pop("Fix The Electricity Wires")
            self.num_of_tasks -=1
            if self.num_of_tasks == 0:
                self.tasks_finished = True
            return True
        return False

    def EmptyGarbage(self):
        task = self.task_array["Empty The Garbage"]
        if task.start_task_Empty_Garbage():
            self.task_array.pop("Empty The Garbage")
            self.num_of_tasks -=1
            if self.num_of_tasks == 0:
                self.tasks_finished = True
            return True
        return False

    def ClearAsteroids(self):
        task = self.task_array["Clear the Asteroids"]
        if task.start_task_Clear_Asteroid():
            self.task_array.pop("Clear the Asteroids")
            self.num_of_tasks -=1
            if self.num_of_tasks == 0:
                self.tasks_finished = True
            return True
        return False

    def AlignEngineOutput(self):
        task = self.task_array["Align Engine Output"]
        if task.start_task_AlignEngineOutput():
            self.task_array.pop("Align Engine Output")
            self.num_of_tasks -=1
            if self.num_of_tasks == 0:
                self.tasks_finished = True
            return True
        return False


    def create_task_instance_by_name(self, task_name):
        """
        Given a task name, return an instance of the corresponding task class.
        """
        task_class_map = {
            #"Turn On The Lights": TurnOnTheLights,
            #"Stabilize The Ship's Navigation": StabilizeNavigation,
            #"Reboot The Wifi": RebootTheWifi,
            "Empty The Garbage": EmptyGarbage,
            "Fix The Electricity Wires": FixWiring,
            #"Divert Power To Reactor": DivertPowerToReactor,
            "Align Engine Output": AlignEngineOutput,
            #"Fuel Lower Engine": FuelLowerEngine,
            "Clear the Asteroids": ClearAsteroids
        }

        task_class = task_class_map.get(task_name)

        if task_class:
            return task_class(self.screen)  # Instantiate the class
        else:
            print(f"No task class found for: {task_name}")
            return None

    def do_task_by_name(self, task_name):
        """
        Given a task name, return an instance of the corresponding task class.
        """
        task_class_map = {
            #"Turn On The Lights": TurnOnTheLights,
            #"Stabilize The Ship's Navigation": StabilizeNavigation,
            #"Reboot The Wifi": RebootTheWifi,
            "Empty The Garbage": self.EmptyGarbage,
            "Fix The Electricity Wires": self.FixWiring,
            #"Divert Power To Reactor": DivertPowerToReactor,
            "Align Engine Output": self.AlignEngineOutput,
            #"Fuel Lower Engine": FuelLowerEngine,
            "Clear the Asteroids": self.ClearAsteroids
        }

        task_class = task_class_map.get(task_name)

        if task_class:
            return task_class()  # Instantiate the class
        else:
            print(f"No task class found for: {task_name}")
            return None




