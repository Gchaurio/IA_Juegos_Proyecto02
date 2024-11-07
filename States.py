from StateMachine import State, Transition

class WanderingState(State):
    def __init__(self, enemy):
        super().__init__()
        self.enemy = enemy

    def enter(self):
        #print("Entering Wandering State")
        pass

    def execute(self):
        self.enemy.dynamic_wander()
    
    def exit(self):
        self.enemy.time_in_state = 0.0
        #print("Exiting Wandering State")

class SeekState(State):
    def __init__(self, enemy):
        super().__init__()
        self.enemy = enemy

    def enter(self):
        self.enemy.change_color((0, 255, 0))
        shrink_width = self.enemy.rect.width * 8 / 9
        shrink_height = self.enemy.rect.height * 8 / 9
        self.enemy.rect.inflate_ip(-shrink_width, -shrink_height)
        #print("Entering Seek State")

    def execute(self):
        player_node = self.enemy.graph.get_closest_node(self.enemy.target.pos)
        self.enemy.follow_path_with_seek(player_node)
    
    def exit(self):
        self.enemy.change_color((0, 125, 0))
        self.enemy.rect = self.enemy.image.get_rect(center=self.enemy.pos)

        shrink_width = self.enemy.rect.width * 1 / 2
        shrink_height = self.enemy.rect.height * 1 / 2
        self.enemy.rect.inflate_ip(-shrink_width, -shrink_height)

        self.enemy.time_in_state = 0.0
        #print("Exiting Seek State")

class SweepState(State):
    def __init__(self, enemy):
        super().__init__()
        self.enemy = enemy

    def enter(self):
        self.enemy.change_color((0, 200, 0))
        pass

    def execute(self):
        self.enemy.sweep()
    
    def exit(self):
        self.enemy.change_color((0, 125, 0))
        self.enemy.time_in_state = 0.0
        #print("Exiting Sweep State")

class Fleeing(State):
    def __init__(self, enemy):
        super().__init__()
        self.enemy = enemy

    def enter(self):
        self.enemy.change_color((0, 55, 0))
        #print("Entering Fleeing State")
        pass

    def execute(self):
        self.enemy.dynamic_flee(self.enemy.target.pos)
    
    def exit(self):
        self.enemy.change_color((0, 125, 0))
        self.enemy.time_in_state = 0.0
        #print("Exiting Fleeing State")

class FreezeState(State):
    def __init__(self, enemy):
        super().__init__()
        self.enemy = enemy

    def enter(self):
        # print("Entering Freeze State")
        self.enemy.velocity = [0.0, 0.0]

    def execute(self):
        self.enemy.velocity = [0.0, 0.0]

    def exit(self):
        self.enemy.time_in_state = 0.0
        # print("Exiting Freeze State")

class PathFollowingNodeState(State):
    def __init__(self, enemy):
        super().__init__()
        self.enemy = enemy

    def enter(self):
        # print("Entering Path Following Node State")
        self.target_node = self.enemy.get_random_node()
        self.enemy.find_path_to_node(self.target_node)

    def execute(self):
        if self.enemy.reached_final_node():
            # print("reached")
            self.target_node = self.enemy.get_random_node()
            self.enemy.find_path_to_node(self.target_node)
        else:
            if self.enemy.path:
                self.enemy.follow_path_with_seek(self.target_node)

    def exit(self):
        self.enemy.time_in_state = 0.0
        # print("Exiting Path Following Node State")

class FleeFromGuardState(State):
    def __init__(self, enemy):
        super().__init__()
        self.enemy = enemy

    def enter(self):
        # print("Entering Flee From Guard State")
        self.enemy.change_color((125, 0, 0))
        self.farthest_node = self.enemy.graph.get_farthest_node(self.enemy.pos)
        self.enemy.find_path_to_node(self.farthest_node)

    def execute(self):
        if self.enemy.path:
            self.enemy.follow_path_with_seek(self.farthest_node)

    def exit(self):
        self.enemy.change_color((255, 0, 0))
        self.enemy.time_in_state = 0.0
        # print("Exiting Flee From Guard State")

