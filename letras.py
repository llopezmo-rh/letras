#!/usr/bin/python3

import collections
import json
import re
import sys
import unicodedata


WORD_FILE_PATH="words.txt"
#WORD_FILE_PATH="test.txt"
CACHE_FILE_PATH="cache.json"


def normalize_word(key):
	"""
	Remove diacritical marks, but not eñes.
	"""
	
	# Temporary protection for eñes because "~" is considered diacritical
	enne_protected = key.replace('Ñ', '__ENYE__').replace('ñ', '__enye__')

	# Convert diacritical marks into normal characters.
	# For example: "ú" into "u´"
	normalized = unicodedata.normalize('NFD', enne_protected)

	# Remove diacritical marks ("Mn" stands for "Nonspacing Mark")
	no_diacritical = "".join(c for c in normalized if unicodedata.category(c) != 'Mn')

	# It seems that normalizing again is needed to make sure that there is not any
	# strange character, but I am not sure why
	renormalized = unicodedata.normalize('NFC', no_diacritical)

	# Recover the eñes and return
	return renormalized.replace('__ENYE__', 'Ñ').replace('__enye__', 'ñ')


def generate_new_entries(file_line):
	"""
	If the line is a single word, simply return a dict with that word and its
	hash key.

	If the line has a comma, return the entries for both the masculine and
	female genders for that word
	"""
	
	# Remove initial and final spaces and convert to upper case
	line = file_line.strip().upper()

	# Initialize dict to be returned
	entries = collections.defaultdict(list)
	
	# For empty lines, return an empty dict
	if line == "":
		return entries

	# If the word has a comma, it means that it has two genders and
	# two diferent dict entries for them have to be created.
	# Example: "camarero, ra"
	if "," in line:
		male_word = line.split(",")[0]
		if male_word[-1:] in ["E", "O"]:
			female_word = male_word[:-1] + "A"
		else:
			female_word = male_word + "A"
			# Remove accent for entries like "patrón, na"
			if female_word[-3] in "ÁÉÓ":
				female_word = female_word[:-3] + normalize_word(female_word[-3]) + female_word[-2:]
		normalized_male_word = normalize_word(male_word)
		normalized_female_word = normalize_word(female_word)
		male_key = "".join(sorted(normalized_male_word))
		female_key = "".join(sorted(normalized_female_word))
		entries[male_key].append(male_word)
		entries[female_key].append(female_word)
	else:
		word = line.upper()
		normalized_word = normalize_word(word)
		key = "".join(sorted(normalized_word))
		entries[key].append(word)

	return entries
		

def generate_dict():
	"""
	If JSON cache file exists: dump it as a dict into memory.
	
	Otherwise:
	1. Dump the text file with the list of words as a dict into memory.
	2. Create a new JSON cache file and dump the memory dict into it.
	   This will improve the performance for future executions.
	3. In case the JSON cache file cannot be created, print warning message
	   but do not stop the execution.
	"""
	
	print(f"Loading JSON cache file \"{CACHE_FILE_PATH}\" into memory...")
	try:
		with open(CACHE_FILE_PATH, "r", encoding="utf-8") as cache_file:
			# If the JSON cache file already exists, there is nothing else
			# to do.
			# Only convert the file to a dict in memory and return it
			return json.load(cache_file)
	except FileNotFoundError:
		print(f"\"{CACHE_FILE_PATH}\" does not exist.")
	# Let PermissionError raise, if any

	print(f"\n\nLoading \"{WORD_FILE_PATH}\" into memory...")
	words_dict = collections.defaultdict(list)
	with open(WORD_FILE_PATH, "r", encoding="utf-8") as word_file:
		for line in word_file:
			new_entries_dict = generate_new_entries(line)
			for key, new_words_list in new_entries_dict.items():
				words_dict[key] += new_words_list


	print(f"Generating JSON cache file \"{CACHE_FILE_PATH}\" "
		"to speed up the next executions...\n")
	# "x" mode instead of "w" because the file should not exist at this point. This
	# function should have already finished in that case. Therefore, cn case it 
	# does exist, something strange should be happening and it would be better
	# to debug the script 
	with open(CACHE_FILE_PATH, "x", encoding="utf-8") as cache_file:
		json.dump(words_dict, cache_file, ensure_ascii=False)
	
	return words_dict


def find_words(words_dict, letters):
	"""
	Find words with a Breadth-First Search. Only if no key with a specific
	length is found, shorter keys are searched
	"""
	# A FIFO "deque" used to carry out a Breadth-First Search.
	# Every queue item stores the key and its length
	first_key = "".join(sorted(letters))
	key_queue = collections.deque([(first_key, len(first_key))])

	# Set searches are O(1). Store visited keys for not processing
	# several times the same one
	visited_keys = set([first_key])

	words = []
	#current_max_len = None

	while key_queue and words == []:
		next_level_parents = []

		while key_queue:
			# popleft is FIFO whereas pop is LIFO
			key, length = key_queue.popleft()

			if key in words_dict:
				words += words_dict[key]
				#current_max_len = length

			if words == [] and length > 2:
				next_level_parents.append(key)

		if words != []:
			break

		for key in next_level_parents:
			for i in range(len(key)):
				child_key = key[:i] + key[(i + 1):]
				assert len(child_key) == len(key) - 1
				if child_key not in visited_keys:
					visited_keys.add(child_key)
					key_queue.append((child_key, length - 1))
	
	return words


if __name__ == "__main__":

	words_dict = generate_dict()
	
	while True:
		while True:
			try:
				letters = input("Letters: ").strip().upper()
			# Exit if Control+C is pressed
			except KeyboardInterrupt:
				print("\nExiting...")
				sys.exit(0)
			if re.fullmatch("[A-ZÑÁÉÍÓÚÜ]+", letters):
				break
			# Ask again for the letters if invalid characters are introduced
			else:
				print("Invalid character/s detected. Introduce letters again")
		
		result_list = find_words(words_dict, letters)
		
		print("\n\nResults:")
		for word in result_list:
			print(word)
		print()
