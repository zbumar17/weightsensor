import time
import RPi.GPIO as GPIO
from hx711 import HX711

# Suppress GPIO warnings
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Define pins
DT = 5  # Data pin
SCK = 6  # Clock pin

# Explicitly set up GPIO pins
GPIO.setup(DT, GPIO.IN)
GPIO.setup(SCK, GPIO.OUT)

# Initialize HX711
print("Initializing HX711...")
hx = HX711(DT, SCK)

try:
    print("Resetting HX711...")
    # Reset HX711
    #hx.reset()

    print("Taring the scale...")
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
