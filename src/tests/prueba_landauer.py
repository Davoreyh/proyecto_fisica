
from src.landauer import (
    energia_minima_por_bit,
    energia_borrado
)

# Temperatura de referencia
temperatura = 300

# Ejemplos teóricos
bits = [1, 1_000_000, 1_000_000_000]

print("PRINCIPIO DE LANDAUER")
print("--------------------")
print("Temperatura:", temperatura, "K")

energia_bit = energia_minima_por_bit(temperatura)

print("\nEnergia minima por bit:")
print(f"{energia_bit:.4e} J")

print("\nEjemplos teoricos:")

for cantidad in bits:

    energia = energia_borrado(cantidad, temperatura)

    print(
        f"{cantidad:,} bits: "
        f"{energia:.4e} J"
    )

print("\n¡Modelo de Landauer funcionando!")
