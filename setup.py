import time
import RPi.GPIO as GPIO
from hx711 import HX711

GPIO.setmode(GPIO.BCM)

DT = 5  # Data pin
SCK = 6  # Clock pin

hx = HX711(DT, SCK)

try:
    hx.set_reading_format("MSB", "MSB")
    hx.reset()
    
    while True:
        raw_data = hx.get_raw_data_mean()
        print(f"Raw Data: {raw_data}")
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
