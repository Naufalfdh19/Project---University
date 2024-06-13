import matplotlib.pyplot as plt
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import cv2
import numpy as np
import time
from xgboost import XGBRegressor
from function import *

# ketik "min" untuk mengukur sudut minimum beta dan ketik bebas untuk mengukur sudut maksimum beta
measurement = "min"

lebar = 640
tinggi = 480

cam = cv2.VideoCapture(0)
cam.set(3, lebar)
cam.set(4, tinggi)
cam.set(10, 50)

detector = HandDetector(detectionCon=0.8, maxHands=2) # HandDetector(detectionCon, maxHands)

# inisialisasi variabel
upperArmAngle = 90
foreArmAngle = 90
handGripCondition = True
shoulderRotationDirection = 0
checkGrip = 1
count = 0

arrayLength = 8
upperArmAngle_arr = np.zeros(arrayLength)
foreArmAngle_arr = np.zeros(arrayLength)

def movingAverage(data_upperArmAngle, data_foreArmAngle):
    global count, upperArmAngle_arr, foreArmAngle_arr
    
    upperArmAngle_arr[len(upperArmAngle_arr)-1] = data_upperArmAngle
    foreArmAngle_arr[len(foreArmAngle_arr)-1] = data_foreArmAngle
    
    for i in range(len(foreArmAngle_arr)-1):
        foreArmAngle_arr[i] = foreArmAngle_arr[i+1]
        upperArmAngle_arr[i] = upperArmAngle_arr[i+1]
    
    totalLb, totalLa = 0, 0
    for i in range(len(upperArmAngle_arr)-1):
        totalLb += upperArmAngle_arr[i]
        totalLa += foreArmAngle_arr[i] 
    
    
    if count < len(upperArmAngle_arr)-1:
        count += 1 
    
    return totalLb/count, totalLa/count

arrBeta = {} # array untuk menampung nilai yang didapatkan secara real-time
realMinBeta = np.array([102, 90, 86, 82,  76.5, 72, 69, 66, 63, 60, 56, 50, 45, 41, 37, 33, 32, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30]) # data eksperimen sudut minimum
realMaxBeta = np.array([153, 152, 152, 150, 150, 150, 149, 146, 142, 138, 130 , 123, 113, 110, 105, 99, 94, 92, 87, 81, 77, 70.5, 68, 64, 61, 57, 52, 45, 40, 33]) # data eksperimen sudut maksimum
alpha = np.array([0,4,8,12,16,20,24,28,32,36,40,46,52,58,64,70,76,82,88,94,100,106,112,118,124,130,136,142,148,154]) # 


while True:

    # membaca video
    success, img = cam.read()
    img = cv2.flip(img, 1) # melakukan mirror pada figure
    hands, img = detector.findHands(img)  

    # memberikan syarat apakah ada tangan yang terdeteksi pada video
    if hands:
        # common Hands    
        lmList = hands[0]["lmList"] # List of 21 Landmarks points

        # variabel default
        shoulderRotationDirection = 0
        
        if len(hands) == 1:
            if lmList[20][0] > lebar/2 and lmList[6][1] < tinggi:
                hand = hands[0]
                lmList = hand["lmList"]  
                fingers = detector.fingersUp(hand)
                
                # Menentukan kondisi grip telapak tangan
                handGripCondition = handGrip(fingers)
                if handGripCondition != None:
                    checkGrip = handGripCondition
                
                # Menentukan rotasi bahu
                shoulderRotationDirection = shoulderRotation(fingers)
                

            else:
                if (lmList[6][0] - lmList[5][0]) != 0 and lmList[6][1] < tinggi:
                    upperArmAngle = hitungSudut(lmList[6], lmList[5], [lmList[5][0] + 25, lmList[5][1]])
                    foreArmAngle = hitungSudut(lmList[7], lmList[6], lmList[5])
                
                        
                
            
        if len(hands) == 2:
            hand1 = hands[0]
            hand2 = hands[1]
            
            if lmList[20][0] > lebar / 2:
                hand1 = hands[1]
                hand2 = hands[0]
            
            # membuat variabel untuk menampung nilai handLanmark dan fingersUp
            lmList2 = hand2["lmList"]  # List of 21 Landmarks points
            fingers2 = detector.fingersUp(hand2)
            lmList1 = hand1["lmList"]  # List of 21 Landmarks points
            fingers1 = detector.fingersUp(hand1)
            
            # menentukan gripper
            handGripCondition = handGrip(fingers2)
            if handGripCondition != None:
                checkGrip = handGripCondition
            
            # Menentukan rotasi bahu
            shoulderRotationDirection = shoulderRotation(fingers2)
            
            # menghitung sudut bagian lengan atas dan lengan bawah arm robot
            if (lmList[6][0] - lmList[5][0]) != 0 and lmList[6][1] < tinggi:
                upperArmAngle = hitungSudut(lmList1[6], lmList1[5], [lmList1[5][0] + 25, lmList1[5][1]])
                foreArmAngle = hitungSudut(lmList1[7], lmList1[6], lmList1[5])
                
        # konversi sudut vektor jari menjadi sudut servo
        foreArmTmp = foreArmAngle
        foreArmTmpEx = foreArmTmp
        foreArmAngle = foreArmAngle + upperArmAngle
        upperArmTmp = upperArmAngle
        upperArmAngle = 180 - upperArmAngle
        
    
        
        # Threshold apabila sudut melampui batas maksimal kemampuan servo motor
        if upperArmAngle < 0:
            upperArmAngle = 0
            upperArmTmp = 180
        elif upperArmAngle > 180:
            upperArmAngle = 180
            upperArmTmp = 0
        
        
        if foreArmAngle > 180:
            foreArmAngle = 180
            foreArmTmp = foreArmAngle - upperArmTmp
        elif foreArmAngle < 0:
            foreArmAngle = 0
        
        print('real value fore arm angle: ', foreArmAngle)
        
        # menerapkan movingAverage kepada hasil fungsi hitungSudut()
        upperArmAngle, foreArmAngle = movingAverage(upperArmAngle, foreArmAngle)

        arrBeta[upperArmTmp] = foreArmTmp

        time.sleep(0.005)
    cv2.imshow("Image", img)
    # Tunggu selama 1 milidetik dan periksa jika tombol "q" ditekan
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


def minMaxGraph(beta, type):
    exTheta = {k: beta[k] for k in sorted(beta.keys())}
    exKeys = list(exTheta.keys())
    exValues = list(exTheta.values())
    if type == 'min':
        realValues = realMinBeta
    else:
        realValues = realMaxBeta

            
    return exKeys, exValues, realValues

exKeys, exValues, exRealValues= minMaxGraph(arrBeta, measurement)

    
exKeys = np.array(exKeys)
exValues = np.array(exValues)
print(exValues)

model = XGBRegressor()
model.fit(exKeys.reshape(-1, 1), exValues)

exValues_pred = model.predict(exKeys.reshape(-1,1))



plt.figure()
plt.plot(alpha, exRealValues, color='blue', label='Eksperimen', marker='^', alpha=0.5)
plt.plot(exKeys, exValues_pred, color='red', label='Simulasi', marker='s', alpha=0.5)

plt.xlabel("Sudut alpha (α°)")
if type == 'min':
    plt.ylabel("Sudut minimum beta (β°)")
else:
    plt.ylabel("Sudut maksimum beta (β°)")

plt.tight_layout()
plt.legend()
plt.show()
