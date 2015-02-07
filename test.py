import crawler

c = crawler.crawler(True, 100)
c.Input("de.wikipedia.org", 80, "/wiki/Base64")

while True:
	try:
		pass
	except KeyboardInterrupt:
		for d in c.domains:
			d.Save()
