# -*- coding: utf-8 -*-
import crawler
import signal
import sys
c = crawler.crawler(True, 1000)
c.Input("de.wikipedia.org", 80, "/wiki/Programmierung")



def escapeHandler(signum, frame):
	try:
		print("AVERGE PARSE TIME:"+unicode(c.avtime)+"s")
		for d in c.domains:
			try:
				c.domains[d].Save()
			except:
				pass
		for w in c.words:
			try:
				c.words[w].Save()
			except:
				pass
		exit()
	except:
		exit()

signal.signal(signal.SIGINT, escapeHandler)

while True:
	pass
