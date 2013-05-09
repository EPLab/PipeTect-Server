import threading

class CondReading:
	reading = None
	write_lock = None
	read_lock = None
	MAX_LEN = 30000
	moving_avg = 0.0
	CIRCULAR = False
	cnt = 0

	def __init__(self, wlock, rlock, idatum, sps):
		self.write_lock = wlock
		self.read_lock = rlock
		self.MAX_LEN = sps * 30
		self.reading = [idatum] * self.MAX_LEN
	
	def __len__(self):
		return len(self.reading)
	
	def update_reading(self, datum):
		with self.write_lock:
			if not self.CIRCULAR and len(self.reading) >= self.MAX_LEN:
				self.CIRCULAR = True
			if self.CIRCULAR:
				self.reading.pop(0)
			self.reading.append(datum)
			if self.cnt < self.MAX_LEN:
				self.cnt = self.cnt + 1
	
	def get_reading(self, under = 0):
		t = []
		if under != 0:
			for idx in range(len(self.reading)):
				if idx % under == 0:
					t.append(self.reading[idx])
		else:
			t = self.reading[:]
		return t
