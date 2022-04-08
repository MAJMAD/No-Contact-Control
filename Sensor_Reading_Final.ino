/*Jacob Mader 3/8/2022*/
/*Edited 3/28/2022 to include sensor read timestamps and limit propagation delay
 *Edited 4/4/2022 to utilize port manipulation rather than digitalWrite
 *Edited 4/5/2022 to return to level rather than a latched position
 */
/*This code facilitates use of the distance sensors to allow for accurate and real-time positioning of the hexapod by the rasp-pi*/

/*define the sensor's pins*/
uint8_t echoPin1 = 17;
uint8_t echoPin2 = 16;

/* define constants */
const int TIMER_TRIGGER_HIGH = 1;
const int TIMER_LOW_HIGH = 10;
const int ARRAY_SIZE = 75;
const int SENSOR_RANGE = 40;
const int SENSOR_LOOKBACK = 1000;
const int DELAY_TIME = 10;
const int SMOOTH = 100;
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

void initArray(float SensorArray[], float SensorTimeArray[]) {
  for (int i = 0; i < ARRAY_SIZE; i++) {
    SensorArray[i] = ARRAY_INIT_VAL;
    SensorTimeArray[i] = ARRAY_INIT_VAL;
  }
}

void updateArray(float SensorArray[], float updateValue, float SensorTimeArray[], float timestamp) {
  for (int i = 0; i < ARRAY_SIZE - 1; i++) {
    SensorArray[i] = SensorArray[i+1];
    SensorTimeArray[i] = SensorTimeArray[i+1];
  }
  SensorArray[ARRAY_SIZE - 1] = updateValue;
  SensorTimeArray[ARRAY_SIZE - 1] = timestamp;
}

float avrArray(float SensorArray[], float SensorTimeArray[]) {
  float AvrValue = 0;
  int counter = 0;
  while (SensorTimeArray[ARRAY_SIZE - 1 - counter] > (SensorTimeArray[ARRAY_SIZE - 1] - SENSOR_LOOKBACK)){
    AvrValue += SensorArray[ARRAY_SIZE - 1 - counter];
    counter += 1; 
  }
  return ((float)((int)((AvrValue / (float)counter) * 10)/1)/10) ;
}

float checkSensorValue(float SensorValue) {
  if (SensorValue > MAX or SensorValue < 0) {
    SensorValue = HOME;
    return SensorValue;
  }
  else {
    return SensorValue/MAX;
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(echoPin1, INPUT);
  pinMode(echoPin2, INPUT);
  DDRD = B11111111; // set PORTD (triggers) to outputs
  initArray(Sensor1Array, Sensor1TimeArray);
  initArray(Sensor2Array, Sensor2TimeArray);
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
        updateArray(Sensor1Array, checkSensorValue(((int) pulseIn(echoPin1, HIGH) / SMOOTH) * SMOOTH), Sensor1TimeArray, millis());
        timeDuration1 = avrArray(Sensor1Array, Sensor1TimeArray);
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
        updateArray(Sensor2Array, checkSensorValue(((int) pulseIn(echoPin2, HIGH) / SMOOTH) * SMOOTH), Sensor2TimeArray, millis());
        timeDuration2 = avrArray(Sensor2Array, Sensor2TimeArray);
        Serial.print(timeDuration1);
        Serial.println(timeDuration2);
        _sensorState = TRIG_LOW1;
        delay(DELAY_TIME);
      } break;
  }//end switch
}//end loop
