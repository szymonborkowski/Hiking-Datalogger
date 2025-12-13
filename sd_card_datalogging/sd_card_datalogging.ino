/*
Logging data using SD card and Arduino
*/

#include <SD.h>

const int chipSelect = 4;  // CS for Arduino Uno Rev3e + seeed studio SD Card Shield v4.4
File myFile;

void setup() {
  // Open serial communications
  Serial.begin(9600);

  while(!Serial);

  if (!SD.begin(chipSelect)) {
    Serial.println("initialisation failed.");
    while (1);
  }
  Serial.println("initialisation done.");

  // Open a new file and write data
  Serial.println("Creating coordinates.txt...");
  myFile = SD.open("coords.txt", FILE_WRITE);  // limited by 8.3 filename format
  
  // If the file opened okay, write to it:
  if (myFile) {
    // Write text to file:
    Serial.print("Writing to coordinates.txt...");
    myFile.println("Example GPS Data: 53.05582501632021, -9.503766786422712");
    
    // Close the file:
    myFile.close();
    Serial.println("done.");

  } else {
    // If the file didn't open, print an error:
    Serial.println("error opening coordinates.txt");

  }

}

void loop() {}
