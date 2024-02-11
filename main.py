import os
import re
import pandas as pd
import pyAgrum as gum

def crearGrafo(tablas: dict[pd.DataFrame], sheet_names) -> gum.BayesNet:
    '''Construye una red bayesiana a partir de tablas de frecuencia.'''
    bn = gum.BayesNet('red-bayesiana')
    for llave in tablas:
        values = list(filter(lambda name: name not in sheet_names, tablas[llave].columns))
        bn.add(gum.LabelizedVariable(llave, llave, values))

    for llave in tablas:
        for column in tablas[llave].columns:
            if column in sheet_names:
                bn.addArc(column, llave)

    cont = 0
    for llave in tablas:
        cont = cont + 1
        for i in range(tablas[llave].shape[0]):
            dependencies = list(filter(lambda name: name in sheet_names, tablas[llave].columns))
            dep_values = list(filter(lambda val: isinstance(val, str), list(tablas[llave].iloc[i].values)))
            values = list(filter(lambda val: not isinstance(val, str), list(tablas[llave].iloc[i].values)))

            if len(dep_values) == 0:
                bn.cpt(llave)[:] = values
                # print("nose",bn.cpt(llave)[:])
            else:
                index = {dependencies[i]: dep_values[i] for i in range(len(dependencies))}
                # print("index",index)
                bn.cpt(llave)[index] = values
                # print(bn.cpt(llave)[index])
    return bn


def limpiarPantalla():
    os.system('cls')


def leerExcel():
    # Pide el nombre del archivo Excel al usuario
    nombrexlsx = input("Ingrese el nombre del documento XLSX (incluya la extensión .xlsx): ")

    # Verifica si el archivo existe
    if os.path.exists(nombrexlsx):
        # Si existe, lee todas las hojas de cálculo del archivo de Excel
        try:
            df = pd.read_excel(nombrexlsx, sheet_name=None)

            # Obtiene los nombres de las hojas
            sheet_names = list(df.keys())

            imprimirTablas(df)
            menu(sheet_names, df)

        except Exception as e:
            print(f"Ocurrió un error al leer el archivo: {e}")
    else:
        # Si el archivo no existe, informa al usuario
        print("El archivo no existe. Por favor, verifique el nombre y la ubicación del archivo.")


# Función para obtener X y E de la entrada
def obtener_X_E(entrada):
    proba_compuesta = re.search(r'P\((.*?)\|', entrada)
    if proba_compuesta:
        X = proba_compuesta.group(1)
    else:
        X = None
    e_match = re.search(r'\|(.*)\)', entrada)
    if e_match:
        E = re.split(r'\^', e_match.group(1))
    else:
        E = []
    return X, E


# Función para buscar sheet_names en el DataFrame
def buscar_sheet_names(df, X, sheet_names):
    sheet_names_encontrados = []

    for sheet_name, tabla in df.items():
        if sheet_name == X:
            sheet_names_encontrados.append(sheet_name)
            break

    for sheet_name, tabla in df.items():
        columnas = tabla.columns.to_list()
        for sheet in sheet_names:
            if sheet in columnas:
                columnas.remove(sheet)
        if X in columnas and sheet_name not in sheet_names_encontrados:
            sheet_names_encontrados.append(sheet_name)

    return sheet_names_encontrados


# Función para buscar sheet_names basados en E
def buscar_sheet_names_con_E(df, E, sheet_names):
    sheet_names_encontrados = []

    for e in E:
        for sheet_name, tabla in df.items():
            columnas = tabla.columns.to_list()
            if e in columnas and sheet_name not in sheet_names_encontrados:
                sheet_names_encontrados.append(sheet_name)

    return sheet_names_encontrados


