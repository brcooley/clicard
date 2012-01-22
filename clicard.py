#! /usr/bin/python3
# -*- coding: utf-8 -*-
# Target - Python 3.1.X and later

''' CLIcards is a command-line vocabulary study tool
	Copyright (C) 2012  Brett Cooley

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>. '''

import sys
import os.path
import random
import json
import re
from optparse import *

PROG_TITLE = 'CLIcards'
VERSION = '0.5a-r3'
VER = VERSION[:4]

PINYIN_TRANSLATIONS = {
	'ü': 'v',
	'ā': 'a1', 'ē': 'e1', 'ī': 'i1', 'ō': 'o1', 'ū': 'u1', 'ǖ': 'v1',
	'á': 'a2', 'é': 'e2', 'í': 'i2', 'ó': 'o2', 'ú': 'u2', 'ǘ': 'v2',
	'ǎ': 'a3', 'ě': 'e3', 'ǐ': 'i3', 'ǒ': 'o3', 'ǔ': 'u3', 'ǚ': 'v3',
	'à': 'a4', 'è': 'e4', 'ì': 'i4', 'ò': 'o4', 'ù': 'u4', 'ǜ': 'v4'
}


#FUT Allow persistant statistics
class SessionStats(object):
	'''Object that manages statistics for a session.'''

	def __init__(self):
		self._tests = 0
		self._isRunning = False
		self._stats = []


	def __str__(self):
		totalCorrect = sum([c for _,c,_ in self._stats])
		totalAttempt = sum([a for _,_,a in self._stats])
		toReturn = '\nYou have taken {}'.format(self._tests)
		if self._tests > 1:
			toReturn += ' tests, '
		else:
			toReturn += ' test, '
		toReturn += 'answering correctly {} times out of {} attempts ({:.2%})'.format(
			totalCorrect, totalAttempt, totalCorrect/totalAttempt)

		toReturn += '\nTEST\t\t\tSCORE\tPER\n'
		toReturn += '='*36
		for i, (tType, correct, attempt) in enumerate(self._stats):
			if tType == 0:
				toReturn += '\nMeaning Test {}:\t\t'.format(i+1)
			elif tType == 1:
				toReturn += '\nIdentification Test {}:\t'.format(i+1)
			elif tType == 2:
				toReturn += '\nRecognition Test {}:\t'.format(i+1)
			toReturn += '{}/{}\t{:.2%}'.format(correct,attempt, correct/attempt)
		return toReturn


	def startTest(self, testType):
		'''Start collecting statistics for a test of type TYPE'''
		self._isRunning = True
		self._tests += 1
		if testType == 'mean':
			self.curTest = 0
		elif testType == 'id':
			self.curTest = 1
		elif testType == 'rec':
			self.curTest = 2
		self.correct = 0
		self.attempt = 0


	def stopTest(self):
		'''Stops stat collection for the current test, does nothing if no test is running'''
		if self._isRunning:
			self._isRunning = False
			self._stats.append((self.curTest, self.correct, self.attempt))

def main():
	parser = OptionParser(description=DESC, prog=PROG_TITLE, version='{} version {}'.format(PROG_TITLE, VERSION))
	parser.add_option('-b','--build', help='Convert raw vocab input into JSON list', metavar='FILE')
	parser.add_option('-r','--human-readable', action='store_const', const=2, help='Prints vocab file with indentation')
	parser.add_option('-i','--interact', action='store_true', help='Enter interactive mode for debugging')
	args, cardfiles = parser.parse_args()
	print()

	ansList  = []
	wrongAns = []

#	胡琴弹奏

	if args.interact:
		while True:
			cmd = input('-=> ').lower()
			print(cmd)
			if cmd == 'q':
				sys.exit(0)
			elif cmd == 'p2a':
				toTrans = input('? ')
				print(pinyinToASCII(toTrans))
			elif cmd == 'a2p':
				toTrans = input('? ')
				print(asciiToPinyin(toTrans, False))

	if args.build:
		try:
			createVocab(args.build, args.human_readable)
		except (IOError, ValueError) as e:
			print(e)
		else:
			print('{}.vocab sucessfully built\n'.format(args.build[:-5]))
		finally:
			sys.exit()

	# Builds list of word data from each file passed in
	wordList = []
	for cFile in cardfiles:
		with open(cFile) as wordsIn:
			wordList += json.load(wordsIn)

	statLog = SessionStats()

	while True:
		print('\n==CLI Flashcards==')
		print('1) Test for meaning (Words shown)')
		print('2) Test for identification (Meaning shown)')
		print('3) Test for recognition (Words shown)')
		print('4) Show statistics')
		print('5) Quit')

		validInput = False
		while not validInput:
			userInput = input('? ')
			validInput = True
			if userInput == '1':
				statLog.startTest('mean')
				testMeaning(wordList, statLog)
			elif userInput == '2':
				pass
			elif userInput == '3':
				pass
			elif userInput == '4':
				print(statLog)
			elif userInput == '5':
				print()
				sys.exit(0)
			else:
				validInput = False
				continue

			statLog.stopTest()


