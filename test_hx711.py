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
hx = HX711(DT, SCK)  # Pass the pins directly without keyword arguments

try:
    # Reset HX711
    hx.reset()

    # Tare to set zero point
    print("Taring... Remove all weights.")
    hx.tare()
    print("Tare complete. Place weight.")

    while True:
        # Read weight
        raw_data = hx.get_weight_mean(5)  # Get an average of 5 readings
        print(f"Weight: {raw_data} grams")

        # Power down the HX711 between readings
        hx.power_down()
        hx.power_up()
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
