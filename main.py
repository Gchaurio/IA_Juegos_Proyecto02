import pygame
import random
import math
from Player import Player
from Enemy import Enemy
from Graph import Graph

pygame.init()
size = (1600, 1200)
BGCOLOR = (255, 255, 255)
COLLISION_COLOR = (255, 165, 0) 
screen = pygame.display.set_mode(size, pygame.RESIZABLE)
modeFont = pygame.font.Font("fonts/UpheavalPro.ttf", 30)
pygame.display.set_caption("IA Testing")

done = False
player_char = pygame.sprite.GroupSingle(Player(screen.get_size()))
enemies = pygame.sprite.Group()
score = 0
clock = pygame.time.Clock()
behaviour_list = ['Kinematic Wandering', 'Kinematic Arrive', 'Kinematic Seek', 'Kinematic Flee', 
                  'Dynamic Flee', 'Dynamic Seek', 'Dynamic Arrive', 'Align', 'Velocity Matching', 
                  'Face', 'Pursue', 'Evade', 'Dynamic Wander', 'Colition Avoidance', 'Obstacle and Wall Avoidance', 'Separation', 'Pursue While Avoid'
                  ,'Pursue and Avoid']

obstacles = pygame.sprite.Group()

tile_size = 25 

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill((150, 150, 150)) 
        self.rect = self.image.get_rect(topleft=(x, y))
        # self.rect.inflate_ip(-self.rect.width // 20, -self.rect.height // 20)

    def draw_hitbox(self, surface):
        pygame.draw.rect(surface, COLLISION_COLOR, self.rect, 1)

def move_entities(player_char, enemies, obstacles_group, timeDelta, player_node):
    score = 0
    player_char.sprite.move(screen.get_size(), timeDelta, obstacles_group)

    # Verificar colisiones entre el jugador y los obstaculos
    if pygame.sprite.spritecollide(player_char.sprite, obstacles_group, False):
        player_char.sprite.velocity[0] = 0 
        player_char.sprite.velocity[1] = 0

    for enemy in enemies:
        # enemy.move(enemies, screen.get_size(), timeDelta, player_char.sprite, obstacles_group)
        # enemy.follow_path_with_seek(timeDelta, player_node)  # Seguir el camino hacia el jugador
        enemy.update(timeDelta, player_char.sprite, screen, obstacles_group, enemies)
        enemy.move(enemies, screen.get_size(), timeDelta, player_char.sprite, obstacles_group)
        
        # Verificar colisiones entre enemigos y obstaculos
        if pygame.sprite.spritecollide(enemy, obstacles_group, False):
            enemy.velocity[0] = 0
            enemy.velocity[1] = 0
    
    return score

def render_entities(player_char, enemies):
    player_char.sprite.render(screen)
    for enemy in enemies:
        enemy.render(screen)

def clear_enemies(enemies):
    for sprite in enemies:
        sprite.kill()

def create_wall_borders(obstacles_group, screensize):
    wall_thickness = 20
    # Pared superior
    obstacles_group.add(Obstacle(0, 0, screensize[0], wall_thickness))
    # Pared inferior
    obstacles_group.add(Obstacle(0, screensize[1] - wall_thickness, screensize[0], wall_thickness))
    # Pared izquierda
    obstacles_group.add(Obstacle(0, 0, wall_thickness, screensize[1]))
    # Pared derecha
    obstacles_group.add(Obstacle(screensize[0] - wall_thickness, 0, wall_thickness, screensize[1]))

# Funcion para crear obstaculos cuadrados de diferentes tamaños y posiciones aleatorias
def create_obstacles(obstacles_group):
    for _ in range(10):
        width = random.randint(50, 100)
        height = random.randint(50, 100)
        x = random.randint(0, size[0] - width)
        y = random.randint(0, size[1] - height)
        obstacle = Obstacle(x, y, width, height)
        obstacles_group.add(obstacle)

def render_obstacles(obstacles_group):
    for obstacle in obstacles_group:
        screen.blit(obstacle.image, obstacle.rect)

def change_mode(enemies, behaviour):

    clear_enemies(enemies)

    behaviour = (behaviour + 1) % len(behaviour_list)
    
    return behaviour


