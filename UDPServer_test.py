#!/usr/bin/env python

import threading
import socket
import SocketServer
import struct

import matplotlib
matplotlib.use('Agg')

from pylab import *
from matplotlib.mlab import *

from datastore import *

from datetime import datetime, timedelta
import time

import multiprocessing

import Queue
import re
import os
import shutil

import sys, traceback
class counter(threading.Thread):
		def __init__(self):
			threading.Thread.__init__(self)
			self.event = threading.Event()

		def run(self):
			global threadPlotManager
			global pool
			global pkt_cnt
			global record_cnt
			global record_pkt
			global pkt_len

			idx = 0
			pool = []
			while not self.event.isSet():
				time.sleep(1)
##				print "recv %d pkts/sec" % pkt_cnt
##				print "handle %d records/sec" % record_cnt
#3				print "%d records (%d bytes)per pkt" % (record_pkt, pkt_len)
				pkt_cnt = 0
				record_cnt = 0
				record_pkt = 0
				pkt_len = 0

		def stop(self):
			self.event.set()

class RR(threading.Thread):
		def __init__(self):
			threading.Thread.__init__(self)
			self.event = threading.Event()

		def run(self):
			global threadPlotManager
			global pool
			global pkt_cnt
			global record_cnt
			global record_pkt
			global pkt_len

			idx = 0
			pool = []
			while not self.event.isSet():
				if not gui:
					continue
				time.sleep(0.5)
				if len(threadPlotManager) > 0:
#					time.sleep(0.3)
					p = threadPlotManager[idx]
#					tmp = p[0](0, p[1], p[2], p[3])
#					tmp.start()
					dp = multiprocessing.Process(target = draw_picture, args = (0, p[1], p[1]))
					dp.start()
#					pool.append(p)
					dp.join(None)
#					for item in pool:
#						if not item.is_alive():
#							pool.remove(item)
#					print "Active Drawing Process ", len(pool)

#					while tmp.isAlive():
#						time.sleep(0.01)
#						tmp.join(None)
					idx = (idx + 1) % len(threadPlotManager)

		def stop(self):
			self.event.set()

class ThreadedPlot(threading.Thread):
	output_ext = ".png"
	output_name = ""
	delay_sec = 0
	target = ""
	lock = None

	def __init__(self, delay, fname, target, debug):
		threading.Thread.__init__(self)
		self.output_name = fname
		self.event = threading.Event()
		self.delay_sec = delay
		self.target = target
		self.debug = debug

	def run(self):
#		p = multiprocessing.process(target = ThreadedPlot.draw_picture, args = (5, ))
#		p.start()
#		self.draw_picture(5)
#		draw_lock.release()
		pass

#		lastThread = None
#		while not self.event.is_set():
#			print "Fire draw picture\t", time.time()
#			nextFire = time.time() + self.delay_sec
#			lastThread = threading.Thread(target=self.draw_picture)
#			lastThread.start()
#			self.draw_picture()
#			self.event.wait(nextFire - time.time())
#		print "Stopping ", self.target

	def stop(self):
		self.event.set()

	def value_transform(self, v, base):
		return (v - base) * 0.0875

def draw_picture(sample_rate, target, fname):
	global readingMap
	global avg_old

	output_ext = ".png"
	limit = []
	tmp = []
	start = time.time()
#	print "get data from datastore"
	tmp = map(lambda x: x.get_reading(sample_rate), readingMap[target]['data'])
#	print "get done"
	value = []
	roocasID = target.split('.')[-1]
	gopherID = int(target.split('_')[-1]) % 16

	for idx in range(3):
		t = tmp[idx][:]
		avg = (0.0 + sum(t)) / len(t)
#			t = map(lambda x: x - avg, t)
#		avg = (0.0 + avg + avg_old[idx]) / 2
		avg_old[idx] = avg
		t = map(lambda x: (x - avg) * 0.0875, t)
		tmp[idx] = t[:]
		lo = min(t)
		hi = max(t)
		value.append("@%d " % avg)
		if lo > -2:
			lo = -2
		else:
			lo = lo * 1.3
		if hi < 2:
			hi = 2
		else:
			hi = hi * 1.3
		abs_limit = max(hi, abs(lo))
		limit.append([-abs_limit, abs_limit])
	if not (len(tmp) >= 3 and len(tmp[0]) and len(tmp[1]) and len(tmp[2])):
		return
	tmp[2].reverse()
	xtickslabels = ['30', '25', '20', '15', '10', '5', '0']
	xtickslabels.reverse()
	xtickslabels_tuple = tuple(xtickslabels)