class PanicFromGuardState(State):
    def __init__(self, enemy):
        super().__init__()
        self.enemy = enemy

    def enter(self):
        # print("Entering Flee From Guard State")
        self.enemy.change_color((75, 0, 0))

    def execute(self):
        self.enemy.flee(self.enemy.looking_at_him.pos)

    def exit(self):
        self.enemy.change_color((255, 0, 0))
        self.enemy.time_in_state = 0.0
        # print("Exiting Flee From Guard State")

class VigilantState(State):
    def __init__(self, enemy):
        super().__init__()
        self.enemy = enemy

    def enter(self):
        pass
        # print("Entering Vigilant State")

    def execute(self):
        self.enemy.face(self.enemy.target.pos)

    def exit(self):
        self.enemy.time_in_state = 0.0
        # print("Exiting Vigilant State")

class MimicState(State):
    def __init__(self, enemy):
        super().__init__()
        self.enemy = enemy

    def enter(self):
        self.enemy.change_color((0, 0, 255))
        # print("Entering Mimic State")

    def execute(self):
        self.enemy.velocity_matching(self.enemy.target.velocity)
        self.enemy.face(self.enemy.target.pos)

    def exit(self):
        self.enemy.change_color((0, 0, 125))
        self.enemy.time_in_state = 0.0
        # print("Exiting Mimic State")

class SeekGuardState(State):
    def __init__(self, enemy):
        super().__init__()
        self.enemy = enemy

    def enter(self):
        # print("Entering Seek Guard State")
        shrink_width = self.enemy.rect.width * 8 / 9
        shrink_height = self.enemy.rect.height * 8 / 9
        self.enemy.rect.inflate_ip(-shrink_width, -shrink_height)
        self.enemy.change_color((0, 0, 75))
        closest_enemy = self.enemy.find_closest_enemy_position(self.enemy.enemies,'guard')
        if closest_enemy:
            self.target_node = self.enemy.graph.get_closest_node(closest_enemy)
            self.enemy.find_path_to_node(self.target_node)

    def execute(self):
        if self.enemy.path:
            self.enemy.follow_path_with_seek(self.target_node)

    def exit(self):
        shrink_width = self.enemy.rect.width * 1 / 2
        shrink_height = self.enemy.rect.height * 1 / 2
        self.enemy.rect.inflate_ip(-shrink_width, -shrink_height)
        self.enemy.change_color((0, 0, 125))
        self.enemy.time_in_state = 0.0
        # print("Exiting Seek Guard State")

class SeekThiefState(State):
    def __init__(self, enemy):
        super().__init__()
        self.enemy = enemy

    def enter(self):
        shrink_width = self.enemy.rect.width * 8 / 9
        shrink_height = self.enemy.rect.height * 8 / 9
        self.enemy.rect.inflate_ip(-shrink_width, -shrink_height)
        self.enemy.change_color((0, 125, 125))
        # print("Entering Seek Thief State")
        closest_enemy = self.enemy.find_closest_enemy_position(self.enemy.enemies,'thief')
        if closest_enemy:
            self.target_node = self.enemy.graph.get_closest_node(closest_enemy)
            self.enemy.find_path_to_node(self.target_node)

    def execute(self):
        if self.enemy.path:
            self.enemy.follow_path_with_seek(self.target_node)

    def exit(self):
        shrink_width = self.enemy.rect.width * 1 / 2
        shrink_height = self.enemy.rect.height * 1 / 2
        self.enemy.rect.inflate_ip(-shrink_width, -shrink_height)
        self.enemy.change_color((0, 0, 125))
        self.enemy.time_in_state = 0.0
        # print("Exiting Seek Thief State")
