# Run a clock on 60 pixel Neopixel ring

# Howto: on a fresh Pico first install the "neopixel.py" library by uploading it to "/"

import json
import network
import socket
import time

# Funktion zum absenden eines HTTP Request und
# Rückgabe des HTTP Response
# Quelle: https://docs.micropython.org/en/latest/esp8266/tutorial/network_tcp.html
def http_get(url):
    result = ''
    received_data = False
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    send_bytes = bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8')
    s.send(send_bytes)
    while not received_data:
        data = s.recv(100)
        if data:
            result = result + str(data, 'utf8')
            print(f"GET result=({result:s})")
            received_data = True
        else:
            print("WARNING: Unable to get data!")
            time.sleep(1)
            s.close()
            s = socket.socket()
            s.connect(addr)
            s.send(send_bytes)
            #break
    s.close()
    return result

# Ermitteln des JSONs aus dem HTTP Response
def findJson(response):
    txt = 'abbreviation'
    return response[response.find(txt)-2:]

def wlan_init():
    ssid = 'puffin-muffin'
    password = 'iwannagotoscotlandagain'
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    print("Waiting to connect:")
    while not wlan.isconnected() and wlan.status() >= 0:
        print(".", end="")   
        time.sleep(1)
    print("")
    print(wlan.ifconfig())

# parsen des Zeitstempels
# Parameter ist das JSON als Dictionary
def parseDateTimeStr(responeDict):
    # umwandeln des UNIX Timestamp in eine Liste aus Datum & Zeit Werten
    dateTime = time.localtime(int(responeDict['unixtime']))
    year = dateTime[0]
    month = dateTime[1]
    dayOfMonth = dateTime[2]
    
    # Wenn der Monat kleiner als 10 ist,
    # dann eine führende Null anhängen
    if month < 10:
        month = str('0' + str(month))
        
    if dayOfMonth < 10:
        dayOfMonth = str('0' + str(dayOfMonth))
    dateStr = str(dayOfMonth)+'.'+str(month)+'.'+str(year)
    hour = dateTime[3]
    minutes = dateTime[4]
    # offset für die Uhrzeit auslesen
    timeOffset = responeDict['utc_offset']
    # Wenn der Offset mit einem Minus beginnt
    # dann soll der Wert abgezogen werden
    if timeOffset[0:1] == '-':
        hour = hour - int(timeOffset[1:3])
    elif timeOffset[0:1] == '+':
        # beginnt der Offset mit einem "+"
        # dann soll die Zeit addiert werden
        hour = hour + int(timeOffset[1:3])
    if hour < 10:
        hour = str('0' + str(hour))
    if minutes < 10:
        minutes = str('0' + str(minutes))
    
    timeStr = str(hour)+':'+str(minutes)
    # auslesen der Zeitzone
    timezone = responeDict['timezone']
    # zurückgeben der Zeitzone, des Datums sowie der Uhrzeit
    return timezone, dateStr, timeStr

def neopixel_init():
    import time
    from neopixel import Neopixel
     
    numpix = 30
    pixels = Neopixel(numpix, 0, 28, "GRB")
     
    yellow = (255, 100, 0)
    orange = (255, 50, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    red = (255, 0, 0)
    color0 = red
     
    pixels.brightness(50)
    pixels.fill(orange)
    pixels.set_pixel_line_gradient(3, 13, green, blue)
    pixels.set_pixel_line(14, 16, red)
    pixels.set_pixel(20, (255, 255, 255))
     
    while True:
        if color0 == red:
           color0 = yellow
           color1 = red
        else:
            color0 = red
            color1 = yellow
        pixels.set_pixel(0, color0)
        pixels.set_pixel(1, color1)
        pixels.show()
        time.sleep(1)

def get_time():
    url = "http://worldtimeapi.org/api/timezone/Europe/Berlin"
    response = http_get(url)
    print("response= "+response)
    jsonData = findJson(response)
    print("jsonData= "+jsonData)
    aDict = json.loads(jsonData)
    timezone, dateStr, timeStr = parseDateTimeStr(aDict)
    #print(timeStr)
    return timeStr

###############################################################
# Main
###############################################################
wlan_init()
timeStr = get_time()
print(timeStr)