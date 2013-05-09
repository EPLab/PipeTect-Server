import threading
import time
from datetime import datetime, timedelta

import zipfile
import os

#from DataLog import DataLog

#from sqlalchemy import *
#from sqlalchemy.orm import *
#from sqlalchemy.ext import sqlsoup

import matplotlib
matplotlib.use('Agg')
from pylab import *
from matplotlib.mlab import *
from matplotlib.ticker import MultipleLocator

import copy


class FTPServer(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.event = threading.Event()
		self.duration = 60

		# database variables
#		self.engine = None
#		self.global_ession = None

		# data plotter
		self.plotters = {}
		self.d_array = {}

	def run(self):
		while not self.event.is_set():
			start_time = time.time()
			nextFire = 0
			if self.duration > 0:
				nextFire = start_time + self.duration
			self.task()
			end_time = time.time()
			print "Task time: %f" % (end_time - start_time)
			if self.duration > 0:
				wait = nextFire - end_time
				if wait < 0:
					print "no wait!!"
					continue
				else:
					self.event.wait(nextFire - end_time)
	
	def stop(self):
		self.event.set()

	def task(self):
		print "Retrive file names"
		for root, dirs, files in os.walk('.'):
			for name in files:
				if name.split('.')[-1] == 'zip' and zipfile.is_zipfile(name):
					print name
					nlist = name.split('_')
					Roocas_ID = nlist[0]
					Gopher_ID = nlist[1]
					print Roocas_ID, Gopher_ID
					dstr = nlist[2]
					tstr = nlist[3].split('.')[0]
					dyear = int(dstr[0:4])
					dmonth = int(dstr[4:6])
					dday = int(dstr[6:])
					dhour = int(tstr[0:2])
					dmin = int(tstr[2:4])
					dsec = int(tstr[4:])
					# load file create time
					dt = datetime(dyear, dmonth, dday, dhour, dmin, dsec, 0)
					db_name = Roocas_ID + '_' + Gopher_ID + '_' + dstr
#					self.db_connect(db_name)
					if db_name not in self.plotters:
						self.plotters[db_name] = dataPlotter(name)
						self.plotters[db_name].start()
					zf = zipfile.ZipFile(name, 'r')
					zfiles = zf.namelist()
					ptime_start = time.time()
					for zfile in zfiles:
						# prepare database
#						self.db_session_begin()
						# init. variables
						prev_seq = 0
						prev_msec = 0
						prev_acc = None
						cur_seq = 0
						cur_msec = 0
						cur_acc = None
						next_seq = 0
						nex_msec = 0
						next_acc = None
						timestamp = dt
						zof = zf.open(zfile, 'r')
						count = 0
						lines = zof.readlines()
						abnormal = False
						records = {}
						records_time = dt
						temp = []
						prev_timestamp = None
						for idx in range(len(lines)):
							line = lines[idx]
							count += 1
							cur_seq, cur_msec, cur_acc = self.parseline(line)
							if idx == 0:
								prev_seq = cur_seq
								prev_msec = cur_msec
								records[records_time] = 0.0
							if idx > 0:
								if not abnormal:
									prev_seq, prev_msec, prev_acc = self.parseline(lines[idx - 1])
								else:
									abnormal = False
								if idx + 1 < len(lines):
									next_seq, next_msec, next_acc = self.parseline(lines[idx + 1])
								# check if seq is jumpping
								if cur_seq != (prev_seq + 1) % 256:
									if cur_seq == 0 or cur_seq == 255:
								 		# abnormal record
										abnormal = True
										count -= 1
										continue
								if cur_seq - prev_seq < 0:
									tdelta = timedelta(microseconds=(cur_seq + 256 - prev_seq) * 1000)
								else:
									tdelta = timedelta(microseconds=(cur_seq - prev_seq) * 1000)
								timestamp += tdelta
								if prev_timestamp != None:
									if timestamp == prev_timestamp:
										tdelta = timedelta(microseconds=1)
										timestamp += tdelta
									prev_timestamp = timestamp
							else:
								pass
							# insert record into the database
#							temp.append(DataLog(cur_seq, cur_acc[0], cur_acc[1], cur_acc[2], timestamp))
#							self.db_insert(DataLog(cur_seq, cur_acc[0], cur_acc[1], cur_acc[2], timestamp))
#							if count % 1000 == 0:
#								self.db_commit(temp)
#								temp = []
							if timestamp - records_time >= timedelta(seconds = 1):
								self.plotters[db_name].pointUpdate(records_time, records[records_time])
								records_time = records_time + timedelta(seconds = 1)
								records[records_time] = 0.0
							else:
							 	if records[records_time] == 0.0:
							 		records[records_time] = cur_acc[2]
								records[records_time] = (records[records_time] + cur_acc[2]) / 2

						zof.close()
#						self.db_insert_all(temp)
#						self.db_commit(temp)
#						self.db_session_close()
						self.plotters[db_name].resume()
					os.remove(name)
					ptime_end = time.time()
					print "Parse %s Done: %f" % (name, (ptime_end - ptime_start))
		
	def parseline(self, line):
		rfields = line.split()
		seq = int(rfields[1][1:4])
		msec = int(rfields[2].split('.')[1])
		acc = (int(rfields[3]), int(rfields[4]), int(rfields[5]))
		return seq, msec, acc

class dataPlotter(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		self.event = threading.Event()
		self.records = [0.0] * (60 * 60 * 24)
		self.duration = 60
		self.lock = threading.Lock()
		self.name = name.split('_')[0] + '_' + name.split('_')[1]
		self.newest_idx = 0
		self.baseline = 0.0
		self.threshold = 500

	def pointUpdate(self, timestamp, data):
		with self.lock:
			idx = self.getIdx(timestamp)
			self.records[idx] = data
			self.newest_idx = idx
#			print "Update %s %5d %s " % (self.name, idx, timestamp), data

	def pause(self):
		self.event.clear()

	def resume(self):
		self.event.set()

	def run(self):
		while True:
			if self.event.is_set():
				start_time = time.time()
				self.task()
				end_time = time.time()
				self.pause()
				print "Plotter %s Task time: %f" % (self.name, (end_time - start_time))
			self.event.wait()

	def stop(self):
		self.event.set()

	def getIdx(self, timestamp):
		return timestamp.hour * 3600 + timestamp.minute * 60 + timestamp.second
	
	def getTimeFromIdx(self, idx):
		return [idx/3600, (idx/60)%60, idx%60]

	def task(self):
		if self.newest_idx == 0:			
			cur_time = datetime.now()
			idx = self.getIdx(cur_time)
		else:
			idx = self.newest_idx
		print "Plotter %s idx %d" % (self.name, idx)
		with self.lock:
			localcopy = self.records[:]
		durations = [1800]
		darray = {}

		for epoch in durations:
			darray[epoch] = {}
			darray[epoch]['data'] = []
			darray[epoch]['xticks'] = None
			xticks = []
			for j in range(6):
				tick = self.getTimeFromIdx(idx+1 - (epoch/5 * j))
				label = "%02d:%02d" % (tick[0], tick[1])
				xticks.insert(0, label)
			xticks.reverse()
			darray[epoch]['xticks'] = tuple(xticks)
			if idx >= epoch:
				darray[epoch]['data'] = localcopy[(idx - epoch):idx]
			else:
				darray[epoch]['data'] = localcopy[len(localcopy)-(epoch-idx):len(localcopy)] + localcopy[:idx]
			v = 0.0
			for i in range(epoch - 1, -1, -1):
				if darray[epoch]['data'][i] != 0.0:
					if v != 0 and abs(darray[epoch]['data'][i] - v) > 1500:
						darray[epoch]['data'][i] = v
					v = darray[epoch]['data'][i]
				else:
					darray[epoch]['data'][i] = v
			darray[epoch]['data'].reverse()
#		move_avg = sum(darray[300]['data'])/len(darray[300]['data'])
#		if self.baseline == 0.0:
#			self.baseline = move_avg
#		else:
#			self.baseline = (self.baseline + move_avg) / 2
#		for epoch in durations:
#			darray[epoch]['data'] = map(lambda x: (x - self.baseline) * 0.0875, darray[epoch]['data'])
		self.draw(darray, self.name)

	def draw(self, darray, fname):
		keys = sorted(darray.keys())
		output_ext = ".png"

		ioff()
#		h = len(keys) * 3.2
		h = 6.4
		fig = figure(figsize = (9.6, h), dpi = 72)
		count = 1
		for key in keys:
			ax = fig.add_subplot(len(keys), 1, count)
			ax.plot(darray[key]['data'], 'g')
#			ax.set_ylabel("Z-axis")
#			ax.set_ylim((int(self.baseline - self.threshold), int(self.baseline + self.threshold)))
#			ax.set_ylim((int(-self.threshold), int(self.threshold)))
			ax.set_yticklabels(())
			ax.xaxis.set_major_locator(LinearLocator(len(darray[key]['xticks'])))
			if darray[key]['xticks'] != None:
				ax.set_xticklabels(darray[key]['xticks'])
			for tick in ax.xaxis.get_major_ticks():
				tick.label.set_fontsize(8)
			for tick in ax.yaxis.get_major_ticks():
				tick.label.set_fontsize(8)
			count += 1

		out = fname + output_ext
		tmp = fname + ".tmp" + output_ext
		show()
		savefig(out)
		close()
#		os.rename(tmp, out)
		ion()

class dataConsumer(threading.Thread):
	def __init__(self, db_name):
		threading.Thread.__init__(self)
		self.event = threading.Event()
		self.db_name = db_name
		self.last_timestamp = None

		# task is starting in pause state
		self.pause()

	def run(self):
		while True:
			if self.event.is_set():
				self.task()
				self.pause()
			self.event.wait()

	def resume(self):
		print self.db_name + "\tTask resume!!"
		self.event.set()

	def pause(self):
		print self.db_name + "\tTask pause!!"
		self.event.clear()
	
	def task(self):
		print self.db_name + "\tTask fire!!"
		q_start = time.time()
		self.engine = create_engine('sqlite:///' + self.db_name + '.db')
		db = sqlsoup.SqlSoup(self.engine)
		dl = db.DataLog.order_by(desc(db.DataLog.id)).first()
		timestamp = dl.Timestamp
		if timestamp.second == 0:
			t_start = datetime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute - 1)
		else:
			t_start = datetime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute)
		t_end = t_start + timedelta(seconds=1)
#		print t_start, t_end
#		test = db.DataLog.filter(db.DataLog.Timestamp.between(t_start, t_end)).all()
#		temp = []
#		for t in test:
#			temp.append(t)
		self.Session = scoped_session(sessionmaker(bind=self.engine))
		for idx in range(60):
			session = self.Session()
			results = session.query(func.avg(DataLog.ACC_Z)).filter(DataLog.Timestamp.between(t_start, t_end))
			for ans in results:
				print "=", t_start, ans
			t_start = t_end
			t_end = t_start + timedelta(seconds=1)
			session.close()
		q_end = time.time()
		print "QUERY TIME %f" % (q_end - q_start)
		print self.db_name + "\tTask done!!"

	def plot(self):
		pass





if __name__ == "__main__":
	try:
		t = FTPServer()
		t.start()
	except KeyboardInterrupt:
		print "USER INTERRUPT"
		main_thread = threading.currentThread()
		for p in thread.ing.enumerate():
			if hassattr(p, "stop"):
				p.stop()
			p.join()

