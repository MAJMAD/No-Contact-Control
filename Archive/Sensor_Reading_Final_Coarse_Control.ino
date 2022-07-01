/*Jacob Mader 3/8/2022*/
/*This code facilitates use of the distance sensors to allow for accurate, real-time, and fine positioning of the hexapod by the rasp-pi*/

/*define the sensor's pins*/
uint8_t echoPin1 = 17;
uint8_t echoPin2 = 16;

/* define constants */
const int TIMER_TRIGGER_HIGH = 1;
const int TIMER_LOW_HIGH = 10;
const int ARRAY_SIZE = 80;
const int SENSOR_RANGE = 40;
const int SENSOR_LOOKBACK = 750;
const int DELAY_TIME = 10;
const int SMOOTH = 100;
const int VALIDITYTHRESH = 60;
const float ARRAY_INIT_VAL = 0;
const float MAX = SENSOR_RANGE*2/0.034;
const float HOME = 0.5;


/*define the states of an ultrasonic sensor*/
enum SensorStates {
  TRIG_LOW1,
  TRIG_HIGH1,
  ECHO_HIGH1,
  TRIG_LOW2,
  TRIG_HIGH2,
  ECHO_HIGH2
};

/* define globals */
float timeDuration1 = 0;
float timeDuration2 = 0;
float Sensor1Array[ARRAY_SIZE];
float Sensor2Array[ARRAY_SIZE];
float Sensor1TimeArray[ARRAY_SIZE];
float Sensor2TimeArray[ARRAY_SIZE];
int Sensor1ValidityArray[ARRAY_SIZE];
int Sensor2ValidityArray[ARRAY_SIZE];
int Sensor1ValidityTemp = 0;
int Sensor1ValidityCount = 0;
int Sensor2ValidityTemp = 0;
int Sensor2ValidityCount = 0;
unsigned long timerStart = 0;

/* set initial state */
SensorStates _sensorState = TRIG_LOW1;

/* Function Definitions */

void startTimer() {
  timerStart = millis();
}

bool isTimerReady(int mSec) {
  return (millis() - timerStart) < mSec;
}

void initArray(float SensorArray[], float SensorTimeArray[], int SensorValidityArray[]) {
  for (int i = 0; i < ARRAY_SIZE; i++) {
    SensorArray[i] = HOME;
    SensorTimeArray[i] = ARRAY_INIT_VAL;
    SensorValidityArray[i] = 1;
  }
}

void updateArray(float SensorArray[], float updateValue, float SensorTimeArray[], float timestamp, int SensorValidityArray[], int ValidityTemp) {
  for (int i = 0; i < ARRAY_SIZE - 1; i++) {
    SensorArray[i] = SensorArray[i+1];
    SensorTimeArray[i] = SensorTimeArray[i+1];
    SensorValidityArray[i] = SensorValidityArray[i+1];
  }
  SensorArray[ARRAY_SIZE - 1] = updateValue;
  SensorTimeArray[ARRAY_SIZE - 1] = timestamp;
  SensorValidityArray[ARRAY_SIZE - 1] = ValidityTemp;
}

float avrArray(float SensorArray[], float SensorTimeArray[], int SensorValidityArray[]) {
  float AvrValue = 0;
  int counter = 0;
  int invalidcounter = 0;
  int timeoutindex = 0;
  int invalidloop = 0;
  while (SensorTimeArray[ARRAY_SIZE - 1 - counter] > (SensorTimeArray[ARRAY_SIZE - 1] - SENSOR_LOOKBACK)){
    timeoutindex = ARRAY_SIZE - 1 - counter;
    if (SensorValidityArray[ARRAY_SIZE - 1 - counter] == 1){
      AvrValue += SensorArray[ARRAY_SIZE - 1 - counter];
      counter += 1; 
    }
    else {
      counter += 1;
      invalidcounter += 1;
    }
  }
  while (invalidloop < invalidcounter){
    if (SensorValidityArray[timeoutindex - invalidloop] == 1){
      AvrValue += SensorArray[timeoutindex - invalidloop];
      invalidloop += 1; 
      //Serial.println(AvrValue)
    }
    else { 
      invalidloop += 1;
      invalidcounter += 1;
    }
    if ((timeoutindex - invalidloop) < 2){
      break;
    }
    
  }
  return ((float)((int)((AvrValue / (float)(counter + invalidloop - invalidcounter)) * 10)/1)/10);
}

float checkSensorValue(float SensorValue, int SensorValidityArray[], int &ValidityTemp, int &ValidityCount) {
  if (SensorValue > MAX or SensorValue < 0) {
    SensorValue = HOME;
    ValidityTemp = 0;
    ValidityCount += 1;
    return SensorValue;
  }
  else {
    ValidityTemp = 1;
    ValidityCount = 0;
    return SensorValue/MAX;
  }
}

