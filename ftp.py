#!/usr/bin/env python
#title           :ftp.py
#description     :Python FTP Deploy script
#author          :Gundars Meness
#date            :20121016
#version         :0.1
#usage           :python ftp.py
#notes           :
#python_version  :2.7.3 
#==============================================================================

import ftplib
import sys
import os
import datetime

olddirname = 'old'
ftp1_host = "66.66.666.66"
ftp1_user = "user"
ftp1_pass = "*******************"
ftp1_type = "TYPE I" # Binary mode
ftp1_pasv = True # Passive mode
ftp1_strt = "startdir"
receivers = {
		0 : {
			'host' : "ftp.anyhost.net",
			'user' : "KimJong",
			'pass' : "northkoreathebest",
			'type' : "TYPE I",
			'pasv' : True,
			'strt' : "/website1.dk/dir/dir/directory",
		},
		1 : {
			'host' : "ftp.anyhost.net",
			'user' : "JomKing",
			'pass' : "northkoreathebest",
			'type' : "TYPE I",
			'pasv' : True,
			'strt' : "/website2.dk/dir/dir/directory",
		},
}


def recurse(ftp):
  dirs = ftp.nlst()
  for d in (path for path in dirs if path not in ('.', '..')):
	try:
		ftp.cwd(d)
		cleanOut(ftp)
		ftp.cwd('..')
		ftp.rmd(d)
	except:
		log('FAIL:  Failed to recursively delete previous project folder on walk_up ftp site')

def cleanOut(ftp):
  log('DEL D: '+ ftp.pwd())
  dirs = ftp.nlst()
  for d in (path for path in dirs if path not in ('.', '..')):
	try:
	  ftp.delete(d) # delete the file
	  log('DEL F: '+ ftp.pwd()+'/'+d)
	except:
	  log('DEL X: '+ ftp.pwd()+'/'+d)
	  ftp.cwd(d) # it's actually a directory; clean it
	  cleanOut(ftp)
	  ftp.cwd('..')
	  ftp.rmd(d)


def ftp_walk_down(ftp):   
	global file_count
	global directory_count

	dirs = ftp.nlst()
	for item in (path for path in dirs if path not in ('.', '..')):
		try:
			ftp.cwd(item)
			directory_count += 1
			log('DIR:  '+ ftp.pwd())
			ftp_walk_down(ftp)
			ftp.cwd('..')
		except Exception, e:
			currdir = ftp.pwd()[1:]
			currpath = currdir+"/"+item
			if not os.path.exists(currdir): os.makedirs(currdir) #Create local directory         
			try:                    
				with open(currdir+"/"+item, 'wb') as f: #Copy ftp file locally
   
					def callback(data):
						f.write(data)

					ftp.retrbinary('RETR %s' % item, callback)
					f.close()
					log('RETR: '+ currpath)
					file_count += 1
			except IOError as e:
				 log('Crash!')

def ftp_walk_up(ftp,localfrom):   
	global file_count
	global directory_count

	file_count = 0
	directory_count = 0  
	starttime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	log('INFO : Starting to remove previous directory')
	recurse(ftp) #delete old directory rec
	log('INFO : Finished to remove previous directory')
	log('INFO : Starting file copy')
	for (path, dirs, files) in os.walk(localfrom):
		path2 = path[:4]
		path = path[5:]
		if path != "":
			ftp.mkd(path)
			directory_count += 1
			log('DIR  :'+ path)
		for f in files:
			if path != "":
				fullf=path+'/'+f
			else:
				fullf=f
			file_count += 1
			fp = open(path2+'/'+fullf,'rb') # file to send
			ftp.storbinary('STOR %s' % fullf, fp) # Send the file
			log('FILE :'+ fullf)
	log('START TIME: '+ starttime)
	log('END TIME:   '+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	log('TOTAL DIRS: '+ str(directory_count))
	log('TOTAL FILES:'+ str(file_count))


def log(data):
	logfile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ ' '+data+'\n')
	logfile2.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ ' '+data+'\n')
	print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ ' '+data

# Open log file
logfile = open('logs/log '+datetime.datetime.now().strftime("%Y-%m-%d %H:%M")+'.txt', 'a')
logfile2 = open('logs/log.txt', 'a')


#Download from deployment folder
ftp = ftplib.FTP(ftp1_host)
ftp.login(ftp1_user, ftp1_pass)
log(''' \n\n
   .'"'.        ___,,,___        .'``.
  : (\  `."'"```         ```"'"-'  /) ;
   :  \                         `./  .'
	`.                            :.'
	  \        _         _        /
	   |       0}       {0       |
	''')

log('CONNECTING TO ' + ftp1_host + ' AS USER ' + ftp1_user)
ftp.sendcmd(ftp1_type)
log('TYPE: ' + ftp1_type)
ftp.set_pasv(ftp1_pasv)
if ftp1_pasv == True: log('PASSIVE MODE ENABLED')
ftp.cwd(ftp1_strt)
log('START DIRECTORY: ' + ftp1_strt)
starttime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
if os.path.isdir(ftp1_strt):
	try:
		# Rename old project first
		os.rename(ftp1_strt, olddirname+'/ '+ftp1_strt+' '+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) #Saves old dir just in case
		log( 'OLD PROJECT FOLDER RENAMED: ' + olddirname+'/ '+ftp1_strt+' '+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	except IOError as e:
		log('Cannot delete local directory')
file_count = 0
directory_count = 0

ftp_walk_down(ftp)

log('START TIME: '+ starttime)
log('END TIME:   '+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
log('TOTAL DIRS: '+ str(directory_count))
log('TOTAL FILES:'+ str(file_count))
ftp.quit()


#Upload to each websites ftp
for i in receivers:
	ftp = ftplib.FTP(receivers[i]['host'])
	ftp.login(receivers[i]['user'], receivers[i]['pass'])
	log('-------------------UPLOAD STARTING--------------------')
	log('CONNECTING TO ' + receivers[i]['host'] + ' AS USER ' + receivers[i]['user'])
	ftp.sendcmd(receivers[i]['type'])
	log('TYPE: ' + receivers[i]['type'])
	ftp.set_pasv(receivers[i]['pasv'])
	if receivers[i]['pasv'] == True: log('PASSIVE MODE ENABLED')
	ftp.cwd(receivers[i]['strt'])
	log('START DIRECTORY: ' + receivers[i]['strt'])
	ftp_walk_up(ftp,'cpdb')
	
	ftp.quit()

# Close log file
logfile.close()
