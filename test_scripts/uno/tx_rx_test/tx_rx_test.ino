String incomingBytes;

void setup() {                
  Serial.begin(9600); // Opens serial port, sets data rate to 9600 bps.
}

void loop() {
  // Send data only when you receive data.
  if (Serial.available() > 0) {
    // Read the incoming bytes.
    incomingBytes = Serial.readString();

    // Echo the data.
    Serial.println(incomingBytes);
  }
}
