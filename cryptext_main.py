#IMPORTS - Ignore import resolution error, the pico will solve this when running with the proper modules.
import utime
from machine import I2C, Pin
import machine
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
from gpiozero import *
from random import choice
import network
from simple import MQTTClient

#GLOBAL VARIABLES - Alternatively using environment variables (on a more capable device) would be more secure.
#PICO_KEY_SET = 'ABCDEFEFGHIJKLMNOPQRSTUVWXYZ.?1234567890$@#!%&*()_/-=|~:;,^` ' #These are the current characters that are compatable.
PRIVATE_KEY = '34X81CG5SI)T#V:0%H?Q/D7B|;FL6!=^"ZJEUO~@+R 9*M$.WP_(NY2KA-&' #Example of a private key created by the generator.
PUBLIC_KEY = ''
MESSAGE = ''
ENCRYPTED_MSG = ''
MENU_POSITION = 0
ALPHA_LIST = [['<','A','1','B','2',' ','C','3','D','4',' ','E','5','F','6','>'],
             ['<','E','1','F','2',' ','G','3','H','4',' ','I','5','J','6','>'],
             ['<','K','1','L','2',' ','M','3','N','4',' ','O','5','P','6','>'],
             ['<','Q','1','R','2',' ','S','3','T','4',' ','U','5','V','6','>'],
             ['<','W','1','X','2',' ','Y','3','Z','4',' ','.','5','?','6','>'],
             ['<','1',' ','2',' ',' ','3',' ','4',' ',' ','5',' ','6',' ','>'],
             ['<','7','1','8','2',' ','9','3','0','4',' ','$','5','@','6','>'],
             ['<','#','1','!','2',' ','%','3','&','4',' ','*','5','(','6','>'],
             ['<',')','1','_','2',' ','/','3','-','4',' ','=','5','|','6','>'],
             ['<','~','1',':','2',' ',';','3',',','4',' ','^','5','`','6','>']]
COORDINATE_CONVERT = [1,3,6,8,11,13]

#LCD SCREEN - Screen address and information for initilization.
I2C_ADDR     = 63
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

#THINGSPEAK - Alternatively AWS would handle this better but MQTT is faster for demo purposes.
MQTT_CLIENT_ID = ""
MQTT_USERNAME = ""
MQTT_PASSWD = ""
MQTT_HOST = "mqtt3.thingspeak.com"
MQTT_PORT = int("")
CHANNEL_ID = ""
MQTT_WRITE_APIKEY = ""
MQTT_PUBLISH_TOPIC = "channels/" + CHANNEL_ID + "/publish"
WIFI_SSID = ""
WIFI_PASSWD = ""
WIFI_USER = ""

#BUTTONS - Defining the device buttons by pin number.
BTN_1 = Button(12)
BTN_2 = Button(11)
BTN_3 = Button(22)
BTN_4 = Button(16)
BTN_5 = Button(17)
BTN_6 = Button(15)
BTN_SPACE = Button(10)
BTN_NEXT = Button(20)
BTN_PREVIOUS = Button(13)
BTN_BACK = Button(14)
BTN_ENTER = Button(21)

#BUTTON CALLBACKS - Redirect the buttons to their correct sub function.
BTN_1.when_pressed = lambda: btn_pressed(0)
BTN_2.when_pressed = lambda: btn_pressed(1)
BTN_3.when_pressed = lambda: btn_pressed(2)
BTN_4.when_pressed = lambda: btn_pressed(3)
BTN_5.when_pressed = lambda: btn_pressed(4)
BTN_6.when_pressed = lambda: btn_pressed(5)
BTN_SPACE.when_pressed = lambda: btn_pressed("SPACE")
BTN_NEXT.when_pressed = lambda: btn_pressed("NEXT")
BTN_PREVIOUS.when_pressed = lambda: btn_pressed("PREVIOUS")
BTN_BACK.when_pressed = lambda: btn_pressed("BACK")
BTN_ENTER.when_pressed = lambda: btn_pressed("ENTER")

