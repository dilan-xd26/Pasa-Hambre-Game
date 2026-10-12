import pygame
from Config import *


class Jugador:

    def __init__(self):

        # Posición inicial: centro de la primera casilla transitable
        self.x = TAM_CASILLA + TAM_CASILLA // 2
        self.y = TAM_CASILLA + TAM_CASILLA // 2

        self.radio = TAM_CASILLA // 2 - 4

        self.velocidad = VELOCIDAD_PACMAN

    def mover(self, direccion, mapa):

        # Calcula la posicion candidata segun la direccion recibida
        nuevo_x = self.x
        nuevo_y = self.y

        if direccion == "ARRIBA":
            nuevo_y -= self.velocidad

        elif direccion == "ABAJO":
            nuevo_y += self.velocidad

        elif direccion == "IZQUIERDA":
            nuevo_x -= self.velocidad

        elif direccion == "DERECHA":
            nuevo_x += self.velocidad

        # Comprobar si chocará con un muro; si no, confirma el movimiento
        if not mapa.es_muro(nuevo_x, nuevo_y):

            self.x = nuevo_x
            self.y = nuevo_y

        # Comer punto en la posicion actual (se mueva o no)
        mapa.comer_punto(self.x, self.y)

    def dibujar(self, pantalla):

        # Cuerpo amarillo
        pygame.draw.circle(
            pantalla,
            AMARILLO,
            (int(self.x), int(self.y)),
            self.radio
        )

        # Ojo
        pygame.draw.circle(
            pantalla,
            NEGRO,
            (
                int(self.x + self.radio // 3),
                int(self.y - self.radio // 3)
            ),
            3
        )

    def obtener_posicion(self):

        # No se usa actualmente en el proyecto
        return self.x, self.y

    def obtener_rect(self):

        # No se usa actualmente en el proyecto
        return pygame.Rect(
            self.x - self.radio,
            self.y - self.radio,
            self.radio * 2,
            self.radio * 2
        )