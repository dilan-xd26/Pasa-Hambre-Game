
import sys
import os

from Config import *
from Camara import Camara
from Mapa import Mapa
from Jugador import Jugador
from Fantasma import Fantasma
from Menu import Menu
from Modos import Modos
from database_json import (
    obtener_modos_completados,
    guardar_modo_completado
)


def iniciar_juego(usuario_id):

    import pygame

    print(f"Usuario autenticado: {usuario_id}")
    print("Iniciando juego...")

    # Indicamos la posición inicial de la ventana del juego.
    # POSICION_VENTANA_JUEGO debe ser una tupla con la posición X e Y.
    os.environ['SDL_VIDEO_WINDOW_POS'] = (
        f"{POSICION_VENTANA_JUEGO[0]},{POSICION_VENTANA_JUEGO[1]}"
    )

    # Inicializamos todos los módulos de Pygame.
    pygame.init()

    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Pasa-Hambre")

    # Creamos un reloj para controlar la velocidad del juego.
    reloj = pygame.time.Clock()
    menu = Menu()

    # Este ciclo permite volver al menú del juego
    while True:

        # -----------------------
        # MENÚ DEL JUEGO
        # -----------------------

        resultado = menu.mostrar(pantalla, usuario_id)

        # Si Menu.mostrar() devuelve None, salir del juego
        if resultado is None:
            break

        modo, dificultad = resultado

        # -----------------------
        # CREAR OBJETOS DE LA PARTIDA
        # -----------------------

        camara = Camara()
        mapa = Mapa(modo)
        jugador = Jugador()
        fantasma = Fantasma()
        modos = Modos(modo, dificultad)

        jugando = True

        while jugando:

            # Limitamos la velocidad del juego a la cantidad de FPS definida.
            # Esto evita que el juego se ejecute demasiado rápido.
            reloj.tick(FPS)

            for evento in pygame.event.get():

                if evento.type == pygame.QUIT:
                    camara.cerrar()
                    pygame.quit()
                    return

            # -----------------------
            # CÁMARA
            # -----------------------

            direccion = camara.obtener_direccion()
            # Algun modo puede invertir los controles.
            direccion = modos.invertir_direccion(direccion)

            # -----------------------
            # JUGADOR
            # -----------------------

            puntaje_antes = mapa.puntaje

            jugador.mover(direccion, mapa)

            if mapa.puntaje > puntaje_antes:

                if modo == "Contra Reloj":
                    modos.sumar_energia()

                modos.registrar_bolita()

            # -----------------------
            # FANTASMA
            # -----------------------

            # En dificultad Fácil, el fantasma se mueve con un
            # comportamiento menos preciso y más aleatorio.
            if dificultad == "Facil":
                fantasma.mover(mapa, jugador, sesgo=0.35)
            else:
                fantasma.perseguir(jugador, mapa)

            # -----------------------
            # MODOS
            # -----------------------

            modos.actualizar(jugador, mapa, fantasma)

            # -----------------------
            # DERROTA
            # -----------------------

            if fantasma.colision(jugador):

                print("GAME OVER")
                jugando = False

            elif modo == "Contra Reloj" and modos.sin_energia():

                print("SIN ENERGIA")
                jugando = False

            # -----------------------
            # VICTORIA
            # -----------------------

            elif not mapa.quedan_puntos():

                print("GANASTE")

                guardar_modo_completado(
                    usuario_id,
                    modo,
                    dificultad
                )

                jugando = False

            # -----------------------
            # DIBUJAR
            # -----------------------

            pantalla.fill(NEGRO)

            mapa.dibujar(pantalla)
            jugador.dibujar(pantalla)
            fantasma.dibujar(pantalla)

            if modo == "Apagon":
                modos.dibujar(pantalla, jugador)

            mapa.mostrar_puntaje(pantalla)
            modos.dibujar(pantalla)

            pygame.display.flip()

        # Cerrar solamente la cámara de esta partida
        camara.cerrar()

        # Al terminar la partida, el while vuelve a ejecutar:
        # resultado = menu.mostrar(pantalla)

    pygame.quit()



if __name__ == "__main__":
    from menu_acceso import mostrar_menu

    while True: 
        usuario_id = mostrar_menu()

        if usuario_id is not None:
            iniciar_juego(usuario_id)
            # Al ganar o perder, vuelve nuevamente al menú de inicio
            break
        print("Debes Iniciar sesion para jugar")
   