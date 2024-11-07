import pygame
import math

PLAYERCOLOR = (255, 0, 0)
BUFFED = (255, 0, 255)

class Player(pygame.sprite.Sprite):

    def __init__(self, screenSize):
        super().__init__()

        self.original_image = pygame.Surface([20, 20], pygame.SRCALPHA)
        pygame.draw.polygon(
            self.original_image,
            PLAYERCOLOR,
            [(0, 0), (20, 10), (0, 20)]
        )
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(screenSize[0] // 2, screenSize[1] // 2))
        shrink_width = self.rect.width * 1 / 2
        shrink_height = self.rect.height * 1 / 2
        self.rect.inflate_ip(-shrink_width, -shrink_height)

        self.pos = [screenSize[0] // 2, screenSize[1] // 2] 
        self.orientation = 0.0 
        self.velocity = [0.0, 0.0]  
        self.rotation = 0.0  
        self.buffed = False

    def move(self, screenSize, tDelta, obstacles_group):
        
        if self.buffed:
            self.change_color(BUFFED)
        else:
            self.change_color(PLAYERCOLOR)
            
        # Posicion antes de posible colision
        original_pos = self.pos[:]

        # Actualizar la posicion basada en la velocidad
        newPos = (
            self.pos[0] + self.velocity[0] * tDelta,
            self.pos[1] + self.velocity[1] * tDelta
        )

        # Limitar dentro de la pantalla
        self.pos[0] = max(0, min(screenSize[0], newPos[0]))
        self.pos[1] = max(0, min(screenSize[1], newPos[1]))

        # Actualizar la orientacion en base a la rotacion
        self.orientation += self.rotation * tDelta
        self.orientation %= (2 * math.pi)

        # Actualizar la posición del rectangulo
        self.rect.center = self.pos

        # Verificar colision con obstáculos
        if pygame.sprite.spritecollide(self, obstacles_group, False):
            self.pos = original_pos
            self.rect.center = self.pos

    def change_color(self, color):
        
        self.current_color = color
        self.original_image.fill((0, 0, 0, 0))
        pygame.draw.polygon(
            self.original_image,
            self.current_color,
            [(0, 0), (20, 10), (0, 20)]
        )
        self.image = self.original_image

    def render(self, surface):
        
        rotated_image = pygame.transform.rotate(
            self.original_image,
            -math.degrees(self.orientation)
        )
        new_rect = rotated_image.get_rect(center=self.rect.center)
        surface.blit(rotated_image, new_rect.topleft)
