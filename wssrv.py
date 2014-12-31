#!/usr/bin/env python
import socket
import sha
from base64 import b64encode
import re
from wsparse import wsparse, wsunparse
import SocketServer
import json

class wsHandler(SocketServer.BaseRequestHandler):

    def getSecKey(self, key):
	GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11' # This is a number specified by the standard (do not change)
	return b64encode(sha.new(key+GUID).digest()) # Concatenate the key and GUID to get the secret hash

    def httpparse(self, headers):
	return dict(re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n", headers)) 

    def datahandler(self, data):
	if data[:3].lower() == 'get':
	    data2 = self.httpparse(data)
	    if data2['Upgrade'].lower()=='websocket':
		return self.wsug(data2) # if the client is looking for websocket verification, give it to them
	else:
	    rdata = wsparse(data)
	    if not 'protocol' in rdata.keys():
		rdata.update({'protocol':None})
	    return rdata

    def wsug(self, data):
	rdict = {'type' : 'html'}
	response = [
		     'HTTP/1.1 101 Switching Protocols',
		     'Connection: Upgrade',
		     'Upgrade: WebSocket',
		     'Sec-WebSocket-Accept: %s' % self.getSecKey(data['Sec-WebSocket-Key'])
		   ]

	if 'Sec-WebSocket-Protocol' in data.keys() and data['Sec-WebSocket-Protocol'] in ('json',):
	    response.append('Sec-WebSocket-Protocol: ' + data['Sec-WebSocket-Protocol']) # If the server wants json, let 'em have it
	    rdict.update({'protocol':data['Sec-WebSocket-Protocol'].lower()})
	else:
	    rdict.update({'protocol':None})
	
	rdict.update({'payload':'\r\n'.join(response)+'\r\n'*2})
	return rdict

    def handle(self):
	
	while not self.closed:
	    data = self.request.recv(1024)
	    rdata = self.datahandler(data)
	    if rdata['protocol']:
		self.protocol = rdata['protocol']
		print "Protocol {}".format(self.protocol)
	    
	    if rdata['type'] == 'html':
		self.request.sendall(rdata['payload'])

	    elif rdata['opcode'] == '0x8': # opcode for connection close
		self.request.sendall(wsunparse({'opcode':8,'payload':rdata['text'][:2]})) # Standards specify that the server must send back a close frame
		self.request.close()
		break
		
	    elif rdata['opcode'] == '0x1': # Text opcode
		try:
		    rgb = json.loads(rdata['text'])
		except ValueError:
		    self.request.sendall(wsunparse({'opcode':8,'payload':'\x03\xea'})) # Protocol error
		    self.request.close()
		    self.closed = True
		    break

		print rgb
    
    def finish(self):
	
	print "Closed connection from %s:%d" % (self.client_address[0] , self.client_address[1])


    def setup(self):
	self.closed = False
	self.protocol = None
	print "Opened connection from %s:%d" % (self.client_address[0] , self.client_address[1])

if __name__ == '__main__':
    host, port = 'localhost' , 8080

    server = SocketServer.ThreadingTCPServer((host, port), wsHandler)
    server.serve_forever()
