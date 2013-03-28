#!/usr/bin/python

# This is a CSV validator ( UTF-8 check and column count ) .
# This script is meant to be run on a crontab and watches a directory for new csv's. 
# It wil process the csv and log and email results
# then sort it into an accepted or rejected folder. 

import os, sys, codecs, csv,  smtplib, datetime

#Optionaly send emails when a CSV is processed 
def sendMail(sendMes):
	fromaddr = ''
	toaddrs = ''
	replyaddrs = ""
	msg = sendMes
	username = '' # Gmail
	password = '' # Gmail
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.ehlo()
	server.starttls()
	server.ehlo()
	server.login(username,password)
	server.sendmail(fromaddr, toaddrs, msg)
	server.quit()

#Optionaly write to a log file
def writeLog(logData):
	log = open('log','a')
	log.write(logData)
	log.close

path = os.getcwd() # get current directory 
dirs = os.listdir( path ) # list all files in the current directory 
for dir in dirs: # look for any folders ( this is where the csv's should be )
	if os.path.isdir(dir) == True: 
		cPath = dir 
		cDirs = os.listdir( cPath ) # list files in the directory
		if not os.path.exists(cPath +"/accepted"): #create file tree
			os.makedirs(cPath +"/accepted") 
		if not os.path.exists(cPath +"/rejected"): #create file tree
			os.makedirs(cPath +"/rejected")
		if not os.path.exists(cPath +"/processing"): #create file tree
			os.makedirs(cPath +"/processing")
		for file in cDirs:
			if file.endswith(".csv"): # if it finds a csv process it 
				now = datetime.datetime.now() # gets the date for loging 
				writeLog("\n\n\n***********************************************************************\n")
				writeLog(str(now) + "\n")
				writeLog("[+] Found a CSV named " + str(file) + "\n")
				writeLog("[+] Moving CSV to processing folder" + "\n")
				file_dst = str(path) + "/" + str(cPath) + "/processing/" + str(file) 
				print file_dst
				os.rename(str(cPath) + "/" + str(file), file_dst) # move csv to processing 
				try:
					writeLog("[+] Checking for UTF-8\n")
					f = codecs.open(file_dst, encoding='utf-8', errors='strict') # open the csv with strict checking for UTF-8
					for line in f:
						pass
				except UnicodeDecodeError: # if there is non UTF-8 stuff
					writeLog("[-] Failed UTF-8 Validation\n")
					writeLog(str(line) + "\n")
					writeLog("[-] Moved to rejected folder\n")
					rejected_path = str(cPath) + "/rejected/" + str(file) + ".utf-8"
					os.rename(file_dst, rejected_path) # move to rejected folder
					writeLog("***********************************************************************\n")
					sendMail("subject:[CSV_VALIDATOR] - " + str(file) +  "\n\n[-] Failed UTF-8 validation\n[-] On Line: " + str(line) + " \n")
					f.close()
					sys.exit()

				lineNumber = 1 # keep track of row in csv
				writeLog("[+] Passed UTF-8 Validation \n")
				writeLog("[+] Starting column Validation \n")
				baseline = 0 # count of columns in first row
				csvInput = csv.reader(open(file_dst, 'rU'), delimiter=',',lineterminator='\n') # open the csv 
				for row in csvInput:
					if row:
						if lineNumber == 1:
							baseline = len(row) # get the column count of the first row
						else:
							lineCheck = len(row)
							if lineCheck != baseline: # check each row's column count against the first row's count 
								writeLog("[-] Failed column validation\n")
								writeLog("[-] Column count is " + str(baseline) + "\n")
								writeLog("[-] Line " + str(lineNumber) + " has " + str(lineCheck) + " columns\n")
								writeLog("[-] " + str(lineNumber) + " : " + str(row) + "\n")
								writeLog("[-] Moved to rejected folder\n")
								writeLog("***********************************************************************\n")
								rejected_path = str(cPath) + "/rejected/" + str(file) + ".count"
								os.rename(file_dst, rejected_path) # move to rejected folder
								sendMail("subject:[CSV_VALIDATOR] - " + str(file) +  "\n\n[-] Failed column validation\n[-] Column count is " + str(baseline) + "\n[-] Line: " + str(lineNumber) + " has " + str(lineCheck) + " columns \n\t: " + str(row) + "\n")
								sys.exit()
					lineNumber +=1 
					lineCheck = 0 
				writeLog("[+] Moving to the accepted folder\n")
				accepted_path = str(cPath) + "/accepted/" + str(file)
				os.rename(file_dst, accepted_path) # move to accepted
				writeLog("***********************************************************************\n")
				sendMail("subject:[CSV_VALIDATOR] - " + str(file) +  "\n\n[+] Passed validation and moved to accepted\n")
				f.close()