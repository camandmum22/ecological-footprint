import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Huellav1.settings")
from Huellav2.Mundo import *
from Footprint.models import *
import serial
import django
django.setup()

ser = serial.Serial('COM3', 9600)

# Continuously read and print packets
while True:
    try:
        print(1)
        #response = xbee.wait_read_frame()
        #dataIn = response['rf_data']
        #decodificacion = dataIn.decode()
        #print(decodificacion)
        #contenedor = decodificacion.split(";")
        #print(contenedor[1])
        #if(contenedor[1]=='A'):
        #    lola = float(contenedor[0])
        #    #print(lola)
        #    DataCollect.guardarEntrada(lola)
        #else:
        #    lola = float(contenedor[0])
        #    #print(lola)
        #    DataCollect.guardarSalida(lola)

    except KeyboardInterrupt:
        break

ser.close()