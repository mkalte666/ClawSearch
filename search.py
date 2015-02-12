# -*- coding: utf-8 -*-
import index
import re
import sys
import cgi
reload(sys)
sys.setdefaultencoding("utf-8")

splitRE = re.compile(ur'([\w@.-]*):?(\d*)?([\w@\/#?&=:.-]*)')

def _mutator(str):
	out = [str,]
	out.append(str.upper())
	out.append(str.lower())
	for i in range(0,len(str)):
		w = str
		h = str
		w = w[:i]+w[i].upper()+w[:i+1]
		h = h[:i]+h[i].upper()+h[:i+1]
		out.append(w)
		out.append(h)
	return out

class ratedSite:
	def __init__(self, site, domain, title=""):
		self.site = site
		self.domain = domain
		self.rating = 0
		self.title = title
		
	def Inc(self, n=1):
		self.rating+=n
class search:
	def __init__(self, indexer, q, maxsites=0, maxPeakFactor=0):
		#get all sites with the words
		self.indexer = indexer
		self.words = []
		self.sites = dict()
		self.domains = dict()
		self.maxsites = maxsites
		self.peaksites = int(maxsites*maxPeakFactor)
		searchWords = q.split(" ")
		self.results = []
		
		firstWord = searchWords[0]
		wordSites = self.indexer.GetSitesForWord(firstWord)
		for d in wordSites:
			for s in d[1]:
				self.sites[d[0].name+s.name] = ratedSite(s, d[0])
		
		if len(self.sites) > self.maxsites and self.maxsites != 0:
			sortedKeys = sorted(self.sites, key=lambda rs: self.sites[rs].rating, reverse=True)[:self.maxsites]
			outdict = dict()
			for k in sortedKeys:
				outdict[k] = self.sites[k]
			self.sites = outdict
		#search the meta data of each page
		for s in self.sites:
			ds = self.sites[s].site
			if ds == None:
				continue
			meta = ds.meta
			for k,v in meta:
				if k=="title":
					self.sites[s].title = v
					for w in searchWords:
						if v.find(w)!=-1:
							self.sites[s].Inc(8)
				for w in searchWords:
					for mutated in _mutator(w):
						if v.find(mutated)!=-1:
							self.sites[s].Inc(5)	
					
		
		
		sortedList = sorted(self.sites, key=lambda rs: self.sites[rs].rating, reverse=True)
		
		for key in sortedList:
			title = cgi.escape(self.sites[key].title)
			if title == "":
				title = cgi.escape(self.sites[key].domain.name+self.sites[key].site.name)
			if len(title) > 100:
				title = title[:93]+"..."
			res = "<a href=\"http://"+cgi.escape(self.sites[key].domain.name+self.sites[key].site.name)+"\" target=\"_blank\">"+title+"</a> Rating: "+str(self.sites[key].rating)+"<br>"
			#print(self.sites[key].title)
			self.results.append(res)
		
	def Write(self):
		f=""
		for r in self.results:
			f+=r+"\n"
		return f