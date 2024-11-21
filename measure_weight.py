import os
import time
import logging
import threading
from typing import Dict, Union

import RPi.GPIO as GPIO
import adafruit_dht
import board
from hx711 import HX711

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables for configuration
DHT_PIN = board.D2
SOUND_PIN = 3
TRIG_PIN = 17
ECHO_PIN = 27
LIGHT_PIN = 4
HX_DOUT_PIN = 9
HX_SCK_PIN = 10

# Initialize GPIO and sensors
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup([SOUND_PIN, LIGHT_PIN], GPIO.IN)
GPIO.setup([TRIG_PIN], GPIO.OUT)
GPIO.setup([ECHO_PIN], GPIO.IN)

# Sensor instances
dht_device = adafruit_dht.DHT11(DHT_PIN)
hx = HX711(dout_pin=HX_DOUT_PIN, pd_sck_pin=HX_SCK_PIN)

# Sensor calibration
tare_offset = 159054  # Existing tare offset
hx.set_offset(tare_offset)
hx.set_scale_ratio(102.372)  # Set the scale ratio (this might need recalibration)

# Function to perform tare
def tare_scale():
    """Tare the scale (set zero offset)."""
    hx.tare()  # Tare the sensor
    logging.info(f"Tare complete. Offset: {hx.offset}")
    time.sleep(1)

# Function to calibrate scale using known weight
def calibrate_scale(known_weight: float):
    """Calibrate scale using a known weight (in kg)."""
    logging.info(f"Calibrating scale with known weight: {known_weight} kg")
    tare_scale()  # Perform tare first

    raw_data = hx.get_raw_data_mean()  # Get raw data for calibration
    logging.info(f"Raw data: {raw_data}")

    scale_ratio = raw_data / (known_weight * 1000)  # Convert known weight to grams
    hx.set_scale_ratio(scale_ratio)
    logging.info(f"Calibration complete. Scale ratio: {scale_ratio}")

# Get weight from the sensor
def get_weight() -> float:
    """Retrieve weight from HX711 sensor."""
    raw_data = hx.get_raw_data_mean()
    logging.info(f"Raw data from HX711: {raw_data}")

    weight = hx.get_weight_mean(readings=10)
    if weight is not None:
        logging.info(f"Weight (grams): {weight}")
        return weight / 1000  # Convert to kg
    else:
        logging.error("Failed to read weight from HX711.")
        return None

# Other sensor functions (distance, temperature, etc.)

def get_distance() -> float:
    """Measure the distance using the ultrasonic sensor."""
    GPIO.output(TRIG_PIN, False)
    time.sleep(0.000002)
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.000001)
    GPIO.output(TRIG_PIN, False)

    pulse_start, pulse_end = time.time(), time.time()
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = (pulse_duration * 34300) / 2
    return round(distance, 1)

def get_temperature_humidity() -> Dict[str, Union[float, str]]:
    """Get temperature and humidity readings from the DHT11 sensor."""
    try:
        return {"temperature": dht_device.temperature, "humidity": dht_device.humidity}
    except RuntimeError as error:
        logging.warning(f"DHT11 sensor error: {error}")
        return {"error": "Failed to read temperature/humidity"}

def is_bee_alive() -> bool:
    """Detect bee presence based on sound."""
    return GPIO.input(SOUND_PIN) == 0

def is_hive_open() -> bool:
    """Check if the hive is open based on light levels."""
    return GPIO.input(LIGHT_PIN) == GPIO.HIGH

# Function to read sensors continuously
def read_sensors():
    """Continuously read all sensor data."""
    while True:
        data = {
            "temperature_humidity": get_temperature_humidity(),
            "distance": get_distance(),
            "bees_alive": is_bee_alive(),
            "hive_open": is_hive_open(),
            "weight": get_weight()
        }
        logging.info(f"Sensor Data: {data}")

        # Delay between readings
        time.sleep(1.0)  # Adjust the interval as needed

if __name__ == '__main__':
    # Calibrate scale (use 1 kg for calibration)
    calibrate_scale(1)  # Assuming 1 kg known weight
    sensor_thread = threading.Thread(target=read_sensors)
    sensor_thread.daemon = True
    sensor_thread.start()
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Program terminated.")
        GPIO.cleanup()
