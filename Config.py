import pygame

# Inicializar Pygame (necesario antes de poder crear la FUENTE mas abajo)
pygame.init()

# -----------------------------
# CONFIGURACIÓN DE LA PANTALLA
# -----------------------------
ANCHO = 800
ALTO = 600
FPS = 60  # cuadros por segundo maximos del juego

# -----------------------------
# POSICION DE LAS VENTANAS
# -----------------------------
# Para que la ventana del juego y la de la camara no queden
# una encima de la otra al abrir.
POSICION_VENTANA_JUEGO = (900, 50)
POSICION_VENTANA_CAMARA = (50, 50)

# Tamaño de cada casilla del mapa, en pixeles
TAM_CASILLA = 40

# -----------------------------
# COLORES (formato RGB)
# -----------------------------
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
AZUL = (0, 0, 255)
AMARILLO = (255, 255, 0)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
GRIS = (100, 100, 100)

# -----------------------------
# JUGADOR
# -----------------------------
VELOCIDAD_PACMAN = 4  # pixeles que avanza por frame

# -----------------------------
# FANTASMAS
# -----------------------------
VELOCIDAD_FANTASMA = 1.5  # valor base; Modos.py lo ajusta segun dificultad

# -----------------------------
# PUNTAJE
# -----------------------------
PUNTOS_POR_BOLA = 10

# -----------------------------
# FUENTE
# -----------------------------
FUENTE = pygame.font.SysFont("Arial", 24)  # fuente de texto usada en todo el juego