/*Jacob Mader 3/4/2022*/
/*This code facilitates use of the distance sensors to allow for accurate and real-time positioning of the hexapod by the rasp-pi
/*define the sensor's pins*/
uint8_t trigPin1 = 1;
uint8_t echoPin1 = 0;
uint8_t trigPin2 = 11;
uint8_t echoPin2 = 12;

/* define constants */
const int TIMER_TRIGGER_HIGH = 1;
const int TIMER_LOW_HIGH = 10;
const int ARRAY_SIZE = 50;
const float ARRAY_INIT_VAL = 0;
const int SENSOR_RANGE = 70;

/*The states of an ultrasonic sensor*/
enum SensorStates {
  TRIG_LOW1,
  TRIG_HIGH1,
  ECHO_HIGH1,
  TRIG_LOW2,
  TRIG_HIGH2,
  ECHO_HIGH2
};

/* define globals */
float timeDuration1, timeDuration2;
float Sensor1Array[ARRAY_SIZE];
float Sensor2Array[ARRAY_SIZE];
float LastSensor1Value = 0.09;
float LastSensor2Value = 0.09;
unsigned long timerStart = 0;

SensorStates _sensorState = TRIG_LOW1;

/* Function Definitions */

void startTimer() {
  timerStart = millis();
}

bool isTimerReady(int mSec) {
  return (millis() - timerStart) < mSec;
}

void initArray(float SensorArray[]) {
  for (int i = 0; i < ARRAY_SIZE; i++) {
    SensorArray[i] = ARRAY_INIT_VAL;
  }
}

void updateArray(float SensorArray[], float updateValue) {
  for (int i = 0; i < ARRAY_SIZE - 1; i++) {
    SensorArray[i] = SensorArray[i+1];
  }
  SensorArray[ARRAY_SIZE - 1] = updateValue;
}

void printArray(float SensorArray[]) {
  for (int i = 0; i < ARRAY_SIZE; i++) {
    Serial.print(SensorArray[i]);
    Serial.print(" ");
  }
  Serial.println("");
}

void printFinalArray(float SensorArray[]) {
  for (int i = 100; i < 400; i++) {
    Serial.print(SensorArray[i]);
    Serial.print(" ");
  }
  Serial.println("");
}

float avrArray(float SensorArray[]) {
  float AvrValue = 0;
  for (int i = 0; i < ARRAY_SIZE; i++) {
    AvrValue += SensorArray[i];
  }
  return (AvrValue / ARRAY_SIZE) ;
}

float checkSensor1Value(float Sensor1Value) {
  if (Sensor1Value > SENSOR_RANGE*2/0.034) {
    Sensor1Value = LastSensor1Value;
    return Sensor1Value;
  }
  else {
    LastSensor1Value = Sensor1Value/(SENSOR_RANGE*2/0.034);
    return Sensor1Value/(SENSOR_RANGE*2/0.034);
  }
}
float checkSensor2Value(float Sensor2Value) {
  if (Sensor2Value > SENSOR_RANGE*2/0.034) {
    Sensor2Value = LastSensor2Value;
    return Sensor2Value;
  }
  else {
    LastSensor2Value = Sensor2Value/(SENSOR_RANGE*2/0.034);
    return Sensor2Value/(SENSOR_RANGE*2/0.034);
   }
}
/*Sets the data rate in bits per second and configures the pins */
void setup() {
  Serial.begin(9600);
  pinMode(trigPin1, OUTPUT);
  pinMode(echoPin1, INPUT);
  pinMode(trigPin2, OUTPUT);
  pinMode(echoPin2, INPUT);
  initArray(Sensor1Array);
  initArray(Sensor2Array);
}

void loop() {
  /*Switch between the ultrasonic sensor states*/
  switch (_sensorState) {
    /* Start with LOW pulse to ensure a clean HIGH pulse*/
    case TRIG_LOW1: {
        digitalWrite(trigPin1, LOW);
        startTimer();
        if (isTimerReady(TIMER_LOW_HIGH)) {
          _sensorState = TRIG_HIGH1;
        }
      } break;

    /*Triggered a HIGH pulse of 10 microseconds*/
    case TRIG_HIGH1: {
        digitalWrite(trigPin1, HIGH);
        startTimer();
        if (isTimerReady(TIMER_TRIGGER_HIGH)) {
          _sensorState = ECHO_HIGH1;
        }
      } break;

    /*Measures the time that ping took to return to the receiver.*/
    case ECHO_HIGH1: {
        digitalWrite(trigPin1, LOW);
        timeDuration1 = pulseIn(echoPin1, HIGH);
        Serial.println(timeDuration1);
        timeDuration1 = (int) timeDuration1 / 10;
        timeDuration1 = timeDuration1 * 10;
        Serial.println(timeDuration1);
        timeDuration1 = checkSensor1Value(timeDuration1);
        Serial.println(timeDuration1);
        updateArray(Sensor1Array, timeDuration1);
        timeDuration1 = avrArray(Sensor1Array);
        Serial.print(timeDuration1);
        /*
           distance = time * speed of sound
           speed of sound is 340 m/s => 0.034 cm/us
        */
        Serial.print("stefan 1: ");
        Serial.println(timeDuration1);
        //Serial.println(" cm");
        _sensorState = TRIG_LOW2;
      } break;
    case TRIG_LOW2: {
        digitalWrite(trigPin2, LOW);
        startTimer();
        if (isTimerReady(TIMER_LOW_HIGH)) {
          _sensorState = TRIG_HIGH2;
        }
      } break;

    /*Triggered a HIGH pulse of 10 microseconds*/
    case TRIG_HIGH2: {
        digitalWrite(trigPin2, HIGH);
        startTimer();
        if (isTimerReady(TIMER_TRIGGER_HIGH)) {
          _sensorState = ECHO_HIGH2;
        }
      } break;

    /*Measures the time that ping took to return to the receiver.*/
    case ECHO_HIGH2: {
        digitalWrite(trigPin2, LOW);
        timeDuration2 = pulseIn(echoPin2, HIGH);
        Serial.println(timeDuration2);
        timeDuration2 = (int) timeDuration2 / 10;
        timeDuration2 = timeDuration2 * 10;
        Serial.println(timeDuration2);
        timeDuration2 = checkSensor2Value(timeDuration2);
        Serial.println(timeDuration2);
        updateArray(Sensor2Array, timeDuration2);
        timeDuration2 = avrArray(Sensor2Array);
        Serial.println(timeDuration2);
        /*
           distance = time * speed of sound
           speed of sound is 340 m/s => 0.034 cm/us
        */
        Serial.print("marcus 2: ");
        Serial.println(timeDuration2);
        //Serial.println(" cm");
        _sensorState = TRIG_LOW1;
      } break;
  }//end switch

}//end loop
