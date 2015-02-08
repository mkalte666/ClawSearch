import crawler
import signal
import sys
c = crawler.crawler(False, 50000)
c.Input("www.sdamned.com", 80, "/")



def escapeHandler(signum, frame):
	try:
		print("AVERGE PARSE TIME:"+str(c.avtime)+"s")
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
