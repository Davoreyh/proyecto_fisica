    
def potencia_adicional(potencia_activa, potencia_reposo):
    """
    ΔP = P_activa - P_reposo

    Unidad: watts (W).
    """
    return potencia_activa - potencia_reposo


def energia_analitica(delta_p, tiempo):
    """
    E = ΔP * t

    Unidad: joules (J).
    """
    if tiempo < 0:
        raise ValueError("El tiempo no puede ser negativo.")

    return delta_p * tiempo

def energia_euler(delta_p, tiempo, paso):
    """
    E[i+1] = E[i] + ΔP * Δt

    delta_p: potencia adicional en W.
    tiempo: duración total en segundos.
    paso: intervalo de integración en segundos.
    """

    if tiempo < 0:
        raise ValueError("El tiempo no puede ser negativo.")

    if paso <= 0:
        raise ValueError("El paso debe ser positivo.")

    energia = 0.0
    tiempo_actual = 0.0

    while tiempo_actual < tiempo:

        dt = min(paso, tiempo - tiempo_actual)

        energia += delta_p * dt

        tiempo_actual += dt

    return energia

def error_relativo(valor_numerico, valor_analitico):

    if valor_analitico == 0:
        return None

    return (
        abs(valor_numerico - valor_analitico)
        / abs(valor_analitico)
    ) * 100


def analizar_medicion(
    potencia_activa,
    potencia_reposo,
    duracion,
    ejecuciones,
    paso=0.01
):
    """
    Calcula:
    Potencia adicional.
    Energía adicional total.
    Energía adicional por ordenamiento.
    Energía mediante Euler.
    Tiempo por ordenamiento.
    """

    if duracion < 0:
        raise ValueError("La duración no puede ser negativa.")

    if ejecuciones <= 0:
        raise ValueError("Las ejecuciones deben ser mayores que cero.")

    delta_p = potencia_adicional(
        potencia_activa,
        potencia_reposo
    )

    energia_total = energia_analitica(
        delta_p,
        duracion
    )

    energia_numerica = energia_euler(
        delta_p,
        duracion,
        paso
    )

    energia_por_ordenamiento = energia_total / ejecuciones

    tiempo_por_ordenamiento = duracion / ejecuciones

    error_euler = error_relativo(
        energia_numerica,
        energia_total
    )

    return {
        "potencia_adicional_W": delta_p,
        "energia_total_modelo_J": energia_total,
        "energia_euler_J": energia_numerica,
        "energia_por_ordenamiento_J": energia_por_ordenamiento,
        "tiempo_modelo_por_ordenamiento_s": tiempo_por_ordenamiento,
        "error_euler_pct": error_euler
    }
