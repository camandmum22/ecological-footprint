from __future__ import division
import serial
import time
from time import sleep
import socket
import sys
import decimal
import traceback
import commands
import struct
import smtplib
import math
from datetime import date, datetime

port = serial.Serial('/dev/ttyAMA0', baudrate=600, timeout=10.0)
TIPO_MEDIDOR = 1#Medidor Monofasico, cambiar a 3 si se esta trabajando con mediores trifasicos
calibras = [chr(0xe6),           chr(0xf6),         chr(0xfe)]
#calibras = [DC Corr & Volt(0), AC Corr & Volt(1), Gain Corr & Volt(2)]
controles = [chr(0xc1),chr(0xc2),chr(0xc3),chr(0xd4),chr(0xd5),chr(0xd8)]
#controles = [Reset(0), Stanby(1), Wakeup(2), Single Conv.(3), Continuous Conv.(4), Halt Conv.(5)]
titulos = ['Potencia Activa', 'Potencia rectiva', 'Corriente RMS','Voltaje RMS','Factor Potencia', 'Potencia Aparente', 'I corriente','V oltaje','P otencia']

mensajes = [chr(0x05), chr(0x0e), chr(0x06),chr(0x07),chr(0x15),chr(0x14),chr(0x02),chr(0x03),chr(0x04)]
#mensajes = [hex(5), hex(14), hex(6), hex(7), hex(21), hex(20), hex(2), hex(3), hex(4)]
lectura =[chr(0x2b),chr(0x00),chr(0x3f),chr(0x17),chr(0x18),chr(0x19),chr(0x07)]
#lectura =[hex(43),hex(0),hex(63),hex(23),hex(24),hex(25),hex(7)] #Rogowski, Escala p18, status0 p0, status1 p0, status2 p0, SerialCtrl p0
paginas = [chr(0x90),chr(0x92),chr(0x80)] ##PAgina 16 10!010000, pagina 18, pagina 0
escritura = [chr(0x61),chr(0x63),chr(0x6b),chr(0x14),chr(0x39),chr(0x58),chr(0x18),chr(0x00),chr(0x00)
			,chr(0x7f),chr(0x63),chr(0x6b),chr(0x14)#Escala 63 p18	4CCCCD
			,chr(0x57),chr(0x63),chr(0x6b),chr(0x14)#Status0 23 p0	C00020
			,chr(0x58),chr(0x63),chr(0x6b),chr(0x14)#Status1 24 p0	C01800
			,chr(0x59),chr(0x63),chr(0x6b),chr(0x14)#Status2 25 p0	00002D
			,chr(0x47),chr(0x63),chr(0x6b),chr(0x14)#SerialCtrl 7 p0 02004D
			]
			#I gain, V gain, Rogowski Coil Integrator gain 01|43, 50hz 0.158, 60hz 0.1875
			#50 hz 0.00101000011100101011000	00010100|00111001|01011000	Dec: 1325400  Hex: 143958 [2 345]
			#60 hz 0.00110000000000000000000	00011000|00000000|00000000	Dec: 1572864  Hex: 180000 [2 678]
tutorial = [chr(0x40),chr(0x10), chr(0x00),chr(0x1a)] #configuracion write and value
mensajes2 = ['pacti','preac','crms','vrms','fapot','papa','i','v','p']
intMaxCorriente = 200
intMaxVoltaje = 240
intMaxPotencia = intMaxVoltaje * intMaxCorriente
total = 0
malas = 0

def leerPuerto(num):
	cad1 = port.read(1).encode('hex')
	cad2 = port.read(1).encode('hex')
	cad3 = port.read(1).encode('hex')
	if not cad1:
		print 'cad1 empty'
		cad1 = '00'
	if not cad2:
		print 'cad2 empty'
		cad2 = '00'
	if not cad3:
		print 'cad3 empty'
		cad3 = '00'
	cadena = cad3+cad2+cad1
	print 'cadena', cadena
	return cadena

def fncVeintitresBitsEscala(valor, decFullScale, bitPunto, decEscala):
	#Potencia activa, Potencia reactiva, Potencia aparente --> Con escala
	#Factor de Potencia --> Sin escala
	print 'valor|decFullScale|bitPunto|decEscala', valor,'|', decFullScale,'|', bitPunto,'|', decEscala
	decReported = 0.0
	intRegister = int(valor,16)
	#intRegister = int((hex(int(valor,16)+0x200) & 0xFFFFFF),16)

	if intRegister <= 8388607:
		decReported = decimal.Decimal(intRegister)#/ 8388607
		#decReported = intRegister
	else:
		intRegister = 16777216 - intRegister
		decReported = decimal.Decimal(intRegister)#/ 8388607
		decReported = decReported * (-1)
		#decReported = intRegister * (-1)

	var1 = decimal.Decimal(math.pow(2, bitPunto))
	var2 = decimal.Decimal(math.pow(2, (23 - bitPunto)))
	decReported = (decReported / var1)
	decReported = (decReported / var2) * decFullScale
	#-------------add-------------
	if decEscala == 0.36:
		#print 'Escala'
		decEscala2 = decimal.Decimal(decEscala)
		decReported = (decReported / decEscala2)

	return decReported

