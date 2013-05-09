#!/usr/bin/env python

import socket
import threading
import SocketServer
import struct

from datetime import datetime, time
from struct import *

import time

#from scapy.all import *
count = 0
time_cnt = 0
max_time_cnt = 1000

class ThreadedUDPRequestHandler(SocketServer.BaseRequestHandler):

	def handle(self):
		global client_list
		global count
		global time_cnt
		global max_time_cnt

		data = self.request[0]
		client_sock = self.request[1]
		host, ip = self.client_address
		cur_thread = threading.currentThread()
		print "Receive Hear Beat Message from: ", host
		print "seq ", count
		count = (count + 1) % 1000
		print "Get: ", data
		if not host in client_list:
			client_list.append(host)
#		if time_cnt == 0:
#			print "Send Time Packet"
		self.sendTime(host)
		time_cnt = (time_cnt + 1) % max_time_cnt
		pkt = pack('>BBBB', ord('{'), ord('H'), ord('A'), 0x99)
		b = bytearray(pkt)
		h, l = self.checksum(pkt)
		pkt += chr(h)
		pkt += chr(l)
		client_sock.sendto(pkt, (host, 2000))
#		client_sock.sendto(pkt, (host, 2000))
#		client_sock.sendto(pkt, (host, 2000))

		
#		cmd_start = [0x7b, 0x41, 0x53, 0x01, 0x00, 0x00]
#		cmd = ""
#		target = cmd_start[:]
#		for e in target:
#			cmd += chr(e)
#		target[4], target[5] = self.checksum(cmd[:4])
#		cmd = ""
#		for e in target:
#			cmd += chr(e)
		print "Send START cmd to the client ", host
		pkt = pack('>BBBB', ord('{'), ord('A'), ord('S'), 1)
		b = bytearray(pkt)
		h, l = self.checksum(pkt)
		pkt += chr(h)
		pkt += chr(l)
		print "HI %02X" % h
		print "LO %02X" % l
		client_sock.sendto(pkt, (host, 2000))
#		client_sock.sendto(pkt, (host, 2000))

#		client_sock.sendto(pkt, (host, 2000))
		pkt = pack('>BBBB', ord('{'), ord('A'), ord('S'), 2)
		b = bytearray(pkt)
		h, l = self.checksum(pkt)
		pkt += chr(h)
		pkt += chr(l)
#		client_sock.sendto(pkt, (host, 2000))
#		client_sock.sendto(pkt, (host, 2000))
#		client_sock.sendto(pkt, (host, 2000))

#		for host in client_list:
#			self.sendTime(host)
		

	def checksum(self, data):
		chksum = 0
		for e in data:
			chksum += ord(e)
		hi = chksum >> 8
		low = chksum % 256
		return hi, low

	def sendTime(self, dst):
		print "Sent time"
		t = datetime.now()
		pkt = pack('<BBBBBBBBBBH', ord('{'), ord('A'), ord('T'), 0xF0, t.month, t.day, t.year % 100, t.hour, t.minute, t.second, t.microsecond / 1000)
		h, l = self.checksum(pkt)
		pkt += chr(h)
		pkt += chr(l)
		pkt += pkt
		UDPSend(dst, 2000, pkt)


def UDPSend(ip, port, message):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	sock.sendto(message, (ip, port))

def checksum(data):
	chksum = 0
	for e in data:
		chksum += ord(e)
	hi = chksum >> 8
	low = chksum % 256
	return hi, low
		
if __name__ == "__main__":
	global client_list
	client_list = []
	left = ""
	
    # Port 0 means to select an arbitrary unused port
	#HOST, PORT = "192.168.1.200", 55555
	#HOST, PORT = "128.195.204.81", 55555
	HOST, PORT = '', 55555
#	HOST, PORT = '', 2000

	#t = threading.Timer(1.0, p.draw_picture())
	#t.start()
	handle = ThreadedUDPRequestHandler

 	cmd_stop = [0x7b, 0x41, 0x46, 0x01, 0x00, 0x00]
	cmd = ""
	target = cmd_stop[:]
	for e in target:
		cmd += chr(e)
	target[4], target[5] = checksum(cmd[:4])
	cmd = ""
	for e in target:
		cmd += chr(e)


	try:
		server = SocketServer.ThreadingUDPServer((HOST, PORT), handle)
		ip, port = server.server_address
		print "Listening of %s %s" % (ip, port)

		server.serve_forever()
	except KeyboardInterrupt:
		for client in client_list:
			pkt = pack('>BBBB', ord('{'), ord('A'), ord('F'), 1)
			b = bytearray(pkt)
			h, l = checksum(pkt)
			pkt += chr(h)
			pkt += chr(l)
			pkt = pkt + pkt + pkt + pkt + pkt
			print "Stoping client\t", client
			for cnt in range(100):
				UDPSend(client, 2000, cmd)
