# Date: Julio 16, 2022
# By Germán López 
# Ingenieria de sistemas
# Fundacion Universitaria del Area Andina


# Import the machine module
import machine
import time
import sh1106
import dht
import utime
import network, time, urequests
from utelegram import Bot

# Constants
INTERVAL = 2000			# Sets the interval to 2 seconds
START_TIME = time.ticks_ms() # Records the current time
TELEGRAM_TOKEN = '5563640181:AAF86QckMH-8q3fZdVcieJuG50yEf7HNDEg'
URL = 'https://api.thingspeak.com/update?api_key=9FEL6A98BE1JD649&field1=0'

ultima_peticion = 0
intervalo_peticiones = 30

# OLED display initializations
scl = machine.Pin(22, machine.Pin.OUT, machine.Pin.PULL_UP)
sda = machine.Pin(21, machine.Pin.OUT, machine.Pin.PULL_UP)
i2c = machine.I2C(scl=scl, sda=sda, freq=400000)
oled = sh1106.SH1106_I2C(128, 64, i2c, addr=0x3C)

# DHT sensor initializations
d = dht.DHT11(machine.Pin(15))

# Photoresistor Sensor
photoresistor_sensor = machine.ADC(machine.Pin(36))  # (ADC(Pin(36)))

# Buzzer initialization
buzzer = machine.Pin(5, machine.Pin.OUT)

# Telegram Bot Initialization
telegram_bot = Bot(TELEGRAM_TOKEN)

########################### FUNCTIONS ################################

# Simple function for displaying the 
# Temperature readings
# in the OLED display
def display_reads(temperature, lumens):    
    # Clear the screen by populating the screen with black
    oled.fill(0)
    # Display the temperature
    oled.text('Temp *C: {}'.format(temperature), 10, 10)
    oled.text("Lumens:  " + str(lumens), 20, 20)
    # Update the screen display
    oled.show()
    print(temperature)
    
def read_temperature():
    # Get the DHT readings
    d.measure()
    t = d.temperature()
    return t
    
def read_lumens(sensor):
    lectura = int(sensor.read())
    return lectura

def play_buzzer():
    buzzer.value(1)

def stop_buzzer():
    buzzer.value(0)

def conectaWifi(red, password):
      global miRed
      miRed = network.WLAN(network.STA_IF)     
      if not miRed.isconnected():              #Si no está conectado…
          miRed.active(True)                   #activa la interface
          miRed.connect(red, password)         #Intenta conectar con la red
          print('Conectando a la red', red +"…")
          timeout = time.time()
          while not miRed.isconnected():           #Mientras no se conecte..
              if (time.ticks_diff (time.time(), timeout) > 10):
                  return False
      return True


######################################################################


################### MAIN FUNCTION ####################################

def run():
    try:
        # permite regular la precisión de lectura
        photoresistor_sensor.width(machine.ADC.WIDTH_12BIT)
        # permite trabajar con 3.3v
        photoresistor_sensor.atten(machine.ADC.ATTN_11DB)
        
        #telegram_bot.start_loop()
        #print("Bloquea")

        # This is the main loop
        while True:
            if conectaWifi ("Pacco", "3L3ctr02021"):
                print ("Conexión exitosa!") 
            if time.ticks_ms() - START_TIME >= INTERVAL:
                # Read sensors
                temperature = read_temperature()
                utime.sleep(0.1)
                lumens = read_lumens(photoresistor_sensor)
                utime.sleep(0.1)
                
                # Update the display
                display_reads(temperature, lumens)
                if temperature >= 30 and lumens <= 1100:
                    # buzz On
                    print("ALERTA!!!")
                    play_buzzer()
                else:
                    # buzzer off
                    print("NO HAY ALARMA")
                    stop_buzzer()
            
            if (time.time() - ultima_peticion) > intervalo_peticiones:
                # Read sensors
                temperature = read_temperature()
                utime.sleep(0.1)
                respuesta = urequests.get(URL + "&field1=" + str(temperature))
                print ("Conexion estable ThingSpeak: " + str(respuesta.status_code))
                respuesta.close ()

                
                
    
    except KeyboardInterrupt:
        stop_buzzer()
        
if __name__ == '__main__':
    run()
