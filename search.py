import index
import re

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
	def __init__(self, q):
		#get all sites with the words
		self.words = []
		self.sites = dict()
		self.domains = dict()
		searchWords = q.split(" ")
		for w in searchWords:
			#do some word mutation, too. if the mutation is the same as the input it causes the word to be loaded double
			#this is ok since it causes a the right spelling to have the most right in the rating
			for mutated in _mutator(w):
				self.words.append(index.word(mutated))
			
		
		for word in self.words:
			for s in word.sites:
				if s not in self.sites:
					self.sites[s] = ratedSite(s)
				self.sites[s].Inc(word.sites[s])
				
		#search the meta data of each page
		for s in self.sites:
			m = splitRE.search(self.sites[s].name)
			dname = m.group(1)
			sname = m.group(3)
			d = index.domain(dname)
			
			ds = d.GetSite(sname)
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
			print(self.sites[key].title+": "+self.sites[key].name)