import pygame
import math
import random
from Graph import *
from StateMachine import Transition, StateMachine
from States import *


# Negro
ENEMY_COLOR = (0, 0, 0)

# Amarillo
COLLISION_COLOR = (255, 165, 0) 


class Enemy(pygame.sprite.Sprite):
    
    def __init__(self, behaviour, pos, graph, state_machine_type):
        super().__init__()
        self.graph = graph
        self.state_machine = StateMachine()
        self.path = []
        self.target_node = None 
        self.time_in_state = 0.0
        self.state_machine_type = state_machine_type

        self.original_image = pygame.Surface([14, 14], pygame.SRCALPHA)
        pygame.draw.polygon(
            self.original_image,
            ENEMY_COLOR,
            [(0, 0), (14, 7), (0, 14)]
        )
        self.image = self.original_image
        self.rect = self.image.get_rect(center=pos)
        self.position_history = []

        # Disminuyo el tamaño del hitbox a 1/7 de su tamaño original
        shrink_width = self.rect.width * 1 / 2
        shrink_height = self.rect.height * 1 / 2
        self.rect.inflate_ip(-shrink_width, -shrink_height)

        # Atributos base para el uso de las funciones
        self.behaviour = behaviour  
        self.pos = list(pos)
        self.orientation = random.uniform(0, 2 * math.pi) 
        self.velocity = [0.0, 0.0]
        self.rotation = 0.0  
        self.acceleration = [0.0, 0.0]
        self.angular_acceleration = 0.0 

        self.looking_at_him = None
                
        # Atributo para wander
        self.wander_orientation = random.uniform(0, 2 * math.pi)

        # Variables para controlar el cambio de color por choque
        self.is_colliding = False
        self.collision_start_time = 0
        self.is_evading_colition = False

        # Destino para el caso de Walls and Obstacle Avoidance
        self.destination = [random.randint(700, 780), random.randint(50, 550)]

        if self.state_machine_type == 1:
            
            # Cambia el color para distinguirlo
            self.change_color((0, 125, 0))

            # Configurar estados
            wandering_state = WanderingState(self)
            seek_state = SeekState(self)
            sweep_state = SweepState(self)
            fleeing_state = Fleeing(self)
            

            # Definir transiciones
            to_seek = Transition(seek_state, lambda: self.can_see_player(self.target.pos, self.screen, self.obstacle_group)and not self.target.buffed)
            to_wander_from_flee = Transition(wandering_state, lambda: not self.can_see_player(self.target.pos, self.screen, self.obstacle_group) and (self.state_machine.current_state == fleeing_state) and (self.time_in_state >= 2.5))
            to_wander_from_sweep = Transition(wandering_state, lambda: not self.can_see_player(self.target.pos, self.screen, self.obstacle_group) and (self.time_in_state >= 2) and (self.state_machine.current_state == sweep_state)) 
            to_wander_from_seek = Transition(wandering_state, lambda: not self.can_see_player(self.target.pos, self.screen, self.obstacle_group) and (self.time_in_state >= 2) and(self.state_machine.current_state == seek_state))
            to_sweep = Transition(sweep_state, lambda: self.time_in_state >= 5 and self.state_machine.current_state == wandering_state)
            to_flee = Transition(fleeing_state, lambda: self.can_see_player(self.target.pos, self.screen, self.obstacle_group) and self.target.buffed)

            wandering_state.add_transition(to_seek)
            wandering_state.add_transition(to_flee)
            wandering_state.add_transition(to_sweep)
            seek_state.add_transition(to_wander_from_seek)
            seek_state.add_transition(to_seek)
            seek_state.add_transition(to_flee)
            fleeing_state.add_transition(to_wander_from_flee)
            fleeing_state.add_transition(to_seek)
            sweep_state.add_transition(to_wander_from_sweep)
            sweep_state.add_transition(to_flee)
            sweep_state.add_transition(to_seek)

            # Estado inicial
            self.state_machine.change_state(wandering_state)

        elif self.state_machine_type == 2:

            # Cambia el color para distinguirlo
            self.change_color((255, 0, 0))

            shrink_width = self.rect.width * 8 / 9
            shrink_height = self.rect.height * 8 / 9
            self.rect.inflate_ip(-shrink_width, -shrink_height)

            # Configurar estado de seguimiento de nodo
            path_following_state = PathFollowingNodeState(self)
            freeze_state = FreezeState(self)
            flee_of_guard_state = FleeFromGuardState(self)
            panic_state = PanicFromGuardState(self)

            # Definir transiciones
            to_freeze = Transition(freeze_state, lambda: self.can_see_player(self.target.pos, self.screen, self.obstacle_group) and self.target.buffed)
            to_pathfinding_from_freeze = Transition(path_following_state, lambda:  not self.can_see_player(self.target.pos, self.screen, self.obstacle_group)
                                                     and (self.state_machine.current_state == freeze_state) and (self.time_in_state >= 2))
            to_pathfinding_from_flee_of_guard = Transition(path_following_state, lambda: any(not self.can_see_player(enemy.pos, self.screen, self.obstacle_group) for enemy in self.enemies if enemy.state_machine_type == 1)
                                                     and (self.state_machine.current_state == flee_of_guard_state) and (self.time_in_state >= 3.5))
            to_pathfinding_from_panic = Transition(path_following_state, lambda: any(not self.can_see_player(enemy.pos, self.screen, self.obstacle_group) for enemy in self.enemies if enemy.state_machine_type == 1)
                                                     and (self.state_machine.current_state == panic_state) and (self.time_in_state >= 3.5))
            to_flee_of_guard = Transition(flee_of_guard_state, lambda: any(self.can_see_player(enemy.pos, self.screen, self.obstacle_group) for enemy in self.enemies if enemy.state_machine_type == 1)
                                          and any(not self.who_is_looking_at_him(enemy, self.screen, self.obstacle_group) for enemy in self.enemies if enemy.state_machine_type == 1))
            to_panic_from_guard = Transition(panic_state, lambda: any(self.who_is_looking_at_him(enemy, self.screen, self.obstacle_group)  for enemy in self.enemies if enemy.state_machine_type == 1) 
                                             and any(self.can_see_player(enemy.pos, self.screen, self.obstacle_group) for enemy in self.enemies if enemy.state_machine_type == 1))
            
            path_following_state.add_transition(to_freeze)
            path_following_state.add_transition(to_flee_of_guard)
            path_following_state.add_transition(to_panic_from_guard)
            flee_of_guard_state.add_transition(to_panic_from_guard)
            flee_of_guard_state.add_transition(to_pathfinding_from_flee_of_guard)
            flee_of_guard_state.add_transition(to_freeze)
            panic_state.add_transition(to_freeze)
            panic_state.add_transition(to_flee_of_guard)
            panic_state.add_transition(to_pathfinding_from_panic)
            freeze_state.add_transition(to_pathfinding_from_freeze)

            self.state_machine.change_state(path_following_state)
        
        elif self.state_machine_type == 3:

            # Cambia el color para distinguirlo
            self.change_color((0, 0, 125))

            # Configurar estados
            vigilant_state = VigilantState(self)
            mimic_state = MimicState(self)
            seek_guard_state = SeekGuardState(self)
            seek_thief_state = SeekThiefState(self)

            # Definir transiciones
            to_mimic = Transition(mimic_state, lambda: self.can_see_player(self.target.pos, self.screen, self.obstacle_group))
            to_vigilant_from_mimic = Transition(vigilant_state, lambda: not self.can_see_player(self.target.pos, self.screen, self.obstacle_group) and self.time_in_state >= 5)
            to_seek_guard = Transition(seek_guard_state, lambda: any(self.can_see_player(enemy.pos, self.screen, self.obstacle_group) for enemy in self.enemies if enemy.state_machine_type == 2) and not self.target.buffed)   
            to_seek_thief = Transition(seek_thief_state, lambda: self.target.buffed)
            to_vigilant_from_seek_guard = Transition(vigilant_state, lambda: self.state_machine.current_state == seek_guard_state and len(self.path) < 1)

            # Agregar transiciones para cada estado
            vigilant_state.add_transition(to_mimic)
            vigilant_state.add_transition(to_seek_guard)
            vigilant_state.add_transition(to_seek_thief)
            mimic_state.add_transition(to_vigilant_from_mimic)
            mimic_state.add_transition(to_seek_guard)
            mimic_state.add_transition(to_seek_thief)
            seek_guard_state.add_transition(to_vigilant_from_seek_guard)
            seek_thief_state.add_transition(Transition(vigilant_state, lambda: True))

            # Estado inicial
            self.state_machine.change_state(vigilant_state)
    
    def draw_hitbox(self, surface):
        pygame.draw.rect(surface, COLLISION_COLOR, self.rect, 1)
    
    
    def update(self, tDelta, player, screen, obstacles_group, enemies):
        self.enemies = enemies
        self.time_in_state += tDelta
        self.tDelta = tDelta
        self.screen = screen 
        self.target = player
        self.obstacle_group = obstacles_group
        self.state_machine.update()

    def find_closest_enemy_position(self, enemies, target):
        closest_enemy = None
        min_distance = float('inf')
        
        for enemy in enemies:
            if target == 'guard':
                if enemy is not self and enemy.state_machine_type == 1:
                    distance = math.hypot(enemy.pos[0] - self.pos[0], enemy.pos[1] - self.pos[1])
                    if distance < min_distance:
                        min_distance = distance
                        closest_enemy = enemy
            if target == 'thief':
                if enemy is not self and enemy.state_machine_type == 2:
                    distance = math.hypot(enemy.pos[0] - self.pos[0], enemy.pos[1] - self.pos[1])
                    if distance < min_distance:
                        min_distance = distance
                        closest_enemy = enemy
        
        return closest_enemy.pos if closest_enemy else None
    
    def can_see_player(self, player_pos, screen, obstacles_group):

        # Distancia entre el enemigo y el jugador
        distance = math.hypot(player_pos[0] - self.pos[0], player_pos[1] - self.pos[1])

        if distance < 200:
            direction_to_player = math.atan2(player_pos[1] - self.pos[1], player_pos[0] - self.pos[0])
            
            angle_diff = abs(self.map_to_range(direction_to_player - self.orientation))
            
            if angle_diff < math.pi / 4:
                line_of_sight = pygame.draw.line(screen, (255, 0, 0), self.rect.center, player_pos, 1)
                for obstacle in obstacles_group:
                    if line_of_sight.colliderect(obstacle.rect):
                        return False
                return True
        return False
    
    def who_is_looking_at_him(self, enemy, screen, obstacles_group):

        distance = math.hypot(enemy.pos[0] - self.pos[0], enemy.pos[1] - self.pos[1])

        if distance < 150:

            direction_to_player = math.atan2(enemy.pos[1] - self.pos[1], enemy.pos[0] - self.pos[0])
            
            angle_diff = abs(self.map_to_range(direction_to_player - self.orientation))
            
            if angle_diff < math.pi / 4:
                line_of_sight = pygame.draw.line(screen, (255, 0, 0), self.rect.center, enemy.pos, 1)
                for obstacle in obstacles_group:
                    if line_of_sight.colliderect(obstacle.rect):
                        self.looking_at_him == None
                        return False
                    
                self.looking_at_him = enemy
                return True
        self.looking_at_him = None
        return False

    def find_path_to_player(self, player_node):
        start_node = self.graph.get_closest_node(self.pos)
        if start_node and player_node:
            heuristic = Heuristic(player_node)
            self.path = pathfindAStar(self.graph, start_node, player_node, heuristic)
            if self.path:
                self.target_node = self.path.pop(0)

    def follow_path_with_seek(self, player_node):

        if self.target_node is None or player_node != self.path[-1] if self.path else True:
            self.find_path_to_player(player_node)

        if self.target_node:
            self.seek((self.target_node.x, self.target_node.y))

            if math.hypot(self.pos[0] - self.target_node.x, self.pos[1] - self.target_node.y) < 5:
                if self.path:
                    self.target_node = self.path.pop(0)
                else:
                    self.target_node = None

    def get_random_node(self):
        return random.choice(self.graph.nodes)

    def reached_final_node(self):
        if len(self.path)<=0:
            return True
        distance = math.hypot(self.pos[0] - self.path[-1].x, self.pos[1] - self.path[-1].y)
        return distance <= 1 

    def find_path_to_node(self, target_node):
        start_node = self.graph.get_closest_node(self.pos)
        if start_node and target_node:
            heuristic = Heuristic(target_node)
            self.path = pathfindAStar(self.graph, start_node, target_node, heuristic)
            if self.path:
                self.target_node = self.path.pop(0) 
        else:
            self.target_node = None

    # Funcion que realiza los movimientos segun los valores de los atributos base.
    def move(self, enemies, screensize, tDelta, player, obstacles_group):
        if self.behaviour == 0:
            self.kinematic_wandering(tDelta)
        elif self.behaviour == 1:
            self.kinematic_arrive(player.pos)
        elif self.behaviour == 2:
            self.seek(player.pos)
        elif self.behaviour == 3:
            self.flee(player.pos)
        elif self.behaviour == 4:
            self.dynamic_flee(player.pos)
        elif self.behaviour == 5:
            self.dynamic_seek(player.pos)
        elif self.behaviour == 6:
            self.dynamic_arrive(player.pos)
        elif self.behaviour == 7:
            self.align(player.orientation)
        elif self.behaviour == 8:
            self.velocity_matching(player.velocity)
        elif self.behaviour == 9:
            self.face(player.pos)
        elif self.behaviour == 10:
            self.pursue(player)
        elif self.behaviour == 11:
            self.evade(player)
        elif self.behaviour == 12:
            self.dynamic_wander()
        elif self.behaviour == 13:
            self.collision_avoidance(enemies)
        elif self.behaviour == 14:
            self.wall_and_obstacle_avoidance(obstacles_group)
        elif self.behaviour == 15:
            self.separation(enemies, player.velocity)
        elif self.behaviour == 16:
            self.pursue_enemy(enemies)
        elif self.behaviour == 17:
            self.evade_enemy(enemies)
        elif self.behaviour == 18:
            pass

        
        # Check Colision, si haym se cambia el color a amarillo
        # for sprite in enemies:
        #     if sprite is not self:
        #         if pygame.sprite.collide_rect(self, sprite):
        #             self.is_colliding = True
        #             self.collision_start_time = pygame.time.get_ticks()
        #             self.change_color(COLLISION_COLOR)

        # # Si el enemigo esta colisionando, cambiar a negro luego de 1 segundo
        # if self.is_colliding:
        #     current_time = pygame.time.get_ticks()
        #     if current_time - self.collision_start_time >= 1000:
        #         self.is_colliding = False
        #         self.change_color(ENEMY_COLOR)

        # Codigo que evita colisiones, devolviendo al personaje a su posicion unos frames antes
        if len(self.position_history) >= 25:
            self.position_history.pop(0)
        self.position_history.append(self.pos[:])

        if pygame.sprite.spritecollide(self, obstacles_group, False):

            if len(self.position_history) >= 15:
                self.pos = self.position_history[0]
            else:
                self.pos = self.position_history[-1]
            self.rect.center = self.pos
            self.position_history.clear()

        newPos = (self.pos[0] + self.velocity[0] * tDelta,self.pos[1] + self.velocity[1] * tDelta)

        # Limites de la pantalla
        self.pos[0] = max(0, min(screensize[0], newPos[0]))
        self.pos[1] = max(0, min(screensize[1], newPos[1]))

        # Actualizar Velocidad
        self.velocity[0] += self.acceleration[0] * tDelta
        self.velocity[1] += self.acceleration[1] * tDelta

        # Limitar Velocidad
        self.limit_velocity()

        # Actualizar rotacion debido a angular
        self.rotation += self.angular_acceleration * tDelta

        # Limitar rotacion
        self.limit_rotation()

        # Cambiar orientacion segun la rotacion
        self.orientation += self.rotation * tDelta
        self.orientation %= (2 * math.pi)

        if not self.is_evading_colition:
            self.acceleration = [0.0, 0.0]
            self.angular_acceleration = 0.0
        
        # Actualizar posicion del centro (rectangulo)
        self.rect.center = self.pos
    
    # Funcion para cambiar el color del character
    def change_color(self, color):
        
        self.current_color = color
        self.original_image.fill((0, 0, 0, 0))
        pygame.draw.polygon(
            self.original_image,
            self.current_color,
            [(0, 0), (14, 7), (0, 14)]
        )
        self.image = self.original_image

    # Implementacion de map to range, cambia angulos a radianes
    def map_to_range(self, angle:float):
        return ((angle + math.pi) % (2 * math.pi) - math.pi)

    # Funcion para limitar velocidad
    def limit_velocity(self):
        max_speed = 300.0
        speed = math.hypot(self.velocity[0], self.velocity[1])
        if speed > max_speed:
            scale = max_speed / speed
            self.velocity[0] *= scale
            self.velocity[1] *= scale

    # Funcion para limitar rotacion
    def limit_rotation(self):
        max_rotation_speed = 5.0
        if abs(self.rotation) > max_rotation_speed:
            self.rotation = max_rotation_speed * (self.rotation / abs(self.rotation))

    def sweep(self):
        self.velocity = [0.0, 0.0]
        rotation_speed = 0.02
        self.orientation += rotation_speed

    # Implementacion de Kinematic Wandering
    def kinematic_wandering(self, tDelta):

        max_speed = 30.0
        max_rotation = 10.0

        # Calcular velocidad en base a la orientacion (sacamos el vector con seno y coseno)
        self.velocity[0] = max_speed * math.cos(self.orientation)
        self.velocity[1] = max_speed * math.sin(self.orientation)

        # Deberia ser entre -1 y 1 pero no rotaba lo suficiente. Dado que max rotation es un valor pequeño, lo obtendre por este valor.
        random_rotation = random.uniform(-max_rotation, max_rotation)

        # Actualizo orientacion 
        self.orientation += random_rotation * tDelta

        # Limito la rotacion a estar dentro de 2pi radianes
        self.orientation %= (2 * math.pi)

    # Implementacion de Kinematic Arrive (Arrive sin aceleracion)
    def kinematic_arrive(self, target_pos):

        max_speed = 200.0
        radius = 200.0

        # Calculo direccion
        direction = [target_pos[0] - self.pos[0], target_pos[1] - self.pos[1]]
        distance = math.hypot(direction[0], direction[1])

        if distance < 10.0:
            self.velocity = [0.0, 0.0]
            return

        # Normalizacion del vector distancia
        direction[0] /= distance
        direction[1] /= distance

        # Calcular la velocidad objetivo
        if distance < radius:
            target_speed = max_speed * (distance / radius)
        else:
            target_speed = max_speed

        # Establecer velocidad objetivo en la direccion deseada
        self.velocity[0] = direction[0] * target_speed
        self.velocity[1] = direction[1] * target_speed

        # Actualizamos orientacion para matchear velocidad
        self.orientation = math.atan2(self.velocity[1], self.velocity[0])
    
    # Implementacion de Kinematic Seek
    def seek(self, target_pos):
    
        max_speed = 125.0
        
        # Calcular direccion hacia el objetivo
        direction = [target_pos[0] - self.pos[0], target_pos[1] - self.pos[1]]
        
        # Calcular distancia al objetivo
        distance = math.hypot(direction[0], direction[1])
        
        if distance == 0:
            self.velocity = [0.0, 0.0]
        else:
            # Normalizar direccion
            direction[0] /= distance
            direction[1] /= distance
            
            # Establecer velocidad máxima hacia el objetivo
            self.velocity[0] = direction[0] * max_speed
            self.velocity[1] = direction[1] * max_speed
            
            # Actualizar orientacion en direccion de movimiento
            self.orientation = math.atan2(self.velocity[1], self.velocity[0])

    # Implementacion de Kinematic Flee
    def flee(self, target_pos):
        
        max_speed = 50.0
        
        # Calcular direccion hacia el objetivo
        direction = [target_pos[0] - self.pos[0], target_pos[1] - self.pos[1]]
        
        # Calcular distancia al objetivo
        distance = math.hypot(direction[0], direction[1])
        
        if distance >= 150:
            self.velocity = [0.0, 0.0]
        else:
            # Normalizar direccion
            direction[0] /= distance
            direction[1] /= distance
            
            # Invertir direccion para huir del objetivo
            self.velocity[0] = -(direction[0] * max_speed)
            self.velocity[1] = -(direction[1] * max_speed)
            
            # Actualizar orientacion en direccion de movimiento
            self.orientation = math.atan2(self.velocity[1], self.velocity[0])

    # Implementación de Variable Matching Seek
    def dynamic_seek(self, target_pos):
        max_acceleration = 300.0
        
        # Calcular direccion hacia el objetivo
        direction = [target_pos[0] - self.pos[0], target_pos[1] - self.pos[1]]
        
        # Calcular la magnitud de la direccion
        distance = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
        
        if distance > 0:
            # Normalizar el vector direccion
            direction[0] /= distance
            direction[1] /= distance
            
            # Escalar el vector con la aceleracion maxima
            self.acceleration[0] = direction[0] * max_acceleration
            self.acceleration[1] = direction[1] * max_acceleration
        else:
            # Detenerse si esta en el objetivo
            self.velocity[0] = 0
            self.velocity[1] = 0
            self.acceleration[0] = 0
            self.acceleration[1] = 0
        
        self.angular_acceleration = 0.0

    # Implementacion de Variable Mathcing Flee
    def dynamic_flee(self, target_pos, max_distance = 250):
        max_acceleration = 300.0
            
        # Calcular direccion hacia el objetivo
        direction = [target_pos[0] - self.pos[0], target_pos[1] - self.pos[1]]
        
        # Calcular la magnitud de la direccion
        distance = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
        
        if distance > 0 and distance < max_distance:
            # Normalizar el vector direccion
            direction[0] /= distance
            direction[1] /= distance
            
            # Escalar el vector con la aceleracion maxima en direccion contraria
            self.acceleration[0] = -direction[0] * max_acceleration
            self.acceleration[1] = -direction[1] * max_acceleration

        else:
            # Detenerse si esta en el objetivo
            self.velocity[0] = 0
            self.velocity[1] = 0
            self.acceleration[0] = 0
            self.acceleration[1] = 0
        
        self.angular_acceleration = 0.0

    # Implementacion de Variable Matching Arrive
    def dynamic_arrive(self, target, target_radius = 30.0, slow_radius = 300.0):
        
        time_to_target = 0.1
        max_speed = 200.0
        max_acceleration = 80.0
        
        # Calcular direccion hacia el objetivo
        direction = [target[0] - self.pos[0], target[1] - self.pos[1]]
        
        # Calcular distancia al objetivo
        distance = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
        
        if distance < target_radius:
            # Detenerse si esta en el radio objetivo
            self.velocity[0] = 0
            self.velocity[1] = 0
            self.acceleration[0] = 0
            self.acceleration[1] = 0
        
        # Normalizar direccion
        direction[0] /= distance
        direction[1] /= distance
        
        if distance > slow_radius:
            # Moverse a máxima velocidad fuera del radio de frenado
            target_speed = max_speed
        else:
            # Reducir velocidad proporcionalmente dentro del radio de frenado
            target_speed = max_speed * (distance / slow_radius)
        
        # Calcular velocidad objetivo
        target_velocity = [direction[0] * target_speed, direction[1] * target_speed]
        
        # Calcular aceleracion necesaria
        self.acceleration[0] = (target_velocity[0] - self.velocity[0]) / time_to_target
        self.acceleration[1] = (target_velocity[1] - self.velocity[1]) / time_to_target
        
        # Limitar aceleracion al valor maximo
        accel_magnitude = math.sqrt(self.acceleration[0] ** 2 + self.acceleration[1] ** 2)
        if accel_magnitude > max_acceleration:
            scale = max_acceleration / accel_magnitude
            self.acceleration[0] *= scale
            self.acceleration[1] *= scale

    # Implementacion de Align
    def align(self, target_orientation):
        
        time_to_target = 0.1
        max_rotation = 5.0
        max_angular_acceleration = 50.0
        target_radius = 0.01
        slow_radius = 0.5
        
        # Calcular diferencia de rotacion
        rotation_dif = target_orientation - self.orientation
        
        # Mapear el ángulo a rango -pi a pi
        rotation_dif = self.map_to_range(rotation_dif)
        
        rotation_size = abs(rotation_dif)
        
        if rotation_size < target_radius:
            # Detenerse si ya esta alineado
            self.rotation = 0
            self.angular_acceleration = 0
        
        if rotation_size > slow_radius:
            # Rotar a máxima velocidad fuera del radio lento
            target_rotation = max_rotation
        else:
            # Rotar proporcionalmente dentro del radio lento
            target_rotation = max_rotation * (rotation_size / slow_radius)
        
        # Direccion de la rotacion
        target_rotation *= rotation_dif / rotation_size
        
        # Calcular aceleracion angular necesaria
        self.angular_acceleration = (target_rotation - self.rotation) / time_to_target
        
        # Limitar aceleracion angular
        angular_acc_size = abs(self.angular_acceleration)
        if angular_acc_size > max_angular_acceleration:
            self.angular_acceleration *= max_angular_acceleration / angular_acc_size

    # Implementacion de Velocity Matching
    def velocity_matching(self, target_velocity):
        
        time_to_target = 0.1
        max_acceleration = 100.0
        
        # Calcular diferencia de velocidad
        velocity_difference = [target_velocity[0] - self.velocity[0],target_velocity[1] - self.velocity[1]]
        
        # Calcular aceleracion necesaria para igualar velocidad
        self.acceleration[0] = velocity_difference[0] / time_to_target
        self.acceleration[1] = velocity_difference[1] / time_to_target
        
        # Limitar aceleracion al valor maximo
        accel_magnitude = math.sqrt(self.acceleration[0] ** 2 + self.acceleration[1] ** 2)
        if accel_magnitude > max_acceleration:
            scale = max_acceleration / accel_magnitude
            self.acceleration[0] *= scale
            self.acceleration[1] *= scale

    # Implementacion de Face
    def face(self, target_position):
        
        # Calcular direccion hacia el objetivo
        direction = [target_position[0] - self.pos[0], target_position[1] - self.pos[1]]
        
        # Calcular orientacion 
        orientation = math.atan2(direction[1], direction[0])
        
        # Alinearse a la orientacion 
        self.align(orientation)

    # Look where you are going
    def look_where_you_are_going(self):
        
        if math.hypot(self.velocity[0], self.velocity[1]) > 0:
            # Ajustar orientacion segun la direccion de la velocidad
            self.orientation = math.atan2(self.velocity[1], self.velocity[0])

    # Implementacion de Pursue
    def pursue(self, target):
        
        prediction_time = 3.0
        
        # Calcular direccion hacia el objetivo
        direction = [target.pos[0] - self.pos[0], target.pos[1] - self.pos[1]]
        
        # Calcular distancia al objetivo
        distance = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
        
        # Calcular velocidad del personaje
        speed = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
        
        if speed <= distance / prediction_time:
            pass
        else:
            # Ajustar tiempo de predicción segun la velocidad
            prediction_time = distance / speed
        
        # Calcular posicion objetivo futura
        target_pos = [target.pos[0] + (target.velocity[0] * prediction_time), target.pos[1] + (target.velocity[1] * prediction_time)]
        
        # Buscar la posicion predicha
        self.dynamic_seek(target_pos)
        
        self.look_where_you_are_going()

    # Implementacion de Evade
    def evade(self, target, max_distance = 500):
    
        prediction_time = 3.0
        
        # Calcular direccion hacia el objetivo
        direction = [target.pos[0] - self.pos[0], target.pos[1] - self.pos[1]]
        
        # Calcular distancia al objetivo
        distance = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
        
        # Calcular velocidad del personaje
        speed = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
        
        if speed <= distance / prediction_time:
            pass
        else:
            # Ajustar tiempo de predicción segun la velocidad
            prediction_time = distance / speed
        
        # Calcular posicion futura del objetivo
        target_pos = [target.pos[0] + (target.velocity[0] * prediction_time), target.pos[1] + (target.velocity[1] * prediction_time)]
        
        # Huir de la posicion predicha
        self.dynamic_flee(target_pos, max_distance)
        
        # Mirar hacia donde va
        self.look_where_you_are_going()

    # Implementacion para Pursue and Evade de IA
    def pursue_enemy(self,enemies):
        for other in enemies:
            if other is not self:
                self.pursue(other)
    def evade_enemy(self,enemies):
        for other in enemies:
            if other is not self:
                self.evade(other)

    # Implementacion de Dynamic Wander
    def dynamic_wander(self):
        
        wanderOffset = 100.0
        wanderRadius = 30.0
        wanderRate = 0.5
        max_acc = 30.0
        max_speed = 40.0
        
        # Actualizar orientacion de wander con un valor random
        self.wander_orientation += random.uniform(-1.0, 1.0) * wanderRate
        
        # Calcular orientacion combinada
        target_orientation = self.wander_orientation + self.orientation
        
        # Calcular centro del ciruclo de wander
        target = [self.pos[0] + wanderOffset * math.cos(self.orientation), self.pos[1] + wanderOffset * math.sin(self.orientation)]
        
        # Calcular posicion objetivo en el borde del ciruclo
        target[0] += wanderRadius * math.cos(target_orientation)
        target[1] += wanderRadius * math.sin(target_orientation)
        
        # Ajustar orientacion hacia el objetivo
        self.face(target)
        
        # Aplicar aceleracion hacia el objetivo
        self.acceleration[0] = max_acc * math.cos(self.orientation)
        self.acceleration[1] = max_acc * math.sin(self.orientation)
        
        # Limitar velocidad
        speed = math.hypot(self.velocity[0], self.velocity[1])
        if speed > max_speed:
            scale = max_speed / speed
            self.velocity[0] *= scale
            self.velocity[1] *= scale

        # Limitar aceleracion angular
        angular_acc_size = abs(self.angular_acceleration)
        if angular_acc_size > 3.0:
            self.angular_acceleration *= 3.0 / angular_acc_size

    # Implementacion de Collision Avoidance
    def collision_avoidance(self, targets):

        max_acceleration = 40.0  
        radius = 40.0
        shortest_time = float('inf')
        first_target = None
        
        # Recorrer los objetivos para calcular colisiones
        for target in targets:
            relative_pos = [target.pos[0] - self.pos[0], target.pos[1] - self.pos[1]]
            relative_vel = [target.velocity[0] - self.velocity[0], target.velocity[1] - self.velocity[1]]
            
            relative_speed = math.hypot(relative_vel[0], relative_vel[1])
            
            if relative_speed == 0:
                continue
            
            # Calcular tiempo hasta la colision
            time_to_collision = (relative_pos[0] * relative_vel[0] + relative_pos[1] * relative_vel[1]) / (relative_speed ** 2)
            
            if time_to_collision <= 0:
                continue
            
            # Calcular la separacion minima
            distance = math.hypot(relative_pos[0], relative_pos[1])
            min_separation = distance - relative_speed * time_to_collision
            
            if min_separation > 2 * radius:
                continue
            
            # Encontrar la colision mas cercana
            if time_to_collision < shortest_time:
                shortest_time = time_to_collision
                first_target = target
                first_min_separation = min_separation
                first_distance = distance
                first_relative_pos = relative_pos
                first_relative_vel = relative_vel
        
        # Si no se encuentra colision, continuar con wander
        if not first_target:
            self.dynamic_wander()
            return
        
        if first_min_separation <= 0 or first_distance < 2 * radius:
            relative_pos = [first_target.pos[0] - self.pos[0], first_target.pos[1] - self.pos[1]]
        else:
            relative_pos = [first_relative_pos[0] + (first_relative_vel[0] * shortest_time), first_relative_pos[1] + (first_relative_vel[1] * shortest_time)] 

        
        # Evitar colision ajustando la aceleracion
        self.is_evading_colition = True
        distance = math.hypot(relative_pos[0], relative_pos[1])

        if distance > 0:
            relative_pos[0] /= distance
            relative_pos[1] /= distance
        
        # Conforme se acercan los personajes la fuerza de separacion va a ir aumentando (evitando que salgan disparados de esta manera)
        if distance < radius:
            dev_strenght = max_acceleration * (radius - distance) / radius
        else:
            dev_strenght = max_acceleration
        
        # Aplicar aceleración de evasión
        self.acceleration[0] -= relative_pos[0] * dev_strenght
        self.acceleration[1] -= relative_pos[1] * dev_strenght

        self.angular_acceleration = 0.0

        # Limitar la aceleracion evitar alejamiento muy subito
        accel_magnitude = math.sqrt(self.acceleration[0] ** 2 + self.acceleration[1] ** 2)
        if accel_magnitude > max_acceleration:
            scale = max_acceleration / accel_magnitude
            self.acceleration[0] *= scale
            self.acceleration[1] *= scale

        # Si el personaje esta mas lo suficientemente lejos del enemigo, resumir wander.
        if distance > radius * 2:
            self.dynamic_wander()
    
    # Implementacion de Wall and Obstacle Avoidance
    def wall_and_obstacle_avoidance(self, obstacles_group):

        lookahead=20
        avoid_distance=10
        max_acceleration=10.0
        
        # Calcular rayo de colision
        ray = [self.velocity[0], self.velocity[1]]
        ray_magnitude = math.sqrt(ray[0] ** 2 + ray[1] ** 2)
        
        if ray_magnitude > 0:
            ray[0] /= ray_magnitude
            ray[1] /= ray_magnitude
        
        ray[0] *= lookahead
        ray[1] *= lookahead
        
        future_position = [self.pos[0] + ray[0], self.pos[1] + ray[1]]
        
        collision = None
        
        # Buscar colision con obstaculos
        for obstacle in obstacles_group:
            if obstacle.rect.collidepoint(future_position):
                collision = obstacle
                break
        
        if not collision:
            # Si no hay colision, buscar destino original
            self.seek(self.destination)
            return
        
        # Crear un objetivo para evitar la colision
        collision_pos = collision.rect.center
        collision_normal = [self.pos[0] - collision_pos[0], self.pos[1] - collision_pos[1]]
        collision_normal_magnitude = math.sqrt(collision_normal[0] ** 2 + collision_normal[1] ** 2)
        
        if collision_normal_magnitude > 0:
            collision_normal[0] /= collision_normal_magnitude
            collision_normal[1] /= collision_normal_magnitude
        
        # Crear nuevo objetivo para evitar el obstáculo
        target = [self.pos[0] + collision_normal[0] * avoid_distance, self.pos[1] + collision_normal[1] * avoid_distance]
        
        # Buscar el nuevo objetivo suavemente
        self.seek(target)
        
        # Limitar la aceleracion
        accel_magnitude = math.sqrt(self.acceleration[0] ** 2 + self.acceleration[1] ** 2)
        if accel_magnitude > max_acceleration:
            scale = max_acceleration / accel_magnitude
            self.acceleration[0] *= scale
            self.acceleration[1] *= scale

    # Implementacion de Separation para Velocity Matching
    def separation(self, enemies, player_velocity):
        
        # Se llama a velocity matching
        self.velocity_matching(player_velocity)

        separation_radius=50.0 
        max_acceleration=80.0
        linear_acceleration = [0.0, 0.0]
        threshold = separation_radius 
        max_acc = max_acceleration     

        # Para todos los enemigos que no son el evaluado (todos se evaluan en cada instancia de enemy)
        for other in enemies:
            if other is not self:

                # Calcular direccion hacia el otro enemigo
                direction = [self.pos[0] - other.pos[0], self.pos[1] - other.pos[1]]
                distance = math.sqrt(direction[0] ** 2 + direction[1] ** 2)

                # Aplicar fuerza de separacion
                if distance < threshold and distance > 0:
                    strength = max_acc * (threshold - distance) / threshold

                    # Normalizar la direccion
                    direction[0] /= distance
                    direction[1] /= distance

                    # Agregar la fuerza de separación a la aceleracion lineal
                    linear_acceleration[0] += strength * direction[0]
                    linear_acceleration[1] += strength * direction[1]

        # Aplicar la aceleracion calculada al enemigo
        self.acceleration[0] += linear_acceleration[0]
        self.acceleration[1] += linear_acceleration[1]

    # Renderizado del enemigo
    def render(self, surface):
        
        # Rotar imagen segun la orientacion
        rotated_image = pygame.transform.rotate(self.original_image, -math.degrees(self.orientation))
        new_rect = rotated_image.get_rect(center=self.rect.center)
        surface.blit(rotated_image, new_rect.topleft)