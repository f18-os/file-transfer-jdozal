#! /usr/bin/env python3

# Echo client program
import socket, sys, re

sys.path.append("../lib")       # for params
import params

from framedSock import framedSend, framedReceive


switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]

if usage:
    params.usage()


try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

s = None
for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        print(" error: %s" % msg)
        s = None
        continue
    try:
        print(" attempting to connect to %s" % repr(sa))
        s.connect(sa)
    except socket.error as msg:
        print(" error: %s" % msg)
        s.close()
        s = None
        continue
    break

if s is None:
    print('could not open socket')
    sys.exit(1)

# Function to open file and send contents to server 
def sendFile(filename):
    # except file not found 
    try:
        # open file 
        f=open(filename, "r")
    except:
        print("Not an available file, try again.\n")
        return
    # first send filename <filepath> to let know user about file    
    line = 'filename' + filename
    framedSend(s, line.encode('UTF-8'), debug)
    
    # read contents of file 
    contents =f.read()
    
    # send contents to server 
    framedSend(s, contents.encode('UTF-8'), debug)

    # let know server that file transfer is over 
    framedSend(s, b"ending file transfer", debug)
    

# instructions to send a file or a line 
print("\n\nTo send a file to the server enter: sendfile <filepath>")
print("To send a line to the server enter: sendline <line>")
print("To exit type 'quit'\n")

while True:
    # getting input from user
    userInput = input()
    
    # if user enters a line send line to server 
    if(userInput.startswith('sendline')):
        # line starts after 'sendline'
        line = userInput[9:]
        
        # send to server 
        framedSend(s, line.encode('UTF-8'), debug)
        
        # 'talking to server'
        print("received:", framedReceive(s, debug))
        print('')
    
    # send file to server 
    elif(userInput.startswith('sendfile')):
        # name of file starts after 'sendfile'
        filename = userInput[9:]
        
        # function to open file and send contents
        sendFile(filename)
        
    elif(userInput == 'quit'):
        break
    else:
        print("Not an available option\n")


