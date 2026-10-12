import pygame
import copy
from collections import deque
from Config import *
from Mapas import MAPAS_POR_MODO, MAPA_CLASICO

# 1 = Muro
# 0 = Camino con punto
# 2 = Camino vacío


class Mapa:

    def __init__(self, modo="Clasico"):

        self.puntaje = 0

        # Elegir el mapa segun el modo. Si el modo no esta en el
        # diccionario, se usa el mapa clasico por defecto.
        # Se hace una copia propia para que comer_punto() no
        # modifique el mapa original compartido en Mapas.py
        mapa_base = MAPAS_POR_MODO.get(modo, MAPA_CLASICO)
        self.mapa = copy.deepcopy(mapa_base)

    def dibujar(self, pantalla):

        # Recorre toda la matriz y dibuja cada casilla segun su valor
        for fila in range(len(self.mapa)):

            for columna in range(len(self.mapa[fila])):

                x = columna * TAM_CASILLA
                y = fila * TAM_CASILLA

                if self.mapa[fila][columna] == 1:

                    # Muro
                    pygame.draw.rect(
                        pantalla,
                        AZUL,
                        (x, y, TAM_CASILLA, TAM_CASILLA)
                    )

                elif self.mapa[fila][columna] == 0:

                    # Punto para comer
                    pygame.draw.circle(
                        pantalla,
                        BLANCO,
                        (
                            x + TAM_CASILLA//2,
                            y + TAM_CASILLA//2
                        ),
                        4
                    )

    def es_muro(self, x, y):

        # Convierte pixeles a fila/columna y revisa si esa casilla es muro
        columna = int(x // TAM_CASILLA)
        fila = int(y // TAM_CASILLA)

        # Fuera del mapa cuenta como muro
        if fila < 0 or fila >= len(self.mapa):
            return True

        if columna < 0 or columna >= len(self.mapa[0]):
            return True

        return self.mapa[fila][columna] == 1

    def comer_punto(self, x, y):

        # Si la celda tiene un punto, lo marca como comido y suma puntaje
        columna = int(x // TAM_CASILLA)
        fila = int(y // TAM_CASILLA)

        if self.mapa[fila][columna] == 0:

            self.mapa[fila][columna] = 2

            self.puntaje += PUNTOS_POR_BOLA

    def mostrar_puntaje(self, pantalla):

        # Dibuja el puntaje actual en la esquina inferior izquierda
        texto = FUENTE.render(
            f"Puntaje: {self.puntaje}",
            True,
            AMARILLO
        )

        pantalla.blit(texto, (10, ALTO - 35))

    def quedan_puntos(self):

        # True si todavia hay algun punto (0) sin comer en el mapa
        for fila in self.mapa:

            if 0 in fila:
                return True

        return False

    def siguiente_paso(self, inicio_x, inicio_y, destino_x, destino_y):

        #Convierte la posición inicial, expresada en píxeles, a una posición dentro del mapa.
        inicio = (
            int(inicio_y // TAM_CASILLA),
            int(inicio_x // TAM_CASILLA)
        )

        destino = (
            int(destino_y // TAM_CASILLA),
            int(destino_x // TAM_CASILLA)
        )

        #Crear la cola de búsqueda
        #BFS utiliza una cola porque procesa las posiciones en el orden en que fueron encontradas
        #Primero entra → primero sale
        cola = deque([inicio])

        #Registrar las casillas visitadas
        #Sirve para evitar que el algoritmo vuelva a recorrer la misma casilla infinitamente.
        visitado = {inicio}

        #El diccionario padre almacena desde qué casilla se llegó a cada posición.
        padre = {}

        #Cada tupla representa un cambio en
        #(fila, columna)
        movimientos = [
            (-1, 0),  # arriba
            (1, 0),   # abajo
            (0, -1),  # izquierda
            (0, 1)    # derecha
        ]


        #Repetir mientras haya casillas por explorar
        while cola:
        #El ciclo continúa mientras la cola tenga posiciones pendientes de revisar.
        #Si la cola queda vacía, significa que ya no hay más casillas alcanzables.


        #Se extrae la primera posición de la cola.
            actual = cola.popleft()


            #Comprobar si se llegó al destino
            #Si la posición actual es el destino, la búsqueda termina.
            if actual == destino:
                break

            #Recorrer los cuatro movimientos
            #Se prueban las cuatro direcciones posibles
            for df, dc in movimientos:
                nf = actual[0] + df
                nc = actual[1] + dc

                #Comprobar si la casilla es válida
                if (
                    0 <= nf < len(self.mapa) and
                    0 <= nc < len(self.mapa[0]) and
                    self.mapa[nf][nc] != 1 and
                    (nf, nc) not in visitado
                ):
                    visitado.add((nf, nc))
                    padre[(nf, nc)] = actual
                    cola.append((nf, nc))

        #Comprobar si existe un camino
        if destino not in padre and destino != inicio:
            return None

        #Comenzar la reconstrucción del camino
        paso = destino
        while padre.get(paso) != inicio:
            if paso == inicio:
                return None
            paso = padre[paso]

        return paso