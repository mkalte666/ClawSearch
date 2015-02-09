# -*- coding: utf-8 -*-
import fetcher
import index
import Queue
import re
import thread
import time

metaRE = re.compile(ur'<\s*meta\s*name\s*=\s*"([\w\s]*)"\s*content\s*=\s*"([\w\s+#*.\'"@,-]*)')
styleRE = re.compile(ur'<\s*style[\w\s="\/\\:;()\[\]@.!-]*>.*<\s*/\s*style[\w\s="\/\\:;()\[\]@.!-]*>', re.DOTALL)
scriptRE = re.compile(ur'<\s*script[\w\s="\/\\:;()\[\]@.!-]*>.*<\s*/\s*script[\w\s="\/\\:;()\[\]@.!-]*>', re.DOTALL)
tagRE = re.compile(ur'(<[\w\s="\/\\:;()\[\]@.!-]*>)')
#linkRE = re.compile(ur'https?://([\w@.-]*):?(\d*)?([\w@\/#?&=:.-]*)')
linkRE = re.compile(ur'h?t?t?p?:?//([\w@.-]*):?(\d*)?([\w@\/\#?&=:.-]*)')
localLinkTagRE = re.compile(ur'\s*href\s*=\s*"(/?[\w@?&=:.-]+[\w@?\/&=:.-]*)[\w@\/\#?&=:.-]*"')
wordRE = re.compile(ur'(\w+)')
titleRE = re.compile(ur'<\s*title\s*>\s*(.*)\s*<\s*\/\s*title\s*>')
NotAWord = ["", "\n", "\t"]

class crawler:
	def __init__(self, StayOnDomain=False, maxsites=None, maxWorkThreads=10, fetchToWorkRatio = 0.25):
		self.fetcher = fetcher.fetcher(int(fetchToWorkRatio*maxWorkThreads))
		self.indexer = index.indexer()
		
		self.domains = dict()
		self.words = dict()
		
		self.domainOnly = StayOnDomain
		self.startdomain = ""
		self.maxsites = maxsites
		
		self.maxthreads = maxWorkThreads
		self.curthreads = 0
		self.input = Queue.Queue()
		self.visited = []
		
		self.avtime = 0
		
		self.fetcher.AddHandler(self.ParsePage)
	
	def ParsePage(self, domainname, sitename, content):
		while self.curthreads >= self.maxthreads:
			pass
		thread.start_new_thread(self.ParsePageWorker, (domainname, sitename, content))
	
	def ParsePageWorker(self, domainname, sitename, content):
		self.curthreads += 1
		starttime = time.time()
		try:
			#get meta-tags
			meta = []
			mlist = metaRE.findall(content)
			for m in mlist:
				meta.append((m[0], m[1]))
			#title is stored in the meta, too
			title = ""
			m = titleRE.search(content)
			if m != None:
				title = m.group(1)
			meta.append(("title", title))
			#check if page has updated
			if domainname not in self.domains:
				self.domains[domainname] = self.indexer.GetDomain(domainname)	
			d = self.domains[domainname]
			
			ParseSite = False
			if d.HasSite(sitename):
				ParseSite = d.HasSiteChanged(sitename, meta, content)
			else: 
				ParseSite = True
				d.AddSite(sitename, meta, content)
				
			#DONT, ONLY TESTING
			#d.Save()
			
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
				#regex way, seems to be slower
				mlist = wordRE.findall(textOnly)
				#internal way, currently used for speed testing, seems to be slower
				#mlist = [e for e in textOnly.split(" ") if e not in NotAWord]
				for m in mlist:
					#create all the words!!
					if m not in self.words:
						self.words[m] = self.indexer.GetWord(m)
					w = self.words[m]
					w.AddSite(domainname, sitename)
					#DONT
					#w.Save()
			#done
			print("DONE:"+domainname+sitename+" In "+unicode(time.time()-starttime)+"s")	
			if self.avtime != 0:
				self.avtime += time.time()-starttime
				self.avtime *= 0.5
			else:
				self.avtime = time.time()-starttime
			print("AV being "+unicode(self.avtime))
		except:
			print("Error parsing "+domainname+sitename)
		finally:
			self.curthreads -= 1
	
	def Input(self, domainname, port, sitename):
		if (domainname, sitename) in self.visited:
			return
		if self.startdomain == "":
			self.startdomain = domainname
		if self.domainOnly == True and self.startdomain != domainname:
			return
			
		#do nothing if we already visited that page and stuff
		if self.maxsites != None:
			self.maxsites-=1
			if self.maxsites<0:
				return

		self.visited.append((domainname, sitename))
		self.fetcher.Fetch((domainname, port, sitename))
		print(domainname+sitename)
