import cv2
import os
import numpy as np
import time

from database_json import (
    obtener_nombre_usuario,
    existe_usuario
)


# =========================================================
# CONFIGURACIÓN
# =========================================================


CARPETA_ROSTROS = "rostros"
ARCHIVO_MODELO = "trainer.yml"
ARCHIVO_TEMPORAL = "trainer_tmp.yml"

os.makedirs(CARPETA_ROSTROS, exist_ok=True)

detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)


def crear_reconocedor():
    """
    Crea el reconocedor LBPH.

    Es necesario instalar:
        pip install opencv-contrib-python
    """

    if not hasattr(cv2, "face"):
        raise RuntimeError(
            "El módulo cv2.face no está disponible. "
            "Instala opencv-contrib-python."
        )

    return cv2.face.LBPHFaceRecognizer_create()


# =========================================================
# REGISTRAR ROSTRO
# =========================================================

def registrar_rostro(usuario_id, cantidad_imagenes=50):
    
    #Registra los rostros de un usuario después de una cuenta regresiva
    #de 3 segundos.

    #Los archivos se guardan con el formato:

        #usuario.ID.NUMERO.jpg
    

    if not hasattr(cv2, "face"):
        print("Error: cv2.face no está disponible.")
        print("Instala opencv-contrib-python.")
        return False

    os.makedirs(CARPETA_ROSTROS, exist_ok=True)

    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )

    if detector.empty():
        print("Error: no se pudo cargar el detector facial.")
        return False

    try:
        usuario_id = int(usuario_id)
    except (ValueError, TypeError):
        print("Error: el ID del usuario debe ser numérico.")
        return False

    camara = cv2.VideoCapture(0)

    if not camara.isOpened():
        print("Error: no se pudo abrir la cámara.")
        return False

    contador_imagenes = 0
    tiempo_inicio = time.time()
    segundos_espera = 3

    print(
        "La captura comenzará en 3 segundos. "
        "Colócate frente a la cámara."
    )

    try:
        while True:
            correcto, imagen = camara.read()

            if not correcto:
                print("Error: no se pudo capturar imagen de la cámara.")
                break

            imagen = cv2.flip(imagen, 1)
            gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

            tiempo_transcurrido = time.time() - tiempo_inicio

            # Cuenta regresiva antes de comenzar
            if tiempo_transcurrido < segundos_espera:
                segundos_restantes = int(
                    segundos_espera - tiempo_transcurrido
                ) + 1

                mensaje = (
                    f"Preparando captura: "
                    f"{segundos_restantes} segundos"
                )

                cv2.putText(
                    imagen,
                    mensaje,
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 255, 255),
                    2
                )

                cv2.putText(
                    imagen,
                    "Mira a la camara y permanece preparado",
                    (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 255),
                    2
                )

                cv2.imshow(
                    "Registro facial",
                    imagen
                )

                tecla = cv2.waitKey(1) & 0xFF

                if tecla == 27:  # ESC
                    print("Registro cancelado.")
                    return False

                continue

            # Detección de rostros después de los 3 segundos
            rostros = detector.detectMultiScale(
                gris,
                scaleFactor=1.3,
                minNeighbors=5,
                minSize=(100, 100)
            )

            for x, y, ancho, alto in rostros:
                rostro = gris[
                    y:y + alto,
                    x:x + ancho
                ]

                if rostro.size == 0:
                    continue

                contador_imagenes += 1

                nombre_archivo = (
                    f"usuario.{usuario_id}."
                    f"{contador_imagenes}.jpg"
                )

                ruta_archivo = os.path.join(
                    CARPETA_ROSTROS,
                    nombre_archivo
                )

                cv2.imwrite(
                    ruta_archivo,
                    rostro
                )

                cv2.rectangle(
                    imagen,
                    (x, y),
                    (x + ancho, y + alto),
                    (0, 255, 0),
                    2
                )

                mensaje = (
                    f"Captura {contador_imagenes}/"
                    f"{cantidad_imagenes}"
                )

                cv2.putText(
                    imagen,
                    mensaje,
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 255, 0),
                    2
                )

                # Evita guardar varios rostros en el mismo fotograma
                break

            cv2.imshow(
                "Registro facial",
                imagen
            )

            tecla = cv2.waitKey(100) & 0xFF

            if tecla == 27:  # ESC
                print("Registro cancelado.")
                return False

            if contador_imagenes >= cantidad_imagenes:
                print(
                    f"Registro completado para el usuario "
                    f"{usuario_id}."
                )
                return True

    except cv2.error as error:
        print(f"Error de OpenCV durante el registro: {error}")
        return False

    except Exception as error:
        print(f"Error durante el registro facial: {error}")
        return False

    finally:
        camara.release()
        cv2.destroyAllWindows()

    return contador_imagenes >= cantidad_imagenes



