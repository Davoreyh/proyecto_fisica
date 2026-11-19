from src.algoritmos import selection_sort, merge_sort


# Lista de prueba
datos = [8, 3, 5, 1, 9, 2]

# Resultado que esperamos
esperado = [1, 2, 3, 5, 8, 9]


# Probamos Selection Sort
resultado_selection, comparaciones_selection = selection_sort(datos)

print("SELECTION SORT")
print("Lista ordenada:", resultado_selection)
print("Comparaciones:", comparaciones_selection)

assert resultado_selection == esperado


# Probamos Merge Sort
resultado_merge, comparaciones_merge = merge_sort(datos)

print("\nMERGE SORT")
print("Lista ordenada:", resultado_merge)
print("Comparaciones:", comparaciones_merge)

assert resultado_merge == esperado


# Verificamos que la lista original no cambió
assert datos == [8, 3, 5, 1, 9, 2]

print("\n¡Todas las pruebas fueron exitosas!")