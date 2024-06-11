#include <Servo.h>

int foreArm, upperArm, shoulder, hand; // variabel untuk menyimpan informasi yang diterima

String serialData; // deklarasi variabel untuk menyimpan data dari Python

// buat objek servo untuk masing-masing bagian
Servo upperArmMotor; // lengan atas
Servo foreArmMotor; // lengan bawah
Servo shoulderMotor; // rotasi atau bahu
Servo handMotor; // gripper

// inisialisasi 
int checkpointUA = 130; // posisi awal lengan atas
int checkpointFA = 180; // posisi awal lengan bawah
int shoulderPosition = 90; // posisi awal rotasi 
int handPosition = 50; // posisi awal gripper
int delay_ = 50; // delay


void setup() {
  
  upperArmMotor.attach(3);
  foreArmMotor.attach(11);
  shoulderMotor.attach(6);
  handMotor.attach(9);

  upperArmMotor.write(checkpointUA);
  foreArmMotor.write(checkpointFA);
  shoulderMotor.write(shoulderPosition);
  handMotor.write(50);
  
  Serial.begin(9600); // Inisialisasi komunikasi Serial
}

void loop() {
    // cek apabila serial memiliki data
    while (Serial.available() == 0) {  
    }
    // jika ada, maka data akan dibaca 
    serialData = Serial.readStringUntil('\r'); // pengambilan data

    Serial.print("angle: ");
    Serial.println(serialData);
   
    selectData(); // ekstrak data string ke integer
    
    upperArmMovement(); // input data dan output gerak motor bagian lengan bawah
    foreArmMovement(); // input data dan output gerak motor bagian lengan atas
    shoulderMovement(); // input data dan output gerak rotasi motor
    handMovement(); // input data dan output gerak capit robot
    
    // Tampilkan hasil
//    Serial.print(upperArm);
//    Serial.print(" | ");
//    Serial.print(foreArm);
//    Serial.print(" | ");
//    Serial.print(shoulder);
//    Serial.print(" | ");
//    Serial.println(hand);
}

void selectData() { 
   // melakukan pemisahan data string menjadi data integer menggunakan substring
   int spaceIndex1 = serialData.indexOf(' '); // Cari indeks spasi pertama
   int spaceIndex2 = serialData.indexOf(' ', spaceIndex1 + 1); // Cari indeks spasi kedua 
   int spaceIndex3 = serialData.indexOf(' ', spaceIndex2 + 1);
   
   // Menyimpan kata-kata ke variabel
   upperArm = serialData.substring(0, spaceIndex1).toInt();
   foreArm = serialData.substring(spaceIndex1 + 1, spaceIndex2).toInt();
   shoulder = serialData.substring(spaceIndex2 + 1, spaceIndex3).toInt();
   hand = serialData.substring(spaceIndex3 + 1).toInt();
}

void upperArmMovement() {\
    if (checkpointUA < upperArm) {
      for (int i = checkpointUA; i <= upperArm; i++) {
        upperArmMotor.write(i);
        delayMicroseconds(delay_);
      }
      
    } else if (checkpointUA > upperArm) {
      for (int i = checkpointUA; i >= upperArm; i--) {
        upperArmMotor.write(i);
        delayMicroseconds(delay_);
      }
    }
  
    checkpointUA = upperArm; 
}

void foreArmMovement() {
    if (checkpointFA < foreArm) {
      for (int i = checkpointFA; i <= foreArm; i++) {
        foreArmMotor.write(i);
        delayMicroseconds(delay_);
      }
      
    } else if (checkpointFA > foreArm) {
      for (int i = checkpointFA; i >= foreArm; i--) {
        foreArmMotor.write(i);
        delayMicroseconds(delay_);
      }
    }
  
    checkpointFA = foreArm;
}

void shoulderMovement() {
  int adding = 3;
  if (shoulder == -1 && shoulderPosition > 0) {
    for (int i = shoulderPosition; i >= shoulderPosition-adding; i--) {
      shoulderMotor.write(i);
      delayMicroseconds(delay_);  
    }
    
    shoulderPosition -= adding;
    
  } else if (shoulder == 1 && shoulderPosition < 180) {
    for (int i = shoulderPosition; i <= shoulderPosition+adding; i++) {
      shoulderMotor.write(i);
      delayMicroseconds(delay_); 
    }
    
    shoulderPosition += adding;
  } 
}

void handMovement() {
  if (hand == 0) {
    handMotor.write(35);
  } else {
    handMotor.write(95);
  }
}
