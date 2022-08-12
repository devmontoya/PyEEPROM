#include "extEEPROM.h"

extEEPROM myEEPROM(kbits_32, 1, 32);

String command;
int readValue;
byte i2cStat;

void setup() {
  Serial.begin(115200);

  uint8_t eepStatus = myEEPROM.begin(extEEPROM::twiClock100kHz);
  if (eepStatus) {
    Serial.print(F("extEEPROM.begin() failed, status = "));
    Serial.println(eepStatus);
    while (1);
  }
}

void loop() {
  if (Serial.available() > 0) {
    command = Serial.readStringUntil('\n');

    if (command.substring(0, 1).equals("r")) {
      readValue = myEEPROM.read(command.substring(2, 6).toInt());
      Serial.println(readValue);
    }
    // Usar "w dirección data" siguiendo el formato "w 0000 000"
    else if (command.substring(0, 1).equals("w")) {
      i2cStat = myEEPROM.update(command.substring(2, 6).toInt(), command.substring(7, 10).toInt());
    }

  }
  delay(10);
}

// Github librería EEPROM https://github.com/PaoloP74/extEEPROM