def process_keys(keys, player_char):

    speed = 200.0 
    rotation_speed = 3.0  

    player_char.sprite.velocity[0] = 0
    player_char.sprite.velocity[1] = 0
    player_char.sprite.rotation = 0

    if keys[pygame.K_w]:
        player_char.sprite.velocity[0] = math.cos(player_char.sprite.orientation) * speed
        player_char.sprite.velocity[1] = math.sin(player_char.sprite.orientation) * speed
    if keys[pygame.K_s]:
        player_char.sprite.velocity[0] = -math.cos(player_char.sprite.orientation) * speed
        player_char.sprite.velocity[1] = -math.sin(player_char.sprite.orientation) * speed
    if keys[pygame.K_a]:
        player_char.sprite.rotation = -rotation_speed
    if keys[pygame.K_d]:
        player_char.sprite.rotation = rotation_speed

def spawn_enemy(enemies, screensize, graph, obstacles_group, state_machine_type):
    behaviour = 18
    pos = (random.randint(0, screensize[0]), random.randint(0, screensize[1]))
    
    # No poner dentro de obstaculos o paredes
    while pygame.sprite.spritecollideany(Obstacle(pos[0], pos[1], 1, 1), obstacles_group):
        pos = (random.randint(0, screensize[0]), random.randint(0, screensize[1]))

    enemy = Enemy(behaviour, pos, graph, state_machine_type)
    player_node = graph.get_closest_node(player_char.sprite.pos)
    enemy.find_path_to_player(player_node)
    enemies.add(enemy)

