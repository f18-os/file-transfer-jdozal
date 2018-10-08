#! /usr/bin/env python3

import sys
sys.path.append("../lib")       # for params
import re, socket, params

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)

sock, addr = lsock.accept()

print("connection rec'd from", addr)


from framedSock import framedSend, framedReceive

# setting path for received files
path='received/'
filename = ''

fileContent = False
while True:
    payload = framedReceive(sock, debug)
    if debug: print("rec'd: ", payload)
    if not payload:
        break
    
    # payload starts with 'filename' server knows that a file is being transfered 
    if payload.startswith(b"filename"):
        # filename starts after 'filename'
        filename = payload[8:].decode()
        # open new file in folder 'received'
        f = open(path+filename,"w+")
        fileContent = True
        continue
    
    # server knows file transfer is over 
    if payload.startswith(b"ending file transfer"):
        fileContent = False
        # close file 
        f.close()
        print("%s received!\n\n" % filename)
        continue
    
    # write contents into file 
    if fileContent:
        f.write(payload.decode())
    else:
        payload += b"!"             # make emphatic!
        framedSend(sock, payload, debug)
