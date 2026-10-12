import pygame

from Config import *
from database_json import (
    obtener_modos_completados,
    obtener_nombre_usuario
)


class Menu:

    def __init__(self):

        self.modos = [
            "Clasico",
            "Espejo",
            "Contra Reloj",
            "Apagon"
        ]

        self.dificultades = [
            "Facil",
            "Media",
            "Dificil"
        ]

        self.modo = 0
        self.dificultad = 0

    def mostrar(self, pantalla, usuario_id):

        reloj = pygame.time.Clock()

        # El ID se usa internamente para consultar la base de datos.
        # El nombre se utiliza únicamente para mostrarlo en pantalla.
        nombre_usuario = obtener_nombre_usuario(usuario_id)

        while True:

            pantalla.fill(NEGRO)

            # Título principal
            titulo = pygame.font.SysFont(
                "Arial",
                48,
                True
            ).render(
                "PASA-HAMBRE",
                True,
                AMARILLO
            )

            pantalla.blit(
                titulo,
                (
                    ANCHO // 2 - titulo.get_width() // 2,
                    40
                )
            )

            # Nombre del usuario que inició sesión
            texto_usuario = FUENTE.render(
                f"Usuario: {nombre_usuario}",
                True,
                AZUL
            )

            pantalla.blit(
                texto_usuario,
                (
                    ANCHO // 2 - texto_usuario.get_width() // 2,
                    105
                )
            )

            # Modo seleccionado
            texto1 = FUENTE.render(
                "Modo: " + self.modos[self.modo],
                True,
                BLANCO
            )

            pantalla.blit(texto1, (80, 170))

            # Dificultad seleccionada
            texto2 = FUENTE.render(
                "Dificultad: " + self.dificultades[self.dificultad],
                True,
                BLANCO
            )

            pantalla.blit(texto2, (80, 220))

            # Controles
            texto3 = FUENTE.render(
                "← → Cambiar modo",
                True,
                VERDE
            )

            pantalla.blit(texto3, (80, 320))

            texto4 = FUENTE.render(
                "↑ ↓ Cambiar dificultad",
                True,
                VERDE
            )

            pantalla.blit(texto4, (80, 360))

            texto5 = FUENTE.render(
                "ENTER = Jugar",
                True,
                AMARILLO
            )

            pantalla.blit(texto5, (80, 430))

            texto_progreso = FUENTE.render(
                "P = Ver mi progreso",
                True,
                AMARILLO
            )

            pantalla.blit(texto_progreso, (80, 470))

            texto6 = FUENTE.render(
                "ESC = Salir",
                True,
                ROJO
            )

            pantalla.blit(texto6, (80, 520))

            pygame.display.flip()

            for evento in pygame.event.get():

                if evento.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if evento.type == pygame.KEYDOWN:

                    if evento.key == pygame.K_RIGHT:

                        self.modo += 1

                        if self.modo >= len(self.modos):
                            self.modo = 0

                    elif evento.key == pygame.K_LEFT:

                        self.modo -= 1

                        if self.modo < 0:
                            self.modo = len(self.modos) - 1

                    elif evento.key == pygame.K_UP:

                        self.dificultad += 1

                        if self.dificultad >= len(self.dificultades):
                            self.dificultad = 0

                    elif evento.key == pygame.K_DOWN:

                        self.dificultad -= 1

                        if self.dificultad < 0:
                            self.dificultad = len(self.dificultades) - 1

                    elif evento.key == pygame.K_RETURN:

                        return (
                            self.modos[self.modo],
                            self.dificultades[self.dificultad]
                        )

                    elif evento.key == pygame.K_p:

                        self.mostrar_progreso(
                            pantalla,
                            usuario_id,
                            nombre_usuario
                        )

                    elif evento.key == pygame.K_ESCAPE:

                        pygame.quit()
                        exit()

            reloj.tick(FPS)

    def mostrar_progreso(
        self,
        pantalla,
        usuario_id,
        nombre_usuario=None
    ):

        reloj = pygame.time.Clock()

        # Permite llamar al método incluso sin enviar el nombre.
        if nombre_usuario is None:
            nombre_usuario = obtener_nombre_usuario(usuario_id)

        while True:

            pantalla.fill(NEGRO)

            # Título
            titulo = pygame.font.SysFont(
                "Arial",
                42,
                True
            ).render(
                "MI PROGRESO",
                True,
                AMARILLO
            )

            pantalla.blit(
                titulo,
                (
                    ANCHO // 2 - titulo.get_width() // 2,
                    35
                )
            )

            # Nombre del jugador en la pantalla de progreso
            texto_usuario = FUENTE.render(
                f"Usuario: {nombre_usuario}",
                True,
                AZUL
            )

            pantalla.blit(
                texto_usuario,
                (
                    ANCHO // 2 - texto_usuario.get_width() // 2,
                    95
                )
            )

            # Se consulta el progreso utilizando el ID interno.
            progreso = obtener_modos_completados(usuario_id)

            y = 150

            if not progreso:

                texto = FUENTE.render(
                    "Todavia no has completado ningun modo.",
                    True,
                    BLANCO
                )

                pantalla.blit(texto, (80, y))

            else:

                for modo, dificultades in progreso.items():

                    texto_modo = FUENTE.render(
                        str(modo) + ":",
                        True,
                        VERDE
                    )

                    pantalla.blit(texto_modo, (80, y))

                    # Permite mostrar correctamente una lista de
                    # dificultades o un único valor.
                    if isinstance(dificultades, (list, tuple, set)):
                        dificultades_texto = ", ".join(
                            str(dificultad)
                            for dificultad in dificultades
                        )
                    else:
                        dificultades_texto = str(dificultades)

                    texto_dificultades = FUENTE.render(
                        "Dificultades: " + dificultades_texto,
                        True,
                        BLANCO
                    )

                    pantalla.blit(
                        texto_dificultades,
                        (120, y + 40)
                    )

                    y += 90

            texto_salida = FUENTE.render(
                "ESC = Volver al menu",
                True,
                ROJO
            )

            pantalla.blit(
                texto_salida,
                (80, ALTO - 60)
            )

            pygame.display.flip()

            for evento in pygame.event.get():

                if evento.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if evento.type == pygame.KEYDOWN:

                    if evento.key == pygame.K_ESCAPE:
                        return

            reloj.tick(FPS)
