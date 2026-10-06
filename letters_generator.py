#!/usr/bin/python3

import random


# Frequency percentage of letters in Spanish. Source: Wikipedia
_LETTER_PROBABILITIES = {
	"A": 12.53,
	"B": 1.42,
	"C": 4.68,
	"D": 5.86,
	"E": 13.68,
	"F": 0.69,
	"G": 1.01,
	"H": 0.70,
	"I": 6.25,
	"J": 0.44,
	"K": 0.02,
	"L": 4.97,
	"M": 3.15,
	"N": 6.71,
	"Ñ": 0.31,
	"O": 8.68,
	"P": 2.51,
	"Q": 0.88,
	"R": 6.87,
	"S": 7.98,
	"T": 4.63,
	"U": 3.93,
	"V": 0.90,
	"W": 0.01,
	"X": 0.22,
	"Y": 0.90,
	"Z": 0.52
	}


def generate_letters(n_letters=9, min_vowels=3, min_consonants=4):
	"""
	Generate a random sequence of letters weighted by Spanish language frequencies.
	Ensures a minimum amount of vowels and consonants for game balance.
	"""
	# Validate arguments
	if not isinstance(n_letters, int) or \
		not isinstance(min_vowels, int) or \
		not isinstance(min_consonants, int):
		raise TypeError("Arguments type not integer")
	if n_letters <= 0 or min_vowels < 0 or min_consonants < 0:
		raise ValueError("Not positive argument introduced")
	if min_vowels + min_consonants > n_letters:
		raise ValueError(f"Minimum guaranteed values ({min_vowels + min_consonants}) " 
			f"are greater than the total number of letters ({n_letters})")

	# Create two separate dicts for vowels and consonants
	vowels_dict = {}
	consonants_dict = {}
	for letter, prob in _LETTER_PROBABILITIES.items():
		if letter in "AEIOU":
			vowels_dict[letter] = prob
		else:
			consonants_dict[letter] = prob
	
	# Create four tuples, two with the letters and two with their respective weights
	vowels, vowel_weights = zip(*vowels_dict.items())
	consonants, consonant_weights = zip(*consonants_dict.items())

	# Pick minimum guaranteed vowels and consonants.
	# random.choices also accepts tuples as arguments
	selected_vowels = random.choices(vowels, weights=vowel_weights, k=min_vowels)
	selected_consonants = random.choices(consonants, weights=consonant_weights, k=min_consonants)
	
	# Fill remaining letters randomly from full frequency distribution
	remaining_count = n_letters - (min_vowels + min_consonants)
	if remaining_count > 0:
		all_keys, all_weights = zip(*_LETTER_PROBABILITIES.items())
		remaining_letters = random.choices(all_keys, weights=all_weights, k=max(0, remaining_count))
	
	# Combine and shuffle so vowels/consonants are not grouped at fixed positions
	result_list = selected_vowels + selected_consonants + remaining_letters
	random.shuffle(result_list)

	return "".join(result_list)


# Just for testing
# Test
if __name__ == "__main__":
	print(generate_letters())
