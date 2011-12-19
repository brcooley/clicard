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

'''	Start 	= [i v]'
	Mid		= [a e h i n o u v]
	End 	= [a e g i n o r u v]
'''

PINYIN_TRANSLATIONS = {
	'ü': 'v',
	'ā': 'a1', 'ē': 'e1', 'ī': 'i1', 'ō': 'o1', 'ū': 'u1', 'ǖ': 'v1',
	'á': 'a2', 'é': 'e2', 'í': 'i2', 'ó': 'o2', 'ú': 'u2', 'ǘ': 'v2',
	'ǎ': 'a3', 'ě': 'e3', 'ǐ': 'i3', 'ǒ': 'o3', 'ǔ': 'u3', 'ǚ': 'v3',
	'à': 'a4', 'è': 'e4', 'ì': 'i4', 'ò': 'o4', 'ù': 'u4', 'ǜ': 'v4'
}

''' DICT = { 	tone0 = {},
			tone1 = {} }
'''


def main():

	parser = OptionParser(description=DESC, prog=PROG_TITLE, version='{} version {}'.format(PROG_TITLE, VERSION))
	parser.add_option('-b','--build', help='Convert raw vocab input into JSON list', metavar='FILE')
	parser.add_option('-t','--to-raw', help='Convert ctxt input into raw', metavar='FILE')
	parser.add_option('-i','--interact', action='store_true', help='Enter interactive mode for debugging')
	#parser.add_argument('-d','-D','--debug', action='store_true', help='enables debugging and logging')
	args, cardfiles = parser.parse_args()

	wordList = []
	ansList  = []
	wrongAns = []

#	胡琴弹奏
# 	āáǎà
# 	ēèěé
# 	īǐíì
# 	ōóǒò
# 	ūúǔù
# 	üǖǘǚǜ

	if args.interact:
		while True:
			cmd = input('-=> ').lower()
			if cmd == 'q':
				sys.exit(0)
			elif cmd == 't':
				toTrans = input('? ')
				print(pinyinToASCII(toTrans))

	if args.build:
		createVocab(args.build)
	if args.to_raw:
		toRaw(args.to_raw)

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


def createVocab(filename):
	'''Convert raw vocab input into a JSON list.'''
	with open(filename,'r') as fIn:
		wordData = fIn.read().split('----')
		words = wordData[0].split()
		alts = wordData[1].split('  ')
		# meanings = wordData[2].split()

		if len(words) != len(alts):  # != len(meanings):
			print('Error converting, unequal number of word/alt pairings.')
			sys.exit(1)
		wordJSON = [{'word':x, 'alt':[''.join(y.split()).strip(), pinyinToASCII(y.strip())], 'pos':[], 'meaning':[]} for x,y in zip(words, alts)]
		# for entry in wordJSON:
			# entry['alt'].append(pinyinToASCII(entry['alt'][0]))
		# for i, entry in enumerate(wordJSON):
			# for meaning in meanings[i]:
				# entry['meaning'].append(meaning)

	if (os.path.isfile(filename.split('.')[0] + '.vocab')):
		if ('y' != input('Warning, .vocab file already exists, overwrite? ')[0].lower()):
			sys.exit(0)

	with open(filename.split('.')[0] + '.vocab', 'w') as fOut:
		json.dump(wordJSON, fOut, indent=2, ensure_ascii=False, sort_keys=True)

	sys.exit(0)


def pinyinToASCII(phrase):
	'''Converts pinyin with tonal marks into conventional word# form.'''
	pWords = phrase.split(' ')
	toReturn = ''
	# print('Working on {}'.format(pWords))
	for word in pWords:
		# translate tonal mark to #
		neutralTone = True
		for ch in word:
			if ch in PINYIN_TRANSLATIONS.keys():
				toReturn += (word[:word.index(ch)] + PINYIN_TRANSLATIONS[ch][0] + word[word.index(ch)+1:] + PINYIN_TRANSLATIONS[ch][1])
				neutralTone = False
				break
		if neutralTone == True:
			toReturn += word
			
	return toReturn


def toRaw(filename):
	'''Converts old ctxt format to raw format.'''
	with open(filename, 'r') as fIn:
		data = [(line.split()[0], line.split()[1]) for line in fIn.readlines()]
	wordStr = '\n'.join([x[0] for x in data])
	altStr = ' '.join([x[1] for x in data])
	with open(filename.split('.')[0] + '.vraw', 'w') as fOut:
		print('{}\n----\n{}'.format(wordStr, altStr), file=fOut)
	sys.exit(0)


DESC = ''' A CLI-flashcard program '''

if __name__ == '__main__':
	main()
