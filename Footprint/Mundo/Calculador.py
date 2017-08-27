import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Huellav1.settings")
from django.conf.global_settings import DATETIME_FORMAT
from Footprint.models import *
import datetime, decimal

def darParFechaMediciones(mediciones):
    par = []
    fechas = obtenerFechaMediciones(mediciones)
    valores = obtenerValorMediciones(mediciones)
    #print('m f v: '+str(len(mediciones))+" "+str(len(fechas))+" "+str(len(valores)))
    for x in range(len(mediciones)):
        valor = [fechas[x],valores[x]]
        par.append(valor)
    return par

def darGranParFechaMediciones(mediciones):
    par = []
    fechas = obtenerFechaMediciones(mediciones)
    valores = obtenerValorMediciones(mediciones)
    edificios = obtenerEdificioMediciones(mediciones)
    puntos = obtenerPuntoMediciones(mediciones)
    tipos = obtenerTipoMediciones(mediciones)
    #print('m f v: '+str(len(mediciones))+" "+str(len(fechas))+" "+str(len(valores)))
    for x in range(len(mediciones)):
        valor = [fechas[x],valores[x],edificios[x],puntos[x],tipos[x]]
        par.append(valor)
    return par

def obtenerFechaMediciones(mediciones):
    N = []
    for x in mediciones:
        N.append(x.fecha)
    return N

def obtenerValorMediciones(mediciones):
    N = []
    for x in mediciones:
        N.append(float(x.valor))
    return N

def obtenerEdificioMediciones(mediciones):
    N = []
    for x in mediciones:
        N.append(x.edificio.id)
    return N

def obtenerPuntoMediciones(mediciones):
    N = []
    for x in mediciones:
        N.append(x.punto.denominacion)
    return N

def obtenerTipoMediciones(mediciones):
    N = []
    for x in mediciones:
        N.append(x.tipo_medicion.id)
    return N

def generarMatriz(lista):
    matriz= []
    for i in lista:
        matriz.append([str(i.id) + "," + str(i.fecha) + "," + str(i.valor) + ","
                    + str(i.punto.denominacion) + "," + str(i.edificio.id) + "," + str(i.tipo_medicion.id)])
    return matriz