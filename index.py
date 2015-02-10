# -*- coding: utf-8 -*-
import fetcher
import os.path
import base64
import re
import xxhash
import time
import struct

_hasher = xxhash.xxh64()
def conent_hash(str):
	_hasher.update(str)
	return _hasher.hexdigest()

wordSiteRE = re.compile(ur'([A-Za-z0-9+-=\[\]]*)<(\d*)>')
domainSiteRE = re.compile(ur'|([A-Za-z0-9+-=\[\]]*)|([A-Za-z0-9+-=\[\]]*)|([A-Za-z0-9+-=]*)|([A-Za-z0-9+-=]*)')
domainRE = re.compile(ur'|([A-Za-z0-9+-=\[\]]*)|([A-Za-z0-9+-=]*)')
wordRE = re.compile(ur'|([A-Za-z0-9+-=]*)')
metaRE = re.compile(ur'([A-Za-z0-9+-=]*)\[([A-Za-z0-9+-=]*)\]')

def decode(s):
	return (base64.b64decode(s))

def encode(s):
	return (base64.b64encode(s))

class site:
	def __init__(self, data, worddata):
		self.name = data[0]
		self.content = data[2]
		self.meta = data[1]
		self.words = worddata[0]
		self.wordCounts = worddata[1]
		
	def serialize(self):
		result = "|"+encode(self.name)
		result += "|"
		for m in self.meta:
			result += encode(m[0])+"["+encode(m[1])+"]"
		result += "|"
		result += encode(self.content)+"|"
		worddata = ""
		for i in range(0,len(self.words)):
			Qbytes = struct.pack('Q', bytes, self.words[i].id)
			Hbytes = struct.pack('H', bytes, self.wordCounts[i])
			worddata += "|"+encode(Qbytes[2:]+Hbytes)
		result+=encode(worddata)
		return result

def deserializeSites(indexerInstance,s):
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
		words = []
		wordCounts = []
		rawWords = wordRE.findall(decode(m[3]))
		for w in rawWords:
			bytes = decode(w[0])
			HBytes = bytes[6:]
			QBytes = '\x00\x00'+bytes[:6]
			wordId = struct.unpack('Q', QBytes)[0]
			wordCount = struct.unpack('H',HBytes)[0]
			words.append(indexerInstance.GetWord(wordId))
			wordCounts.append(wordCount)
		newsite = site((title, meta, content), (words, wordCounts))
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

		
	def GetSitesWithWordId(self, id):
		sites = [s for s in self.sites if any(w.id==id for w in s.sites)]
		
	def serialize(self):
		result = "|"
		result += encode(self.name)+"|"
		sites = ""
		for s in self.sites:
			sites+=s.serialize()
		result+=encode(sites)
		return result
		
def deserializeDomain(s):
	m = domainRE.match(s)
	if m==None:
		return None
	name = decode(m.group(1))
	sites = deserializeSites(decode(m.group(2)))
	newDomain = domain(name, sites)
	return newDomain


	
class word:
	def __init__(self, name, id):
		self.name = name
		self.id = id
	
	def serialize(self):
		result = encode(self.name)
		return result

def deserializeWord(s,id):	
	name = decode(s)
	newWord = word(name, id)
	return newWord
	
class indexer:
	def __init__(self):
		self.domains = dict()
		self.words = []
		self.numwords = 0
		
		print("loading word index...")
		if os.path.isfile("index/domaindb.db")==True:
			with open("index/worddb.db", "r") as f:
				wordsRaw = f.readlines()
				
				for raw in wordsRaw:
					newWord = deserializeWord(raw,self.numwords)
					if newWord != None:
						self.words.append(newWord)
						self.numwords+=1
				f.close()
			print("Done")
		else:
			print("Running for the first first time, wont load word index")
		
		print("loading domain index...")
		if os.path.isfile("index/domaindb.db") == True:
			with open("index/domaindb.db", "r") as f:
				domainsRaw = f.readlines()
				for raw in domainsRaw:
					newDomain = deserializeDomain(self, raw)
					if newDomain != None:
						self.domains[newDomain.name] = newDomain
				f.close()
			print("Done")
		else:
			print("Running for the first first time, wont load domain index")
		
	
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
		
	def GetWord(self, id):
		if id not in self.words:
			return None
		return self.words[id]
	
	def GetWordName(self, name):
		
	def GetDomain(self, name):
		if name not in self.domains:
			self.domains[name] = domain(name)
		return self.domains[name]
		
	def GetSitesForWord(self, wordname):
		result = []
		for w in self.words:
			if w.name==wordname:
				id = w.id
				sites = []
				