#from xbee import XBee
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PDG.settings")
from Huellav2.Mundo import *
from Footprint.models import *
import django
django.setup()

class DataCollect(object):

    def guardarMedicion(valor1, punto1, edificio1, tipo_medicion1):

        valor2 = int(float(valor1))
        edificio2 = Edificio.objects.get(id=str(edificio1))
        punto2 = Punto_Monitoreo.objects.get(id=int(float(punto1)))
        tipo_medicion2 = Punto_Monitoreo.objects.get(id=int(float(tipo_medicion1)))

        medicion = Medicion(id=len(Medicion.objects.all())+1,valor=valor2,
                   punto = punto2, edificio = edificio2, tipo_medicion = tipo_medicion2)

        medicion.save()

#Recolector.guardarEntrada(60)
#Recolector.guardarSalida(50)
#totalProcesos = Proceso.objects.all()
#print(totalProcesos)

