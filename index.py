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

def deserializeSite(s):
		rawE = re.compile(ur'SITE<([A-Za-z0-9+-=\[\]]*)>META<([A-Za-z0-9+-=\[\]]*)>CONTENT<([A-Za-z0-9+-=]*)>')
		m = rawE.match(s)
		if m == None:
			return None
		title = base64.b64decode(m.group(1))
		raw_meta = m.group(2)
		meta = []
		metaE = re.compile(ur'([A-Za-z0-9+-=]*)\[([A-Za-z0-9+-=]*)\]')
		metaPairs = metaE.findall(raw_meta)
		for metaPair in metaPairs:
			meta.append((base64.b64decode(metaPair[0]),base64.b64decode(metaPair[1])))
		content = base64.b64decode(m.group(3))
		newsite = site((title, meta, content))
		return newsite	

class domain:
	def __init__(self, name):
		self.sites = []
		self.name = name
		try:
			if os.path.isfile("index/domaindb/"+base64.urlsafe_b64encode(name))==True:
				content = []
				with open("index/domaindb/"+base64.urlsafe_b64encode(name),"r") as f:
					content = f.readlines()
				for line in content:
					newSite = deserializeSite(line)
					if newSite != None:
						self.sites.append(newSite)
				#file system takes some time... better wait for it
				time.sleep(0.02)
			else:
				f = open("index/domaindb/"+base64.urlsafe_b64encode(name),"w")
				f.close()
		except:
			print("Could not load domain"+self.name)
		
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
		
	def Save(self):
		try:
			with open("index/domaindb/"+base64.urlsafe_b64encode(self.name),"w") as f:
				for s in self.sites:
					f.write(s.serialize()+"\n")
				f.close()
			#file system takes some time... better wait for it
			#time.sleep(0.02)
		except:
			print("Could not save domain +"+self.name)
class word:
	def __init__(self, name):
		self.name = name
		self.sites = dict()
		try:
			if os.path.isfile("index/worddb/"+base64.urlsafe_b64encode(name))==True:
				content = []
				with open("index/worddb/"+base64.urlsafe_b64encode(name),"r") as f:
					content = f.readlines()
				for line in content:
					m = wordSiteRE.match(line)
					self.sites[base64.b64decode(m.group(1))] = int(m.group(2))
				#file system takes some time... better wait for it
				time.sleep(0.02)
			else:
				f = open("index/worddb/"+base64.urlsafe_b64encode(name),"w")
				f.close()
		except:
			print("Could not load Word "+self.name)
	def AddSite(self, domain, site):
		if (domain+site) not in self.sites:
			self.sites[domain+site] = 0
		self.sites[domain+site] += 1
	
	def Save(self):
		try:
			with open("index/worddb/"+base64.urlsafe_b64encode(self.name),"w") as f:
				#print("saved word "+self.name)
				for s in self.sites:
					f.write(base64.b64encode(s)+"<"+unicode(self.sites[s])+">\n")
				f.close()
			#file system takes some time... better wait for it
			#time.sleep(0.02)
		except:
			print("Could not save Word "+self.name)