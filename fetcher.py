# -*- coding: utf-8 -*-
import socket
import Queue
import thread
import time
import re

class fetcher:
	def __init__(self, maxthreads):
		self.running = True
		self.maxthreads = maxthreads
		self.curthreads = 0
	
		self.toFetch = Queue.Queue();
		self.fetched = Queue.Queue();
		
		self.DataHandlers = []
		thread.start_new_thread(self.HandlerWorker, ())
		thread.start_new_thread(self.FetchManagerWorker, ())

		
	def AddHandler(self, handler):
		self.DataHandlers.append(handler)
	
	def RemoveHandler(self, handler):
		try:
			self.DataHandler.remove(handler)
		except:
			pass

	def HandlerWorker(self):
		while self.running == True:
			item = self.fetched.get()
			for handler in self.DataHandlers:
				handler(item[0], item[1], item[2])
	
	def FetchManagerWorker(self):
		while self.running == True:
			if self.curthreads < self.maxthreads:
				item = self.toFetch.get()
				thread.start_new_thread(self.FetchWorker, (item[0],item[1]))
	
	def FetchWorker(self, item, timeout = 3):
		self.curthreads += 1	
		try:
			s = socket.socket()
			s.connect((item[0], item[1]))
			s.send("GET "+item[2]+" HTTP/1.0\n")
			s.send("User-Agent: ClawSearchBot\n")
			s.send("Host: "+item[0]+"\n\n")
			s.send("Connection: Close")
			
			result = ""
			endtime = time.time()+timeout
			while time.time()<endtime:
				c = s.recv(1)
				result += c
				if c=='':
					break	
			lenRE = re.compile(ur'Content-Length:\s*(\d*)')
			m = lenRE.search(result)
			if m!= None:
				result = result[0-int(m.group(1)):]
			self.fetched.put((item[0],item[2], result))
		except:
			print("warning, fetching error!")
			pass
		finally:
			self.curthreads -= 1

	def Fetch(self, item, timeout=3):
		self.toFetch.put((item, timeout))	
