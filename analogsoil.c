/*Mini Program to read values from specified analog pin (A0). The pin maps the output of the 10-bit-analog to digital converter,
/so input voltages between 0 and the operating voltage (for the capactive soil sensor attached this is 5V) into integer values between 0 and 1023
#Arduino used: Mega2560, Output pin A0, operating voltage: 5, 10 bits max resolution
Dry int constant (sensor was in air): 516
Earth int constant (sensor was in dry earth): 311
Wet int constant (sensor was immersed in water): 191
#Author: Amalie Wilke
5.09.2023*/


int analogPin=A0; //analog pin on Arduino sensor is connected to over Aout

int volt=0; //integer to store volt reading

int percent=0; //integer to store percentage of volt reading

const int dry=511; //sensor in air

const int wet=191; //sensor immersed in water

void setup() {
 Serial.begin(9600);

}

void loop() {

  //Uses analogRead() to mirror voltage output with integer value
  volt=analogRead(analogPin);
  //use map function to create range with dry (dry soil, no water or plant) and wet (immersed in water) constants
  percent=map(volt, wet, dry, 100, 0);
  //prints integer value read
  Serial.print(analogPin);
  Serial.print(",");
  Serial.print(analogRead(analogPin));
  Serial.print(",");
  Serial.print(percent);
  Serial.println(";");
  
  //delay for using Putty to print serial output to csv
  delay(900000);
  //delay for checking for values, uncomment during active testing
  //delay(1200);
}
