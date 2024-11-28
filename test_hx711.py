import time
import RPi.GPIO as GPIO
from hx711 import HX711

# Suppress GPIO warnings
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Define pins
DT = 5  # Data pin
SCK = 6  # Clock pin

# Initialize HX711
hx = HX711(DT, SCK)

try:
    # Reset HX711
    hx.reset()
    
    # Tare the scale (set zero point)
    hx.tare()
    print("Tare complete. Place a weight.")

    while True:
        # Get weight reading
        raw_data = hx.get_raw_data_mean(5)
        print(f"Raw Data: {raw_data}")
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
