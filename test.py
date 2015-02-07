import crawler

c = crawler.crawler(True, 1000)
c.Input("de.wikipedia.org", 80, "/wiki/Programmierung")

while True:
	try:
		pass
	except KeyboardInterrupt:
		for d in c.domains:
			d.Save()
