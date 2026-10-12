import json
import os


RUTA_JSON = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "usuarios.json"
)


def cargar_usuarios():
    """
    Carga los usuarios desde usuarios.json.

    Devuelve un diccionario vacío si el archivo no existe,
    está vacío o contiene un formato incorrecto.
    """

    if not os.path.exists(RUTA_JSON):
        return {}

    try:
        with open(RUTA_JSON, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

        if not isinstance(datos, dict):
            return {}

        # Normalizar las claves para que todos los IDs sean texto.
        usuarios_normalizados = {}

        for usuario_id, datos_usuario in datos.items():
            usuario_id = str(usuario_id).strip()

            if not isinstance(datos_usuario, dict):
                datos_usuario = {}

            datos_usuario.setdefault("nombre", usuario_id)
            datos_usuario.setdefault("modos_completados", {})

            if not isinstance(datos_usuario["modos_completados"], dict):
                datos_usuario["modos_completados"] = {}

            usuarios_normalizados[usuario_id] = datos_usuario

        return usuarios_normalizados

    except json.JSONDecodeError:
        print("Error: el archivo usuarios.json está dañado.")
        return {}

    except OSError as error:
        print(f"Error al leer usuarios.json: {error}")
        return {}


def guardar_usuarios(usuarios):
    """
    Guarda los usuarios en usuarios.json.

    Todas las claves de usuario se convierten a texto antes de guardar.
    """

    usuarios_normalizados = {}

    for usuario_id, datos_usuario in usuarios.items():
        usuario_id = str(usuario_id).strip()

        if not isinstance(datos_usuario, dict):
            datos_usuario = {}

        datos_usuario.setdefault("nombre", usuario_id)
        datos_usuario.setdefault("modos_completados", {})

        usuarios_normalizados[usuario_id] = datos_usuario

    try:
        with open(RUTA_JSON, "w", encoding="utf-8") as archivo:
            json.dump(
                usuarios_normalizados,
                archivo,
                indent=4,
                ensure_ascii=False
            )

    except OSError as error:
        print(f"Error al guardar usuarios.json: {error}")


def obtener_usuarios():
    """
    Devuelve todos los usuarios registrados.
    """

    return cargar_usuarios()


def obtener_usuario(usuario_id):
    """
    Busca un usuario por su ID.

    Devuelve los datos del usuario si existe.
    Devuelve None si no existe.
    """

    usuario_id = str(usuario_id).strip()
    usuarios = cargar_usuarios()

    return usuarios.get(usuario_id)


def obtener_nombre_usuario(usuario_id):
    """
    Obtiene el nombre asociado a un ID.

    Si el usuario no existe o no tiene nombre,
    devuelve el propio ID como respaldo.
    """

    usuario_id = str(usuario_id).strip()
    usuario = obtener_usuario(usuario_id)

    if usuario is None:
        return usuario_id

    nombre = usuario.get("nombre", usuario_id)

    if not nombre:
        return usuario_id

    return str(nombre).strip()


def existe_usuario(usuario_id):
    """
    Comprueba si existe un usuario con el ID indicado.
    """

    usuario_id = str(usuario_id).strip()
    usuarios = cargar_usuarios()

    return usuario_id in usuarios


def existe_nombre_usuario(nombre):
    """
    Comprueba si ya existe un usuario con ese nombre.

    La comparación no distingue entre mayúsculas y minúsculas.
    """

    nombre = str(nombre).strip().lower()

    if not nombre:
        return False

    usuarios = cargar_usuarios()

    for datos_usuario in usuarios.values():
        nombre_guardado = str(
            datos_usuario.get("nombre", "")
        ).strip().lower()

        if nombre_guardado == nombre:
            return True

    return False


def crear_usuario(usuario_id, nombre):
    """
    Crea un usuario nuevo en usuarios.json.

    El ID se utiliza internamente para el reconocimiento facial,
    mientras que el nombre se muestra en la interfaz.
    """

    usuario_id = str(usuario_id).strip()
    nombre = str(nombre).strip()

    if not usuario_id:
        raise ValueError("El ID del usuario no puede estar vacío.")

    if not nombre:
        raise ValueError("El nombre del usuario no puede estar vacío.")

    usuarios = cargar_usuarios()

    if usuario_id in usuarios:
        raise ValueError("El usuario ya existe.")

    usuarios[usuario_id] = {
        "nombre": nombre,
        "modos_completados": {}
    }

    guardar_usuarios(usuarios)

    return usuarios[usuario_id]

def obtener_modos_completados(usuario_id):
    """
    Obtiene los modos completados por el usuario.
    """
    usuario_id = str(usuario_id)
    usuarios = cargar_usuarios()

    if usuario_id not in usuarios:
        crear_usuario(usuario_id)
        usuarios = cargar_usuarios()

    if "modos_completados" not in usuarios[usuario_id]:
        usuarios[usuario_id] = {
            "modos_completados": {}
        }

        guardar_usuarios(usuarios)

    return usuarios[usuario_id]["modos_completados"]


def guardar_modo_completado(usuario_id, modo, dificultad):
    """
    Guarda una dificultad completada dentro de un modo.
    """
    usuario_id = str(usuario_id)
    modo = str(modo).lower().strip()
    dificultad = str(dificultad).lower().strip()

    usuarios = cargar_usuarios()

    if usuario_id not in usuarios:
        usuarios[usuario_id] = {
            "modos_completados": {}
        }

    if "modos_completados" not in usuarios[usuario_id]:
        usuarios[usuario_id]["modos_completados"] = {}

    modos_completados = usuarios[usuario_id]["modos_completados"]

    if modo not in modos_completados:
        modos_completados[modo] = []

    if dificultad not in modos_completados[modo]:
        modos_completados[modo].append(dificultad)

    guardar_usuarios(usuarios)


def verificar_modo_completado(usuario_id, modo, dificultad):
    """
    Devuelve True si el usuario completó ese modo y dificultad.
    """
    modo = str(modo).lower().strip()
    dificultad = str(dificultad).lower().strip()

    modos_completados = obtener_modos_completados(usuario_id)

    return dificultad in modos_completados.get(modo, [])