def fncVeinticuatroBits(valor, decCurrentFullScale, decDivisor):
	#Voltaje RMS, Corriente RMS
	print 'valor|decCurrentFullScale|decDivisor', valor,'|', decCurrentFullScale,'|', decDivisor
	intCurrentRegister = int(valor, 16)
	decCurrentRegister = (intCurrentRegister / 16777215)
	decReportedCurrentActual = (decCurrentRegister * decCurrentFullScale) / decDivisor
	return decReportedCurrentActual

def conversion(hexa,bin,tipo,a,b,c):
	#Read IRMS, VRMS, and PAVG. Scale the IRMS, VRMS, and PAVG back into true value by:
	#Amps = Full_Scale_Current * (IRMS /0.6)
	#Volts = Full_Scale_Voltage * (VRMS /0.6)
	#Watts = Full_Scale_Power * (PAVG /0.36)
	result2 = 0
	if tipo == 'pacti':#potencia activa Pg=16,Ad=5
		result2 = fncVeintitresBitsEscala(hexa,intMaxPotencia, 23, 0.36)
	elif tipo == 'preac':#potencia reactiva Pg=16,Ad=14
		result2 = fncVeintitresBitsEscala(hexa,intMaxPotencia,  23, 0.36)
	elif tipo == 'crms':#corrienteRMS Pg=16,Ad=6
		result2 = fncVeinticuatroBits(hexa,intMaxCorriente, 0.6)
	elif tipo == 'vrms':#voltajeRMS Pg=16,Ad=7
		result2 = fncVeinticuatroBits(hexa,intMaxVoltaje, 0.6)
	elif tipo == 'fapot':#factor de potencia Pg=16,Ad=21
		result2 = fncVeintitresBitsEscala(hexa,1, 23, 0)
	elif tipo == 'papa':#potencia aparente Pg=16,Ad=20
		result2 = fncVeintitresBitsEscala(hexa,intMaxPotencia, 23, 0.36)
	elif tipo == 'i':#Corriente Pg=16,Ad=2
		result2 = fncVeintitresBitsEscala(hexa,intMaxCorriente, 23,0)
	elif tipo == 'v':#Voltaje Pg=16,Ad=3
		result2 = fncVeintitresBitsEscala(hexa,intMaxVoltaje, 23,0)
	elif tipo == 'p':#Potencia Pg=16,Ad=4
		result2 = fncVeintitresBitsEscala(hexa,intMaxPotencia, 23, 0.36)
	
	s2 = "{0:.6f}".format(result2)
	print 'result',s2
	return s2

def senMail(data):
	try:
		server = 'smtp.gmail.com'
		server_port = '587'
		username = ''
		password = ''
		fromaddr = 'arquitecturacomputadoresicesi@gmail.com'
		toaddr = 'camilo2.2@outlook.com'
		message = 'Rpi #1: ' + str(data)
		time.sleep(60) ## cambiar a time.sleep(30)
		headers = ["From: " + fromaddr,
					"To: " + toaddr,
					"MIME-Version: 1.0",
					"Content-Type: text/html"]
		headers = "\r\n".join(headers)

		server = smtplib.SMTP(server + ':' + server_port)
		server.ehlo()
		server.starttls()
		server.ehlo()
		server.login(fromaddr,'computer2014')
		server.sendmail(fromaddr, toaddr, headers + "\r\n\r\n" + message)
		server.quit()
		print("SEND MAIL")
	except:
		print("NOT SEND")

def enviarAServer(mensaje):
	try:
		#TCP_IP = '192.168.130.182'
		#TCP_IP = '192.168.130.66'
		TCP_IP = '172.16.0.127' #Server Icesi
		TCP_PORT = 5005
		BUFFER_SIZE = 1024

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((TCP_IP, TCP_PORT))
		s.send(mensaje)
		data = s.recv(BUFFER_SIZE)
		s.close()
		print "SERVER OK:", data
	except:
		print("NOT SERVER")
		malas+=1

def cleanRepo():
	try:
		f = open("repo.txt","a")
		f.close()
	except:
		print "Fallo CLEAN"

def darBinFromHex(rcv):
	data = ''
	for r in rcv:
		data += bin(int(r, 16))[2:].zfill(len(r) * 4)
	return data

def saveData(data):
	try:
		f = open("repo.txt","a")
		f.write(data+"\n")
		f.close()
	except:
		f = open("dump.txt","a")
		f.write(data+"\n")
		f.close()

def separar3(cadena):
	data = []
	data=[cadena[x:x+8] for x in range(0,len(cadena),8)]
	return data

