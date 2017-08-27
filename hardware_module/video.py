import serial
import time
from time import sleep
import socket
import sys
import binascii
import decimal
import traceback
import commands
import re
import struct
import smtplib
from ast import literal_eval
from io import BytesIO

#param1 = sys.argv[1] #Primer argumento
port = serial.Serial('/dev/ttyAMA0', baudrate=600, timeout=10.0)
TIPO_MEDIDOR = 1#Medidor Monofasico, cambiar a 3 si se esta trabajando con mediores trifasicos
calibras = [chr(0xe6),           chr(0xf6),         chr(0xfe)]
#calibras = [DC Corr & Volt(0), AC Corr & Volt(1), Gain Corr & Volt(2)]
controles = [chr(0xc1),chr(0xc2),chr(0xc3),chr(0xd4),chr(0xd5),chr(0xd8)]
#controles = [Reset(0), Stanby(1), Wakeup(2), Single Conv.(3), Continuous Conv.(4), Halt Conv.(5)]

pagina =[chr(0x90),chr(0x90),chr(0x90),chr(0x90),chr(0x90),chr(0x90)]#PAgina 16 10!010000
titulos = ['Potencia Activa', 'Potencia rectiva', 'Corriente RMS','Voltaje RMS','Factor Potencia', 'Potencia Aparente']
#mensajes = [chr(0x80)+chr(0x17), chr(0x90)+chr(0x07), chr(0x90)+chr(0x03),chr(0x64)+'\n\r',chr(0x89)+'\n\r']
mensajes = [chr(0x05), chr(0x0e), chr(0x06),chr(0x07),chr(0x15),chr(0x14)]
paginaRog = [chr(0x92),chr(0x2b)] #pagina 18 10|010010,  lectura Rogowski
escritura = [chr(0x61),chr(0x63),chr(0x6b),chr(0x14),chr(0x39),chr(0x58),chr(0x18),chr(0x00),chr(0x00)]
			#I gain, V gain, Rogowski Coil Integrator gain 01|43, 50hz 0.158, 60hz 0.1875
			#50 hz 0.00101000011100101011000	00010100|00111001|01011000	Dec: 1325400  Hex: 143958 [2 345]
			#60 hz 0.00110000000000000000000	00011000|00000000|00000000	Dec: 1572864  Hex: 180000 [2 678]
tiposBin = [1,1,2,2,1,3]#
mensajes2 = ['pacti','preac','crms','vrms','fapot','papa']

def conversion(bin, tipo, a,b,c):
	#Read IRMS, VRMS, and PAVG. Scale the IRMS, VRMS, and PAVG back into true value by:
	#Amps = Full_Scale_Current * (IRMS /0.6)
	#Volts = Full_Scale_Voltage * (VRMS /0.6)
	#Watts = Full_Scale_Power * (PAVG /0.36)
	result = 0
	if tipo == 'crms':#corrienteRMS Pg=16,Ad=6
		result = (dec_to_float_CS5490_0(a,b,c)/0.6)*16
	elif tipo == 'vrms':#voltajeRMS Pg=16,Ad=7
		result = (dec_to_float_CS5490_0(a,b,c)/0.6)*310
	elif tipo == 'pacti':#potencia activa Pg=16,Ad=5
		#result = (dec_to_float_CS5490_1(a,b,c)/0.36)*4960
		d = decodificar(bin1,1)
		result = (d/0.36)*4960
	elif tipo == 'preac':#potencia reactiva Pg=16,Ad=14
		#result = (dec_to_float_CS5490_1(a,b,c)/0.36)*4960
		d = decodificar(bin1,1)
		result = (d/0.36)*4960
	elif tipo == 'papa':#potencia aparente Pg=16,Ad=20
		#result =  (dec_to_float_CS5490_1(a,b,c)/0.36)*4960
		d = decodificar(bin1,3)
		result = (d/0.36)*4960
	elif tipo == 'fapot':#factor de potencia Pg=16,Ad=21
		#result = dec_to_float_CS5490_1(a,b,c)
		d = decodificar(bin1,1)
		result = abs(d)#d
	else:#RARO 
		result +=0
	return result

