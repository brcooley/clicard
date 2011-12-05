#! /usr/bin/python3
# -*- coding: utf-8 -*-

'''


'''

import sys
import os.path
import random
import json
from optparse import *

PROG_TITLE = 'ChineseFlashcards'
VERSION = '0.3'


def main():

	parser = OptionParser(description=DESC, prog=PROG_TITLE, version='{} version {}'.format(PROG_TITLE, VERSION))
	parser.add_option('-r','--raw', help='Convert raw vocab input into empty JSON list', metavar='FILE')
	#parser.add_argument('-d','-D','--debug', action='store_true', help='enables debugging and logging')
	args, cardfiles = parser.parse_args()

	wordList = []
	ansList  = []
	wrongAns = []

	if args.raw != None:
		createRaw(args.raw)

	for cFile in cardfiles:
		cardIn = open(cFile,'r')
		for char in cardIn.readlines():
			word, answer = char.split()
			for ans in answer.split(';'):
				ansList.append(ans.strip().lower())
			wordList.append([word.strip().lower(),ansList])
			ansList = []
		cardIn.close()

	random.shuffle(wordList)

	for word in wordList:
		possAns = input('{}? '.format(word[0]))
		if possAns.lower() not in word[1]:
			print('Correct answer is {}'.format(word[1][0]))
			wrongAns.append(word)
	print('Need to study {} characters again'.format(len(wrongAns)))

	while len(wrongAns):
		for word in wrongAns[:]:
			possAns = input('{}? '.format(word[0]))
			if possAns.lower() not in word[1]:
				print('Correct answer is {}'.format(word[1][0]))
				#print(wrongAns)
			else:
				wrongAns.remove(word)
		random.shuffle(wrongAns)


def createRaw(filename):
	'''Convert raw vocab input into a JSON list.'''
	with open(filename,'r') as fIn:
		wordData = fIn.read().split('----')
		if len(wordData[0].split()) != len(wordData[1].split()):
			print('Error converting, unequal number of word/alt pairings.')
			sys.exit(1)
		wordJSON = [{'word':x, 'alt':[y], 'pos':[], 'meaning':[]}
					for x,y in zip(wordData[0].split(), wordData[1].split())]

	if ((os.path.isfile(filename.split('.')[0] + '.vocab')) and
		('y' == input('Warning, .vocab file already exists, overwrite? ')[0].lower())):
		with open(filename.split('.')[0] + '.vocab', 'w') as fOut:
			json.dump(wordJSON,fOut, indent=2)

	sys.exit(0)


DESC = ''' A CLI-flashcard program '''

if __name__ == '__main__':
	main()
