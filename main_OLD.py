# Run a clock on 60 pixel Neopixel ring

# Howto: on a fresh Pico first install the "neopixel.py" library by uploading it to "/"
# Source: https://gist.github.com/aallan/581ecf4dc92cd53e3a415b7c33a1147c


import network
import socket
import time
import struct

from neopixel import Neopixel

from machine import Pin

NTP_DELTA = 2208988800
host = "pool.ntp.org"

led = Pin("LED", Pin.OUT)

ssid = 'puffin-muffin'
password = 'iwannagotoscotlandagain'

def set_time():
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    val = struct.unpack("!I", msg[40:44])[0]
    t = val - NTP_DELTA    
    tm = time.gmtime(t)
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
    
def neopixel_set_time_h(pixels, numpix, time_h):
    pixels.brightness(50)
    pix_h = int((time_h%12)/12*numpix)
    print(f"h={pix_h}")
    pixels.set_pixel_line_gradient(pix_h, pix_h-5, blue_weak, green)
    pixels.show()

def neopixel_set_time_m(pixels, numpix, time_m):
    pixels.brightness(50)
    pix_m = int((time_m)/60*numpix)
    print(f"m={pix_m}")
    pixels.set_pixel_line_gradient(pix_m, pix_m-2, yellow, red)
    pixels.show()

def neopixel_set_time_s(pixels, numpix, time_s, en):
    pixels.brightness(50)
    pix_s = int((time_s)/60*numpix)
    print(f"s={pix_s}")
    if en:
        pixels.set_pixel(pix_s, (255,255,255))
        pixels.set_pixel(pix_s-1, (60,60,60))
    else:
        pixels.set_pixel(pix_s, (0,0,0))
    pixels.show()

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )

led.on()
#set_time()
time_now = time.localtime()
print(time.localtime())
led.off()


# LEDs
numpix = 60
pixels = Neopixel(numpix, 0, 28, "GRB")

off = (0,0,0)
yellow = (255, 100, 0)
orange = (255, 50, 0)
green = (0, 255, 0)
green_weak = (0, 50, 0)
blue = (0, 0, 255)
blue_weak = (0, 0, 50)
red = (255, 0, 0)
color0 = red

pixels.fill(off)

while True:
    time_now = time.localtime()
    pixels.fill(off)
    neopixel_set_time_h(pixels, numpix, time_now[3])
    neopixel_set_time_m(pixels, numpix, time_now[4])
    neopixel_set_time_s(pixels, numpix, time_now[5], True)
    time.sleep(1)
    #neopixel_set_time_s(pixels, numpix, time_now[5], False)
    #time.sleep(0.25)

