import fetcher
import index
import Queue
import re
import thread

metaRE = re.compile(ur'<\s*meta\s*name\s*=\s*"([\w\s]*)"\s*content\s*=\s*"([\w\s+#*.\'"@,-]*)')
styleRE = re.compile(ur'<\s*style[\w\s="\/\\:;()\[\]@.!-]*>.*<\s*/\s*style[\w\s="\/\\:;()\[\]@.!-]*>', re.DOTALL)
scriptRE = re.compile(ur'<\s*script[\w\s="\/\\:;()\[\]@.!-]*>.*<\s*/\s*script[\w\s="\/\\:;()\[\]@.!-]*>', re.DOTALL)
tagRE = re.compile(ur'<[\w\s="\/\\:;()\[\]@.!-]*>')
#linkRE = re.compile(ur'https?://([\w@.-]*):?(\d*)?([\w@\/#?&=:.-]*)')
linkRE = re.compile(ur'h?t?t?p?:?//([\w@.-]*):?(\d*)?([\w@\/#?&=:.-]*)')
localLinkTagRE = re.compile(ur'\s*href\s*=\s*"(/?[\w@?&=:.-]+[\w@?\/&=:.-]*)[\w@\/#?&=:.-]*"')
wordRE = re.compile(ur'(\w\w*)')

class crawler:
	def __init__(self, StayOnDomain=False, maxsites=None, maxthreads=10):
		self.fetcher = fetcher.fetcher(10)

		self.domains = dict()
		self.words = dict()
		
		self.domainOnly = StayOnDomain
		self.startdomain = ""
		self.maxsites = maxsites
		
		self.maxthreads = maxthreads
		self.curthreads = 0
		self.input = Queue.Queue()
		self.visited = []
		
		self.fetcher.AddHandler(self.ParsePage)
	
	def ParsePage(self, domainname, sitename, content):
		while self.curthreads >= self.maxthreads:
			pass
		thread.start_new_thread(self.ParsePageWorker, (domainname, sitename, content))
	
	def ParsePageWorker(self, domainname, sitename, content):
		self.curthreads += 1
		try:
			#get meta-tags
			meta = []
			mlist = metaRE.findall(content)
			for m in mlist:
				meta.append((m[0], m[1]))
			
			#check if page has updated
			if domainname not in self.domains:
				self.domains[domainname] = index.domain(domainname)	
			d = self.domains[domainname]
			
			ParseSite = False
			if d.HasSite(sitename):
				ParseSite = d.HasSiteChanged(sitename, meta, content)
			else: 
				ParseSite = True
				d.AddSite(sitename, meta, content)
				
			#DONT, ONLY TESTING
			d.Save()
			
			if ParseSite == True:
				#fetch the links from the page
				mlist = linkRE.findall(content)
				for m in mlist:
					#input all the links!
					port = 80
					if m[1] != "":
						port = int(m[1])
					self.Input(m[0], port, m[2])
				#local links, too, after removing normal links
				FewLinkContent = linkRE.sub("", content)
				mlist = localLinkTagRE.findall(FewLinkContent)
				for m in mlist:
					port = 80
					self.Input(domainname, port, m)
				#remove tags (tag blocks need seperate magic :/)
				textOnly = tagRE.sub("", scriptRE.sub("", styleRE.sub("", FewLinkContent)))
				
				#get words
				mlist = wordRE.findall(textOnly)
				for m in mlist:
					#create all the words!!
					if m not in self.words:
						self.words[m] = index.word(m)
					w = self.words[m]
					w.AddSite(domainname, sitename)
					#DONT
					w.Save()
			#done
				print("DONE:"+domainname+sitename)	
			else:
				print("DONE (no update):"+domainname+sitename)	
		except:
			print("Error parsing "+domainname+sitename)
		finally:
			self.curthreads -= 1
	
	def Input(self, domainname, port, sitename):
		#do nothing if we already visited that page and stuff
		if self.maxsites != None:
			self.maxsites-=1
			if self.maxsites<0:
				return
		
		if (domainname, sitename) in self.visited:
			return
		if self.startdomain == "":
			self.startdomain = domainname
		if self.domainOnly == True and self.startdomain != domainname:
			return
		
		self.visited.append((domainname, sitename))
		self.fetcher.Fetch((domainname, port, sitename))
		print(domainname+sitename)