void checkValidity(float SensorArray[], int SensorValidityArray[], int ValidityCount) {
  if ((SensorValidityArray[ARRAY_SIZE - 1] == 1) != 1) {
    if (ValidityCount == VALIDITYTHRESH) {
      for (int i = 0; i < VALIDITYTHRESH; i++) {
        SensorValidityArray[ARRAY_SIZE - 1 - i] = 1;
        ValidityCount = 0;
      }
    }
    else if ( SensorArray[ARRAY_SIZE - 2] == 0.5 and SensorValidityArray[ARRAY_SIZE - 2] == 1){
      SensorValidityArray[ARRAY_SIZE - 1] = 1;
    }
  }
}

void printArray(float SensorArray[]) {
  for (int i = 0; i < ARRAY_SIZE - 1; i++) {
    Serial.print(SensorArray[i]);
    Serial.print(" ");
  }
  Serial.println(" ");
}

void printArray(int SensorArray[]) {
  for (int i = 0; i < ARRAY_SIZE - 1; i++) {
    Serial.print(SensorArray[i]);
    Serial.print(" ");
  }
  Serial.println(" ");
}

void setup() {
  Serial.begin(115200);
  pinMode(echoPin1, INPUT);
  pinMode(echoPin2, INPUT);
  DDRD = B11111111; // set PORTD (triggers) to outputs
  initArray(Sensor1Array, Sensor1TimeArray, Sensor1ValidityArray);
  initArray(Sensor2Array, Sensor2TimeArray, Sensor2ValidityArray);
}

void loop() {
  /*Switch between the ultrasonic sensor states*/
  switch (_sensorState) {
    /* Start with LOW pulse to ensure a clean HIGH pulse*/
    case TRIG_LOW1: {
        PORTD = B00000000;
        startTimer();
        if (isTimerReady(TIMER_LOW_HIGH)) {
          _sensorState = TRIG_HIGH1;
        }
      } break;

    /*Triggered a HIGH pulse of 10 microseconds*/
    case TRIG_HIGH1: {
        PORTD = B00000100;
        startTimer();
        if (isTimerReady(TIMER_TRIGGER_HIGH)) {
          _sensorState = ECHO_HIGH1;
        }
      } break;

    /*Measures the time that ping took to return to the receiver and processes the data.*/
    case ECHO_HIGH1: {
        PORTD = B00000000;
        timeDuration1 =  checkSensorValue((((int) pulseIn(echoPin1, HIGH) / SMOOTH) * SMOOTH), Sensor1ValidityArray, Sensor1ValidityTemp, Sensor1ValidityCount);
        updateArray(Sensor1Array, timeDuration1, Sensor1TimeArray, millis(), Sensor1ValidityArray, Sensor1ValidityTemp);
        checkValidity(Sensor1Array, Sensor1ValidityArray, Sensor1ValidityCount);
        timeDuration1 = avrArray(Sensor1Array, Sensor1TimeArray, Sensor1ValidityArray);
        Serial.print(timeDuration1);
        Serial.println(timeDuration2);
        _sensorState = TRIG_LOW2;
        delay(DELAY_TIME);
      } break;
    case TRIG_LOW2: {
        PORTD = B00000000;
        startTimer();
        if (isTimerReady(TIMER_LOW_HIGH)) {
          _sensorState = TRIG_HIGH2;
        }
      } break;
    case TRIG_HIGH2: {
        PORTD = B00001000;
        startTimer();
        if (isTimerReady(TIMER_TRIGGER_HIGH)) {
          _sensorState = ECHO_HIGH2;
        }
      } break;
    case ECHO_HIGH2: {
        PORTD = B00000000;
        timeDuration2 = checkSensorValue((((int) pulseIn(echoPin2, HIGH) / SMOOTH) * SMOOTH),Sensor2ValidityArray, Sensor2ValidityTemp, Sensor2ValidityCount);
        updateArray(Sensor2Array, timeDuration2, Sensor2TimeArray, millis(), Sensor2ValidityArray, Sensor2ValidityTemp);
        checkValidity(Sensor2Array, Sensor2ValidityArray, Sensor2ValidityCount);
        timeDuration2 = avrArray(Sensor2Array, Sensor2TimeArray, Sensor2ValidityArray);
        Serial.print(timeDuration1);
        Serial.println(timeDuration2);
        _sensorState = TRIG_LOW1;
        delay(DELAY_TIME);
      } break;
  }//end switch
}//end loop
