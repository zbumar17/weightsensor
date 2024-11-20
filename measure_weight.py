import RPi.GPIO as GPIO
import time
from hx711 import HX711

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

hx = HX711(dout_pin=9, pd_sck_pin=10)

calibration_factor = 102.372
zero_offset = 0

def tare_scale():
    global zero_offset
    try:
        print("Taring the scale... Please make sure it's empty and stable.")
        hx.reset()
        time.sleep(2)  # Allow some time for the sensor to stabilize

        raw_readings = []
        for _ in range(10):  # Take 10 readings to get the tare value
            raw_readings.append(hx.get_raw_data_mean())
            time.sleep(0.1)

        print("Raw readings for tare:", raw_readings)
        zero_offset = sum(raw_readings) / len(raw_readings)
        print(f"Taring complete. Zero offset: {zero_offset}")

    except Exception as e:
        print(f"Error during tare operation: {e}")

def calibrate_scale(known_weight):
    global calibration_factor
    try:
        print(f"Calibrating the scale with known weight: {known_weight} kg")
        tare_scale()

        # Ensure tare scale is performed
        raw_readings = []
        for _ in range(10):
            raw_readings.append(hx.get_raw_data_mean())
            time.sleep(0.1)

        print("Raw readings for calibration:", raw_readings)
        average_raw_data = sum(raw_readings) / len(raw_readings)
        calibration_factor = average_raw_data / known_weight  # Update calibration factor
        print(f"Calibration complete. Calibration factor: {calibration_factor}")

    except Exception as e:
        print(f"Error during calibration: {e}")

def get_weight_filtered():
    try:
        readings = []
        for _ in range(15):
            reading = hx.get_weight_mean(readings=10)
            if reading is not None:
                readings.append(reading)
            time.sleep(0.1)  # Add delay between readings to reduce noise

        if len(readings) < 10:
            raise ValueError("Not enough valid readings for filtering")

        readings.sort()
        filtered_readings = readings[len(readings) // 10: -len(readings) // 10]

        print("Sorted readings:", readings)
        print("Filtered readings:", filtered_readings)

        weight = sum(filtered_readings) / len(filtered_readings)
        print("Average weight (in grams):", weight)

        weight_kg = weight / 1000
        print(f"Weight (filtered): {weight_kg:.2f} kg")
        return weight_kg
    except Exception as e:
        print(f"Error getting filtered weight: {e}")
        return None

if __name__ == '__main__':
    tare_scale()
    calibrate_scale(1000)  # Assuming 1kg as the known weight for calibration

    while True:
        get_weight_filtered()  # Get filtered weight and print the result
        time.sleep(2)
