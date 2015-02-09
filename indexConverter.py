import os
import base64

print("Reading in filenames of the domainDb...")
domainFileNames = next(os.walk("index/domaindb"))[2]
print("Done\n Reding in filenams of the worddb...")
wordFileNames = next(os.walk("index/worddb"))[2]
print("Done\n Converting Domain data...")

domainData = []
wordData = []

#domain data blob
percentage = 0.0
maxNum = len(domainFileNames)
cur = 0.0
for name in domainFileNames:
	with open("index/domaindb/"+name, "r") as f:
		noLinesContent = ""
		content = f.readlines()
		for line in content:
			noLinesContent+=line
		domainData.append("DOMAIN<"+base64.b64encode(base64.urlsafe_b64decode(name))+">SITES<"+base64.b64encode(noLinesContent)+">")
		f.close()
	cur+=1
	p = cur/maxNum
	if p-percentage >=.05:
		print(str(int(p*100))+"%")
		percentage = p


print("Done\n Writing Domain data...")
percentage = 0.0
cur = 0.0
with open("index/domaindb.db", "w") as f:
	for line in domainData:
		f.write(line+"\n")
		cur+=1
		p = cur/maxNum
		if p-percentage >=.05:
			print(str(int(p*100))+"%")
			percentage = p
	f.close()
	
	
print("Done\n Converting Word data...")
#word data blob
percentage = 0.0
maxNum = len(wordFileNames)
cur = 0.0
for name in wordFileNames:
	with open("index/worddb/"+name, "r") as f:
		noLinesContent = ""
		content = f.readlines()
		for line in content:
			noLinesContent+=line
		wordData.append("WORD<"+base64.b64encode(base64.urlsafe_b64decode(name))+">SITES<"+base64.b64encode(noLinesContent)+">")
		f.close()
	cur+=1
	p = cur/maxNum
	if p-percentage >=.05:
		print(str(int(p*100))+"%")
		percentage = p


print("Done\n Writing Word data...")
percentage = 0.0
cur = 0.0
with open("index/worddb.db", "w") as f:
	for line in wordData:
		f.write(line+"\n")
		cur+=1
		p = cur/maxNum
		if p-percentage >=.05:
			print(str(int(p*100))+"%")
			percentage = p
	f.close()