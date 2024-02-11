import os
import re
import pandas as pd


def limpiarPantalla():
    os.system('clear')


def leerExcel():
    # Lee todas las hojas de cálculo del archivo de Excel
    df = pd.read_excel("probabilidades.xlsx", sheet_name=None)

    # Obtiene los nombres de las hojas y conviértelos en una lista
    sheet_names = list(df.keys())

    tablas = []

    if sheet_names:
        # Guarda los nombres en una lista
        for hoja in sheet_names:
            tablas.append(df[hoja])

        # Imprime los nombres en una lista
        for i in tablas:
            print(i)
            print("\n")

    else:
        print("No se encontraron hojas en el archivo Excel.")

    menu(sheet_names, tablas)


def inferenciaBayesiana(sheet_names, tablas, entrada):
    proba_compuesta = re.search(r'P\((.*?)\|', entrada)

    if entrada:
        X = proba_compuesta.group(1)
    else:
        X = None

    # Utiliza una expresión regular para extraer "Ligera" y "No" como elementos en la lista E
    e_match = re.search(r'\|(.*)\)', entrada)
    if e_match:
        E = re.split(r'\^', e_match.group(1))
    else:
        E = []

    # probIndividual(tablas)
    # print(probIndividual(tablas))

    print("X:", X)
    print("E:", E)
    print("\n")

    # -----Bucar los valores que si tenemos para encontrar los que no tenemos
    # Buscar en los sheets directamente con la entrada Si es el nombre del sheet (Este ciclo solo funciona con la variable X)
    sheet_names_encontrados = [];
    lista_col = [];
    it_sheet = 0
    for sheet in sheet_names:
        if sheet == X:
            sheet_names_encontrados.append(sheet)
            print("ENCONTRE SHEET ", it_sheet, ":", sheet_names_encontrados[0])
            break
        else:
            it_sheet = it_sheet + 1

    # Buscar los demas sheets buscando dentro de las tablas los nombres no son iguales a los sheets (Este ciclo sirve con los valores de E y de X)
    for tabla in tablas:
        columnas = tabla.columns.to_list()

        # Este ciclo es para eliminar el nombre de los sheets de las columnas
        for sheet in sheet_names:
            if sheet in columnas:
                columnas.remove(sheet)

        lista_col.append(columnas)
    # -----------------------------------------------------------

    conta = 0
    for lista in lista_col:
        for elemento in lista:
            if (X == elemento):
                sheet_names_encontrados.append(sheet_names[conta])
        print()  # Agrega una línea en blanco después de cada lista interna
        conta += 1

    for e in E:
        for conta, lista in enumerate(lista_col):  # Usar enumerate para obtener el índice
            for elemento in lista:
                if e == elemento:
                    sheet_names_encontrados.append(sheet_names[conta])

    print("\t---- Sheet names Encontrados ---")
    print(sheet_names_encontrados, "\n")

    Y = []
    for sheet_name in sheet_names:
        if sheet_name not in sheet_names_encontrados:
            Y.append(sheet_name)

    print("Elementos no encontrados [Y]:")
    for elemento in Y:
        print(elemento)


"""
def probIndividual(tablas):
    if tablas:
        primera_tabla = tablas[0]
        none_values = primera_tabla.loc[0, "None"]
        return 1-none_values
    else:
        print("No hay informacion de tablas")
"""


def imprimirTablas(sheet_names, tablas):
    i = 0
    for tabla in tablas:
        print("\t" + "--" + sheet_names[i] + "--")
        i = i + 1
        print(tabla)
        print("\n")


def menu(sheet_names, tablas):
    limpiarPantalla()
    print("\tELIJA UNA OPCION")
    print("1. Inferencia Bayesiana")
    print("2. imprimir tablas")
    print("--------------------")
    opcion = input("Opcion: ")

    if opcion == "1":
        print("FORMATO: P(X|E)")
        entrada = input("Buscar probabilidad: ")
        inferenciaBayesiana(sheet_names, tablas, entrada)

    elif opcion == "2":
        imprimirTablas(sheet_names, tablas)


leerExcel()