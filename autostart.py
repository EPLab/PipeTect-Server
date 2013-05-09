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
start111 = False
start115 = False

start_cnt = 0

known_hosts = []

class ThreadedUDPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        global client_list
        global count
        global time_cnt
        global max_time_cnt

        global start111
        global start115

        global start_cnt

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

        if data == "111_start":
            print "start 111"
            start111 = True
        if data == "115_start":
            print "start 115"
            start115 = True
        if data == "111_stop":
            start111 = False
        if data == "115_stop":
            start115 = False

        time_cnt = (time_cnt + 1) % max_time_cnt

        ackPkt = pack('>BBBB', ord('{'), ord('H'), ord('A'), 0x99)
        b = bytearray(ackPkt)
        h, l = self.checksum(ackPkt)
        ackPkt += chr(h)
        ackPkt += chr(l)

        startPkt = pack('>BBBB', ord('{'), ord('A'), ord('S'), 1)
        b = bytearray(startPkt)
        h, l = self.checksum(startPkt)
        startPkt += chr(h)
        startPkt += chr(l)

        stopPkt = pack('>BBBB', ord('{'), ord('A'), ord('F'), 1)
        b = bytearray(stopPkt)
        h, l = self.checksum(stopPkt)
        stopPkt += chr(h)
        stopPkt += chr(l)

        tPkt = self.genTimePkt()

#		if host == "192.168.2.111":
#			if start111:
#				print "send start command to ", host
#				pkt = ackPkt + tPkt + pkt
#			else:
#				pkt = ackPkt + tPkt
#		else:
#			if start115:
#				print "send start command to ", host
#				pkt = ackPkt + tPkt + pkt
#			else:
#				pkt = ackPkt + tPkt

        if host in known_hosts:
            if start_cnt % 17 == 0:
                print "ACK and START"
                pkt = ackPkt + startPkt
            else:
                print "ACK ONLY"
                pkt = ackPkt
            pkt = ackPkt + startPkt
        else:
            print "SEND TIME"
            pkt = ackPkt + tPkt + startPkt
            known_hosts.append(host)
#		pkt = ackPkt + tPkt + startPkt

        UDPSend(host, 2000, pkt)

        start_cnt = (start_cnt + 1) % 100



    def checksum(self, data):
        chksum = 0
        for e in data:
            chksum += ord(e)
        hi = chksum >> 8
        low = chksum % 256
        return hi, low

    def genTimePkt(self):
        print "Sent time"
        t = datetime.now()
        pkt = pack('<BBBBBBBBBBH', ord('{'), ord('A'), ord('T'), 0xF0, t.month, t.day, t.year % 100, t.hour, t.minute, t.second, t.microsecond / 1000)
        h, l = self.checksum(pkt)
        pkt += chr(h)
        pkt += chr(l)
        return pkt


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
    HOST, PORT = '', 55555

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
