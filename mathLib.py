import math as mt
from math import isclose

def MxM(m1, m2):
    r = [[0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]]

    for i in range(len(m1)):
        for j in range(len(m2[0])):
            for k in range(len(m1[0])):
                r[i][j] += m1[i][k]*m2[k][j]
    return r

def MxV(v, m):
    if len(v) == len(m):
        C = [0,0,0,0]

        for i in range(len(v)):
            for j in range(len(m[0])):
                C[i] += m[i][j] * v[j]

        return C

def MsubM(A,B):
     if isinstance(A,list):
         return [ MsubM(ra,rb) for ra,rb in zip(A,B) ]
     else:
         return A-B
     
def MplusM(A,B):
     if isinstance(A,list):
         return [ MsubM(ra,rb) for ra,rb in zip(A,B) ]
     else:
         return A+B

def barycentricCoords(A, B, C, P):
    
    # Se saca el �rea de los subtri�ngulos y del tri�ngulo
    # mayor usando el Shoelace Theorem, una f�rmula que permite
    # sacar el �rea de un pol�gono de cualquier cantidad de v�rtices.

    areaPCB = abs((P[0]*C[1] + C[0]*B[1] + B[0]*P[1]) - 
                  (P[1]*C[0] + C[1]*B[0] + B[1]*P[0]))

    areaACP = abs((A[0]*C[1] + C[0]*P[1] + P[0]*A[1]) - 
                  (A[1]*C[0] + C[1]*P[0] + P[1]*A[0]))

    areaABP = abs((A[0]*B[1] + B[0]*P[1] + P[0]*A[1]) - 
                  (A[1]*B[0] + B[1]*P[0] + P[1]*A[0]))

    areaABC = abs((A[0]*B[1] + B[0]*C[1] + C[0]*A[1]) - 
                  (A[1]*B[0] + B[1]*C[0] + C[1]*A[0]))

    # Si el �rea del tri�ngulo es 0, retornar nada para
    # prevenir divisi�n por 0.
    if areaABC == 0:
        return None

    # Determinar las coordenadas baric�ntricas dividiendo el 
    # �rea de cada subtri�ngulo por el �rea del tri�ngulo mayor.
    u = areaPCB / areaABC
    v = areaACP / areaABC
    w = areaABP / areaABC

    # Si cada coordenada est� entre 0 a 1 y la suma de las tres
    # es igual a 1, entonces son v�lidas.
    if 0<=u<=1 and 0<=v<=1 and 0<=w<=1 and isclose(u+v+w, 1.0):
        return (u, v, w)
    else:
        return None

#Menor de la matriz
def minor(matrix,i,j):
    return [row[:j] + row[j+1:] for row in (matrix[:i]+matrix[i+1:])]

#Determinante
def determinant(matrix):
    if len(matrix) == 2: #case for 2x2 matrix
        return matrix[0][0]*matrix[1][1]-matrix[0][1]*matrix[1][0]
    det = 0
    for c in range(len(matrix)):
        det += ((-1)**c)*matrix[0][c]*determinant(minor(matrix,0,c))
    return det

#Inversa de la matriz
def inverseMatrix(mx):
    det = determinant(mx)
    if(det==0):
        print('Determinant is zero')
        return
    if len(mx) == 2: #case for 2x2 matrix 
        return [[mx[1][1]/det, -1*mx[0][1]/det],
                [-1*mx[1][0]/det, mx[0][0]/det]]
    cofactors = []
    for i in range(len(mx)):
        cRow = []
        for j in range(len(mx)):
            minorValue = minor(mx,i,j)
            cRow.append(((-1)**(i+j)) * determinant(minorValue))
        cofactors.append(cRow)
        
    inverse = list(map(list,zip(*cofactors)))
    for i in range(len(inverse)):
        for j in range(len(inverse)):
            inverse[i][j] = inverse[i][j]/det
    return inverse

#Resta de vectores
def substractV(v1, v2):
    if len(v1) != len(v2):
        raise ValueError("Se necesitan vectores de la misma magnitud.")

    r = [v1[i] - v2[i] for i in range(len(v1))]
    return r

#Suma de vectores
def addV(v1, v2):
    if len(v1) != len(v2):
        raise ValueError("Se necesitan vectores de la misma magnitud.")

    r = [v1[i] + v2[i] for i in range(len(v1))]
    return r

#Multiplicacion de vectores
def mulV(v1, v2):
    if len(v1) != len(v2):
        raise ValueError("Se necesitan vectores de la misma magnitud.")

    r = [v1[i] * v2[i] for i in range(len(v1))]
    return r

#Producto cruz
def crossProd(a,b):
    cross_product = [a[1] * b[2] - a[2] * b[1],
                     a[2] * b[0] - a[0] * b[2],
                     a[0] * b[1] - a[1] * b[0]]
    return cross_product

#Normalizacion
def normalizeV(vector):
    vectorList = list(vector)
    mag = mt.sqrt(sum(e ** 2 for e in vectorList))
    if mag == 0: #error if magnitude is 0
        print("Unable to normalize")
    
    normVector = [e / mag for e in vectorList]
    return normVector

#Producto punto     
def dotProd(v1, v2):
    return sum(x*y for x, y in zip(v1, v2))

#Sacar magnitud de un vector
def magV(vector):
    vectorList = list(vector)
    return mt.sqrt(sum(e ** 2 for e in vectorList))

#Vector por escalar
def VxE(v, e):
    r = [e*v[i] for i in range(len(v))]
    return r

def VplusE(v, e):
    r = [e+v[i] for i in range(len(v))]
    return r

def VdivE(v, e):
    r = [e/v[i] for i in range(len(v))]
    return r

#Agregar en libreria matematica
def reflectVector(normal, direction):
    dot_product = dotProd(direction, normal)
    reflection = [2 * dot_product * normal[i] - direction[i] for i in range(len(direction))]
    return reflection
    