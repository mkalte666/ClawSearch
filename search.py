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
	def __init__(self, name, title=""):
		self.name = name
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
		for w in searchWords:
			#do some word mutation, too. if the mutation is the same as the input it causes the word to be loaded double
			#this is ok since it causes a the right spelling to have the most right in the rating
			#for mutated in _mutator(w):
			#	self.words.append(index.word(mutated))
			self.words.append(self.indexer.GetWord(w))
			
		firstWord = self.words[0]
		for s in firstWord.sites:
			if s not in self.sites:
				self.sites[s] = ratedSite(s)
			self.sites[s].Inc(firstWord.sites[s])
			if len(self.sites)>=self.peaksites and self.maxsites:
				break
			
		for word in self.words[1:]:
			for s in self.sites:
				isSomewhere = False
				if s not in word.sites:
					del self.sites[s]
					break
				self.sites[s].Inc(word.sites[s])
		
		
		if len(self.sites) > self.maxsites and self.maxsites != 0:
			sortedKeys = sorted(self.sites, key=lambda rs: self.sites[rs].rating, reverse=True)[:self.maxsites]
			outdict = dict()
			for k in sortedKeys:
				outdict[k] = self.sites[k]
			self.sites = outdict
		#search the meta data of each page
		for s in self.sites:
			m = splitRE.search(self.sites[s].name)
			dname = m.group(1)
			sname = m.group(3)
			d = self.indexer.GetDomain(dname)
			
			ds = d.GetSite(sname)
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
				title = cgi.escape(self.sites[key].name)
			if len(title) > 100:
				title = title[:93]+"..."
			res = "<a href=\"http://"+cgi.escape(self.sites[key].name)+"\" target=\"_blank\">"+title+"</a> Rating: "+str(self.sites[key].rating)+"<br>"
			#print(self.sites[key].title)
			self.results.append(res)
		
	def Write(self):
		f=""
		for r in self.results:
			f+=r+"\n"
		return f