import math
import numpy as np

count = 0



def hitungSudut(A, B, C):
    # Menghitung vektor AB dan vektor BC
    BA = (A[0] - B[0], A[1] - B[1])
    BC = (C[0] - B[0], C[1] - B[1])

    # Menghitung panjang vektor AB dan BC
    lengthAB = math.sqrt(BA[0] ** 2 + BA[1] ** 2)
    lengthBC = math.sqrt(BC[0] ** 2 + BC[1] ** 2)

    # Menghitung dot product AB dan BC
    dot_product = BA[0] * BC[0] + BA[1] * BC[1]

    # Menghitung sudut berdasarkan dot product dan panjang vektor
    radianAngle = math.acos(dot_product / (lengthAB * lengthBC))
    degreeAngle = math.degrees(radianAngle)

    return degreeAngle


def pembulatan(x):
    if x - math.floor(x) >= 0.5:
        return math.floor(x) + 1
    else:
        return math.floor(x)

def arrToString(arr):
    newStr = ''
    for i in arr:
        newStr += str(i) + " "
    return newStr + '\r'

def handGrip(arr):
    if arr == [0, 0, 0, 0, 0]:
        gripper = 0
        return gripper

    elif arr == [1, 1, 1, 1, 1]:
        gripper = 1
        return gripper
        
def shoulderRotation(arr):
    if arr == [1, 0, 0, 0, 0]:
        directionOfRotation = 1
        return directionOfRotation
    elif arr == [0, 0, 0, 0, 1]:
        directionOfRotation = -1
        return directionOfRotation
    return 0


    
    