def senMail(data):
    try:
        server = 'smtp.gmail.com'
        server_port = '587'
        username = ''
        password = ''
        fromaddr = 'arquitecturacomputadoresicesi@gmail.com'
        toaddr = 'camilo2.2@outlook.com'
        message = 'message from Rpi #1 IP: '
        time.sleep(30) ## cambiar a time.sleep(30)
        message += ", ".join(data)
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
        print("send")
    except:
        print("not Send MAil")

def longBitsToFloat(bits):
    return struct.unpack('d', struct.pack('Q', bits))[0]

def parse_bin(s):
    t = s.split('.')
    return int(t[0], 2) + int(t[1], 2) / 2.**len(t[1])
	
def parse_bin_complement(s):
    t = s.split('.')
    n =  int(t[0], 2)
    if n == 0:
        return int(t[1], 2) / 2.**len(t[1])
    else:#n==1
        return - int(t[1], 2) / 2.**len(t[1])


def darBinFromHex(rcv):
    data = ''
    for r in rcv:
        data += bin(int(r, 16))[2:].zfill(len(r) * 4)
    return data

def saveData(data):
    try:
        f = open("repo.txt","a")
        f.write(data+"/n")
        f.close()
    except:
        f = open("dump.txt","a")
        f.write(data+"/n")
        f.close()

def decodificar(binario, opt):
    data = ''
    if opt == 1:#Valor Complemento a 2 coma a la derecha de MSB: potencia activa, potencia reactiva, factor de potencia
        data = binario[:1] + '.' + binario[1:]
        #print 'decode pre 1',data
        data = parse_bin_complement(data)
        #print 'decode post 1',data
    elif opt == 2:#Valor unsigned coma a la izquierda de MSB: corriente RMS, voltaje RMS
        data = '0.' + binario[0:]
        #data = data.rstrip("0")
        #print 'decode pre 2',data
        data = parse_bin(data)
        #print 'decode post 2',data
    else:# opt == 3:#Valor unsigned coma a la derecha de MSB: potencia aparente
        data = binario[:1] + '.' + binario[1:]
        #lista = list(binario)
        #lista[0] = '0'
        #data = binario
        data = parse_bin(data)
        #data = data+ '.'	
    return data

def enviarAServer(mensaje):
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
    print "respuesta server:", data

def concatenar(lista):
    return ''.join(lista)

def separar3(cadena):
	data = []
	data=[cadena[x:x+8] for x in range(0,len(cadena),8)]
	return data

def dec_to_float_CS5490_0(c, b, a):
	#where c = MSB, b = MID ,a = LSB
	#CS5490_0 format for value in the range (0 <= val < 1.0)
	sum=0.0
	i=0
	n=1

	#process c
	for i in range(8):
		sum = sum + (( 1 if c[i]=='1' else 0 )* pow(2,-(n)))
		n += 1
	
	#process b
	for i in range(8):	
		sum = sum + (( 1 if b[i]=='1' else 0 )* pow(2,-(n)))
		n += 1
	
 	#process a
 	for i in range(8):
 		sum = sum + (( 1 if a[i]=='1' else 0 )* pow(2,-(n)))
		n += 1
		
	return sum;

def dec_to_float_CS5490_1(c, b, a):
	#where c = MSB, b = MID ,a = LSB
	#CS5490_1 format for value in the range (-1.0 <= val < 1.0)
	sum = 0
	i=0
	n=1
	
	if c[0]=='O' or c[0]=='0':#check the 24th(last)(MSB) bit in the 24-bit number ,if = 1 number is -ve,else +ve
		sum = 0.0;

		#process c
		for i in range(8):
			sum = sum + (( 1 if c[i]=='1' else 0 )* pow(2,-(n)))
			n += 1
	
		#process b
		for i in range(8):
			sum = sum + (( 1 if b[i]=='1' else 0 )* pow(2,-(n)))
			n += 1
	
	 	#process a
		for i in range(8):
			sum = sum + (( 1 if a[i]=='1' else 0 )* pow(2,-(n)))
			n += 1
	else: #if number is -ve, XXXX UNTESTESTED BLOCK XXXX
		print 'ENTRO ELSE RASO'
		#make sure we copy them in other variables,bcoz values may change during conversions
		v=0
		#uint8_t cc[9],bb[9],aa[9],_c,_b,_a,*x;
		cc = c#MSB
		bb = b#MID
		aa = a#LSB
		listcc = list(cc)
		listcc[0]='O'#make msb of c[7:0] = 0
		cc = ''.join(listcc)
		#v = ( bin_to_dec(cc)*256*256 + bin_to_dec(bb)*256 + bin_to_dec(aa) );#get the decimal of number[22:0]
		#v = -v;//negate (2' complement)
		#x=(uint8_t*)&v;
		#_a=*(x+0);//LSB
		#_b=*(x+1);//MID
		#_c=*(x+2);//MSB
		#_c = _c & ~(1<<7);//clear D7 bit of c byte
		return -dec_to_float_CS5490_1(c,b,a)

	return sum