#	print "start drawing"
	ioff()
	fig = figure(figsize = (6.4, 4.8), dpi = 72)
#	ax1 = fig.add_subplot(3, 1, 1)
#	ax1.plot(range(len(tmp[0])), tmp[0], 'b')
#	ax1.set_ylabel("X-axis")
#	ax1.set_ylabel("X")
#	ax1.set_ylim(limit[0])
#	ax2 = fig.add_subplot(2, 1, 1)
#	ax2.plot(range(len(tmp[1])), tmp[1], 'r')
#	ax2.set_ylabel("Y-axis")
#	ax2.set_ylabel("Y")
#	ax2.set_ylim(limit[1])
	ax3 = fig.add_subplot(1, 1, 1)
	ax3.plot(range(len(tmp[2])), tmp[2], 'g')
	ax3.set_ylabel("Z-axis")
#	ax3.set_ylabel("Z")
	ax3.set_ylim(limit[2])

#	ax3.set_xticklabels(('0', '5', '10', '15', '20', '25', '30'))
	ax3.set_xticklabels(xtickslabels_tuple)

#	setp(ax1.get_xticklabels(0), visible = False)
#	setp(ax2.get_xticklabels(0), visible = False)
	xlabel_str = 'Node ' + target.split('.')[-1]
	xlabel_str = 'Roocas ' + roocasID + ' Gopher ' + str(gopherID)
	xlabel(xlabel_str)
	fig.text(0.01, 0.5, 'ACC. (cm/s^2)', rotation = 'vertical')
	fig.text(0.85, 0.05, 'time (sec)')

#	print "show"
#	draw()
	show()
	real = fname + output_ext
	tmp = fname + ".tmp" + output_ext
#	print "save", fig.get_dpi(), fig.get_size_inches()
	savefig(tmp)
#	print "close"
	close()
	ion()
#	print "rename"
	os.rename(tmp, real)
	end = time.time()
##	print "Output %s for %f" % (fname, end - start)
#	print "Active Threads %d" % (threading.activeCount())

class UDPServer:
	def __init__(self, HOST = '', PORT = 8255, sps=1000):
		global readingMap
		global left
		global threadPlotManager
		global avg_old

		global mlock

		global record
		global record_name

		global gui

		global recv_q

		global pkt_cnt
		global record_cnt
		global record_pkt
		global pkt_len

		global old_seq
		global sample_per_sec
		sample_per_sec = sps



		avg_old = [0.0, 0.0, 0.0]

		old_seq = 0

		pkt_cnt = 0
		record_cnt = 0
		record_pkt = 0
		pkt_len = 0

		recv_q = Queue.Queue()

		record = True
		cur_t = datetime.now()
		record_name = ""

		gui = True

		mlock = threading.Lock()
		left = ""
		readingMap = {}
		threadPlotManager = []
		self.HOST, self.PORT = HOST, PORT

	def main(self):
		global threadPlotManager
		handle = ThreadedUDPRequestHandler

		pktParser = ThreadedPktParser()
		pktParser.start()

		sched = RR()
		sched.start()

		pktCnt = counter()
		pktCnt.start()

		try:
			server = SocketServer.ThreadingUDPServer((self.HOST, self.PORT), handle)
			ip, port = server.server_address
			print "Start UDP server on %s %d" % (ip , port)

			#p.start()
			server.serve_forever()

		except KeyboardInterrupt:
			record = False
			main_thread = threading.currentThread()
			for p in threading.enumerate():
				if p is main_thread:
					continue
				if hasattr(p, "stop"):
					p.stop()
				p.join()

class ThreadedUDPRequestHandler(SocketServer.BaseRequestHandler):

	def handle(self):
		global recv_q
		global mlock
		global pkt_cnt

		with mlock:
			pkt_cnt += 1
			data = self.request[0]
			client_sock = self.request[1]
			self.host, self.port = self.client_address
#print "RECV ", self.host
			recv_q.put((self.host, data))

