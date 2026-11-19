from pathlib import Path
import math
import pandas as pd


def trabajo_algoritmo(algoritmo, n):
    """
    Funcion que representa el crecimiento del trabajo
    computacional de cada algoritmo.
    """

    if algoritmo == "Selection Sort":
        return n * (n - 1) / 2

    elif algoritmo == "Merge Sort":
        return n * math.log2(n)

    else:
        raise ValueError(f"Algoritmo desconocido: {algoritmo}")


def ajustar_modelo(datos_calibracion, algoritmo):
    """
    Ajusta el coeficiente energetico usando los tamaños
    de entrada destinados a calibracion.
    """

    trabajos = []
    energias = []

    for _, fila in datos_calibracion.iterrows():
        trabajo = trabajo_algoritmo(
            algoritmo,
            fila["n"]
        )

        trabajos.append(trabajo)
        energias.append(fila["energia_media"])

    numerador = sum(
        trabajo * energia
        for trabajo, energia in zip(trabajos, energias)
    )

    denominador = sum(
        trabajo ** 2
        for trabajo in trabajos
    )

    if denominador == 0:
        raise ValueError("No se puede ajustar el modelo.")

    return numerador / denominador


def generar_predicciones(resumen, carpeta_resultados):
    """
    Calibra el modelo con n=500 y n=1000.
    Predice la energia para n=2000.
    Compara la prediccion con la medicion experimental.
    """

    tamanos_calibracion = [500, 1000]
    tamano_validacion = 2000

    resultados = []

    for algoritmo, grupo in resumen.groupby("algoritmo"):

        calibracion = grupo[
            grupo["n"].isin(tamanos_calibracion)
        ]

        validacion = grupo[
            grupo["n"] == tamano_validacion
        ]

        if len(calibracion) != 2:
            raise ValueError(
                f"Faltan datos de calibracion para {algoritmo}."
            )

        if len(validacion) != 1:
            raise ValueError(
                f"Falta la medicion de validacion para {algoritmo}."
            )

        # Ajustar el coeficiente con 500 y 1000
        coeficiente = ajustar_modelo(
            calibracion,
            algoritmo
        )

        # Obtener el valor medido para 2000
        fila_validacion = validacion.iloc[0]

        energia_medida = fila_validacion["energia_media"]

        trabajo_validacion = trabajo_algoritmo(
            algoritmo,
            tamano_validacion
        )

        # Calcular la prediccion
        energia_predicha = (
            coeficiente * trabajo_validacion
        )

        # Calcular el error relativo porcentual
        error_relativo = (
            abs(energia_predicha - energia_medida)
            / abs(energia_medida)
        ) * 100

        resultados.append({
            "algoritmo": algoritmo,
            "tamanos_calibracion": "500 y 1000",
            "tamano_validacion": tamano_validacion,
            "coeficiente_energetico": coeficiente,
            "energia_predicha_J": energia_predicha,
            "energia_medida_J": energia_medida,
            "error_relativo_pct": error_relativo
        })

    tabla_predicciones = pd.DataFrame(resultados)

    # Guardar los resultados
    carpeta_resultados = Path(carpeta_resultados)
    carpeta_resultados.mkdir(
        parents=True,
        exist_ok=True
    )

    archivo_salida = (
        carpeta_resultados / "validacion_modelo.csv"
    )

    tabla_predicciones.to_csv(
        archivo_salida,
        index=False
    )

    print("\nVALIDACION DEL MODELO PREDICTIVO")
    print("--------------------------------")

    print(
        tabla_predicciones.to_string(
            index=False,
            float_format=lambda x: f"{x:.8f}"
        )
    )

    print("\nPredicciones guardadas correctamente.")

    return tabla_predicciones
