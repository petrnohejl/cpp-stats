#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Stats version 1.0

Copyright (C)2008 Petr Nohejl, jestrab.net

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

This program comes with ABSOLUTELY NO WARRANTY!
"""

# TODO:
# RemComment(): odstrani i komentare ve stringu


### IMPORT #####################################################################

import sys		# argv
import glob		# ziskani nazvu souboru dle * konvence
import os		# prace se soubory a adresari
import string	# prace s retezci
import re		# regularni vyrazy



### SEZNAMY A KONSTANTY ########################################################

# klicova slova jazyka c++
keywords = ( \
"asm" ,"auto" ,"bool" ,"break" ,"case" ,"catch" ,"char" ,"class" ,"const" ,"const_cast" \
,"continue" ,"default" ,"delete" ,"do" ,"double" ,"dynamic_cast" ,"else" ,"enum" ,"explicit" \
,"export" ,"extern" ,"false" ,"float" ,"for" ,"friend" ,"goto" ,"if" ,"inline" ,"int" \
,"long" ,"mutable" ,"namespace" ,"new" ,"operator" ,"private" ,"protected" ,"public" \
,"register" ,"reinterpret_cast" ,"return" ,"short" ,"signed" ,"sizeof" ,"static" ,"static_cast" \
,"struct" ,"switch" ,"template" ,"this" ,"throw" ,"true" ,"try" ,"typedef" ,"typeid" \
,"typename" ,"union" ,"unsigned" ,"using" ,"virtual" ,"void" ,"volatile" ,"wchar_t" ,"while" \
)

# RE pro operatory jazyka c++, neuvazujeme pretypovani, ternarni operator ? :, (), [], operator carky, sizeof, new, delete...
# :: -> . ++ -- ! ~ -
# + * & ->* .* /
# % << >> < <= >
# >= == != ^ | && ||
# = += -= *= /= %= &=
# ^= |= <<= >>=
operators = ( \
"::" ,"->[^\*]" ,"[a-zA-Z_]\w*\.[a-zA-Z_]\w*" ,"\+\+" ,"--" ,"![^=]" ,"~" ,"[^-]-[^->=]" \
,"[^\+]\+[^\+=]" ,"[^\.>]\*[^=]" ,"[^&]&[^&=]" ,"->\*" ,"\.\*" ,"\/[^=]" \
,"%[^=]" ,"<<[^=]" ,">>[^=]" ,"[^<]<[^<=]" ,"[^<]<=" ,"[^>-]>[^>=*]" \
,"[^>]>=" ,"==" ,"!=" ,"\^[^=]" ,"[^\|]\|[^\|=]" ,"&&" ,"\|\|" \
,"[^\*=<>!\+-\/%&\^\|]=[^=]" ,"\+=" ,"-=" ,"\*=" ,"\/=" ,"%=" ,"&=" \
,"\^=" ,"\|=" ,"<<=" ,">>=" \
)

# seznam koncovek souboru
extension = [".cpp", ".cc", ".c++", ".c", ".hpp", ".h", ".h++"]

CONST_SPACE = 3				# velikost odsazeni vysledku od nazvu souboru ve vypisu
CONST_TOTAL = "CELKEM:"		# napis celkem



### HELP #######################################################################

def Help():
	print "Stats version 1.0"
	print ""
	print "Copyright (c)2008 Petr Nohejl, jestrab.net"
	print ""
	print "Funkce: program prochazi soubory v aktualnim adresari a ve vsech podadresarich a"
	print "        vytvari statistiky ze zdrojovych kodu jazyka C/C++"
	print ""
	print "Parametry programu:"
	print "--help       vypise tuto napovedu"
	print "-k           vypise pocet klicovych slov mimo komentare, retezce a direktivy"
	print "-o           vypise pocet operatoru mimo komentare, retezce a direktivy"
	print "             nepocita: pretypovani, operator carky, sizeof, ternarni operator ? :, zavorky () []"
	print "-ik          vypise pocet identifikatoru vcetne klicovych slov mimo komentare, retezce a direktivy"
	print "-w <pattern> vypise pocet textovych retezcu \"pattern\""
	print "-c           vypise delku komentaru v bytech"
	print "-s           vypise delku retezcu v bytech mimo komentare a direktivy"
	print "-l           vypise pocet radku"
	print "-u           vypise pocet nevyuzitych radku (obsahujicich pouze bile znaky nebo komentare)"
	print "-n           vypise pocet ciselnych literalu mimo komentare, retezce a direktivy"
	print "-p           volitelny prepinac, program vypisuje soubory bez uplne cesty"

	return



### KEYWORDS ###################################################################

def Keywords(relPath):
	
	counter = 0				# citac
	semaphore = False		# jsem uvnitr komentare?
	result = []				# seznam s vysledky
	
	# ziskani seznamu souboru
	files = GetFiles([], os.getcwd())
	
	# pruchod jednotlivymi soubory
	for x in range(len(files)):
		
		counter = 0
		
		# otevreni souboru
		try:
			file = open(files[x], "r")
		except:
			ErrorFile()
			return
		
		# pruchod radky v souboru
		while(1):
			line = file.readline()
			if(line == ""):
				break
				
			# odstraneni komentaru
			ret = RemComment(line, semaphore)
			line = ret[0]
			semaphore = ret[1]
			
			line = RemString(line)		# odstraneni stringu
			line = RemChar(line)		# odstraneni charu
			line = RemDirect(line)		# odstraneni direktiv preprocesoru

			# pruchod klicovymi slovy
			for y in range(len(keywords)):
				regexp = re.compile("\W" + keywords[y] + "\W|^" + keywords[y] + "\W|\W" + keywords[y] + "$") # \Wint\W|^int\W|\Wint$
				found = regexp.findall(line)
				counter += len(found)
		
		result.append(counter)	# ulozeni vysledku do seznamu
		file.close	# uzavreni souboru
	
	# vypis statistik
	PrintStats(files, result, relPath)
	return



### OPERATORS ##################################################################

def Operators(relPath):

	counter = 0				# citac
	semaphore = False		# jsem uvnitr komentare?
	result = []				# seznam s vysledky
	
	# ziskani seznamu souboru
	files = GetFiles([], os.getcwd())
	
	# pruchod jednotlivymi soubory
	for x in range(len(files)):
		
		counter = 0
		
		# otevreni souboru
		try:
			file = open(files[x], "r")
		except:
			ErrorFile()
			return
		
		# pruchod radky v souboru
		while(1):
			line = file.readline()
			if(line == ""):
				break
				
			# odstraneni komentaru
			ret = RemComment(line, semaphore)
			line = ret[0]
			semaphore = ret[1]
			
			line = RemString(line)		# odstraneni stringu
			line = RemChar(line)		# odstraneni charu
			line = RemDirect(line)		# odstraneni direktiv preprocesoru

			# pruchod operatory
			for y in range(len(operators)):
				regexp = re.compile(operators[y])
				found = regexp.findall(line)
				#if(len(found) > 0):
				#	print found
				counter += len(found)
		
		result.append(counter)	# ulozeni vysledku do seznamu
		file.close	# uzavreni souboru
	
	# vypis statistik
	PrintStats(files, result, relPath)
	return
	
	
	
### IDENTIFKEY #################################################################

def IdentifKey(relPath):
	
	counter = 0				# citac
	semaphore = False		# jsem uvnitr komentare?
	result = []				# seznam s vysledky
	
	# ziskani seznamu souboru
	files = GetFiles([], os.getcwd())
	
	# pruchod jednotlivymi soubory
	for x in range(len(files)):
		
		counter = 0
		
		# otevreni souboru
		try:
			file = open(files[x], "r")
		except:
			ErrorFile()
			return
		
		# pruchod radky v souboru
		while(1):
			line = file.readline()
			if(line == ""):
				break
				
			# odstraneni komentaru
			ret = RemComment(line, semaphore)
			line = ret[0]
			semaphore = ret[1]
			
			line = RemString(line)		# odstraneni stringu
			line = RemChar(line)		# odstraneni charu
			line = RemDirect(line)		# odstraneni direktiv preprocesoru
			line = RemNum(line)			# odstraneni ciselnych literalu

			# hledani klicovych slov a identifikatoru
			regexp = re.compile("[a-zA-Z_]\w*")
			found = regexp.findall(line)
			
			counter += len(found)
		
		result.append(counter)	# ulozeni vysledku do seznamu
		file.close	# uzavreni souboru
	
	# vypis statistik
	PrintStats(files, result, relPath)
	return
	
	
	
### IDENTIF ####################################################################

def Identif(relPath):
	
	counter = 0				# citac
	semaphore = False		# jsem uvnitr komentare?
	result = []				# seznam s vysledky
	
	# ziskani seznamu souboru
	files = GetFiles([], os.getcwd())
	
	# pruchod jednotlivymi soubory
	for x in range(len(files)):
		
		counter = 0
		
		# otevreni souboru
		try:
			file = open(files[x], "r")
		except:
			ErrorFile()
			return
		
		# pruchod radky v souboru
		while(1):
			line = file.readline()
			if(line == ""):
				break
				
			# odstraneni komentaru
			ret = RemComment(line, semaphore)
			line = ret[0]
			semaphore = ret[1]
			
			line = RemString(line)		# odstraneni stringu
			line = RemChar(line)		# odstraneni charu
			line = RemDirect(line)		# odstraneni direktiv preprocesoru
			line = RemNum(line)			# odstraneni ciselnych literalu

			# hledani identifikatoru
			regexp = re.compile("[a-zA-Z_]\w*")
			found = regexp.findall(line)
			filtred = []
			
			# pruchod nalezenymi slovy
			for y in range(len(found)):
				# hledani identifikatoru, ktere nejsou klicovym slovem
				if(found[y] not in keywords):
					filtred.append(found[y])

			counter += len(filtred)
		
		result.append(counter)	# ulozeni vysledku do seznamu
		file.close	# uzavreni souboru
	
	# vypis statistik
	PrintStats(files, result, relPath)
	return
	
	
	
### WORD #######################################################################

def Word(relPath, word):
	
	counter = 0				# citac
	result = []				# seznam s vysledky
	
	# ziskani seznamu souboru
	files = GetFiles([], os.getcwd())
	
	# pruchod jednotlivymi soubory
	for x in range(len(files)):
		
		counter = 0
		
		# otevreni souboru
		try:
			file = open(files[x], "r")
		except:
			ErrorFile()
			return
		
		# pruchod radky v souboru
		while(1):
			line = file.readline()
			if(line == ""):
				break

			# hledani slova
			regexp = re.compile(word)
			found = regexp.findall(line)
			
			counter += len(found)
		
		result.append(counter)	# ulozeni vysledku do seznamu
		file.close	# uzavreni souboru
	
	# vypis statistik
	PrintStats(files, result, relPath)
	return
	
	
	
### COMMENT ####################################################################

def Comment(relPath):
	
	counter = 0				# citac
	withComm = 0			# velikost s komentari
	withoutComm = 0			# velikost bez komentaru
	semaphore = False		# jsem uvnitr komentare?
	result = []				# seznam s vysledky
	
	# ziskani seznamu souboru
	files = GetFiles([], os.getcwd())
	
	# pruchod jednotlivymi soubory
	for x in range(len(files)):
		
		counter = 0
		
		# otevreni souboru
		try:
			file = open(files[x], "r")
		except:
			ErrorFile()
			return
		
		# pruchod radky v souboru
		while(1):
			line = file.readline()
			if(line == ""):
				break
				
			# ulozeni delky radku vcetne komentaru
			withComm = len(line)
			
			# odstraneni komentaru
			ret = RemComment(line, semaphore)
			line = ret[0]
			semaphore = ret[1]
			
			# ulozeni delky radku bez komentaru
			withoutComm = len(line)

			# delka komentaru v bytech
			counter += withComm - withoutComm
		
		result.append(counter)	# ulozeni vysledku do seznamu
		file.close	# uzavreni souboru
	
	# vypis statistik
	PrintStats(files, result, relPath)
	return
	
	
	
### STRING ####################################################################

def Str(relPath):
	
	counter = 0				# citac
	withStr = 0				# velikost s komentari
	withoutStr = 0			# velikost bez komentaru
	semaphore = False		# jsem uvnitr komentare?
	result = []				# seznam s vysledky
	
	# ziskani seznamu souboru
	files = GetFiles([], os.getcwd())
	
	# pruchod jednotlivymi soubory
	for x in range(len(files)):
		
		counter = 0
		
		# otevreni souboru
		try:
			file = open(files[x], "r")
		except:
			ErrorFile()
			return
		
		# pruchod radky v souboru
		while(1):
			line = file.readline()
			if(line == ""):
				break

			# odstraneni komentaru
			ret = RemComment(line, semaphore)
			line = ret[0]
			semaphore = ret[1]
			
			line = RemChar(line)			# odstraneni charu
			line = RemDirect(line)			# odstraneni direktiv preprocesoru
			withStr = len(line)				# ulozeni delky radku vcetne stringu
			line = RemString(line)			# odstraneni stringu
			withoutStr = len(line)			# ulozeni delky radku bez stringu
			counter += withStr - withoutStr	# delka komentaru v bytech
		
		result.append(counter)	# ulozeni vysledku do seznamu
		file.close	# uzavreni souboru
	
	# vypis statistik
	PrintStats(files, result, relPath)
	return



### LINE #######################################################################

def Line(relPath):
	
	counter = 0				# citac
	result = []				# seznam s vysledky
	
	# ziskani seznamu souboru
	files = GetFiles([], os.getcwd())
	
	# pruchod jednotlivymi soubory
	for x in range(len(files)):
		
		counter = 0
		
		# otevreni souboru
		try:
			file = open(files[x], "r")
		except:
			ErrorFile()
			return
		
		# pruchod radky v souboru
		while(1):
			line = file.readline()
			
			counter += 1	# pocet radku
			
			# konec souboru
			if(line == ""):
				break
		
		result.append(counter)	# ulozeni vysledku do seznamu
		file.close	# uzavreni souboru
	
	# vypis statistik
	PrintStats(files, result, relPath)
	return
	
	
	
### UNUSED LINE ################################################################

def UnusedLine(relPath):
	
	counter = 0				# citac
	semaphore = False		# jsem uvnitr komentare?
	result = []				# seznam s vysledky
	
	# ziskani seznamu souboru
	files = GetFiles([], os.getcwd())
	
	# pruchod jednotlivymi soubory
	for x in range(len(files)):
		
		counter = 0
		
		# otevreni souboru
		try:
			file = open(files[x], "r")
		except:
			ErrorFile()
			return
		
		# pruchod radky v souboru
		while(1):
			line = file.readline()
			
			# konec souboru
			if(line == ""):
				counter += 1
				break
			
			# odstraneni komentaru
			ret = RemComment(line, semaphore)
			line = ret[0]
			semaphore = ret[1]
			
			# orezani bilych znaku
			line = string.strip(line) + "\n"	
			
			# pocet nevyuzitych radku
			if(line == "\n"):
				counter += 1
			
		result.append(counter)	# ulozeni vysledku do seznamu
		file.close	# uzavreni souboru
	
	# vypis statistik
	PrintStats(files, result, relPath)
	return



### NUMBER ####################################################################

def Number(relPath):

	counter = 0				# citac
	semaphore = False		# jsem uvnitr komentare?
	result = []				# seznam s vysledky
	
	# ziskani seznamu souboru
	files = GetFiles([], os.getcwd())
	
	# pruchod jednotlivymi soubory
	for x in range(len(files)):
		
		counter = 0
		
		# otevreni souboru
		try:
			file = open(files[x], "r")
		except:
			ErrorFile()
			return
		
		# pruchod radky v souboru
		while(1):
			line = file.readline()
			if(line == ""):
				break
				
			# odstraneni komentaru
			ret = RemComment(line, semaphore)
			line = ret[0]
			semaphore = ret[1]
			
			line = RemString(line)		# odstraneni stringu
			line = RemChar(line)		# odstraneni charu
			line = RemDirect(line)		# odstraneni direktiv preprocesoru
			
			# osetreni cislic v identifikatorech
			regexp = re.compile("\d[eE][+-]")
			line = regexp.sub('', line)
			regexp = re.compile("[a-zA-Z_][\w]*")
			line = regexp.sub(' ', line)

			# pocet cisel
			numLiterals = "(?:(?:\d+\.\d*|\d*\.\d+)(?:[eE][\+\-]?\d+)?(?:[fFlL])?|(?:\d+)(?:[eE][\+\-]?\d+)(?:[fFlL])?)|(?:(?:[1-9]\d*|0[^xX][0-7]*|0[xX][\da-fA-F]*)(?:[lL][uU]|[uU][lL]|[lL]|[uU])?)"
			regexp = re.compile(numLiterals)
			found = regexp.findall(line)
			counter += len(found)
		
		result.append(counter)	# ulozeni vysledku do seznamu
		file.close	# uzavreni souboru
	
	# vypis statistik
	PrintStats(files, result, relPath)
	return
	
	
	
### REMOVE COMMENT #############################################################

def RemComment(line, semaphore):
	
	# odstraneni radkoveho komentare
	splitted = string.split(line, "//", 1)
	if(len(splitted) == 2):
		line = splitted[0]
	
	# odstraneni velkeho komentare	
	while(1):	
		start = string.find(line, "/*")
		end = string.find(line, "*/")
		
		# syntakticky spatne napsany komentar, osetreni zacykleni
		while(start > end):
			end = string.find(line, "*/", end+2)
			if(end == -1):
				break
				
		# nenachazim se uvnitr komentare	
		if(semaphore == False):
			# /* ... */
			if(start != -1 and end != -1):
				line = line[:start] + line[end+2:]
				continue
			# /* ...
			elif(start != -1 and end == -1):
				line = line[:start]
				semaphore = True
				break
			# ukoncujici podminka
			elif(start == -1 and end == -1):
				break
				
		# nachazim se uvnitr komentare	
		else:
			# ... */
			if(end != -1):
				line = line[end+2:]
				semaphore = False
				continue
			# ukoncujici podminka
			else:
				line = ""
				break

	return [line, semaphore]



### REMOVE STRING ##############################################################

def RemString(line):
	
	# odstraneni retezcu
	regexp = re.compile('\"(?:\\\\.|[^\"])*\"')
	line = regexp.sub('', line)
	
	return line



### REMOVE CHARS ###############################################################

def RemChar(line):

	# odstraneni charu
	regexp = re.compile("\'(?:\\\\.|[^\'])*\'")
	line = regexp.sub('', line)
	
	return line

	
	
### REMOVE DIRECTIVES ##########################################################

def RemDirect(line):
	
	# odstraneni direktiv preprocesoru
	index = string.find(line, "#")
	if(index == 0):
		line = ""
	
	return line
	
	

### REMOVE NUMBERS #############################################################

def RemNum(line):
	
	# odstraneni ciselnych literalu
	numLiterals = "(?:(?:\d+\.\d*|\d*\.\d+)(?:[eE][\+\-]?\d+)?(?:[fFlL])?|(?:\d+)(?:[eE][\+\-]?\d+)(?:[fFlL])?)|(?:(?:[1-9]\d*|0[^xX][0-7]*|0[xX][\da-fA-F]*)(?:[lL][uU]|[uU][lL]|[lL]|[uU])?)"
	regexp = re.compile(numLiterals)
	line = regexp.sub(' ', line)
	
	return line
	
	
	
### GETFILES ###################################################################

def GetFiles(files, actDir):
	
	os.chdir(actDir)			# nastaveni aktualniho adresare
	dirs = []					# seznam adresaru
	elements = glob.glob("*")	# seznam souboru a adresaru
	
	# ziskani adresaru
	for x in range(len(elements)):
		if(os.path.isdir(elements[x])):
			dirs.append(elements[x])

	# ziskani a ulozeni souboru
	for x in range(len(extension)):
		type = glob.glob("*" + extension[x])
		# pridani absolutni cesty
		for x in range(len(type)):
			type[x] = os.path.join(actDir, type[x])
		files += type
		 
	# vnoreni do dalsiho podadresare
	if(dirs != []):
		for x in range(len(dirs)):
			GetFiles(files, os.path.join(actDir, dirs[x]))
	
	return files



### PRINT STATS ################################################################

def PrintStats(files, result, relPath):
	
	total = 0		# celkem
	maxFile = 0		# delka nejdelsiho nazvu souboru
	maxResult = 0	# delka retezce nejvetsi hodnoty
	
	# kontrola delky seznamu
	if(len(files) != len(result)):
		print "Error: Neznama chyba!\n"
		return
	
	# parametr -p - vypise pouze nazev souboru bez cesty 
	if(relPath == True):
		for x in range(len(files)):
			files[x] = os.path.basename(files[x])
			
	# vypocet celkem
	for x in range(len(result)):
		total += result[x]
		
	# vypocet maxResult
	maxResult = len(str(total))
	
	# vypocet maxFile
	for x in range(len(files)):
		maxCurrent = len(files[x])
		if(maxCurrent > maxFile):
			maxFile = maxCurrent
	if(maxFile < len(CONST_TOTAL)):
		maxFile = len(CONST_TOTAL)
	
	# vypis statistik
	for x in range(len(files)):
		print files[x].ljust(maxFile + CONST_SPACE), repr(result[x]).rjust(maxResult)

	# vypis celkem
	print CONST_TOTAL.ljust(maxFile + CONST_SPACE), repr(total).rjust(maxResult)

	return



### ERROR ######################################################################

def ErrorArg():
	print "Error: Neplatne argumenty!\nNapovedu zobrazite spustenim programu s parametrem --help."
	return
	
def ErrorFile():
	print "Error: Soubor nelze nacist!"
	return



### STATS ######################################################################

def Stats():
	
	# osetreni parametru programu
	
	relPath = False	# pouziti prikazu -p
	
	# 2 parametry
	if(len(sys.argv) == 2):
		if(sys.argv[1] == "--help" or sys.argv[1] == "-h" ):
			Help()
		elif(sys.argv[1] == "-k"):
			Keywords(relPath)
		elif(sys.argv[1] == "-o"):
			Operators(relPath)
		elif(sys.argv[1] == "-ik"):
			IdentifKey(relPath)
		elif(sys.argv[1] == "-i"):
			Identif(relPath)
		elif(sys.argv[1] == "-c"):
			Comment(relPath)
		elif(sys.argv[1] == "-s"):
			Str(relPath)
		elif(sys.argv[1] == "-l"):
			Line(relPath)
		elif(sys.argv[1] == "-u"):
			UnusedLine(relPath)
		elif(sys.argv[1] == "-n"):
			Number(relPath)
		else:
			ErrorArg()
			return
		
	# 3 parametry
	elif(len(sys.argv) == 3):
	
		# pouziti prikazu -p
		if("-p" in sys.argv):
			relPath = True
			if("-k" in sys.argv):
				Keywords(relPath)
			elif("-o" in sys.argv):
				Operators(relPath)
			elif("-ik" in sys.argv):
				IdentifKey(relPath)
			elif("-i" in sys.argv):
				Identif(relPath)
			elif("-c" in sys.argv):
				Comment(relPath)
			elif("-s" in sys.argv):
				Str(relPath)
			elif("-l" in sys.argv):
				Line(relPath)
			elif("-u" in sys.argv):
				UnusedLine(relPath)
			elif("-n" in sys.argv):
				Number(relPath)
			else:
				ErrorArg()
				return
				
		elif(sys.argv[1] == "-w"):	
			Word(relPath, sys.argv[2])
				
		else:
			ErrorArg()
			return	
				
	# 4 parametry
	elif(len(sys.argv) == 4):
			
		# pouziti prikazu -w a -p
		if("-w" in sys.argv and "-p" in sys.argv):
			relPath = True
			indexW = sys.argv.index("-w")
			indexP = sys.argv.index("-p")
			
			if(indexW == 1 and indexP == 3):
				Word(relPath, sys.argv[indexW+1])
			elif(indexW == 2 and indexP == 1):
				Word(relPath, sys.argv[indexW+1])
			else:
				ErrorArg()
				return

		else:
			ErrorArg()
			return
		
	# jiny pocet parametru			
	else:
		ErrorArg()
		return

	return



### MAIN #######################################################################

if (__name__=="__main__"):
	Stats()
	