from cvzone.HandTrackingModule import HandDetector
import cv2
import numpy as np
import time
import serial
from function import *
import paho.mqtt as mqtt
 
# ketik "mqtt" untuk menggunakan komunikasi MQTT dan ketik bebas untuk serial
communication = "mqtt"

# lebar dan tinggi 
lebar = 640
tinggi = 480

# setting tinggi, lebar, dan intensitas cahaya dari kamera
cam = cv2.VideoCapture(0)
cam.set(3, lebar)
cam.set(4, tinggi)
cam.set(10, 50)


# Buat objek deteksi tangan
detector = HandDetector(detectionCon=0.8, maxHands=2) # HandDetector(detectionCon, maxHands)

# konfigurasi komunikasi Serial 
ser = serial.Serial('/dev/cu.usbserial-1410', 9600) # serial.Serial(port, baundrate)

# konfigurasi komunikasi MQTT
###
# Variabel MQTT
client = mqtt.Client()

mqttBroker = "broker.mqtt-dashboard.com"
port = 1883

# Setting MQTT
client.connect(mqttBroker, port)
client.subscribe("dajjal123")
###

# inisialisasi variabel
upperArmAngle = 90 # sudut lengan atas
foreArmAngle = 90 # sudut lengan bawah
handGripCondition = True 
shoulderRotationDirection = 0
checkGrip = 1
count = 0


arrayLength = 8 # jumlah data moving average
upperArmAngle_arr = np.zeros(arrayLength) 
foreArmAngle_arr = np.zeros(arrayLength)


# fungsi moving average
def movingAverage(data_upperArmAngle, data_foreArmAngle):
    global count, upperArmAngle_arr, foreArmAngle_arr
    
    # Ganti data terakhir dalam array dengan nilai baru
    upperArmAngle_arr[len(upperArmAngle_arr)-1] = data_upperArmAngle
    foreArmAngle_arr[len(foreArmAngle_arr)-1] = data_foreArmAngle
    
    # ganti data ke-i dalam array dengan data ke-i+1
    for i in range(len(foreArmAngle_arr)-1):
        foreArmAngle_arr[i] = foreArmAngle_arr[i+1]
        upperArmAngle_arr[i] = upperArmAngle_arr[i+1]
    
    # menentukan total nilai di dalam array, kecuali data terakhir
    totalLb, totalLa = 0, 0
    for i in range(len(upperArmAngle_arr)-1):
        totalLb += upperArmAngle_arr[i]
        totalLa += foreArmAngle_arr[i] 
    
    
    if count < len(upperArmAngle_arr)-1:
        count += 1 
    
    # return nilai moving average
    return totalLb/count, totalLa/count


while True:
    success, img = cam.read()
    img = cv2.flip(img, 1) 
    hands, img = detector.findHands(img)  

    # posisi garis tengah
    center_x = lebar // 2

    # gambar garis tengah
    color = (0, 255, 0) 
    thickness = 2
    cv2.line(img, (center_x, 0), (center_x, tinggi), color, thickness) 

    # memberikan syarat apakah ada tangan yang terdeteksi pada video
    if hands:
        lmList = hands[0]["lmList"] # List of 21 Landmarks points
        
        shoulderRotationDirection = 0
        
        # jika tangan yang dideteksi hanya satu tangan
        if len(hands) == 1:
            # kondisi jika tangan berada di sebelah kanan garis tengah
            if lmList[20][0] > lebar/2 and lmList[6][1] < tinggi:
                hand = hands[0]
                lmList = hand["lmList"]  
                fingers = detector.fingersUp(hand)
                
                # Menentukan kondisi grip telapak tangan
                handGripCondition = handGrip(fingers)
                if handGripCondition != None:
                    checkGrip = handGripCondition
                
                # Menentukan rotasi shoulder
                shoulderRotationDirection = shoulderRotation(fingers)
            
            # kondisi jika tangan berada di sebelah kiri garis tengah
            else:
                if (lmList[6][0] - lmList[5][0]) != 0 and lmList[6][1] < tinggi:
                    upperArmAngle = hitungSudut(lmList[6], lmList[5], [lmList[5][0] + 25, lmList[5][1]])
                    foreArmAngle = hitungSudut(lmList[7], lmList[6], lmList[5])
                
        # jika tangan yang dideteksi ada dua
        if len(hands) == 2:
            hand1 = hands[0]
            hand2 = hands[1]
            
            # jika posisi tangan pertama berada di sebelah kanan garis tengah
            if lmList[20][0] > lebar / 2:
                hand1 = hands[1]
                hand2 = hands[0]
            
            # membuat variabel untuk menampung nilai handLanmark dan fingersUp
            lmList1 = hand1["lmList"]  # List of 21 Landmarks points
            fingers1 = detector.fingersUp(hand1)
            lmList2 = hand2["lmList"]  # List of 21 Landmarks points
            fingers2 = detector.fingersUp(hand2)
            
            
            # menentukan gripper
            handGripCondition = handGrip(fingers2)
            if handGripCondition != None:
                checkGrip = handGripCondition
            
            # Menentukan rotasi bahu
            shoulderRotationDirection = shoulderRotation(fingers2)
            
            # menghitung sudut bagian lengan atas dan lengan bawah arm robot
            if (lmList1[6][0] - lmList1[5][0]) != 0 and lmList1[6][1] < tinggi:
                upperArmAngle = hitungSudut(lmList1[6], lmList1[5], [lmList1[5][0] + 25, lmList1[5][1]])
                foreArmAngle = hitungSudut(lmList1[7], lmList1[6], lmList1[5])
                
        # konversi sudut vektor jari menjadi sudut servo
        foreArmAngle = foreArmAngle + upperArmAngle
        upperArmAngle = 180 - upperArmAngle
    
        
        # Threshold apabila sudut melampui batas maksimal kemampuan servo motor
        if upperArmAngle < 0:
            upperArmAngle = 1
        elif upperArmAngle > 160:
            upperArmAngle = 160
        
        if foreArmAngle < 90:
            foreArmAngle = 90
        elif foreArmAngle > 180:
            foreArmAngle = 180
        
        
        
        # menerapkan movingAverage kepada hasil fungsi hitungSudut()
        upperArmAngle, foreArmAngle = movingAverage(upperArmAngle, foreArmAngle)

        # keluaran
        result = arrToString([pembulatan(upperArmAngle), 
                            pembulatan(foreArmAngle), 
                            shoulderRotationDirection, checkGrip])   
        print(result)
        
        if communication == 'mqtt':
            try:
                client.publish("dajjal123", result)
            except serial.SerialTimeoutException as e:
                print("Serial write failed: {}".format(e))
            except serial.SerialException as e:
                print("Serial write failed: {}".format(e))
            print('')
            
            time.sleep(0.1)
            
        else:
            try:
                ser.write(result.encode('utf-8'))
            except serial.SerialTimeoutException as e:
                print("Serial write failed: {}".format(e))
            except serial.SerialException as e:
                print("Serial write failed: {}".format(e))
            print('')
            
            time.sleep(0.05)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
