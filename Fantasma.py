import pygame
import random

from Config import *


class Fantasma:

    def __init__(self):

        # Posición inicial (columna 18, fila 9, centrado en la casilla)
        self.x = 18 * TAM_CASILLA + TAM_CASILLA // 2
        self.y = 9 * TAM_CASILLA + TAM_CASILLA // 2

        self.radio = TAM_CASILLA // 2 - 4

        self.velocidad = VELOCIDAD_FANTASMA
        self.ultima_direccion = None  # no se usa actualmente
        self.direccion = random.choice(
            ["ARRIBA", "ABAJO", "IZQUIERDA", "DERECHA"]
        )

        # Probabilidad (%) por frame de girar aunque el camino
        # siga libre. Mas alta = explora/reacciona mas seguido
        # en vez de irse largo por un pasillo sin fijarse en nada.
        self.prob_giro = 8

    def mover(self, mapa, jugador=None, sesgo=0.0):

        # sesgo: probabilidad (0.0 a 1.0) de que, al elegir nueva
        # direccion, en vez de tirar una opcion al azar elija la
        # que mas lo acerca al jugador. Con sesgo=0 se mueve 100%
        # al azar. Se usa en dificultad Facil para que amenace un
        # poco sin llegar a perseguir de verdad como Media/Dificil.

        # Si la direccion actual choca contra un muro (o todavia
        # no tiene direccion), elegir una nueva SOLO entre las
        # que de verdad estan libres.
        if self.direccion is None or self._choca(mapa, self.direccion):

            self.direccion = self._elegir_direccion(mapa, jugador, sesgo)

        # A veces cambia de direccion aunque no haya muro,
        # pero tambien solo entre las opciones validas
        elif random.randint(1, 100) <= self.prob_giro:

            self.direccion = self._elegir_direccion(mapa, jugador, sesgo)

        # Calcula la posicion candidata segun la direccion actual
        nuevo_x = self.x
        nuevo_y = self.y

        if self.direccion == "ARRIBA":
            nuevo_y -= self.velocidad

        elif self.direccion == "ABAJO":
            nuevo_y += self.velocidad

        elif self.direccion == "IZQUIERDA":
            nuevo_x -= self.velocidad

        elif self.direccion == "DERECHA":
            nuevo_x += self.velocidad

        # Solo se mueve de verdad si la posicion candidata no es muro
        if not mapa.es_muro(nuevo_x, nuevo_y):

            self.x = nuevo_x
            self.y = nuevo_y

    def _choca(self, mapa, direccion):

        # Calcula donde quedaria el fantasma si se moviera en
        # "direccion", sin moverlo de verdad, y consulta si esa
        # posicion hipotetica es un muro
        x, y = self.x, self.y

        if direccion == "ARRIBA":
            y -= self.velocidad

        elif direccion == "ABAJO":
            y += self.velocidad

        elif direccion == "IZQUIERDA":
            x -= self.velocidad

        elif direccion == "DERECHA":
            x += self.velocidad

        return mapa.es_muro(x, y)

    def _elegir_direccion(self, mapa, jugador=None, sesgo=0.0):

        direcciones = ["ARRIBA", "ABAJO", "IZQUIERDA", "DERECHA"]

        opuesta = {
            "ARRIBA": "ABAJO",
            "ABAJO": "ARRIBA",
            "IZQUIERDA": "DERECHA",
            "DERECHA": "IZQUIERDA",
        }

        # Solo direcciones que no chocan contra un muro
        validas = [
            d for d in direcciones if not self._choca(mapa, d)
        ]

        # Si no hay ninguna direccion libre (caso raro), se queda igual
        if not validas:
            return self.direccion

        # Si hay mas de una opcion, evitar devolverse por donde vino
        # para que explore en vez de ir para atras y para adelante
        if self.direccion in opuesta:

            sin_retroceso = [
                d for d in validas if d != opuesta[self.direccion]
            ]

            if sin_retroceso:
                validas = sin_retroceso

        # Con probabilidad "sesgo", en vez de tirar una direccion al
        # azar, elegir la que mas acerca al jugador
        if jugador is not None and sesgo > 0 and random.random() < sesgo:

            return min(
                validas,
                key=lambda d: self._distancia_si_va(d, jugador)
            )

        return random.choice(validas)

    def _distancia_si_va(self, direccion, jugador):

        # Distancia (al cuadrado) al jugador si se avanzara
        # una casilla completa en "direccion"
        x, y = self.x, self.y

        if direccion == "ARRIBA":
            y -= TAM_CASILLA

        elif direccion == "ABAJO":
            y += TAM_CASILLA

        elif direccion == "IZQUIERDA":
            x -= TAM_CASILLA

        elif direccion == "DERECHA":
            x += TAM_CASILLA

        return (x - jugador.x) ** 2 + (y - jugador.y) ** 2

    def perseguir(self, jugador, mapa):

        # Pide al mapa el siguiente paso del camino mas corto (BFS)
        paso = mapa.siguiente_paso(
            self.x, self.y,
            jugador.x, jugador.y
        )

        if paso is None:
            return  # no hay camino posible, no se mueve este frame

        fila, columna = paso

        # Casilla objetivo convertida a pixeles (su centro)
        objetivo_x = columna * TAM_CASILLA + TAM_CASILLA // 2
        objetivo_y = fila * TAM_CASILLA + TAM_CASILLA // 2

        dx = objetivo_x - self.x
        dy = objetivo_y - self.y

        # Avanza en el eje con mayor distancia pendiente, sin
        # pasarse del centro de la casilla objetivo
        if abs(dx) > abs(dy):
            if dx > 0:
                self.x += min(self.velocidad, dx)
            elif dx < 0:
                self.x -= min(self.velocidad, -dx)
        else:
            if dy > 0:
                self.y += min(self.velocidad, dy)
            elif dy < 0:
                self.y -= min(self.velocidad, -dy)

    def dibujar(self, pantalla):

        # Cuerpo rojo
        pygame.draw.circle(
            pantalla,
            ROJO,
            (int(self.x), int(self.y)),
            self.radio
        )

        # Ojos blancos
        pygame.draw.circle(
            pantalla,
            BLANCO,
            (int(self.x - 6), int(self.y - 5)),
            3
        )

        pygame.draw.circle(
            pantalla,
            BLANCO,
            (int(self.x + 6), int(self.y - 5)),
            3
        )

    def colision(self, jugador):

        # Distancia real entre centros; hay colision si es menor
        # a la suma de ambos radios
        distancia = (
            (self.x - jugador.x) ** 2 +
            (self.y - jugador.y) ** 2
        ) ** 0.5

        return distancia < self.radio + jugador.radio