# =========================================================
# ENTRENAR MODELO
# =========================================================

def entrenar_modelo():
    
    #Entrena el modelo LBPH utilizando todas las imágenes de rostros
    #almacenadas en la carpeta CARPETA_ROSTROS.

    #Los archivos deben tener un nombre similar a:

    #    usuario.1.1.jpg
    #    usuario.1.2.jpg
    #   usuario.2.1.jpg

    #El número situado entre los puntos corresponde al usuario_id. 

    if not hasattr(cv2, "face"):
        print(
            "Error: cv2.face no está disponible."
        )
        print(
            "Instala opencv-contrib-python:"
        )
        print(
            "pip install opencv-contrib-python"
        )
        return False

    if not os.path.exists(CARPETA_ROSTROS):
        print(
            f"Error: no existe la carpeta "
            f"'{CARPETA_ROSTROS}'."
        )
        return False

    try:
        detector_entrenamiento = cv2.CascadeClassifier(
            cv2.data.haarcascades +
            "haarcascade_frontalface_default.xml"
        )

        if detector_entrenamiento.empty():
            print(
                "Error: no se pudo cargar el detector facial."
            )
            return False

        rostros = []
        etiquetas = []
        imagenes_procesadas = 0
        imagenes_ignoradas = 0

        extensiones_validas = (
            ".jpg",
            ".jpeg",
            ".png",
            ".bmp"
        )

        archivos = sorted(
            os.listdir(CARPETA_ROSTROS)
        )

        for nombre_archivo in archivos:
            ruta_imagen = os.path.join(
                CARPETA_ROSTROS,
                nombre_archivo
            )

            # Ignorar carpetas y archivos que no sean imágenes
            if not os.path.isfile(ruta_imagen):
                continue

            if not nombre_archivo.lower().endswith(
                extensiones_validas
            ):
                continue

            partes = nombre_archivo.split(".")

            # Formato esperado:
            # usuario.ID.NUMERO.jpg
            if len(partes) < 4:
                print(
                    f"Archivo ignorado por formato incorrecto: "
                    f"{nombre_archivo}"
                )
                imagenes_ignoradas += 1
                continue

            try:
                if partes[0].lower() != "usuario":
                    print(
                        f"Archivo ignorado: {nombre_archivo}"
                    )
                    imagenes_ignoradas += 1
                    continue

                usuario_id = int(partes[1])

            except (ValueError, IndexError):
                print(
                    f"No se pudo obtener el ID de: "
                    f"{nombre_archivo}"
                )
                imagenes_ignoradas += 1
                continue

            imagen = cv2.imread(
                ruta_imagen,
                cv2.IMREAD_GRAYSCALE
            )

            if imagen is None:
                print(
                    f"No se pudo leer la imagen: "
                    f"{nombre_archivo}"
                )
                imagenes_ignoradas += 1
                continue

            caras = detector_entrenamiento.detectMultiScale(
                imagen,
                scaleFactor=1.3,
                minNeighbors=5,
                minSize=(100, 100)
            )

            if len(caras) == 0:
                print(
                    f"No se detectó ningún rostro en: "
                    f"{nombre_archivo}"
                )
                imagenes_ignoradas += 1
                continue

            # Si hay más de un rostro, se utiliza el primero
            x, y, ancho, alto = caras[0]

            rostro_recortado = imagen[
                y:y + alto,
                x:x + ancho
            ]

            if rostro_recortado.size == 0:
                print(
                    f"Rostro vacío en: {nombre_archivo}"
                )
                imagenes_ignoradas += 1
                continue

            rostros.append(rostro_recortado)
            etiquetas.append(usuario_id)
            imagenes_procesadas += 1

        if len(rostros) == 0:
            print(
                "No se encontraron rostros válidos "
                "para entrenar el modelo."
            )
            return False

        if len(set(etiquetas)) == 0:
            print(
                "No se encontraron etiquetas de usuarios válidas."
            )
            return False

        print(
            f"Imágenes procesadas: {imagenes_procesadas}"
        )

        if imagenes_ignoradas > 0:
            print(
                f"Imágenes ignoradas: {imagenes_ignoradas}"
            )

        print(
            f"Usuarios encontrados: {len(set(etiquetas))}"
        )

        reconocedor = cv2.face.LBPHFaceRecognizer_create(
            radius=1,
            neighbors=8,
            grid_x=8,
            grid_y=8
        )

        reconocedor.train(
            rostros,
            np.array(etiquetas, dtype=np.int32)
        )

        # Guardar temporalmente para proteger el modelo original
        carpeta_modelo = os.path.dirname(
            ARCHIVO_MODELO
        )

        if carpeta_modelo:
            os.makedirs(
                carpeta_modelo,
                exist_ok=True
            )

        archivo_temporal = ARCHIVO_MODELO + ".tmp"

        if os.path.exists(archivo_temporal):
            os.remove(archivo_temporal)

        reconocedor.write(archivo_temporal)

        # Verificar que el archivo temporal se creó correctamente
        if not os.path.exists(archivo_temporal):
            print(
                "Error: no se pudo crear el modelo temporal."
            )
            return False

        # Reemplazar el modelo anterior
        os.replace(
            archivo_temporal,
            ARCHIVO_MODELO
        )

        print(
            f"Modelo entrenado correctamente: "
            f"{ARCHIVO_MODELO}"
        )

        return True

    except cv2.error as error:
        print(
            f"Error de OpenCV durante el entrenamiento: {error}"
        )
        return False

    except Exception as error:
        print(
            f"Error durante el entrenamiento: {error}"
        )
        return False

    finally:
        # Si ocurrió un error y quedó un archivo temporal,
        # se elimina para evitar confusiones posteriores.
        archivo_temporal = ARCHIVO_MODELO + ".tmp"

        if os.path.exists(archivo_temporal):
            try:
                os.remove(archivo_temporal)
            except OSError:
                pass



