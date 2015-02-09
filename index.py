# -*- coding: utf-8 -*-
import fetcher
import os.path
import base64
import re
import xxhash
import time

_hasher = xxhash.xxh64()
def conent_hash(str):
	_hasher.update(str)
	return _hasher.hexdigest()

wordSiteRE = re.compile(ur'([A-Za-z0-9+-=\[\]]*)<(\d*)>')
domainSiteRE = re.compile(ur'SITE<([A-Za-z0-9+-=\[\]]*)>META<([A-Za-z0-9+-=\[\]]*)>CONTENT<([A-Za-z0-9+-=]*)>')
domainRE = re.compile(ur'DOMAIN<([A-Za-z0-9+-=\[\]]*)>SITES<([A-Za-z0-9+-=]*)>')
wordRE = re.compile(ur'WORD<([A-Za-z0-9+-=\[\]]*)>SITES<([A-Za-z0-9+-=]*)>')
metaRE = re.compile(ur'([A-Za-z0-9+-=]*)\[([A-Za-z0-9+-=]*)\]')

def decode(s):
	return (base64.b64decode(s))

class site:
	def __init__(self, data):
		self.name = data[0]
		self.content = data[2]
		self.meta = data[1]
    
	def serialize(self):
		result = "SITE<"+base64.b64encode(self.name)+">"
		result += "META<"
		for m in self.meta:
			result += base64.b64encode(m[0])+"["+base64.b64encode(m[1])+"]"
		result += ">CONTENT<"
		result += base64.b64encode(self.content)+">"
		return result

def deserializeSites(s):
	siteList = []
	mList = domainSiteRE.findall(s)
	for m in mList:	
		title = decode(m[0])
		raw_meta = m[1]
		meta = []
		metaPairs = metaRE.findall(raw_meta)
		for metaPair in metaPairs:
			meta.append((decode(metaPair[0]),decode(metaPair[1])))
		content = decode(m[2])
		newsite = site((title, meta, content))
		siteList.append(newsite)
	return siteList

class domain:
	def __init__(self, name, sites=[]):
		self.sites = sites
		self.name = name
		
		
	def AddSite(self,name, meta, content):
		newSite = site((name, meta, conent_hash(content)))
		if newSite != None:
			self.sites.append(newSite)
	
	def HasSite(self, name):
		return any(s.name == name for s in self.sites)
	
	def GetSite(self, name):
		for s in self.sites:
			if s.name == name:
				return s
		return None
	
	def HasSiteChanged(self, name, meta, content):
		hashContent = conent_hash(content)
		for s in[sl for sl in self.sites if sl.name==name]:
			if meta != s.meta or hashContent != s.content:
				s.meta = meta
				s.content = hashContent
				return True
		return False

	def serialize(self):
		result = "DOMAIN<"
		result += base64.b64encode(self.name)+">SITES<"
		sites = ""
		for s in self.sites:
			sites+=s.serialize()
		result+=base64.b64encode(sites)+">"
		return result
		
def deserializeDomain(s):
	m = domainRE.match(s)
	if m==None:
		return None
	name = decode(m.group(1))
	sites = deserializeSites(decode(m.group(2)))
	newDomain = domain(name, sites)
	return newDomain

def deserializeWord(s):	
	m = wordRE.match(s)
	if m == None:
		return None
	name = decode(m.group(1))
	sites = dict()
	siteMatches = wordSiteRE.findall(decode(m.group(2)))
	for site in siteMatches:
		sites[decode(site[0])] = int(site[1])
	newWord = word(name, sites)
	return newWord
	
class word:
	def __init__(self, name, sites=dict()):
		self.name = name
		self.sites = sites
		
	def AddSite(self, domain, site):
		if (domain+site) not in self.sites:
			self.sites[domain+site] = 0
		self.sites[domain+site] += 1
	
	def serialize(self):
		result = "WORD<"+base64.b64encode(self.name)+">SITES<"
		sites = ""
		for s in self.sites:
			sites+=base64.b64encode(s)+"<"+str(self.sites[s])+">"
		result+=base64.b64encode(sites)+">"
		return result
		
class indexer:
	def __init__(self):
		self.domains = dict()
		self.words = dict()
		
		print("loading domain index...")
		if os.path.isfile("index/domaindb.db") == True:
			with open("index/domaindb.db", "r") as f:
				domainsRaw = f.readlines()
				for raw in domainsRaw:
					newDomain = deserializeDomain(raw)
					if newDomain != None:
						self.domains[newDomain.name] = newDomain
				f.close()
			print("Done")
		else:
			print("Running for the first first time, wont load domain index")
		print("loading word index...")
		if os.path.isfile("index/domaindb.db")==True:
			with open("index/worddb.db", "r") as f:
				wordsRaw = f.readlines()
				for raw in wordsRaw:
					newWord = deserializeWord(raw)
					if newWord != None:
						self.words[newWord.name] = newWord
				f.close()
			print("Done")
		else:
			print("Running for the first first time, wont load word index")
	def Save(self):
		print("saving domain index...")
		with open("index/domaindb.db", "w") as f:
			for d in self.domains:
				f.write(self.domains[d].serialize()+"\n")
			f.close()
		print("done!")
		print("saving word index...")
		with open("index/worddb.db", "w") as f:
			for w in self.words:
				f.write(self.words[w].serialize()+"\n")
			f.close()
		print("done!")
		
	def GetWord(self, name):
		if name not in self.words:
			self.words[name] = word(name)
		return self.words[name]
		
	def GetDomain(self, name):
		if name not in self.domains:
			self.domains[name] = domain(name)
		return self.domains[name]