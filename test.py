# -*- coding: utf-8 -*-
import crawler
import signal
import sys
c = crawler.crawler(False, 200000, 25)
c.Input("blog.fefe.de", 80, "/")
c.Input("de.wikipedia.org", 80, "/wiki/Programmierung")
c.Input("stackoverflow.com", 80, "/")
c.Input("Bbc.co.uk", 80, "/")
c.Input("www.sdamned.com", 80, "/")

def escapeHandler(signum, frame):
	try:
		print("AVERGE PARSE TIME:"+unicode(c.avtime)+"s")
		c.indexer.Save()
		exit()
	except:
		exit()

signal.signal(signal.SIGINT, escapeHandler)

while True:
	pass