# =========================================================
# CAPTURAR NUEVAS IMÁGENES
# =========================================================

def capturar_nuevas_imagenes(usuario_id, cantidad=5):
    """
    Captura imágenes nuevas de un usuario ya reconocido.
    """

    usuario_id = int(usuario_id)

    camara = cv2.VideoCapture(0)

    if not camara.isOpened():
        print("No se pudo abrir la cámara.")
        return False

    archivos_existentes = [
        archivo
        for archivo in os.listdir(CARPETA_ROSTROS)
        if archivo.startswith(f"usuario.{usuario_id}.")
        and archivo.lower().endswith(".jpg")
    ]

    contador = len(archivos_existentes)
    capturas = 0

    print("Rostro reconocido correctamente.")
    print("Mira a la cámara para actualizar el reconocimiento.")
    print("Presiona ESC para cancelar.")

    while capturas < cantidad:
        correcto, imagen = camara.read()

        if not correcto:
            print("No se pudo obtener la imagen.")
            break

        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

        rostros = detector.detectMultiScale(
            gris,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(100, 100)
        )

        for x, y, ancho, alto in rostros:
            rostro = gris[y:y + alto, x:x + ancho]

            contador += 1
            capturas += 1

            nombre_archivo = (
                f"usuario.{usuario_id}.{contador}.jpg"
            )

            ruta = os.path.join(
                CARPETA_ROSTROS,
                nombre_archivo
            )

            cv2.imwrite(ruta, rostro)

            cv2.rectangle(
                imagen,
                (x, y),
                (x + ancho, y + alto),
                (0, 255, 0),
                2
            )

            break

        cv2.putText(
            imagen,
            f"Nuevas capturas: {capturas}/{cantidad}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.imshow(
            "Actualizando reconocimiento facial",
            imagen
        )

        tecla = cv2.waitKey(150) & 0xFF

        if tecla == 27:
            print("Actualización cancelada.")
            break

    camara.release()
    cv2.destroyAllWindows()

    if capturas > 0:
        print(f"Se guardaron {capturas} nuevas imágenes.")
        return True

    print("No se guardaron imágenes nuevas.")
    return False


# =========================================================
# INICIAR SESIÓN
# =========================================================

