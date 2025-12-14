/*
Logging data from a GPS module using SD card and Arduino
*/

// Libraries:
#include <SD.h>
#include <SoftwareSerial.h>

// SD Card Shield:
const int chipSelect = 4;  // CS for Arduino Uno Rev3e + seeed studio SD Card Shield v4.4
File coordinateLogs;
volatile unsigned int counter = 0;

// GPS: 
SoftwareSerial gpsSerial(8,7);  // Change to hardware serial when I swap to Mega board
#define PMTK_SET_NMEA_UPDATE_1HZ  "$PMTK220,1000*1F"
#define PMTK_SET_NMEA_OUTPUT_ALLDATA "$PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0*28"


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

  // Open file and overwrite data if exists
  Serial.println("creating file");
  coordinateLogs = SD.open("coords_F.txt", O_WRITE | O_CREAT | O_TRUNC);  // limited by 8.3 filename format  

  Serial.println("init gps");
  gpsSerial.println(PMTK_SET_NMEA_OUTPUT_ALLDATA);
  gpsSerial.println(PMTK_SET_NMEA_UPDATE_1HZ);

}

void loop() {
  if (gpsSerial.available()) {
    char c = gpsSerial.read();  // Read stream from GPS
    Serial.write(c);

    counter++;

    // If the file opened okay, write to it:
    if (coordinateLogs) {
      coordinateLogs.print(c);
      
      // Every 1000 chars save the file
      if (counter % 1000 == 0) {
        coordinateLogs.flush();
      }
    } else {
      // File reached 100 characters
      Serial.println("error opening file");
    }
  }
}
