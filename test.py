import crawler

c = crawler.crawler(True, 1000)
c.Input("blog.fefe.de", 80, "/")

while True:
	try:
		pass
	except KeyboardInterrupt:
		for d in c.domains:
			d.Save()
