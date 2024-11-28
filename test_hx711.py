import time
import RPi.GPIO as GPIO
from hx711 import HX711

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

DT = 5  # Data pin
SCK = 6  # Clock pin

GPIO.setup(DT, GPIO.IN)
GPIO.setup(SCK, GPIO.OUT)

print("Initializing HX711...")
hx = HX711(DT, SCK)

time.sleep(1)  # Add a small delay to allow the HX711 to stabilize

try:
    print("Getting raw data from HX711...")
    while True:
        raw_data = hx.get_raw_data()
        print(f"Raw Data: {raw_data}")
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
