# Run a clock on 60 pixel Neopixel ring (bits 0..59)
# Show weather data on 48 pixel ring (bits 60..107)

# Howto: on a fresh Pico first install the "neopixel.py" library by uploading it to "/"
# then upload this main.py to "/"
# Source: https://gist.github.com/aallan/581ecf4dc92cd53e3a415b7c33a1147c

# WARNING: Do not turn on all LEDs at full brightness! This will lead to high current draw and strange errors/crashes!

import network
import socket
import time
import struct

from neopixel import Neopixel

# for weather
import urequests

from machine import Pin

BRIGHTNESS = 50

NTP_DELTA = 2208988800
host = "pool.ntp.org"

led = Pin("LED", Pin.OUT)

ssid = 'puffin-muffin'
password = 'iwannagotoscotlandagain'

openweather_api_key = "ENTERYOUROWNAPIKEYHERE"

# LEDs
numpix_outer = 60
numpix_inner = 48
numpix = numpix_outer + numpix_inner

# Colors
off = (0,0,0)
yellow = (255, 100, 0)
yellow_weak = (10, 4, 0)
orange = (255, 50, 0)
green = (0, 255, 0)
green_weak = (0, 10, 0)
blue = (0, 0, 255)
blue_weak = (0, 0, 10)
red = (255, 0, 0)
red_weak = (10, 0, 0)
white = (255, 255, 255)
white_weak = (10, 10, 10)

# Weather Vars
weather_cnt = 60
weather_color = red_weak
temp_cur = 0
temp_min = 0
temp_max = 0
# Time Vars
timezone = 0
hours = 0
mins = 0
secs = 0

DEBUG = True

def printd(in_str):
    if DEBUG:
        print(in_str)
        
def indicate_time_was_set(pixels, reps):
    for i in range(reps):
        pixels.fill(white)
        pixels.show()
        time.sleep(0.5)
        pixels.fill(yellow)
        pixels.show()
        time.sleep(0.5)

def set_time(pixels):
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
    
    # Blink a few times to show that we were successful
    indicate_time_was_set(pixels, 3)
    
# Calculate the correct pixel location by 1. mirroring and 2. rotating
def clock_mirror_rotate(pixel_in):
    pixel_out = numpix_outer - pixel_in
    pixel_out = pixel_out + (numpix_outer/2)
    pixel_out = pixel_out % numpix_outer
    return int(pixel_out)
    
def neopixel_set_time_h(pixels, numpix, time_h):
    pix_h     = int((time_h%12)/12*numpix_outer)
    pix_h     = clock_mirror_rotate(pix_h)+3
    pix_h_end = pix_h-5
    pixels.set_pixel_line_gradient(pix_h, pix_h_end, green_weak, green)
    #printd(f"h={time_h} -> pix={pix_h}")
    #printd(f"  after mirror + rotate: {pix_h} to {pix_h_end} (green)")

def neopixel_set_time_m(pixels, numpix, time_m):
    pix_m     = int((time_m)/60*numpix_outer)
    pix_m     = clock_mirror_rotate(pix_m)
    pix_m_end = pix_m-1
    pixels.set_pixel_line_gradient(pix_m, pix_m_end, orange, red)
    #printd(f"m={time_m} -> pix={pix_m}")
    #printd(f"  after mirror + rotate: {pix_m} to {pix_m_end} (red)")

def neopixel_set_time_s(pixels, numpix, time_s, en):
    pix_s     = int((time_s)/60*numpix_outer)
    pix_s     = clock_mirror_rotate(pix_s)
    pix_s_end = pix_s-1
    if en:
        pixels.set_pixel(pix_s,     (255,255,255))
        pixels.set_pixel(pix_s_end, (60,60,60))
    else:
        pixels.set_pixel(pix_s, (0,0,0))
    #printd(f"s={time_s} -> pix={pix_s}")
    #printd(f"  after mirror + rotate: {pix_s} to {pix_s_end} (white)\n")
        
# Open Weather
TEMPERATURE_UNITS = {
    "standard": "K",
    "metric": "°C",
    "imperial": "°F",
}
 
SPEED_UNITS = {
    "standard": "m/s",
    "metric": "m/s",
    "imperial": "mph",
}
 
units = "metric"
 
def get_weather(city, api_key, units='metric', lang='en'):
    '''
    Get weather data from openweathermap.org
        city: City name, state code and country code divided by comma, Please, refer to ISO 3166 for the state codes or country codes. https://www.iso.org/obp/ui/#search
        api_key: Your unique API key (you can always find it on your openweather account page under the "API key" tab https://home.openweathermap.org/api_keys
        unit: Units of measurement. standard, metric and imperial units are available. If you do not use the units parameter, standard units will be applied by default. More: https://openweathermap.org/current#data
        lang: You can use this parameter to get the output in your language. More: https://openweathermap.org/current#multi
    '''
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units={units}&lang={lang}"
    print(url)
    res = urequests.post(url)
    return res.json()
 
