import logging
import time
from typing import Dict, Union
import RPi.GPIO as GPIO
from hx711 import HX711
from DHT11 import DHT11
import math

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Pin definitions
dout_pin = 5
pd_sck_pin = 6

# Initialize HX711 and DHT11 sensors
hx = HX711(dout_pin=dout_pin, pd_sck_pin=pd_sck_pin)
dht11 = DHT11(pin=17)

# Calibration factor (adjust this based on your scale)
calibration_factor = 1000

def tare_scale():
    """
    Tare the scale by resetting the offset to zero.
    """
    try:
        logging.info("Taring the scale... Please make sure it's empty and stable.")
        # Tare operation (offset set to integer)
        offset = int(0)  # Ensure offset is an integer
        hx.set_offset(offset)
        raw_data = hx.get_raw_data()
        logging.info(f"Raw readings for tare: {raw_data}")
        logging.info("Taring complete. Zero offset: 0")
    except Exception as e:
        logging.error(f"Error during tare operation: {e}")

def calibrate_scale(known_weight: float):
    """
    Calibrate the scale with a known weight.
    """
    try:
        tare_scale()  # Perform tare first
        logging.info(f"Calibrating scale with known weight: {known_weight} kg")
        
        # Perform calibration
        raw_data = hx.get_raw_data()
        logging.info(f"Raw readings for calibration: {raw_data}")
        
        # Calibration factor calculation
        calibration_factor = known_weight / sum(raw_data) * 1000
        logging.info(f"Calibration complete. Calibration factor: {calibration_factor}")
    except Exception as e:
        logging.error(f"Error during calibration: {e}")

def get_temperature_humidity() -> Dict[str, Union[float, str]]:
    """
    Get the temperature and humidity data from the DHT11 sensor.
    """
    try:
        humidity, temperature = dht11.read()
        if humidity is not None and temperature is not None:
            return {'temperature': temperature, 'humidity': humidity}
        else:
            return {'error': 'Failed to read temperature/humidity'}
    except Exception as e:
        logging.error(f"DHT11 sensor error: {e}")
        return {'error': 'Failed to read temperature/humidity'}

def get_weight() -> float:
    """
    Get the weight reading from the HX711 sensor.
    """
    try:
        raw_data = hx.get_raw_data()
        weight = sum(raw_data) / len(raw_data) * calibration_factor
        return weight
    except Exception as e:
        logging.error(f"Error during weight reading: {e}")
        return 0.0

def main():
    # Calibrate the scale with a known weight (e.g., 1 kg)
    calibrate_scale(1)  # Assuming 1 kg known weight
    
    while True:
        temperature_humidity = get_temperature_humidity()
        weight = get_weight()
        
        # Log sensor data
        sensor_data = {
            'temperature_humidity': temperature_humidity,
            'weight': weight
        }
        logging.info(f"Sensor Data: {sensor_data}")
        
        time.sleep(1)  # Adjust sleep time as necessary

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Program terminated.")
        GPIO.cleanup()
