import socket

s = socket.socket()

s.connect(("bee-more-random.tk", 80))

s.send("GET / HTTP/1.1\n")
s.send("Host: bee-more-random.tk\n\n")

b = "" 
while True:
	c = s.recv(1)
	if c == '\n':
		print b
		b = ""
	elif c == '':
		print b
		break
	else:
		b+=c	
