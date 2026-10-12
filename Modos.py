import pygame
from Config import *


class Modos:

    def __init__(self, modo, dificultad):

        self.modo = modo
        self.dificultad = dificultad

        # -------------------
        # CONTRA RELOJ
        # -------------------
        self.energia = 100

        if dificultad == "Facil":
            self.velocidad_energia = 0.05

        elif dificultad == "Media":
            self.velocidad_energia = 0.10

        else:
            self.velocidad_energia = 0.12

        # -------------------
        # ESPEJO
        # -------------------
        self.invertido = False
        self.tiempo = pygame.time.get_ticks()  # momento del ultimo cambio

        # -------------------
        # APAGON
        # -------------------
        if dificultad == "Facil":
            self.radio_apagon = 3 * TAM_CASILLA

        else:
            self.radio_apagon = 1.5 * TAM_CASILLA

        # Destello del Apagon: al comer cierta cantidad de bolitas
        # se enciende la luz un instante y luego vuelve a la normalidad
        self.bolitas_comidas = 0
        self.destello_activo = False
        self.tiempo_destello = 0
        self.duracion_destello = 700  # ms que dura encendida la luz

        if dificultad == "Media":
            self.bolitas_para_destello = 5

        elif dificultad == "Dificil":
            self.bolitas_para_destello = 8

        else:
            self.bolitas_para_destello = None  # Facil no tiene destello

    ##################################################
    # GENERAL (aplica a todos los modos)
    ##################################################

    def actualizar(self, jugador, mapa, fantasma):

        # Se llama una vez por frame; reparte el trabajo segun el modo activo
        self.ajustar_velocidad_fantasma(fantasma)

        if self.modo == "Espejo":
            self.modo_espejo()

        elif self.modo == "Contra Reloj":
            self.modo_contra_reloj()

        elif self.modo == "Apagon":
            self.modo_apagon()

    def ajustar_velocidad_fantasma(self, fantasma):

        # Define que tan rapido va el fantasma segun dificultad y modo
        if self.dificultad == "Facil":
            fantasma.velocidad = 2

        elif self.dificultad == "Media":
            fantasma.velocidad = 2.5

        else:
            # Dificil: Clasico y Apagon van rapido (casi como el jugador);
            # Espejo y Contra Reloj van mas lento porque ya complican de otra forma
            if self.modo == "Clasico" or self.modo == "Apagon":
                fantasma.velocidad = 3.2

            else:
                fantasma.velocidad = 2.7

    ##################################################
    # MODO ESPEJO
    ##################################################

    def modo_espejo(self):

        # Alterna controles invertidos segun dificultad
        if self.dificultad == "Facil":

            self.invertido = True  # siempre invertido

        elif self.dificultad == "Media":

            # Cambia cada 15 segundos
            if pygame.time.get_ticks() - self.tiempo > 15000:

                self.invertido = not self.invertido
                self.tiempo = pygame.time.get_ticks()

        elif self.dificultad == "Dificil":

            # Cambia cada 7 segundos
            if pygame.time.get_ticks() - self.tiempo > 7000:

                self.invertido = not self.invertido
                self.tiempo = pygame.time.get_ticks()

    def invertir_direccion(self, direccion):

        # Devuelve la direccion opuesta si corresponde invertir
        if self.modo != "Espejo":
            return direccion

        if not self.invertido:
            return direccion

        if direccion == "ARRIBA":
            return "ABAJO"

        elif direccion == "ABAJO":
            return "ARRIBA"

        elif direccion == "IZQUIERDA":
            return "DERECHA"

        elif direccion == "DERECHA":
            return "IZQUIERDA"

        return direccion  # QUIETO no se invierte

    ##################################################
    # MODO CONTRA RELOJ
    ##################################################

    def modo_contra_reloj(self):

        # Descuenta energia por frame, sin bajar de 0
        self.energia -= self.velocidad_energia

        if self.energia < 0:
            self.energia = 0

    def sumar_energia(self):

        # Recompensa por comer punto, sin pasar de 100
        self.energia += 10

        if self.energia > 100:
            self.energia = 100

    def sin_energia(self):

        # Condicion de fin de partida en este modo
        return self.energia <= 0

    ##################################################
    # MODO APAGON
    ##################################################

    def modo_apagon(self):

        # Apaga el destello cuando se cumple su duracion
        if self.destello_activo:

            if pygame.time.get_ticks() - self.tiempo_destello > self.duracion_destello:

                self.destello_activo = False

    def registrar_bolita(self):

        # Cuenta bolitas comidas y activa el destello al llegar al umbral
        if self.modo != "Apagon" or self.bolitas_para_destello is None:
            return

        self.bolitas_comidas += 1

        if self.bolitas_comidas >= self.bolitas_para_destello:

            self.bolitas_comidas = 0
            self.destello_activo = True
            self.tiempo_destello = pygame.time.get_ticks()

    def dibujar_apagon(self, pantalla, jugador):

        # Cubre la pantalla dejando un circulo transparente alrededor del jugador
        color_transparente = (1, 1, 1)  # "casi negro", distinto del negro puro

        oscuridad = pygame.Surface((ANCHO, ALTO))
        oscuridad.fill(NEGRO)
        oscuridad.set_colorkey(color_transparente)  # ese color se vuelve invisible

        # Radio gigante si el destello esta activo, si no el radio normal
        if self.destello_activo:
            radio = max(ANCHO, ALTO)
        else:
            radio = int(self.radio_apagon)

        # Perfora el "agujero" transparente centrado en el jugador
        pygame.draw.circle(
            oscuridad,
            color_transparente,
            (int(jugador.x), int(jugador.y)),
            radio
        )

        pantalla.blit(oscuridad, (0, 0))  # se pega encima de todo lo ya dibujado

    ##################################################
    # DIBUJADO (Contra Reloj, Apagon y Espejo)
    ##################################################

    def dibujar(self, pantalla, jugador=None):

        if self.modo == "Contra Reloj":

            # Fondo rojo de la barra (siempre igual)
            pygame.draw.rect(
                pantalla,
                ROJO,
                (580, 10, 200, 20)
            )

            # Relleno verde proporcional a la energia actual
            pygame.draw.rect(
                pantalla,
                VERDE,
                (580, 10, self.energia * 2, 20)
            )

            texto = FUENTE.render(
                "Energia",
                True,
                BLANCO
            )

            pantalla.blit(texto, (580, 35))

        elif self.modo == "Apagon" and jugador is not None:

            self.dibujar_apagon(pantalla, jugador)

        elif self.modo == "Espejo":

            # Solo se avisa en Media/Dificil, ya que en Facil
            # esta invertido todo el tiempo y no hace falta avisar
            if self.dificultad != "Facil" and self.invertido:

                texto = FUENTE.render(
                    "Controles invertidos",
                    True,
                    ROJO
                )

                pantalla.blit(
                    texto,
                    (ANCHO // 2 - texto.get_width() // 2, 10)
                )