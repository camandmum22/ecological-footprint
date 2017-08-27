# -*- coding: utf-8 -*-
####--------------------------------------------------------
#### Name:            sendip.py
#### Programmer:      Carlos Díaz
#### Created:         09/10/2012
#### Purpose:         Send a text message of the local 
####                  IP address
#### tomado y adaptado de: 
#### http://blog.turningdigital.com/2012/09/get-ip-address-of-raspberry-pi-operating-headlessly/
####--------------------------------------------------------
import time
import commands
import re
import smtplib
import os

server = 'smtp.gmail.com' #smtp server address
server_port = '587' #port for smtp erver
username = '' #gmail account
password = '' #password for that gmail account

fromaddr = 'arquitecturacomputadoresicesi@gmail.com' #address to send from
toaddr = 'camilo2.2@outlook.com' #address to send IP to
message = 'Rpi #1 IP: ' #message that is sent

#the interface may be wifi and it needs time to initialize
#so wait a little bit before parsing ifconifg
time.sleep(90) ## cambiar a time.sleep(30)

#extract the ip address (or addresses) from ifconfig
found_ips = []
ips = re.findall( r'[0-9]+(?:\.[0-9]+){3}', commands.getoutput("/sbin/ifconfig"))
for ip in ips:
    if ip.startswith("255") or ip.startswith("127") or ip.endswith("255"):
        continue
    found_ips.append(ip)

message += ", ".join(found_ips)
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
print("START 4")
os.system("sudo python /home/pi/Desktop/PdG-raspbi/new_tutorial_v4.py")