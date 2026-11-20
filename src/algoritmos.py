def selection_sort(lista):

    arreglo = lista.copy()
    comparaciones = 0

    n = len(arreglo)

    for i in range(n - 1):

        minimo = i

        for j in range(i + 1, n):

            comparaciones += 1

            if arreglo[j] < arreglo[minimo]:
                minimo = j

        arreglo[i], arreglo[minimo] = arreglo[minimo], arreglo[i]

    return arreglo, comparaciones

def merge_sort(lista):
    

    if len(lista) <= 1:
        return lista.copy(), 0

    mitad = len(lista) // 2

    izquierda, comp_izquierda = merge_sort(lista[:mitad])
    derecha, comp_derecha = merge_sort(lista[mitad:])

    resultado = []

    i = 0
    j = 0

    comparaciones = comp_izquierda + comp_derecha

    while i < len(izquierda) and j < len(derecha):

        comparaciones += 1

        if izquierda[i] <= derecha[j]:
            resultado.append(izquierda[i])
            i += 1

        else:
            resultado.append(derecha[j])
            j += 1

    resultado.extend(izquierda[i:])
    resultado.extend(derecha[j:])

    return resultado, comparaciones