# Need to implement '..., or X' functionality, handling of using "to" with verbs, plural meanings and better support for
# case insensitivity
def testMeaning(wordList, statLog):
	'''Uses generated wordlist to test for meaning knowledge'''
	sentinel = ''
	wordSet = wordList[:]
	random.shuffle(wordSet)

	print('Type "q" at any time to quit')

	while statLog.correct < len(wordList):
		word = wordSet.pop(0)
		if word['word'] == sentinel:
			random.shuffle(wordSet)
		possAns = input('What does {} mean? '.format(word['word'])).lower()
		if possAns == 'q':
			return
		statLog.attempt += 1

		if possAns in word['meaning']:
			statLog.correct += 1
			print('Correct, {} means {}'.format(word['word'], possAns))
			if len(word['meaning']) > 1:
				print('{} could also mean '.format(word['word']),end='')
				for other in [x for x in word['meaning'] if x != possAns]:
					print('{}, '.format(other),end='')
				print('\b\b ')
				sys.stdout.flush()
		else:
			sentinel = word['word']
			try:
				word['tries'] += 1
			except KeyError:
				word['tries'] = 1
			if word['tries'] < 4:
				print('Sorry, that is not correct, {word} will be tested again'.format(**word))
			else:
				print('That is incorrect, {word} means {meaning[0]}'.format(**word))
			wordSet.append(word)


def stripComments(inputList):
	'''Takes a list and removes comments from each line, returning a new list.'''
	toReturn = []
	for line in inputList:
		try:
			if line.index('#') != 0:
				toReturn.append(line[:line.index('#')].strip())
		except ValueError:
			toReturn.append(line.strip())
	return toReturn


def createVocab(filename, indentLevel):
	'''Convert vraw vocab input into a JSON list.'''
	if filename[-5:] != '.vraw':
		raise IOError('File must be of type VRAW')
	with open(filename,'r') as fIn:
		rawData = [x for x in stripComments(fIn.readlines())]
		wordData = '\n'.join(rawData).split('----')

	counts = []
	words = alts = meanings = pos = []
	convertPinyin = False
	sep = '\n'

	for dataSec in wordData:
		tag, rest = dataSec.split(':',1)
		tag = tag.strip()
		if tag == 'LNG' and rest.strip() == 'Chinese':
			convertPinyin = True
		elif tag == 'WRD':
			words = [x for x in rest.split(sep) if x != '']
			counts.append(len(words))
		elif tag == 'ALT':
			alts = [x for x in rest.split(sep) if x != '']
			counts.append(len(alts))
		elif tag == 'DEF':
			meanings = [x for x in rest.split(sep) if x != '']
			counts.append(len(meanings))
		elif tag == 'POS':
			pos = [x for x in rest.split(sep) if x != '']
			counts.append(len(pos))
		elif tag == 'EXT':
			#Currently, we ignore this section, can be put to use later
			continue
		else:
			raise ValueError('A section of type {} is undefined'.format(tag))

	if [x for x in counts if x != counts[0]]:
		raise ValueError('Mismatched number of entries in word data')

	if convertPinyin:		#This is a custom-feature, it may not behave as everyone would expect/like
		alts = [', '.join([', '.join([''.join(x.split()), pinyinToASCII(x)]) for x in altList.strip().split(', ')])
				for altList in alts]

	wordJSON = [{'word':w, 'alt':x.strip().split(', '), 'meaning':y.strip().lower().split(', '),
				'pos':z.strip().split(', ')} for w,x,y,z in zip(words, alts, meanings, pos)]

	for wordEntry in wordJSON:
		if len(wordEntry['meaning']) != len(wordEntry['pos']):
			raise ValueError('"{}" does not have a matching number of meanings ({}) and parts of speech({})'
				.format(wordEntry['word'], len(wordEntry['meaning']), len(wordEntry['pos'])))

	if (os.path.isfile(filename.split('.')[0] + '.vocab')):
		if ('y' != input('Warning, .vocab file already exists, overwrite? ')[0].lower()):
			sys.exit(0)

	with open(filename.split('.')[0] + '.vocab', 'w') as fOut:
		json.dump(wordJSON, fOut, indent=indentLevel, ensure_ascii=False, sort_keys=True)


def pinyinToASCII(phrase):
	'''Converts pinyin with tonal marks into conventional word# form.'''
	pWords = phrase.split(' ')
	toReturn = ''
	for word in pWords:
		# translate tonal mark to #
		neutralTone = True
		for ch in word:
			if ch in PINYIN_TRANSLATIONS.keys():
				toReturn += (word[:word.index(ch)] + PINYIN_TRANSLATIONS[ch][0] +
					word[word.index(ch)+1:] + PINYIN_TRANSLATIONS[ch][1])
				neutralTone = False
				break
		if neutralTone == True:
			toReturn += word
	return toReturn


def asciiToPinyin(phrase, preserveSpaces=True):
	'''Inverse of pinyinToASCII, converts words from word# into pinyin.'''
	aWords = phrase.split(' ')
	toReturn = ''
	for word in aWords:
		if word[-1:] in ['1','2','3','4']:
			vowels = [x.lower() for x in re.findall(r'[a|e|i|o|u|v]*', word, re.IGNORECASE) if len(x) > 0][0]
			vowel = sorted(vowels)[0] if vowels[0] != 'i' or len(vowels) == 1 else vowels[1]
			ASCII_TRANSLATIONS = {v:k for k, v in PINYIN_TRANSLATIONS.items()}
			toReturn += word[:word.index(vowel)] + ASCII_TRANSLATIONS[vowel + word[-1:]] + word[word.index(vowel)+1:-1]
		elif 'v' in word:
			toReturn += word[:word.index('v')] + 'ü' + word[word.index('v')+1:]
		else:
			toReturn += phrase
		if preserveSpaces:
			toReturn += ' '
	return toReturn.strip()


DESC = '''A CLI-flashcard program'''

if __name__ == '__main__':
	main()
