from database_json import (
    crear_usuario,
    obtener_usuario,
    obtener_usuarios
)

from face_system import (
    registrar_rostro,
    entrenar_modelo,
    iniciar_sesion
)


def obtener_siguiente_id():
    #Genera automáticamente el siguiente ID numérico disponible.
    

    usuarios = obtener_usuarios()

    if not usuarios:
        return 1

    ids = []

    for usuario_id in usuarios.keys():
        try:
            ids.append(int(usuario_id))
        except ValueError:
            continue

    if not ids:
        return 1

    return max(ids) + 1


def registrar_usuario_menu():
    
    #Registra un usuario solicitando únicamente su nombre.
    #El ID numérico se genera automáticamente.
    

    print("\n===== REGISTRO DE USUARIO =====")

    nombre = input("Introduce tu nombre: ").strip()

    if not nombre:
        print("El nombre no puede estar vacío.")
        return

    # Comprobar si ya existe un usuario con ese nombre
    usuarios = obtener_usuarios()

    for usuario in usuarios.values():
        if usuario.get("nombre", "").lower() == nombre.lower():
            print("Ya existe un usuario registrado con ese nombre.")
            return

    usuario_id = obtener_siguiente_id()

    try:
        crear_usuario(usuario_id, nombre)

        print(f"\nUsuario creado correctamente.")
        print(f"Nombre: {nombre}")

        print("\nComenzará la captura facial.")
        print("Mira a la cámara y sigue las instrucciones.")

        registrar_rostro(usuario_id)

        print("\nCaptura facial completada.")
        print("Entrenando el modelo...")

        entrenar_modelo()

        print("\nRegistro completado correctamente.")
        print("Ya puedes iniciar sesión.")

    except Exception as error:
        print(f"\nError durante el registro: {error}")


def iniciar_sesion_menu():
    
    #Inicia sesión mediante reconocimiento facial.
    

    print("\n===== INICIO DE SESIÓN =====")
    print("Mira a la cámara para identificarte.")

    try:
        usuario_id = iniciar_sesion()

        if usuario_id is None:
            print("No se pudo reconocer el rostro.")
            return None

        usuario = obtener_usuario(usuario_id)

        if usuario is None:
            print("El rostro fue reconocido, pero el usuario no existe.")
            return None

        nombre = usuario.get("nombre", str(usuario_id))

        print(f"\nBienvenido, {nombre}.")

        # Se devuelve el ID porque el resto del sistema
        # puede necesitarlo para guardar el progreso.
        return usuario_id

    except Exception as error:
        print(f"\nError durante el inicio de sesión: {error}")
        return None


def mostrar_menu():
    """
    Menú principal de acceso.
    """

    while True:
        print("\n==============================")
        print("       MENÚ DE ACCESO")
        print("==============================")
        print("1. Registrar usuario")
        print("2. Iniciar sesión")
        print("3. Salir")

        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            registrar_usuario_menu()

        elif opcion == "2":
            usuario_id = iniciar_sesion_menu()

            if usuario_id is not None:
                return usuario_id

        elif opcion == "3":
            print("Hasta luego.")
            return None

        else:
            print("Opción no válida. Inténtalo de nuevo.")


if __name__ == "__main__":
    usuario_id = mostrar_menu()

    if usuario_id is not None:
        print(f"Sesión iniciada correctamente para el usuario {usuario_id}.")
