#include <Servo.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// perbarui nilai dibawah dengan koneksi yang anda kenakan
const char* ssid = "DODOT";
const char* password = "210310PH";
const char* mqtt_server = "broker.mqtt-dashboard.com";

WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE  (50)
char msg[MSG_BUFFER_SIZE];

// objek Servo
Servo upperArmMotor;
Servo foreArmMotor;
Servo shoulderMotor;
Servo handMotor;

int checkpointUA = 180;
int handPosition = 50;
int shoulderPosition = 90;
int checkpointFA = 180;
int delay_ = 1;
int foreArm, upperArm, shoulder, hand; 


void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}


void callback(char* topic, byte* payload, unsigned int length) {
//  Serial.print("Message arrived [");
//  Serial.print(topic);
//  Serial.print("] ");
  outputValue = "";
  for (int i = 0; i < length; i++) {
    outputValue += (char)payload[i];
  }

  selectData();

  upperArmMovement(); // input data dan output gerak motor bagian lengan bawah
  foreArmMovement(); // input data dan output gerak motor bagian lengan atas
  shoulderMovement(); // input data dan output gerak rotasi motor
  handMovement(); // input data dan output gerak capit robot

  Serial.print("angle: ");
  Serial.println(outputValue);
  
//  Serial.print(upperArm);
//  Serial.print(" | ");
//  Serial.print(foreArm);
//  Serial.print(" | ");
//  Serial.print(shoulder);
//  Serial.print(" | ");
//  Serial.println(hand);
//  
  
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.publish("outTopic", "hello world");
      // ... and resubscribe
      client.subscribe("dajjal123");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup() {
  upperArmMotor.attach(D1);
  foreArmMotor.attach(D2);
  shoulderMotor.attach(D3);
  handMotor.attach(D4);

  upperArmMotor.write(checkpointUA);
  foreArmMotor.write(checkpointFA);
  shoulderMotor.write(shoulderPosition);
  handMotor.write(handPosition);
  
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  Serial.begin(115200);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

void selectData() { 
   // melakukan pemisahan data string menjadi data integer menggunakan substring
   int spaceIndex1 = outputValue.indexOf(' '); // Cari indeks spasi pertama
   int spaceIndex2 = outputValue.indexOf(' ', spaceIndex1 + 1); // Cari indeks spasi kedua 
   int spaceIndex3 = outputValue.indexOf(' ', spaceIndex2 + 1);
   
   // Menyimpan kata-kata ke variabel
   upperArm = outputValue.substring(0, spaceIndex1).toInt();
   foreArm = outputValue.substring(spaceIndex1 + 1, spaceIndex2).toInt();
   shoulder = outputValue.substring(spaceIndex2 + 1, spaceIndex3).toInt();
   hand = outputValue.substring(spaceIndex3 + 1).toInt();
}

void upperArmMovement() {\
    if (checkpointUA < upperArm) {
      for (int i = checkpointUA; i <= upperArm; i++) {
        upperArmMotor.write(i);
      }
    } else if (checkpointUA > upperArm) {
      for (int i = checkpointUA; i >= upperArm; i--) {
        upperArmMotor.write(i);
      }
    }
    
    checkpointUA = upperArm; 
}

void foreArmMovement() {
    if (checkpointFA < foreArm) {
      for (int i = checkpointFA; i <= foreArm; i++) {
        foreArmMotor.write(i);
      }
    } else if (checkpointFA > foreArm) {
      for (int i = checkpointFA; i >= foreArm; i--) {
        foreArmMotor.write(i); 
      }
    }
    
    checkpointFA = foreArm;
}

void shoulderMovement() {
  int adding = 3;
  if (shoulder == -1 && shoulderPosition > 0) {
    for (int i = shoulderPosition; i >= shoulderPosition-adding; i--) {
      shoulderMotor.write(i);
    }
    
    shoulderPosition -= adding; 
    
  } else if (shoulder == 1 && shoulderPosition < 180) {
    for (int i = shoulderPosition; i <= shoulderPosition+adding; i++) {
      shoulderMotor.write(i); 
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
