import cv2
import numpy as np

from Config import POSICION_VENTANA_CAMARA


class Camara:

    def __init__(self):

        self.cap = cv2.VideoCapture(0)  # indice de la camara a usar

        self.direccion = "QUIETO"

        # Crear y posicionar la ventana de la camara aparte,
        # para que no quede encima de la ventana del juego
        cv2.namedWindow("Camara", cv2.WINDOW_NORMAL)
        cv2.moveWindow(
            "Camara",
            POSICION_VENTANA_CAMARA[0],
            POSICION_VENTANA_CAMARA[1]
        )

    def obtener_direccion(self):

        ret, frame = self.cap.read()

        if not ret:
            return "QUIETO"  # fallo la lectura de la camara

        # Imagen espejo
        #frame = cv2.flip(frame, 1)

        alto, ancho, _ = frame.shape

        # HSV detecta color de forma mas estable que RGB ante cambios de luz
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Color verde (el objeto que se mueve con la mano)
        azul_bajo1 = np.array([35, 120, 100], dtype=np.uint8)
        azul_alto1 = np.array([65, 255, 255], dtype=np.uint8)

        azul_bajo2 = np.array([65, 100, 100], dtype=np.uint8)
        azul_alto2 = np.array([85, 255, 255], dtype=np.uint8)

        # Mascara: blanco donde hay color detectado, negro en el resto
        mascara1 = cv2.inRange(hsv, azul_bajo1, azul_alto1)
        mascara2 = cv2.inRange(hsv, azul_bajo2, azul_alto2)

        mascara = mascara1 + mascara2

        # Bordes de las zonas detectadas como el color buscado
        contornos, _ = cv2.findContours(
            mascara,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        self.direccion = "QUIETO"

        if len(contornos) > 0:

            # Se queda con el contorno mas grande (el objeto real)
            contorno = max(contornos, key=cv2.contourArea)

            # Filtra manchas chicas / ruido (area minima)
            if cv2.contourArea(contorno) > 600:

                x, y, w, h = cv2.boundingRect(contorno)

                centro_x = x + w // 2
                centro_y = y + h // 2

                # Dibujar
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
                cv2.circle(frame, (centro_x, centro_y), 5, (255,0,0), -1)

                # Zona central "quieta": entre estos limites no hay movimiento
                limite_izq = int(ancho * 0.40)      # 40% de la pantalla
                limite_der = int(ancho * 0.60)      # 60% de la pantalla
                limite_arriba = int(alto * 0.30)    # 30%
                limite_abajo = int(alto * 0.60)     # 60%

                # Líneas guía
                cv2.line(frame, (limite_izq, 0), (limite_izq, alto), (255,255,255), 2)
                cv2.line(frame, (limite_der, 0), (limite_der, alto), (255,255,255), 2)
                cv2.line(frame, (0, limite_arriba), (ancho, limite_arriba), (255,255,255), 2)
                cv2.line(frame, (0, limite_abajo), (ancho, limite_abajo), (255,255,255), 2)

                # Direccion segun en que zona cae el centro del objeto
                if centro_x < limite_izq:
                    self.direccion = "IZQUIERDA"

                elif centro_x > limite_der:
                    self.direccion = "DERECHA"

                elif centro_y < limite_arriba:
                    self.direccion = "ARRIBA"

                elif centro_y > limite_abajo:
                    self.direccion = "ABAJO"

                else:
                    self.direccion = "QUIETO"

                cv2.putText(
                    frame,
                    self.direccion,
                    (20,40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0,255,0),
                    2
                )

        cv2.imshow("Camara", frame)

        cv2.waitKey(1)  # necesario para refrescar la ventana de OpenCV

        return self.direccion


    def cerrar(self):

        self.cap.release()
        cv2.destroyAllWindows()