def dec_to_float_CS5490_2(c, b, a):
	#where c = MSB, b = MID ,a = LSB
	#CS5490_0 format for value in the range (-2.0 <= val < 2.0)
	sum=0.0
	i=0
	n=1
	
	if (c[0]=='0' or c[0]=='O') and c[1]=='1':
		sum = 1.0
	else:
		sum = 0.0

	#process c
	for i in range(8):
		sum = sum + (( 1 if c[i]=='1' else 0 )* pow(2,-(n)))
		n += 1
	
	#process b
	for i in range(8):
		sum = sum + (( 1 if b[i]=='1' else 0 )* pow(2,-(n)))
		n += 1
	
 	#process a
	for i in range(8):
		sum = sum + (( 1 if a[i]=='1' else 0 )* pow(2,-(n)))
		n += 1
		
	if c[0]=='1' and (c[1]=='0' or c[1]=='O'):#-0 XXXX UNTESTES XXXX
		sum = -sum
	elif c[0]=='1' and c[1]=='1':#-1 XXXX UNTESTES XXXX
		sum = -(sum+1.0)

	return sum

def alistar_medidor():
	print 'Inicializando y calibrando medidor'
	port.open()
	#controles = [Reset(0), Stanby(1), Wakeup(2), Single Conv.(3), Continuous Conv.(4), Halt Conv.(5)]
	#port.write(controles[0]) #Reset
	#sleep(2)
	port.write(controles[2])#Wakewup
	sleep(0.5)
	#port.write(controles[3])#Single Conv.
	#sleep(0.5)
	#port.write(controles[4])#Continuous Conv.
	#sleep(0.5)

	#Read IRMS, VRMS, and PAVG. Scale the IRMS, VRMS, and PAVG back into true value by:
	#Amps = Full_Scale_Current * (IRMS /0.6)
	#Volts = Full_Scale_Voltage * (VRMS /0.6)
	#Watts = Full_Scale_Power * (PAVG /0.36)

	port.write(calibras[0])
	sleep(0.5)
	port.write(calibras[1])
	sleep(0.5)
	port.write(calibras[2])
	sleep(0.5)
	#port.write(paginaRog[0])
	#port.write(escritura[2])
	#port.write(escritura[6])#3 6
	#port.write(escritura[7])#4 7
	#port.write(escritura[8])#5 8
	#sleep(0.8)

	port.write(paginaRog[0])
	port.write(paginaRog[1])
	sleep(0.2)
	m = port.read(3)
	rcv2 = m.encode('hex')
	#print 'rogow hex', rcv2
	bin1 = darBinFromHex(rcv2)
	#print 'rogow bin', bin1
	#port.close()

alistar_medidor()
#w=0
while True:
	sleep(2) # Cade 5 segundos, por ejemplo cambiar para 300 si se desea cada 5 minutos
	x = 0
	rcv_all = ''
	for mensaje in mensajes:
	    #port.open() #Abro Conexion con medidor
	    print 'midiendo:',titulos[x]
	    port.write(pagina[x])
	    port.write(mensaje)
	    sleep(0.2)
	   
	    m = port.read(3)
	    rcv2 = m.encode('hex')
	    print 'dato hex', rcv2
	    bin1 = darBinFromHex(rcv2)
	    print 'dato bin', bin1

	    data = separar3(bin1)
	    print 'bytes',data
	    a=data[0]#LSB octet
	    b=data[1]#Middle octet
	    c=data[2]#MSB octet

	    num0 = conversion(bin1, mensajes2[x],a,b,c)
	    print 'dato decimal',num0
	    if x<5:
	    	rcv_all += str(num0)+'|'
	    else:#x>=5 ultimo
	    	rcv_all += str(num0)
	    x+=1
	#w+=1
	print 'mensaje',rcv_all
	enviarAServer(rcv_all)
	saveData(rcv_all)

#enviarAServer('off')
