import fetcher
import os.path
	
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
		result += base64.b64encode(self.content)+">\n"
		return result

	def deserializeSite(s):
		rawE = re.compile(ur'SITE<(/?[\w\.\/\?\=\-\&]*)>META<([A-Za-z0-9+-=\[\]]*)>CONTENT<([A-Za-z0-9+-=]*)>')
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
		if os.path.isfile("index/domaindb/"+name)==True:
			content = []
			with open("index/domaindb/"+name,"r") as f
				content = f.readlines()
			for line in content:
				self.sites.append(site.deserializeSite(line))
			
	def AddSite

class crawler:
	def __init__():
		self.fetcher = fetcher.fetcher()

