#!/usr/bin/python3
from hx711 import HX711
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
hx = HX711(dout_pin=6, pd_sck_pin=5, gain_channel_A=64, select_channel='A')
err = hx.reset()

result = hx.zero(readings=30)
data = hx.get_raw_data_mean(readings=30)
print(data)

input("Put object, press enter")
data = hx.get_data_mean(readings=2)
value = float(5.7)
ratio = data / value
hx.set_scale_ratio(ratio)

while True:
    hx.power_up()
    input("read on enter")
    print(hx.get_weight_mean(30), 'g')
    input("remove object")