def create_rooms(obstacles_group):
    wall_thickness = 20

    # Dimensiones de las habitaciones y pasillos
    room_width = 400
    room_height = 300
    hallway_width = 100

    # Lista de posiciones para habitaciones con salidas
    room_positions = [
        # Habitacion superior izquierda
        (50, 50),  
        # Habitacion central izquierda
        (50, 450),
        # Habitacion inferior izquierda
        (50, 850),
        # Habitacion superior central  
        (600, 50),
        # Habitacion central
        (600, 450),  
        # Habitacion inferior central
        (600, 850),  
        # Habitacion superior derecha
        (1150, 50),  
        # Habitacion central derecha
        (1150, 450),  
        # Habitacion inferior derecha
        (1150, 850),  
    ]

    for pos in room_positions:
        x, y = pos

        # Paredes superiores e inferiores 
        if y != 850: 
            obstacles_group.add(Obstacle(x, y, room_width, wall_thickness))
            obstacles_group.add(Obstacle(x, y + room_height - wall_thickness, (room_width - hallway_width) // 2, wall_thickness))
            obstacles_group.add(Obstacle(x + room_width - (room_width - hallway_width) // 2, y + room_height - wall_thickness, (room_width - hallway_width) // 2, wall_thickness))
        else:
            obstacles_group.add(Obstacle(x, y, (room_width - hallway_width) // 2, wall_thickness))
            obstacles_group.add(Obstacle(x + room_width - (room_width - hallway_width) // 2, y, (room_width - hallway_width) // 2, wall_thickness))

        # Paredes izquierda y derecha 
        if x != 1150: 
            obstacles_group.add(Obstacle(x, y, wall_thickness, room_height))
            obstacles_group.add(Obstacle(x + room_width - wall_thickness, y, wall_thickness, (room_height - hallway_width) // 2))
            obstacles_group.add(Obstacle(x + room_width - wall_thickness, y + room_height - (room_height - hallway_width) // 2, wall_thickness, (room_height - hallway_width) // 2)) 
            obstacles_group.add(Obstacle(x, y, wall_thickness, (room_height - hallway_width) // 2))
            obstacles_group.add(Obstacle(x, y + room_height - (room_height - hallway_width) // 2, wall_thickness, (room_height - hallway_width) // 2))

    # Crear pasillos

    # Pasillos horizontales
    # Entre hab. superior izq y central
    obstacles_group.add(Obstacle(450, 100, hallway_width, wall_thickness)) 
    # Entre hab. central izq y central 
    obstacles_group.add(Obstacle(450, 500, hallway_width, wall_thickness))  
    # Entre hab. inferior izq y central
    obstacles_group.add(Obstacle(450, 900, hallway_width, wall_thickness))
    # Entre hab. superior central y derecha
    obstacles_group.add(Obstacle(1000, 100, hallway_width, wall_thickness))
    # Entre hab. central central y derecha
    obstacles_group.add(Obstacle(1000, 500, hallway_width, wall_thickness))
    # Entre hab. inferior central y derecha
    obstacles_group.add(Obstacle(1000, 900, hallway_width, wall_thickness))

    # Pasillos verticales
    # Entre hab. superior izq y central izq
    obstacles_group.add(Obstacle(200, 400, wall_thickness, hallway_width))
    # Entre hab. central izq y inferior izq
    obstacles_group.add(Obstacle(200, 800, wall_thickness, hallway_width))
    # Entre hab. superior central y central
    obstacles_group.add(Obstacle(750, 400, wall_thickness, hallway_width))
    # Entre hab. central y inferior central
    obstacles_group.add(Obstacle(750, 800, wall_thickness, hallway_width))
    # Entre hab. superior derecha y central derecha
    obstacles_group.add(Obstacle(1300, 400, wall_thickness, hallway_width))
    # Entre hab. central derecha e inferior derecha
    obstacles_group.add(Obstacle(1300, 800, wall_thickness, hallway_width))

def render_tiles_and_nodes(screen, graph):
    # tile_color = (200, 200, 200)
    node_color = (0, 0, 255)

    for node in graph.nodes:
        pygame.draw.circle(screen, node_color, (node.x, node.y), 3)

def render_connections(screen, graph, render_connections):
    connection_color = (0, 255, 0)

    if render_connections:
        for node in graph.nodes:
            for connection in node.connections:
                to_node = connection.getToNode()
                pygame.draw.line(screen, connection_color, (node.x, node.y), (to_node.x, to_node.y), 1)

def render_target_node(screen, target_node):
    pygame.draw.circle(screen, (255, 0, 0), (target_node.x, target_node.y), 10)

def game_loop():
    done = False
    player_char = pygame.sprite.GroupSingle(Player(screen.get_size()))
    enemies = pygame.sprite.Group()
    obstacles_group = pygame.sprite.Group()
    render_connections_flag = False

    create_wall_borders(obstacles_group, screen.get_size())
    create_rooms(obstacles_group)


    graph = Graph(tile_size, size, obstacles_group)

    while not done:
        player_node = graph.get_closest_node(player_char.sprite.pos)
        timeDelta = clock.get_time() / 1000.0
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    spawn_enemy(enemies, screen.get_size(), graph, obstacles_group, 1)
                elif event.key == pygame.K_2:
                    spawn_enemy(enemies, screen.get_size(), graph, obstacles_group, 2)
                elif event.key == pygame.K_3:
                    spawn_enemy(enemies, screen.get_size(), graph, obstacles_group, 3)
                elif event.key == pygame.K_4:
                    render_connections_flag = not render_connections_flag
                elif event.key == pygame.K_0:
                    player_char.sprite.buffed = not player_char.sprite.buffed
                elif event.key == pygame.K_9:
                    if enemies:
                        last_enemy = list(enemies)[-1]
                        last_enemy.kill()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                print(f"Clic en posición: x={x}, y={y}")

        screen.fill(BGCOLOR)

        # Renderizar las paredes en cada fotograma
        render_obstacles(obstacles_group)
        render_tiles_and_nodes(screen, graph)
        render_connections(screen, graph, render_connections_flag)

        process_keys(keys, player_char)
        move_entities(player_char, enemies, obstacles_group, timeDelta, player_node)
        render_entities(player_char, enemies)
        for enemy in enemies:
            enemy.draw_hitbox(screen)
            if enemy.path:
                for node in enemy.path:
                    pygame.draw.circle(screen, (255, 0, 0), (node.x, node.y), 3)
                pygame.draw.circle(screen, (255, 0, 0), (enemy.path[-1].x, enemy.path[-1].y), 6)
                # render_target_node(screen, enemy.target_node)
        for obstacle in obstacles_group:
            obstacle.draw_hitbox(screen)

        behaviourRender = modeFont.render("WR: Tile Graph", True, pygame.Color('black'))
        behaviourRect = behaviourRender.get_rect()
        behaviourRect.right = size[0] - 20
        behaviourRect.top = 5
        screen.blit(behaviourRender, behaviourRect)

        pygame.display.flip()
        clock.tick(120)

    return done

done = game_loop()
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
    keys = pygame.key.get_pressed()
pygame.quit()