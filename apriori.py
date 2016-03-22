from collections import OrderedDict
from itertools import combinations
from itertools import chain

import timeit

support=0
confidence=0

def getInitialData(f):
	lines=f.readlines()
	categories=lines[0].split()	#get categories
	categories=OrderedDict.fromkeys(categories, 0) #initialize categories dict with start num 0
	data=lines[1:] #get all data,except fist line
	for i in data:
		data[data.index(i)]=i.split() 
	#data is now a list of lists. each list is 1 row
	
	for line in data: #check each line
		for index,value in enumerate(line): #get value and index of each element in the list
			if value=="1":
				categories[categories.keys()[index]]+=1
	return categories,data

def getPairFreq(pairs,data):
	pair_set=[]
	for pair in pairs: #for each pair set
		for line in data: #and every line in the data
			check=0 #this goes up, everytime we find 1 in the examined index
			for x in pair: #x is the index
				if line[int(x)]=="1": #if the element is 1
					check+=1
			if check == len(pair): #if the pair consists of n elements, check needs to be n to approve the pair 
				pair_set.append(pair)
	return pair_set
			
def prunePairs(pairs,rows):
	#build list of unique pairs
	uniques=[]#this one for checking
	r_uniques=[]#this one for returning to previous function
	for i in pairs:
		if i in uniques:
			continue
		uniques.append(i)
	#check support of each unique pair
	for i in uniques:
		check=0
		for x in pairs:
			if i==x:
				check+=1
		pair_support=float((check*100)/rows) #turn pair support into percentage
		if pair_support<support:
			continue #this means we dont append the pair
		r_uniques.append(i)
		
	return r_uniques	
	
def generateItemset(itemArray,depth,data):
	x=list(combinations(itemArray,depth)) #make combinations with the data
	pairs=getPairFreq([list(elem) for elem in x],data)
	pairs=prunePairs(pairs,len(data)) 
	return list(set((chain.from_iterable(pairs)))),pairs #return a list of unique elements left in order to build the next itemset 
	
def getItemArray(categories,data): #Get the pairs and the unique items that survived. Do wee need to return the unique items?
	itemArray=[]
	for i in range(0,len(categories)):
		itemArray.append(i)
	temp=itemArray
	temp1=[]
	i=1
	while True:
		temp,temp1=generateItemset(temp,i,data)
		if len(temp)==0:
			break
		itemArray=temp
		pairs=temp1
		i+=1
	return itemArray,pairs	
	
def genAssocRules(data):
	#build temp more clever in order to be more dynamic
	first_part=[] #rules are separated by 2 parts. 1st and 2nd
	second_part=[]
	for pair in data:
		all_temp=[]
		for x in reversed(range(1,len(pair))):
			all_temp.append(list(combinations(pair,x)))# here we have the parts. take each part, subtract from data.
		for x in all_temp:
			for i in x:
				temp=list(i)
				#print temp,list(set(pair)-set(temp)) #print temp, items in pair that dont exist in temp
				first_part.append(temp)
				second_part.append(list(set(pair)-set(temp)))
	return first_part,second_part #return the rules in 2 parts, easier to implement check on the file

def getIndices(list, item):
     return [index for index in xrange(len(list)) if list[index] == item] #what kind of sorcery is this?
		#return indices that contain duplicates.
		#convinient if you want to optimize rule checking

def checkRules(data,first,second,categories):
	temp=[]
	for part in first:
		if part in temp:
			continue
		temp.append(part)
		temp_data=[]
		line_count=0
		for line in data:
			check1=0
			for i in part:
				if line[int(i)]=="1": #if the element is 1
					check1+=1
			if check1 == len(part): #if the part consists of n elements, check needs to be n to approve the part in the line 
				temp_data.append(line) #temp data has all lines containing a part.
		indices2=getIndices(first,part)
		for index in indices2:
			part2=second[index]
			check2=0
			for line in temp_data:
				for item2 in part2:
					if line[int(item2)]=="1":
						check2+=1
					if check2 == len(item2):
						line_count+=1
			ruleConfidence=float((check2*100)/len(temp_data))
			if(ruleConfidence<confidence): #if ruleConfidence < setpoint dont print the parts
				continue
			for i in part:
				print categories.keys()[int(i)],
			print "->",
			for i in part2:
				print categories.keys()[int(i)],
			print ""	

def getParameters(): #read confidence & support from keyboard
	global support
	global confidence
	while True:
		support=input("[*] Support? ")
		confidence=input("[*] Confidence? ")
		if support<101 and support>0 and confidence<101 and confidence>0:
			return
		print "[*] Wrong values for support or confidence, must be between 100 and 1"
	
def main():
	getParameters()
	start_time = timeit.default_timer()
	f=open("aprioriDb","r")
	#f=open("apriori.txt","r")
	print "[*] Parsing file",f.name
	categories,data=getInitialData(f)#get categories+data,find category frequency
	print "[*] Found",len(categories),"categories"
	print "[*]",len(data),"total transactions"
	itemArray,pairs=getItemArray(categories,data)
	print "[*] Pairs are",pairs #returns itemsets in a list of lists [[0, 2], [0, 3], [2, 3]]
	#now build possible rules
	first,second=genAssocRules(pairs)
	first=[[str(j) for j in i] for i in first] #convert lists of int into strings
	second=[[str(j) for j in i] for i in second]		
	checkRules(data,first,second,categories)	
	print timeit.default_timer() - start_time, "seconds" #12-13 secs for 10.000 rows. improved down to 5 secs woohoo
	#it's over, it's finally done.
	return 0

if __name__ == '__main__':
	main()