def print_weather(weather_data):
    print(f'Timezone: {int(weather_data["timezone"] / 3600)}')
    sunrise = time.localtime(weather_data['sys']['sunrise']+weather_data["timezone"])
    sunset = time.localtime(weather_data['sys']['sunset']+weather_data["timezone"])
    print(f'Sunrise: {sunrise[3]}:{sunrise[4]}')
    print(f'Sunset: {sunset[3]}:{sunset[4]}')   
    print(f'Country: {weather_data["sys"]["country"]}')
    print(f'City: {weather_data["name"]}')
    print(f'Coordination: [{weather_data["coord"]["lon"]}, {weather_data["coord"]["lat"]}')
    print(f'Visibility: {weather_data["visibility"]}m')
    print(f'Weather: {weather_data["weather"][0]["main"]}')
    print(f'Temperature: {weather_data["main"]["temp"]}{TEMPERATURE_UNITS[units]}')
    print(f'Temperature min: {weather_data["main"]["temp_min"]}{TEMPERATURE_UNITS[units]}')
    print(f'Temperature max: {weather_data["main"]["temp_max"]}{TEMPERATURE_UNITS[units]}')
    print(f'Temperature feels like: {weather_data["main"]["feels_like"]}{TEMPERATURE_UNITS[units]}')
    print(f'Humidity: {weather_data["main"]["humidity"]}%')
    print(f'Pressure: {weather_data["main"]["pressure"]}hPa')
    print(f'Wind speed: {weather_data["wind"]["speed"]}{SPEED_UNITS[units]}')
    #print(f'Wind gust: {weather_data["wind"]["gust"]}{SPEED_UNITS[units]}')
    print(f'Wind direction: {weather_data["wind"]["deg"]}°')
    if "clouds" in weather_data:
        print(f'Cloudiness: {weather_data["clouds"]["all"]}%')
    elif "rain" in weather_data:
        print(f'Rain volume in 1 hour: {weather_data["rain"]["1h"]}mm')
        print(f'Rain volume in 3 hour: {weather_data["rain"]["3h"]}mm')
    elif "snow" in weather_data:
        print(f'Snow volume in 1 hour: {weather_data["snow"]["1h"]}mm')
        print(f'Snow volume in 3 hour: {weather_data["snow"]["3h"]}mm')

def update_weather(weather_data):
    # Update bg color (see API docu https://openweathermap.org/weather-conditions)
    print(f"DBG: got weather {weather_data["weather"][0]["main"]}")
    weather_cur = weather_data["weather"][0]["main"]
    if weather_cur == "Rain":
        weather_color = blue
    elif weather_cur == "Thunderstorm":
        weather_color = white
    elif weather_cur == "Drizzle":
        weather_color = blue_weak
    elif weather_cur == "Snow":
        weather_color = red_weak
    elif weather_cur == "Clear":
        weather_color = yellow_weak
    elif weather_cur == "Clouds":
        weather_color = white_weak
    else:
        weather_color = off
    # TODO: add effects instead of static colors
    
    # Update temps
    temp_cur = int(weather_data["main"]["temp"])
    temp_min = int(weather_data["main"]["temp_min"])
    temp_max = int(weather_data["main"]["temp_max"])
    
    # Update timezone
    timezone = int(weather_data["timezone"] / 3600)
    
    return timezone, weather_color, temp_cur, temp_min, temp_max
    
def neopixel_set_weather(pixels):
    # Set the inner colors "background" color according to weather
    pixels.set_pixel_line(numpix_outer, numpix_outer + numpix_inner - 1, weather_color)
    # Set a color gradient from min to max temp for today
    pixels.set_pixel_line_gradient(numpix_outer + temp_min, numpix_outer + temp_max, green, orange)
    # Set the current temperature as single white pixel
    pixels.set_pixel(numpix_outer + temp_cur, white)
    printd(f"DBG: neopixel_set_weather: {numpix_outer+temp_cur} {numpix_outer + temp_min} {numpix_outer + temp_max}")
    # TODO: Handle negative temps
    # TODO: Properly define temp scale (which max/min should be handled?) (What is an easy to understand scale?)
    
def update_time():
    time_now = time.localtime()
    hours = time_now[3] + timezone
    mins = time_now[4]
    secs = time_now[5]
    return hours, mins, secs

def wlan_init(pixels):
    printd('Trying to connect to WLAN')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        printd('waiting for connection...')
        pixels.fill(blue)
        pixels.show()
        time.sleep(0.5)
        pixels.fill(white)
        pixels.show()
        time.sleep(0.5)

    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
        pixels.fill(red)
        pixels.show()
    else:
        printd('connected')
        status = wlan.ifconfig()
        printd( 'ip = ' + status[0] )
        pixels.fill(green)
        pixels.show()
    time.sleep(2)


def led_init():
    pixels = Neopixel(numpix, 0, 28, "GRB")
    pixels.brightness(5)
    pixels.fill(off)
    pixels.set_pixel_line(0, 107, red)
    pixels.show()
    pixels.brightness(BRIGHTNESS)
    return pixels

# Initialization
printd('Init')
pixels = led_init()

wlan_init(pixels)

led.on()
set_time(pixels)
time_now = time.localtime()
printd(time.localtime())
led.off()

# Initialize weather
weather_data = get_weather('winterthur', openweather_api_key, units=units)
timezone, weather_color, temp_cur, temp_min, temp_max = update_weather(weather_data)
if DEBUG:
    print_weather(weather_data)

# Periodically update time and weather
while True:
    hours, mins, secs = update_time()
    pixels.fill(off)
    neopixel_set_time_h(pixels, numpix, hours)
    neopixel_set_time_m(pixels, numpix, mins)
    neopixel_set_time_s(pixels, numpix, secs, True)
    neopixel_set_weather(pixels)
    pixels.show()

    time.sleep(1)

    # Get weather once every minute
    if weather_cnt > 0:
        weather_cnt -= 1
    else:
        weather_cnt = 60
        weather_data = get_weather('winterthur', openweather_api_key, units=units)
        timezone, weather_color, temp_cur, temp_min, temp_max = update_weather(weather_data)
        if DEBUG:
            print_weather(weather_data)
