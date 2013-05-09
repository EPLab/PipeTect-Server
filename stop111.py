#!/usr/bin/env python

import socket

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
	cmd = "111_stop"

	client = "192.168.2.101"

	UDPSend(client, 55555, cmd)