def inicializar():
	date = str(datetime.now())
	cleanRepo()
	print "INICIO",date
	enviarAServer("INICIO "+date)
	senMail("INICIO "+date)

	port.open()
	port.write(controles[0]) #Reset
	sleep(1)
	port.write(controles[2])#Wakewup
	sleep(0.8)
	port.write(controles[4])#3-Single Conv.  4-Continous Conv.
	sleep(0.8)
	#Read IRMS, VRMS, and PAVG. Scale the IRMS, VRMS, and PAVG back into true value by:
	#Amps = Full_Scale_Current * (IRMS /0.6)
	#Volts = Full_Scale_Voltage * (VRMS /0.6)
	#Watts = Full_Scale_Power * (PAVG /0.36)

	##LA ESCRITURA AL REVEZ: 678-->876
	#Write Rogowski 60 hz		180000
	port.write(paginas[1]) #pagina
	port.write(escritura[2]) #Write
	port.write(escritura[8])#3 6
	port.write(escritura[7])#4 7
	port.write(escritura[6])#5 8
	sleep(0.8)
	#Write Configuracion 2		10001A
	port.write(paginas[0]) #pagina
	port.write(tutorial[0]) #Write
	port.write(tutorial[3])
	port.write(tutorial[2])
	port.write(tutorial[1])
	sleep(0.8)
	##Write Escala		4CCCCD
	#port.write(paginas[1]) #pagina
	#port.write(escritura[9]) #Write
	#port.write(escritura[12])
	#port.write(escritura[11])
	#port.write(escritura[10])
	#sleep(0.8)
	##Write Status0		C00020
	#port.write(paginas[2]) #pagina
	#port.write(escritura[13]) #Write
	#port.write(escritura[16])
	#port.write(escritura[15])
	#port.write(escritura[14])
	#sleep(0.8)
	##Write Status1		C01800
	#port.write(paginas[2]) #pagina
	#port.write(escritura[17]) #Write
	#port.write(escritura[20])
	#port.write(escritura[19])
	#port.write(escritura[18])
	#sleep(0.8)
	##Write Status2		00002D
	#port.write(paginas[2]) #pagina
	#port.write(escritura[21]) #Write
	#port.write(escritura[24])
	#port.write(escritura[23])
	#port.write(escritura[22])
	#sleep(0.8)
	##Write SerialCtrl	02004D
	#port.write(paginas[2]) #pagina
	#port.write(escritura[25]) #Write
	#port.write(escritura[28])
	#port.write(escritura[27])
	#port.write(escritura[26])
	#sleep(0.8)

	#Read Rogowski 60 hz
	port.write(paginas[1]) #pagina
	port.write(lectura[0])
	sleep(0.5)
	m1 = leerPuerto(3)#port.read(3)
	#Read Configuracion 2
	port.write(paginas[0]) #pagina
	port.write(lectura[1])
	sleep(0.5)
	m2 = leerPuerto(3)
	#Read Escala
	port.write(paginas[1]) #pagina
	port.write(lectura[2])
	sleep(0.5)
	m3 = leerPuerto(3)
	#Read status0
	port.write(paginas[2]) #pagina
	port.write(lectura[3])
	sleep(0.5)
	m4 = leerPuerto(3)
	#Read status1
	port.write(paginas[2]) #pagina
	port.write(lectura[4])
	sleep(0.5)
	m5 = leerPuerto(3)
	#Read status2
	port.write(paginas[2]) #pagina
	port.write(lectura[5])
	sleep(0.5)
	m6 = leerPuerto(3)
	#Read SerialCtrl
	port.write(paginas[2]) #pagina
	port.write(lectura[6])
	sleep(0.5)
	m7 = leerPuerto(3)

	#rm1 = m1.encode('hex')#El RESTO se BORRO

	print 'HEX rogow,config2,escala,status0,status1,status2,SerialCtrl', m1,m2,m3,m4,m5,m6,m7
	#bm1 = darBinFromHex(rm1)
	#bm2 = darBinFromHex(rm2)
	#print 'rogow,config2 bin', bm1,bm1
	#port.close()

inicializar()
w=0
while True:
	sleep(1) # Cade 5 segundos, por ejemplo cambiar para 300 si se desea cada 5 minutos
	x = 0
	rcv_all = ''
	while x < len(mensajes)-3:#-4
		mensaje = mensajes[x]
		print 'X', x
		print 'mensaje:',str(paginas[0])+'|'+str(mensaje)+'|'+str(mensajes2[x])+'|'+titulos[x]
		port.write(paginas[0])
		port.write(mensaje)
		sleep(0.2)

		hexa = leerPuerto(3)#port.read(3)
		#hexa = m.encode('hex')
		bin1 = darBinFromHex(hexa)
		data = separar3(bin1)
		print 'hexa|bin|data', hexa,bin1,data

		a=data[0]#LSB octet
		b=data[1]#Middle octet
		c=data[2]#MSB octet

		num0 = conversion(hexa, bin1, mensajes2[x],a,b,c)

		if x<len(mensajes)-4:
			rcv_all += str(num0)+'|'
		else:#x=len(mensajes)-1
			rcv_all += str(num0)
		x+=1
	print 'rcv_all',rcv_all
	total+=1
	enviarAServer(rcv_all)
	saveData(rcv_all)
	w+=1
	if w%12 == 0:
		date = str(datetime.now())
		senMail("STATUS REPORT "+date+" total="+str(total)+" malas="+str(malas))#cada hora email de control
	#if w >= 1 : break

#enviarAServer('off')