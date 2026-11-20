from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

from modelo_energia import analizar_medicion
from prediccion import generar_predicciones

BASE = Path(__file__).resolve().parents[1]

ARCHIVOS = [
    BASE / "datos_experimentales" / "resultados_energia" / "resultados.csv",
    BASE / "datos_experimentales" / "resultados_energia_rep2" / "resultados.csv",
    BASE / "datos_experimentales" / "resultados_energia_rep3" / "resultados.csv"
]

CARPETA_RESULTADOS = BASE / "resultados" / "analisis"
CARPETA_FIGURAS = BASE / "figuras"

CARPETA_RESULTADOS.mkdir(parents=True, exist_ok=True)
CARPETA_FIGURAS.mkdir(parents=True, exist_ok=True)


COLUMNAS = [
    "algoritmo",
    "n",
    "ejecuciones",
    "duracion_s",
    "potencia_media_cpu_W",
    "potencia_reposo_W",
    "energia_adicional_por_ordenamiento_J",
    "tiempo_por_ordenamiento_s"
]

tablas = []

for numero, archivo in enumerate(ARCHIVOS, start=1):

    if not archivo.exists():
        raise FileNotFoundError(
            f"No se encontro el archivo: {archivo}"
        )

    datos = pd.read_csv(archivo)

    for columna in COLUMNAS:
        if columna not in datos.columns:
            raise ValueError(
                f"Falta la columna {columna} en {archivo}"
            )

    datos = datos[COLUMNAS].copy()
    datos["repeticion"] = numero

    tablas.append(datos)


todos = pd.concat(tablas, ignore_index=True)

resultados_modelo = []

for _, fila in todos.iterrows():

    resultado = analizar_medicion(
        potencia_activa=fila["potencia_media_cpu_W"],
        potencia_reposo=fila["potencia_reposo_W"],
        duracion=fila["duracion_s"],
        ejecuciones=fila["ejecuciones"],
        paso=0.01
    )

    resultados_modelo.append(resultado)


modelo = pd.DataFrame(resultados_modelo)

todos = pd.concat(
    [todos.reset_index(drop=True), modelo],
    axis=1
)


comparacion = todos[
    [
        "algoritmo",
        "n",
        "repeticion",
        "energia_adicional_por_ordenamiento_J",
        "energia_por_ordenamiento_J"
    ]
].copy()

comparacion["diferencia_absoluta_J"] = (
    comparacion["energia_por_ordenamiento_J"]
    - comparacion["energia_adicional_por_ordenamiento_J"]
).abs()

comparacion["error_relativo_pct"] = (
    comparacion["diferencia_absoluta_J"]
    / comparacion["energia_adicional_por_ordenamiento_J"].abs()
    .where(
        comparacion["energia_adicional_por_ordenamiento_J"] != 0
    )
) * 100

comparacion.to_csv(
    CARPETA_RESULTADOS / "comparacion_energia_modelo.csv",
    index=False
)

print("\nCOMPARACION ENTRE ENERGIA ORIGINAL Y MODELO FISICO")
print("--------------------------------------------------")

print(
    comparacion.to_string(
        index=False,
        float_format=lambda x: f"{x:.12f}"
    )
)

print("\nTabla comparativa guardada correctamente.")



todos["diferencia_energia_J"] = (
    todos["energia_por_ordenamiento_J"]
    - todos["energia_adicional_por_ordenamiento_J"]
)

todos["diferencia_tiempo_s"] = (
    todos["tiempo_modelo_por_ordenamiento_s"]
    - todos["tiempo_por_ordenamiento_s"]
)


print("\nCOMPROBACION DEL MODELO FISICO")
print("--------------------------------")

print(
    todos[
        [
            "algoritmo",
            "n",
            "repeticion",
            "energia_adicional_por_ordenamiento_J",
            "energia_por_ordenamiento_J",
            "energia_euler_J",
            "error_euler_pct"
        ]
    ].to_string(index=False)
)


todos.to_csv(
    CARPETA_RESULTADOS / "resultados_combinados.csv",
    index=False
)


resumen = (
    todos.groupby(["algoritmo", "n"])
    .agg(
        energia_media=(
            "energia_por_ordenamiento_J",
            "mean"
        ),

        energia_desviacion=(
            "energia_por_ordenamiento_J",
            "std"
        ),

        tiempo_medio=(
            "tiempo_por_ordenamiento_s",
            "mean"
        ),

        tiempo_desviacion=(
            "tiempo_por_ordenamiento_s",
            "std"
        ),

        numero_repeticiones=("repeticion", "count")
    )
    .reset_index()
)


print("\nRESUMEN ESTADISTICO DEL MODELO")
print("--------------------------------")

print(
    resumen.to_string(
        index=False,
        float_format=lambda x: f"{x:.9f}"
    )
)


resumen.to_csv(
    CARPETA_RESULTADOS / "resumen_estadistico.csv",
    index=False
)


predicciones = generar_predicciones(
    resumen,
    CARPETA_RESULTADOS
)

plt.figure(figsize=(9, 6))

for algoritmo, grupo in resumen.groupby("algoritmo"):

    grupo = grupo.sort_values("n")

    plt.errorbar(
        grupo["n"],
        grupo["energia_media"],
        yerr=grupo["energia_desviacion"],
        marker="o",
        capsize=5,
        label=algoritmo
    )

plt.xlabel("Tamano de entrada (n)")
plt.ylabel("Energia adicional (J/ordenamiento)")
plt.title("Energia adicional frente al tamano de entrada")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    CARPETA_FIGURAS / "energia_vs_tamano.png",
    dpi=300
)

plt.show()


plt.figure(figsize=(9, 6))

for algoritmo, grupo in resumen.groupby("algoritmo"):

    grupo = grupo.sort_values("n")

    plt.errorbar(
        grupo["n"],
        grupo["tiempo_medio"],
        yerr=grupo["tiempo_desviacion"],
        marker="o",
        capsize=5,
        label=algoritmo
    )

plt.xlabel("Tamano de entrada (n)")
plt.ylabel("Tiempo por ordenamiento (s)")
plt.title("Tiempo de ejecucion frente al tamano de entrada")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    CARPETA_FIGURAS / "tiempo_vs_tamano.png",
    dpi=300
)

plt.show()


print("\nAnalisis experimental completado.")
print("El modelo fisico se aplico a todas las mediciones.")
