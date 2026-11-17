"""Conjunto de datos de entrenamiento para las intenciones conversacionales.

Avance de Proyecto 2 - MBIA2602.
Amplía el vocabulario de ejemplos del Avance de Proyecto 1 (donde cada intención
tenía ~5 frases, suficientes para comparar raíces) a un conjunto más grande y
variado, apto para entrenar un clasificador de Machine Learning (Naive Bayes / SVM).
Mantiene las mismas 6 intenciones + fallback del Asistente virtual de Servicios
Escolares para conservar la coherencia con el Avance de Proyecto 1.
"""

DATASET = [
    # ------------------------------------------------------------------ saludo
    ("hola", "saludo"),
    ("hola buenas", "saludo"),
    ("buenos dias", "saludo"),
    ("buenas tardes", "saludo"),
    ("buenas noches", "saludo"),
    ("que tal", "saludo"),
    ("hola que onda", "saludo"),
    ("hola como estas", "saludo"),
    ("buen dia", "saludo"),
    ("hola necesito ayuda", "saludo"),
    ("hola buenas tardes como estas", "saludo"),
    ("saludos", "saludo"),
    ("hey hola", "saludo"),
    ("ola", "saludo"),
    ("buenas", "saludo"),
    # ----------------------------------------------------- consultar_horario
    ("cual es el horario de atencion", "consultar_horario"),
    ("a que hora abren", "consultar_horario"),
    ("a que hora cierran", "consultar_horario"),
    ("cuando atienden", "consultar_horario"),
    ("horario de servicios escolares", "consultar_horario"),
    ("en que horario puedo ir a servicios escolares", "consultar_horario"),
    ("abren los sabados", "consultar_horario"),
    ("hasta que hora dan servicio", "consultar_horario"),
    ("que dias atienden", "consultar_horario"),
    ("necesito saber el horario de oficinas", "consultar_horario"),
    ("a que hora abre la ventanilla", "consultar_horario"),
    ("estan abiertos los fines de semana", "consultar_horario"),
    ("cual es el horario de servicios escolares los viernes", "consultar_horario"),
    ("que horario tienen", "consultar_horario"),
    ("hay atencion los domingos", "consultar_horario"),
    # ----------------------------------------------------- pagar_colegiatura
    ("como pago mi colegiatura", "pagar_colegiatura"),
    ("quiero pagar la colegiatura", "pagar_colegiatura"),
    ("fecha limite de pago", "pagar_colegiatura"),
    ("donde pago la colegiatura", "pagar_colegiatura"),
    ("cuanto cuesta la colegiatura", "pagar_colegiatura"),
    ("quiero pagar mi colegiatura de noviembre", "pagar_colegiatura"),
    ("cual es la fecha limite de pago", "pagar_colegiatura"),
    ("puedo pagar con tarjeta la colegiatura", "pagar_colegiatura"),
    ("necesito la referencia para pagar", "pagar_colegiatura"),
    ("se me paso la fecha de pago que hago", "pagar_colegiatura"),
    ("hay recargo si pago tarde la colegiatura", "pagar_colegiatura"),
    ("como saco mi ficha de pago", "pagar_colegiatura"),
    ("donde esta el portal de pagos", "pagar_colegiatura"),
    ("quiero liquidar la colegiatura de diciembre", "pagar_colegiatura"),
    ("cuanto tengo que pagar este mes", "pagar_colegiatura"),
    # --------------------------------------------------- solicitar_constancia
    ("necesito una constancia de estudios", "solicitar_constancia"),
    ("como pido una constancia", "solicitar_constancia"),
    ("quiero mi carta de no adeudo", "solicitar_constancia"),
    ("necesito el kardex", "solicitar_constancia"),
    ("como saco una constancia", "solicitar_constancia"),
    ("como descargo mi historial academico", "solicitar_constancia"),
    ("quiero mi constancia de inscripcion", "solicitar_constancia"),
    ("donde solicito la carta de no adeudo", "solicitar_constancia"),
    ("necesito mi kardex para una beca", "solicitar_constancia"),
    ("en cuanto tiempo entregan la constancia", "solicitar_constancia"),
    ("quiero tramitar una constancia de estudios", "solicitar_constancia"),
    ("como obtengo mi historial academico", "solicitar_constancia"),
    ("necesito comprobante de inscripcion", "solicitar_constancia"),
    ("donde descargo la constancia", "solicitar_constancia"),
    ("quiero solicitar mi kardex", "solicitar_constancia"),
    # --------------------------------------------------- soporte_plataforma
    ("no puedo entrar a canvas", "soporte_plataforma"),
    ("olvide mi contrasena", "soporte_plataforma"),
    ("mi correo institucional no funciona", "soporte_plataforma"),
    ("blackboard no carga", "soporte_plataforma"),
    ("no me deja iniciar sesion", "soporte_plataforma"),
    ("canvas marca error", "soporte_plataforma"),
    ("no puedo entrar a mi correo institucional", "soporte_plataforma"),
    ("blackboard se queda cargando", "soporte_plataforma"),
    ("se me olvido la contrasena de canvas", "soporte_plataforma"),
    ("mi usuario esta bloqueado", "soporte_plataforma"),
    ("no carga la plataforma de examenes", "soporte_plataforma"),
    ("tengo un error al entrar a blackboard", "soporte_plataforma"),
    ("no puedo subir mi tarea a canvas", "soporte_plataforma"),
    ("se cerro mi sesion y no puedo volver a entrar", "soporte_plataforma"),
    ("mi correo institucional marca contrasena incorrecta", "soporte_plataforma"),
    # ----------------------------------------------------------- despedida
    ("gracias", "despedida"),
    ("hasta luego", "despedida"),
    ("adios", "despedida"),
    ("eso es todo", "despedida"),
    ("nos vemos", "despedida"),
    ("muchas gracias por tu ayuda", "despedida"),
    ("ya no necesito nada mas", "despedida"),
    ("gracias eso era todo", "despedida"),
    ("bye", "despedida"),
    ("ok gracias hasta pronto", "despedida"),
    ("perfecto gracias adios", "despedida"),
    ("ya quedo gracias", "despedida"),
    ("nos vemos luego", "despedida"),
    ("esta bien gracias por la informacion", "despedida"),
    ("listo gracias", "despedida"),
    # --------------------------------------------------------------- fallback
    ("quiero pizza", "fallback"),
    ("xq no me deja entrar jaja", "fallback"),
    ("cual es la capital de francia", "fallback"),
    ("me puedes contar un chiste", "fallback"),
    ("que clima hace hoy", "fallback"),
    ("cuanto es dos mas dos", "fallback"),
    ("recomiendame una pelicula", "fallback"),
    ("quien gano el partido de ayer", "fallback"),
    ("como se hace un pastel", "fallback"),
    ("cuentame sobre el universo", "fallback"),
    ("hola quiero comprar un boleto de avion", "fallback"),
    ("necesito ayuda con mi tarea de matematicas", "fallback"),
    ("dime un dato curioso", "fallback"),
    ("que opinas de la inteligencia artificial", "fallback"),
    ("ayudame a planear un viaje", "fallback"),
]

INTENCIONES_ORDEN = [
    "saludo",
    "consultar_horario",
    "pagar_colegiatura",
    "solicitar_constancia",
    "soporte_plataforma",
    "despedida",
    "fallback",
]


def textos_y_etiquetas():
    """Devuelve (lista_de_textos, lista_de_etiquetas) listas para vectorizar."""
    textos = [t for t, _ in DATASET]
    etiquetas = [i for _, i in DATASET]
    return textos, etiquetas


if __name__ == "__main__":
    from collections import Counter

    conteo = Counter(etq for _, etq in DATASET)
    print(f"Total de ejemplos: {len(DATASET)}")
    for intencion in INTENCIONES_ORDEN:
        print(f"  {intencion}: {conteo[intencion]} ejemplos")
