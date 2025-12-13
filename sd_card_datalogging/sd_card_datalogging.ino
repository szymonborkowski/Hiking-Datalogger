/*
Logging data from a GPS module using SD card and Arduino
*/

// Libraries:
#include <SD.h>
#include <SoftwareSerial.h>

// SD Card Shield:
const int chipSelect = 4;  // CS for Arduino Uno Rev3e + seeed studio SD Card Shield v4.4
File coordinateLogs;

// GPS: 
SoftwareSerial gpsSerial(8,7);  // Change to hardware serial when I swap to Mega board
#define PMTK_SET_NMEA_UPDATE_1HZ  "$PMTK220,1000*1F"
#define PMTK_SET_NMEA_OUTPUT_ALLDATA "$PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0*28"

// Temp counter:
volatile unsigned int counter = 0;

void setup() {
  while(!Serial);

  // Open serial communications
  Serial.begin(115200);  // Arduino <-> Laptop
  gpsSerial.begin(9600);  // GPS Module <-> Arduino
  delay(2000);  // Allow for opening of serial monitor tool

  if (!SD.begin(chipSelect)) {
    Serial.println("init failed.");
    while (1);
  }
  Serial.println("init done.");

  // Open a new file and write data
  Serial.println("creating file");
  coordinateLogs = SD.open("coords.txt", FILE_WRITE);  // limited by 8.3 filename format  

  Serial.println("test...");
  gpsSerial.println(PMTK_SET_NMEA_OUTPUT_ALLDATA);
  gpsSerial.println(PMTK_SET_NMEA_UPDATE_1HZ);

}

void loop() {
  if (gpsSerial.available()) {
    char c = gpsSerial.read();  // Read stream from GPS
    Serial.write(c);

    // If the file opened okay, write to it:
    if (coordinateLogs) {
      coordinateLogs.println(c);
      
      // Close the file after 100 characters:
      if (counter == 100) {
        coordinateLogs.close();
      }
    } else {
      // File reached 100 characters
      Serial.println("closed file");
    }
  }
}