def iniciar_sesion(
    umbral_confianza=60,
    coincidencias_necesarias=6,
    actualizar_modelo=True,
    nuevas_capturas=5
):
    
    #Inicia sesión mediante reconocimiento facial.

    #La cámara se activa inmediatamente, pero el reconocimiento
    #comienza después de una cuenta regresiva de 3 segundos.

    #Devuelve el usuario_id numérico reconocido.

    #Verifica la existencia del Trainer que es el modelo LBPH
    if not os.path.exists(ARCHIVO_MODELO):
        print("No existe el archivo trainer.yml.")
        print("Primero debes registrar un rostro y entrenar el modelo.")
        return None

    try:
        reconocedor = crear_reconocedor()
        reconocedor.read(ARCHIVO_MODELO)

    except Exception as error:
        print("No se pudo cargar el modelo facial.")
        print(f"Detalle: {error}")
        return None

    camara = cv2.VideoCapture(0)

    if not camara.isOpened():
        print("No se pudo abrir la cámara.")
        return None

    usuario_id = None
    coincidencias = 0
    segundos_espera = 3
    tiempo_inicio = time.time()
    inicio_confirmado = False

    print("Mira a la cámara para iniciar sesión.")
    print("El reconocimiento comenzará en 3 segundos.")
    print("Presiona ESC para cancelar.")

    try:
        while True:
            correcto, imagen = camara.read()

            if not correcto:
                print("No se pudo obtener la imagen.")
                break

            # Espejo horizontal para que la imagen sea más natural
            #imagen = cv2.flip(imagen, 1)

            tiempo_transcurrido = time.time() - tiempo_inicio

            # -------------------------------------------------
            # CUENTA REGRESIVA
            # -------------------------------------------------
            if tiempo_transcurrido < segundos_espera:
                segundos_restantes = segundos_espera - int(
                    tiempo_transcurrido
                )

                cv2.putText(
                    imagen,
                    f"Comenzando en {segundos_restantes}...",
                    (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 255),
                    2
                )

                cv2.putText(
                    imagen,
                    "Coloca tu rostro frente a la camara",
                    (20, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 255),
                    2
                )

            # -------------------------------------------------
            # RECONOCIMIENTO FACIAL
            # -------------------------------------------------
            else:
                if not inicio_confirmado:
                    inicio_confirmado = True
                    print("Reconocimiento iniciado.")

                gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

                # Siempre se inicializa antes de utilizarse
                rostros = detector.detectMultiScale(
                    gris,
                    scaleFactor=1.3,
                    minNeighbors=5,
                    minSize=(100, 100)
                )

                usuario_detectado = None

                for x, y, ancho, alto in rostros:
                    rostro = gris[y:y + alto, x:x + ancho]

                    if rostro.size == 0:
                        continue

                    try:
                        id_detectado, confianza = reconocedor.predict(
                            rostro
                        )
                    except cv2.error as error:
                        print(f"Error al reconocer el rostro: {error}")
                        continue

                    if confianza < umbral_confianza:
                        usuario_detectado = int(id_detectado)

                        texto = (
                            f"ID: {id_detectado} | "
                            f"Confianza: {confianza:.1f}"
                        )
                        color = (0, 255, 0)

                    else:
                        texto = (
                            f"No reconocido | "
                            f"Confianza: {confianza:.1f}"
                        )
                        color = (0, 0, 255)

                    cv2.rectangle(
                        imagen,
                        (x, y),
                        (x + ancho, y + alto),
                        color,
                        2
                    )

                    cv2.putText(
                        imagen,
                        texto,
                        (x, max(y - 10, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.65,
                        color,
                        2
                    )

                    # Solo procesa el primer rostro detectado
                    break

                # ---------------------------------------------
                # VALIDAR COINCIDENCIAS
                # ---------------------------------------------
                if usuario_detectado is not None:
                    if usuario_detectado == usuario_id:
                        coincidencias += 1
                    else:
                        usuario_id = usuario_detectado
                        coincidencias = 1

                    cv2.putText(
                        imagen,
                        (
                            f"Verificando: "
                            f"{coincidencias}/"
                            f"{coincidencias_necesarias}"
                        ),
                        (20, 90),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 0),
                        2
                    )

                    if coincidencias >= coincidencias_necesarias:
                        break

                else:
                    usuario_id = None
                    coincidencias = 0

            # La ventana se muestra tanto durante la cuenta regresiva
            # como durante el reconocimiento
            cv2.imshow(
                "Inicio de sesion facial",
                imagen
            )

            tecla = cv2.waitKey(1) & 0xFF

            if tecla == 27:
                print("Inicio de sesión cancelado.")
                usuario_id = None
                break

    finally:
        camara.release()
        cv2.destroyAllWindows()

    if usuario_id is None:
        print("No se reconoció ningún usuario.")
        return None

    # Validar que el ID reconocido exista realmente en la base de datos
    if not existe_usuario(usuario_id):
        print(
            "El rostro fue reconocido, pero el usuario "
            "no existe en usuarios.json."
        )
        return None

    nombre_usuario = obtener_nombre_usuario(usuario_id)

    print(
        f"Inicio de sesión correcto. "
        f"Bienvenido/a, {nombre_usuario}."
    )

    # Capturar imágenes adicionales únicamente después de iniciar sesión
    if actualizar_modelo:
        nuevas_imagenes_guardadas = capturar_nuevas_imagenes(
            usuario_id,
            nuevas_capturas
        )

        if nuevas_imagenes_guardadas:
            if entrenar_modelo():
                print("El modelo facial fue actualizado correctamente.")
            else:
                print("No se pudo actualizar el modelo facial.")

    # Se devuelve el ID numérico para utilizarlo internamente
    return usuario_id



# =========================================================
# OBTENER NOMBRE DESPUÉS DEL INICIO DE SESIÓN
# =========================================================

def obtener_nombre_usuario_reconocido(usuario_id):
    """
    Devuelve el nombre del usuario reconocido.
    """

    return obtener_nombre_usuario(usuario_id)