# Función principal
def calcularProba(valores, bn, sheet_names_encontrados):  # valores=X y E   bn=red   sheet_names_encontrados=Tablas
    # Función interna para obtener la probabilidad simple de una variable
    def obtener_probabilidad_simple(nombre_tabla, valor):
        return float(bn.cpt(nombre_tabla)[{nombre_tabla: valor}])

    # calcula la probabilidad condicional de la variable en la red bayesiana, teniendo en cuenta sus dependencias.
    def obtener_probabilidad_condicional(nombre_tabla, valor, info_valores):
        deps = list(bn.parents(nombre_tabla))
        nombre_dependencias = [bn.cpt(i).names[0] for i in deps]

        condiciones = {nombre_tabla: valor}
        for val, nombre in info_valores:
            if nombre in nombre_dependencias:
                condiciones[nombre] = val
        return float(bn.cpt(nombre_tabla)[condiciones])

    # Combinar los valores y los nombres de las tablas
    info_valores = list(zip(valores, sheet_names_encontrados))
    prob = 1.0

    # Calcular la probabilidad total iterando a través de los valores y tablas
    for val, nombre_tabla in info_valores:
        if len(list(bn.parents(nombre_tabla))) == 0:
            # Si no hay dependencias, usar probabilidad simple
            prob *= obtener_probabilidad_simple(nombre_tabla, val)
        else:
            # Si hay dependencias, usar probabilidad condicional
            prob *= obtener_probabilidad_condicional(nombre_tabla, val, info_valores)

    return prob


def inferenciaBayesiana(sheet_names, df, entrada):
    def normalizar(resultados):
        suma_total = sum(resultados)
        return [resultado / suma_total for resultado in resultados]

    X, E = obtener_X_E(entrada)
    print("X:", X)
    print("E:", E)

    bn = crearGrafo(df, sheet_names)
    resultados = []

    if X in sheet_names:
        ValoresX = bn.cpt(X).variablesSequence()[0].labels()
        for i in ValoresX:
            resultado = inferenciaParidad(i, E, sheet_names, df, bn)
            resultados.append(resultado)
    else:
        resultado = inferenciaParidad(X, E, sheet_names, df, bn)
        resultados.append(resultado)

    print("Resultados sin normalizar:")
    for resultado in resultados:
        print(resultado)

    resultados_normalizados = normalizar(resultados)

    print("Resultados normalizados:")
    for resultado in resultados_normalizados:
        print(resultado)

    return resultados_normalizados


def inferenciaParidad(X, E, sheet_names, df, bn):
    sheet_names_encontrados = []
    # nombre_nodo = "Tren"
    # cpt = bn.cpt(nombre_nodo)
    # print(cpt)
    for sheet_name, tabla in df.items():
        columnas = tabla.columns.to_list()

        if X and X in columnas:
            sheet_names_encontrados.insert(0, sheet_name)

        for e in E:
            if e in columnas and sheet_name not in sheet_names_encontrados:
                sheet_names_encontrados.append(sheet_name)

    print("\t---- Sheet names Encontrados ---")
    print(sheet_names_encontrados, "\n")

    Y = [sheet_name for sheet_name in sheet_names if sheet_name not in sheet_names_encontrados]
    sheet_names_encontradosY = sheet_names_encontrados.copy()
    print("Elementos no encontrados [Y]:")
    for elemento in Y:
        print(elemento)

    sumProbas = 0
    sheet_names_encontradosY += Y
    if Y:
        ValoresY = bn.cpt(elemento).variablesSequence()[0].labels()
        for valor in ValoresY:
            elementosPregunta = E.copy()
            elementosPregunta.insert(0, X)
            elementosPregunta.append(valor)
            probabilidad = calcularProba(elementosPregunta, bn, sheet_names_encontradosY)
            elementosPregunta.pop()
            sumProbas += probabilidad
    else:
        elementosPregunta = E.copy()
        elementosPregunta.insert(0, X)
        probabilidad = calcularProba(elementosPregunta, bn, sheet_names_encontrados)
        elementosPregunta.pop()
        sumProbas += probabilidad
    return sumProbas

def imprimirTablas(df):
    for sheet_name, tabla in df.items():
        print("\t" + "--" + sheet_name + "--")
        print(tabla)
        print("\n")

def menu(sheet_names, df):
    limpiarPantalla()
    print("\tELIJA UNA OPCION")
    print("1. Inferencia Bayesiana")
    print("2. imprimir tablas")
    print("--------------------")
    opcion = input("Opcion: ")

    if opcion == "1":
        print("FORMATO: P(X|E)")
        entrada = input("Buscar probabilidad: ")
        inferenciaBayesiana(sheet_names, df, entrada)

    elif opcion == "2":
        imprimirTablas(df)

leerExcel()
