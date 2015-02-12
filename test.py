# -*- coding: utf-8 -*-
import crawler
import signal
import sys
import thread

c = crawler.crawler(False, 10000, 25)
c.Input("blog.fefe.de", 80, "/")
c.Input("de.wikipedia.org", 80, "/wiki/Programmierung")
c.Input("www.stackoverflow.com", 80, "/")
c.Input("Bbc.co.uk", 80, "/")
c.Input("www.sdamned.com", 80, "/")
#c.Input("www.heise.de", 80, "/newsticker/meldung/NSA-Skandal-Obama-bittet-Deutsche-um-Vertrauensbonus-2545215.html")

def escapeHandler(signum, frame):
	try:
		thread.exit()	
	except:
		print("AVERGE PARSE TIME:"+unicode(c.avtime)+"s")
		c.indexer.Save()
		exit()

signal.signal(signal.SIGINT, escapeHandler)

while True:
	pass