#BUTTON FUNCTIONS - Control how the program responds to a button press.
def update_lcd_menu(): #Everytime a button is pressed the screen must be updated.
    lcd.clear()
    lcd.move_to(0,1)
    lcd.putstr(ALPHA_LIST[MENU_POSITION])
    lcd.move_to(0,0)
    if len(MESSAGE) > 16:
        lcd.putstr(MESSAGE[-16:]) #Only display the most recent characters.
    else:
        lcd.putstr(MESSAGE)

def btn_pressed(btn):
    global MENU_POSITION, MESSAGE

    if btn in range(6): #Grab the character that relates to the button value from the character map and append it to the message.
        coordinate = COORDINATE_CONVERT[btn]
        MESSAGE += ALPHA_LIST[MENU_POSITION][coordinate]
        pass

    if btn == "SPACE": #Append a space character to the message.
        MESSAGE += ' ' #Note that space must be in the private key naturally and not displayed in the menu.
        pass

    if btn == "NEXT": #Scroll the menu position one forward.
        MENU_POSITION += 1
        if MENU_POSITION >= len(ALPHA_LIST):
            MENU_POSITION = 0

    if btn == "PREVIOUS": #Scroll the menu position one backward.
        MENU_POSITION -= 1
        if MENU_POSITION < 0:
            MENU_POSITION = len(ALPHA_LIST)-1
    
    if btn == "BACK": #Remove one character from the message.
        MESSAGE = MESSAGE[:-1]
    
    update_lcd_menu() #Update the lcd menu to reflect the updated message or menu position.

    if btn == "ENTER": #We need a buffer time to send the message so a simple hardcoded animation will work for demo purposes.
            encrypt()
            send_msg()
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr("Sending")
            utime.sleep(0.2)
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr("Sending.")
            utime.sleep(0.2)
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr("Sending..")
            utime.sleep(0.2)
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr("Sending...")
            utime.sleep(0.2)
            utime.sleep(0.2)
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr("Sent.")
            utime.sleep(2)
            lcd.clear()
            MESSAGE = ''
            MENU_POSITION = 0
            start_here()
    
#ENCRYPTION FUNCTIONS - Pico supported encryption algorithm.
def encrypt(): 
    global PRIVATE_KEY, PUBLIC_KEY, MESSAGE,ENCRYPTED_MSG
    temp_key = PRIVATE_KEY
    for i in range(len(MESSAGE)):
        char = choice(temp_key)
        temp_key.replace(char, '')
        PUBLIC_KEY += char
    for i in range(len(MESSAGE)):
        new_i = PRIVATE_KEY.index(MESSAGE[i]) + PRIVATE_KEY.index(PUBLIC_KEY[i])
        if new_i >= len(PRIVATE_KEY):
            new_i -= len(PRIVATE_KEY)
        ENCRYPTED_MSG += PRIVATE_KEY[new_i]

#MESSAGE SEND FUNCTION - Connect to the client and send the message.
def send_msg():
    WiFiLed = machine.Pin("LED", machine.Pin.OUT)
    WiFiLed.value(0)

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.scan()
    wlan.isconnected()

    wlan.connect(WIFI_SSID, WIFI_PASSWD)
    while not wlan.isconnected():
        machine.idle()

    WiFiLed.value(1)
    client = MQTTClient(client_id=MQTT_CLIENT_ID, server=MQTT_HOST, port=MQTT_PORT, user=MQTT_USERNAME, password=MQTT_PASSWD, ssl=False)
    client.connect(clean_session=True)
    pub_topic = f"field1=[{ENCRYPTED_MSG}][{PUBLIC_KEY}]"
    client.publish(MQTT_PUBLISH_TOPIC, pub_topic)

def start_here(): #Load directly into the map menu.
    lcd.clear()
    lcd.move_to(0,1)
    lcd.putstr(ALPHA_LIST[0]) 

#GREETING MESSAGE AND MENU LOAD - Load the initial menu before the code so no input can be taken during startup.
lcd.clear()
lcd.move_to(3,0)
lcd.putstr("Welcome To")
lcd.move_to(0,1)
lcd.putstr("Project CrypT3x!")
utime.sleep(2)
lcd.clear()
lcd.move_to(4,0)
lcd.putstr("Made By")
lcd.move_to(0,1)
lcd.putstr("Kolby MacDonald")
utime.sleep(1)
start_here()

while True:
    pass