class ThreadedPktParser(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.event = threading.Event()

	def run(self):
		global recv_q
		global mlock

		while not self.event.isSet():
			self.host, pkt = recv_q.get()
			self.parse(pkt)
			if recv_q.qsize() > 1000:
				print "Queue Size: ", recv_q.qsize()
			recv_q.task_done()

	def stop(self):
		self.event.set()

	def checksum(self, data):
		chksum = 0
		for e in data:
			chksum += ord(e)
		hi = chksum >> 8
		low = chksum % 256
		return hi, low

	def sendTimePkt(self, ip):
		t = datetime.now()
		pkt = struct.pack('<BBBBBBBBBBH', ord('{'), ord('A'), ord('T'), 0xF0, t.month, t.day, t.year % 100, t.hour, t.minute, t.second, t.microsecond / 1000)
		h, l = self.checksum(pkt)
		pkt += chr(h)
		pkt += chr(l)
		self.UDPSend(ip, pkt)

	def UDPSend(self, ip, message):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.sendto(message, (ip, 2000))

#		global threadPlotManager
#		global mlock

#		img_name = self.host + "_" + str(self.node_id - 1)
#		mlock.acquire()
#		for task in threadPlotManager:
#			if task[1] == img_name and task[2] == self.host:
#				mlock.release()
#				return
#		debug = 0
#		print "Add a task into threadPlotManager"
#		task = (ThreadedPlot, img_name, self.host, debug)
#		threadPlotManager.append(task)
#		f = open("template.html", 'r+')
#		o = open("liveAll.html", 'w+')
#		lines = f.readlines()
#		f.close()
#		for line in lines:
#			if 'IMGFILE' in line:
#				for i in range(len(threadPlotManager)):
#					p = threadPlotManager[i]
#					name = "%s.png" % p[1]
#					line = "<img src=\"%s\" id=\"%s\">\n" % (name, name)
#					o.write(line)
#			else:
#				o.write(line)
#		o.close()
#		mlock.release()
	def create_entry(self, host, sid):
		global threadPlotManager
		global readingMap
		global record
		global sample_per_sec

		key = "%s_%s" % (host, sid)
		if key not in readingMap:
			tmp = []
			cur_t = datetime.now()
			print "creating a new entry for ", key
			readingMap[key] = {}
			readingMap[key]['fname'] = ""
			readingMap[key]['ftime'] = None
			readingMap[key]['time'] = cur_t
			readingMap[key]['fd'] = None
			if re.search(r'^166\.140.*', key):
				readingMap[key]['sps'] = 1000
			elif re.search(r'169.234.4.173*', key):
				readingMap[key]['sps'] = 1000
			else:
				readingMap[key]['sps'] = 100
			for i in range(3):
				tmp.append(CondReading(threading.Lock(), threading.Lock(), 0.0, readingMap[key]['sps']))
#				if re.search(r'^166\.140.*', key):
#					tmp.append(CondReading(threading.Lock(), threading.Lock(), 0.0, 1000))
#				else:
#					tmp.append(CondReading(threading.Lock(), threading.Lock(), 0.0, 100))
			readingMap[key]['data'] = tmp[:]


#		create picture name for this task
			print "Add a task into ThreadPlotManager"
			task = (ThreadedPlot, key, key, False)
			threadPlotManager.append(task)
			readingMap[key]['save_order'] = len(threadPlotManager) % 5
			f = open("template.html", 'r+')
			o = open("liveAll.html", 'w+')
			lines = f.readlines()
			f.close()
			for line in lines:
				if 'IMGFILE' in line:
					for i in range(len(threadPlotManager)):
						p = threadPlotManager[i]
						name = "%s.png" % p[1]
						line = "<img src=\"%s\" id=\"%s\">\n" % (name, name)
						o.write(line)
				else:
					o.write(line)
			o.close()

		if record:
			if readingMap[key]['fname'] == "":
				cur_t = datetime.now()
				readingMap[key]['ftime'] = cur_t
				record_name = "data/%s/%s/%s_%s.log" % (cur_t.strftime("%Y%m%d"), cur_t.strftime("%H"), key, cur_t.strftime("%Y%m%d_%H%M%S"))
				d = os.path.dirname(record_name)
				if not os.path.exists(d):
					os.makedirs(d)
				readingMap[key]['fname'] = record_name
				readingMap[key]['fd'] = open(record_name, 'w+')
			else:
				if readingMap[key]['fd'] == None:
					print "open append"
					record_name = readingMap[key]['fname']
					readingMap[key]['fd'] = open(record_name, 'a+')

	def parse(self, load):
		global pkt_len
		global record_pkt
		global partial_record

		partial_record = ""

		pkt_len = len(load)
		state = 0
		record = ""
		recv_cnt = 0
		record_len = 0
		for b in load:
			if state == 0: # waiting for record delimeter
				if b == '{':
					record = ""
					state += 1
					recv_cnt = 2
				else:
					pass
			elif state == 1: # recv action header
				record += b
				recv_cnt -= 1
				if recv_cnt == 0:
					state = 2
				else:
					pass
			elif state == 2: # recv record length
				record_len = ord(b)
				recv_cnt = record_len
				record += b
				state += 1
			elif state == 3: # recv rest of the record
				record += b
				recv_cnt -= 1
				if recv_cnt == 0:
					state += 1
					recv_cnt = 2
				else:
					pass
			elif state == 4: # recv 2-byte CRC
				record += b
				recv_cnt -= 1
				if recv_cnt == 0: # recv record complete, invode associated function
					record_pkt += 1
					state = 0
#					if '{' in record:
#						print "Record :",
#						for t in record:
#							print "0x%02X" % ord(t),
#						print ""

					self.record_handle(record)
				else:
					pass
			else:
				print "state %d %02X" % (state , ord(b))
				print record
				state = 0


	def record_handle(self, t):
		global threadPlotManager
		global readingMap
		global record
		global record_name
		global gui

		global mlock

		global record_cnt

		global old_seq


		key = ""

		if len(t) == 5 and t[0] == 'S' and t[1] == 'G':
			value = ord(t[2])
			if value:
				gui = True
			else:
				gui = False
			return

		if (len(t) == 14 and t[0] == 'A' and t[1] == 'T'):
			length = ord(t[2])
			node_id = ord(t[3])
			key = "%s_%s" % (self.host, node_id)
#			if key not in readingMap:
#				continue
#			with mlock:
#				self.create_entry(self.host, node_id)
			(month, day, year, hour, minute, sec, msec)= struct.unpack('<bbbbbbH',t[4:12])
			"""
			if msec > 1000:
				msec = 0
			cur_t = datetime.now()
			if month > 12 or month < 1:
				month = cur_t.month
			if day > 31 or day < 1:
				day = cur_t.day
			if hour > 23 or hour < 0:
				hour = cur_t.hour
			if minute > 59 or minute < 0:
				minute = cur_t.minute
			if sec > 59 or sec < 0:
				sec = cur_t.second
			"""
			cur_t = datetime.now()
#			month = cur_t.month
#			day = cur_t.day
#			year = cur_t.year
			for key in readingMap.keys():
				if key.split('_')[0] == self.host:
					old_time = readingMap[key]['time']
					new_time = datetime(year + 2000, month, day, hour, minute, sec, msec * 1000)
					if new_time == old_time:
						print "SAME TIME"
					if new_time < old_time:
						td = new_time - old_time
						if td > timedelta(seconds = 1):
							print key, "time stamp is old ", new_time, old_time
							self.sendTimePkt(self.host)
					try:
						if new_time > old_time:
							print self.host, key, "Update Time", new_time, old_time
							readingMap[key]['time'] = new_time
					except Exception:
						print "TIME FORMAT ERROR"
						errlog = open('error.log', 'a+')
						traceback.print_exec(file=errlog)
						errlog.write("%d %d %d %d %d %d %d\n" % year, month, day, hour, minute, sec, msec)
						errlog.flush()
						errlog.close()
			debug = True
			if debug:
				print "Host:%s\t" % self.host,
#				print "LEN: %3d\t" % length,
				print "ID: 0x%02X\t" % node_id,
#				for key in readingMap.keys():
				if key in readingMap:
					print "Time: %s" % readingMap[key]['time'],
				print ""
			return

		if (len(t) > 13 and t[0] == 'A' and t[1] == 'D'):
			record_cnt += 1
			length = ord(t[2])
			node_id = ord(t[3])
			key = "%s_%s" % (self.host, node_id)
			with mlock:
				self.create_entry(self.host, node_id)
			seq = ord(t[4])
			debug = False
			if debug:
				if old_seq:
					if seq == old_seq:
						print "!!!!! seq is the same"
					elif seq > old_seq:
						if seq - old_seq > 1:
							print "!!!!!!Lost", (seq - old_seq), seq, old_seq
					else:
						if seq + 256 - old_seq > 1:
							print "!!!!!!Lost", (seq + 256 - old_seq), seq, old_seq
					old_seq = seq
				else:
					old_seq = seq
			value = struct.unpack('>hhh', t[5:11])
			timestamp = struct.unpack('<H',t[11:13])
			ts = timestamp[0] % 1000
			d = timedelta(milliseconds = ts)

			for idx in range(3):
				readingMap[key]['data'][idx].update_reading(value[idx])
			prev_rtime = readingMap[key]['time']
			timediff = 1000 / readingMap[key]['sps']
			if timediff < 1:
			 	timediff = 1
			exp_d = timedelta(milliseconds = timediff)
			exp_rtime = prev_rtime + exp_d
			rtime = datetime(prev_rtime.year, prev_rtime.month, prev_rtime.day, prev_rtime.hour, prev_rtime.minute, prev_rtime.second, ts * 1000)
			if ((exp_rtime - rtime) > exp_d):
				tmp_rtime = rtime + timedelta(seconds = 1)
				if (tmp_rtime - exp_rtime) < timedelta(milliseconds = (timediff * 3)):
#					print self.host, "RTIME SLOW", rtime, exp_rtime
#					print "Correct to", tmp_rtime
					rtime = tmp_rtime
				else:
					print self.host, "RTIME SLOW", rtime, exp_rtime

#				if exp_rtime.second - rtime.second == 1:
#					if abs(ts - (exp_rtime.microsecond/ 1000)) < timediff:
#						rtime = datetime(exp_rtime.year, exp_rtime.month, exp_rtime.day, exp_rtime.hour, exp_rtime.minute, exp_rtime.second, ts * 1000)
#						print "Correct to", timediff, rtime
			readingMap[key]['time'] = rtime
#			if re.search("111", key):
#				print "%02d:%02d:%02d.%03d\t" % (rtime.hour, rtime.minute, rtime.second, rtime.microsecond / 1000)
#				print "RTIME ", rtime, exp_rtime
#			readingMap[key]['time'] = rtime
			debug = False
			if record:
				output = "%3d\t[%03d]\t" % (node_id, seq)
				output += "%02d:%02d:%02d.%03d\t" % (rtime.hour, rtime.minute, rtime.second, rtime.microsecond / 1000)
				for idx in range(3):
					output += "%5d\t" % value[idx]
				output += "\n"
				readingMap[key]['fd'].write(output)
			if debug:
				print "Host:%s\t" % self.host,
				print "ID: %3d\t" % node_id,
				print "seq:%3d\t" % seq,
				print value, rtime

			if record:
				cur_t = datetime.now()
				if key not in readingMap:
					print "no key ", key
					return
				if "ftime" not in readingMap[key]:
					print "not ftime"
				if cur_t - readingMap[key]['ftime'] >= timedelta(minutes = 1):
#				if cur_t - readingMap[key]['ftime'] >= timedelta(seconds = 10):
						if readingMap[key]['save_order'] == (cur_t.minute % 5):
							print "log switching ", key, readingMap[key]['save_order']
							fname = readingMap[key]['fname']
							readingMap[key]['fname'] = ""
							p = multiprocessing.Process(target = closeFile, args = (readingMap[key]['fd'], fname))
							p.start()
							p.join(None)
#					print "save processing done"
							readingMap[key]['fd'] = None
#					readingMap[key]['fd'].flush()
#					readingMap[key]['fd'].close()
							host = key.split('_')[0]
							sid = key.split('_')[1]
							self.create_entry(host, sid)
#			p = multiprocessing.Process(target = relay, args = (fname,))
#			p.start()
			return

		print "invalid pkt", len(t)
		for c in t:
			if c == 'A' or c == 'D' or c == 'T':
				print c,
			else:
				print "0x%02X" % ord(c),
		print ""


# process to close fd
def closeFile(fd, fname):
#	fd.flush()
	fd.close()
	print "FNAME: %s" % fname
	# do log file checek
	fd = open(fname, 'r')
	tmplog = fname + ".tmp"
	ofd = open(tmplog, 'w')
	for line in fd.readlines():
		ofd.write(line)
		if len(line.split()) != 6:
			print fname, line
			break
	fd.close()
	ofd.close()
	os.remove(fname)
	shutil.copy(tmplog, fname)
	os.remove(tmplog)

# a function to be called by process
def relay(fname, server = "tchien.eng.uci.edu"):
	print "gen zip file for %s" % fname
	import os.path
	import os

	from ftplib import FTP
	import zipfile
	try:
		import zlib
		compression = zipfile.ZIP_DEFLATED
	except:
		compression = zipfile.ZIP_STORED

	ofname = ""
	for word in fname.split('.'):
		if word != "log":
			ofname += word + "."
	ofname += "zip"
	if os.path.exists(ofname) and os.path.isfile(ofname):
		return
	zf = zipfile.ZipFile(ofname, 'w')

	try:
		if os.path.exists(ofname) and os.path.isfile(fname):
			zf.write(fname, compress_type = compression)
	finally:
		zf.close()

#	if os.path.exists(ofname) and os.path.isfile(ofname):
#		ftp = FTP(server)
#		ftp.login("tcchien", "eecsadmin")
#		ftp.cwd("WebDocs/PipeTect/OCSD_log")
#		f = open(ofname, 'rb')
#		ftp.storbinary("STOR " + ofname, f)
#		ftp.quit()
#		f.close()
#		os.remove(ofname)
#		print "Upload data to " + server + " with file: " + ofname


if __name__ == "__main__":
    if len(sys.argv) > 1:
        rate = int(sys.argv[1])
    s = UDPServer(sps = rate)
    s.main()
