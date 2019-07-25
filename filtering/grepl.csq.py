import re 
import sys
sys.path.append('/mpba0/vcolonna/silvia/prioritiz/greplib.py')
import greplib as gp
import argparse
import gzip


########################################################
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-f", help="path to  input  file ",type=str,required=True)
	parser.add_argument("-i", help="threshold per SOTerm Impact  ", type=int,required=True)                                                                                        
	parser.add_argument("-v", help="path to table of vep consequences  ",type=str, required= True)                                                                                 
	#parser.add_argument("-o", help="pathto output file",type=str,required=True)
	args = parser.parse_args()
	#output = open(args.o,'w')
	#print(args) 


	##  READ VEP consequences rank ########
	dRank={"HIGH":4, "LOW": 2, "MODERATE":3, "MODIFIER":1}
	dSOTermRank={}
	lSOTerm=[]

	countlinesCsq= True
	for csqLine in open(args.v, 'r'):
		if countlinesCsq:
			csqTitle=csqLine.rstrip().split('\t')
			countlinesCsq=False
		else:
			myRowList=csqLine.rstrip().split('\t')
			dCsq= dict(zip(csqTitle, myRowList ))
			dSOTermRank[dCsq['SO term']]=dRank[dCsq['IMPACT']]
			lSOTerm.append(myRowList[0])

	#print (lSOTerm)
	lScores=list(reversed(range(len(lSOTerm)))) 
	#print (lScores) 
	dSOTermFineRank=dict(zip(lSOTerm, lScores))
	#print (dSOTermFineRank)






############################################################
	dInfo={}
	header=["chr", "pos", "csqAllel", "csqAlleleCount", "GTLiklihood" , "ENSTID", "ImpactScore", "FineImpactScore", "rare","Embryo","GnomAD","CellCycle","DDD"]
	print("\t".join(map(str, header) )  ) 

	#gzip.open(args.f, 'r')	
	for line in open(args.f, 'r'):
		if not re.match('#', line): 
			#print("this is a new line ") ## line split by  tab 
			linesplit=line.rstrip().split()
		
			## basic info 
			mychr=linesplit[0]; mypos=linesplit[1]; myref=linesplit[3]; myalt=linesplit[4] 

			## split INFO field
			tempinfo=linesplit[7] 
			for i in tempinfo.split(";"):  
				temp=i.split("=") 
				dInfo[temp[0]]=temp[1]
			
			#for i in dInfo["AC"]:
				#splAC=dInfo["AC"].split(",")
				

			## split FORMAT field
			tempformattitle=linesplit[8].split(":")
			tempformatcontent=linesplit[9].split(":")
			dFormat=dict(zip(tempformattitle, tempformatcontent))

			## work on dInfo[CSQ]
			## split for multiple consequences separated by ","
			multipleCsq=dInfo["CSQ"].split(",") 

			for mcsq in multipleCsq:  ### single consequence  
				myres=[]
				myres+=[mychr, mypos]
				dCsq=dict(zip(csqHeader, mcsq.split("|") ))  #############    ALL VEP INFO 
			
				#~~~~~~~~~
				mycsqAllele=dCsq["Allele"] ## identify the allele with consequences 
				#print(dInfo["AC"])
				#~~~~~~~~~~~
				myres+= gp.csqAlleleFeatures(mycsqAllele, myalt, int(dInfo["AC"]), (dFormat["GL"]) ) ## features of csqAll
		
				#~~~~~~~~~~~~~
				myres.append(dCsq['Feature'])
				
				#~~~~~~~~~~~~~~~~
				
				myind=[]
				for tl in dCsq['Consequence'].split("&"): 
					myind.append(lSOTerm.index(tl ))	
				mostSevereCsq=lSOTerm[min(myind)]
				#print(dCsq['Consequence']) 
				#print(mostSevereCsq)
				myres.append( dSOTermRank[mostSevereCsq ]) ## score based on the impact of the consequence       	
				myres.append( dSOTermFineRank[mostSevereCsq ])

				#~~~~~~~~~~~~~~~~~~~~~
			
				thresh=0.01
				freqlist = [float(x) for x in  [dCsq["AFR_AF"],dCsq["AMR_AF"],dCsq["EAS_AF"],dCsq["EUR_AF"],dCsq["SAS_AF"]] if x ] 
				rare = gp.checkFreq (freqlist, thresh) # check if it is a rare variant (af<thresh) 
				myres.append(rare)
								
				#~~~~~~~~~~~~~~~~~~~~~~~~~~
			
				# check if row have Embryo,CellCycle,DDD,GmomAD genes
				embryo=False ; DDD=False; cellcycle=False; gnomAD=False

				if re.search("annotation", line): embryo=True
				myres.append(embryo)
				if re.search("ANN3", line): gnomAD=True
				myres.append(gnomAD)
				if re.search("ANN2", line): cellcyle=True
				myres.append(cellcycle)
				if re.search("ANN1", line): DDD=True
				myres.append(DDD)

			#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	

				 			
				if dSOTermFineRank[mostSevereCsq ] > args.i and rare==True and cellcycle==True  and embryo==True: 	
					print ( "\t".join( map(str, myres) )  )

		else: 
			if re.search("ID=CSQ" ,line ): 
				csqHeader=line.rstrip().split(":")[1].lstrip().rstrip("\">").split("|")		
				#print (csqHeader)	



 


if __name__ == "__main__":
	main() 