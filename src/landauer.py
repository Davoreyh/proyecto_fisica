import math

# Constante de Boltzmann en J/K
K_B = 1.380649e-23


def energia_minima_por_bit(temperatura):
    """
    Calcula el límite de Landauer para borrar
    irreversiblemente un bit de información.

    E_min = k_B * T * ln(2)

    Temperatura: kelvin (K)
    Resultado: joules (J)
    """

    if temperatura <= 0:
        raise ValueError("La temperatura debe ser mayor que cero.")

    return K_B * temperatura * math.log(2)


def energia_borrado(bits, temperatura):
    """
    Calcula el límite energético para borrar
    una cantidad determinada de bits.
    """

    if bits < 0:
        raise ValueError("La cantidad de bits no puede ser negativa.")

    return bits * energia_minima_por_bit(temperatura)
