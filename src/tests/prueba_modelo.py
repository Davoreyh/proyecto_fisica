
from src.modelo_energia import (
    potencia_adicional,
    energia_analitica,
    energia_euler,
    error_relativo
)

# Datos hipotéticos para probar el modelo
potencia_activa = 3.0
potencia_reposo = 0.5
tiempo = 10.0
paso = 0.01

# 1. Calcular potencia adicional
delta_p = potencia_adicional(
    potencia_activa,
    potencia_reposo
)

# 2. Calcular energía analítica
energia_exacta = energia_analitica(
    delta_p,
    tiempo
)

# 3. Calcular energía mediante Euler
energia_numerica = energia_euler(
    delta_p,
    tiempo,
    paso
)

# 4. Calcular error
error = error_relativo(
    energia_numerica,
    energia_exacta
)

print("MODELO FISICO DE ENERGIA")
print("-------------------------")

print("Potencia activa:", potencia_activa, "W")
print("Potencia en reposo:", potencia_reposo, "W")
print("Potencia adicional:", delta_p, "W")

print("\nEnergia analitica:", energia_exacta, "J")
print("Energia por Euler:", energia_numerica, "J")
print("Error relativo:", error, "%")

assert abs(energia_exacta - 25.0) < 1e-9
assert abs(energia_numerica - energia_exacta) < 1e-9

print("\n¡El modelo fisico funciona correctamente!")
