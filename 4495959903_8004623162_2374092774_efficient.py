import sys
from resource import *
import time
import psutil

alpha_values = [[0, 110, 48, 94], [110, 0, 118, 48], [48, 118, 0, 110], [94, 48, 110, 0]]
delta_value = 30

## To generate Sequence from base string and its pattern
def generate_sequence(base_string, modifications):

	## converting string to list for better complexity as strings are immutable

	character_list = [x for x in base_string]

	for i, num in enumerate(modifications):

		if num >= len(character_list):
			return None

		character_list = character_list[0 : num+1] + character_list[: :] + character_list[num+1 :]

	return "".join(x for x in character_list)


# Read input file, send to generate string and validate correctness of both inputs and generations, returns sequences from base strings
def input_reader(input_file):

	i = 0

	base_string1 = ""  
	base_string2 = ""  

	number_list1 = [] # to store numbers which will modify the first base string
	number_list2 = [] # to store numbers which will modify the second base string

	with open(input_file, 'r') as f:
		lines = f.readlines()
	
	lines = [line.strip('\n') for line in lines]

	for word in lines:

		if word == "":
			return [None, None]
		
		if word[0] in ('A', 'C', 'T', 'G'):  	# this should happen twice only (since there are 2 strings)
			for alphabet in word:         		# checking that each item in this alphabet list is A,C,T,G
				if alphabet not in ('A', 'C', 'T', 'G'):
					return [None, None]        

			if base_string1 == "":
				base_string1 = word
			elif base_string2 == "":
				base_string2 = word
			else:
				return [None, None]             # do this error handling if 3 strings are given


		else:  									# that is if word is a number

			for number in word:                 # checking that each number is valid
				if number not in ('0','1','2','3','4','5','6','7','8','9'):
					return [None, None] 
			
			if base_string2 == "": 					# string 2 is empty and hence this number belongs to string1 modifications
				number_list1.append(int(word))
			else: 						 			# string 2 is now active and hence this number belongs to string2 modifications
				number_list2.append(int(word))


	sequence1 = generate_sequence(base_string1, number_list1)
	sequence2 = generate_sequence(base_string2, number_list2)

	if sequence1 is None or sequence2 is None:
		return [None, None] 

	return [sequence1, sequence2]


# To get the index of the character to be used in the alpha_values matrix
def find_character_index(character):
	if character == 'A':
		return 0
	elif character == 'C':
		return 1
	elif character == 'G':
		return 2
	elif character == 'T':
		return 3

def find_min(p, q, r):
	if p <= q and p <= r:
		return p
	elif q <= p and q <= r:
		return q
	return r


# Computed the mismatch penalty using matrix of size  n * 2 (2 column DP)
def compute_sequence_mismatch_penalty(a, b):

	n = len(a)
	m = len(b)

	if n == 0:
		return m * delta_value
	if m == 0:
		return n * delta_value

	dp = [[0 for i in range(2)] for j in range(n+1)]

	for i in range(n+1):
		dp[i][0] = i * delta_value


	for j in range(1, m+1):
		dp[0][1] = j * delta_value
		for i in range(1, n+1):
			x_idx = find_character_index(a[i-1])
			y_idx = find_character_index(b[j-1])
			dp[i][1] = find_min(dp[i-1][0] + alpha_values[x_idx][y_idx], dp[i-1][1] + delta_value, dp[i][0] + delta_value)

		# move the values from the second column to the first column
		for i in range(n+1):
			dp[i][0] = dp[i][1]

	return dp


# helper function which is used for computing alignments and mismatch penalty for base cases in the main divide_and_conquer function (sequence_alignment_driver)
def sequence_alignment_using_dp(a, b):

	n = len(a)
	m = len(b)

	dp = [[0 for i in range(m+1)] for j in range(n+1)]

	# initializing the dp table (matrix)
	for i in range(m+1):
		dp[0][i] = i * delta_value

	for i in range(n+1):
		dp[i][0] = i * delta_value

	
	# Filling the dp table
	for i in range(1, n+1):
		for j in range(1, m+1):
			x_index = find_character_index(a[i-1])
			y_index = find_character_index(b[j-1])
			dp[i][j] = find_min(dp[i-1][j-1] + alpha_values[x_index][y_index], 
								dp[i-1][j] + delta_value, 
								dp[i][j-1] + delta_value)

	a_aligned = ""	
	b_aligned = ""
	i = n
	j = m 

	# Generating alignments 
	while i > 0 and j > 0:

		x = a[i-1]
		y = b[j-1]
		x_index = find_character_index(x)
		y_index = find_character_index(y)

		if dp[i][j] == dp[i-1][j-1] + alpha_values[x_index][y_index]:
			a_aligned = x + a_aligned
			b_aligned = y + b_aligned
			j -= 1
			i -= 1

		elif dp[i][j] == dp[i][j-1] + delta_value:
			a_aligned = '_' + a_aligned
			b_aligned = y + b_aligned
			j -= 1

		elif dp[i][j] == dp[i-1][j] + delta_value:
			a_aligned = x + a_aligned
			b_aligned = '_' + b_aligned
			i -= 1

	# Generating the remaining sequence from a when j has reached 0
	while i > 0:
		a_aligned = a[i-1] + a_aligned
		b_aligned = '_' + b_aligned
		i -= 1

	# Generating the remaining sequence from b when i has reached 0
	while j > 0:
		a_aligned = '_' + a_aligned
		b_aligned = b[j-1] + b_aligned
		j -= 1

	return [a_aligned, b_aligned, dp[n][m]]

# Orchaestrator function (Divide and Conquer)
def sequence_alignment_driver(a, b):

	x_size = len(a)
	y_size = len(b)
	
	# Base case
	if(x_size <= 2 or y_size <= 2):
		return sequence_alignment_using_dp(a, b)
		

	x_mid = x_size // 2
	x_left = a[0 : x_mid]
	x_right = a[x_mid : ]
	x_right = x_right[ : : -1] # reverse x_right

	y = b
	y_forward = b
	y_backward = y[ : : -1]

	dp_forward = compute_sequence_mismatch_penalty(y_forward, x_left) # for storing mismatch_penalties in forward strings 
	dp_backward = compute_sequence_mismatch_penalty(y_backward, x_right) # for storing mismatch_penalties in reversed strings

	size = len(dp_forward)
	index_of_minimum_sum = -1 # index where the second string will be divided
	minimum_sum = sys.maxsize

	# find the minimum combined costs

	for i in range(size):
		s = dp_forward[i][1] + dp_backward[size-i-1][1]
		if s < minimum_sum:
			minimum_sum = s
			index_of_minimum_sum = i

	y_left_final = b[0 : index_of_minimum_sum]
	y_right_final = b[index_of_minimum_sum : ]
	y_right_final = y_right_final[ : : -1]

	# recursively call for both parts
	left_result = sequence_alignment_driver(x_left, y_left_final)
	right_result = sequence_alignment_driver(x_right, y_right_final)

	alignment1_left = left_result[0]

	r1 = right_result[0] 
	r1 = r1[ : : -1] # Reversing r1

	alignment1_right = r1

	alignment2_left = left_result[1]

	r2 = right_result[1] 
	r2 = r2[ : : -1] # Reversing r2

	alignment2_right = r2

	alignment1_final = alignment1_left + alignment1_right
	alignment2_final = alignment2_left + alignment2_right
	mismatch_penalty = left_result[2] + right_result[2]
	
	
	return [alignment1_final, alignment2_final, mismatch_penalty]


def process_memory():
	process = psutil.Process()
	memory_info = process.memory_info()
	memory_consumed = memory_info.rss / 1024
	return memory_consumed


if __name__ == '__main__':

	start_time = time.time()
	input_file = sys.argv[1]

	# Read input strings and generate sequences
	sequence1, sequence2 = input_reader(input_file)

	# Generate Alignments and compute mismatch penalty
	alignment1, alignment2, mismatch_penalty = sequence_alignment_driver(sequence1, sequence2)

	n1 = len(alignment1)
	n2 = len(alignment2)

	# Taking first and last 50 characters of the sequences
	alignment1_left = alignment1 if len(alignment1) < 50 else alignment1[0 : 50]
	alignment1_right = alignment1 if len(alignment1) < 50 else alignment1[n1-50 : n1]
	alignment2_left = alignment2 if len(alignment2) < 50 else alignment2[0 : 50]
	alignment2_right = alignment2 if len(alignment2) < 50 else alignment2[n2-50 : n2]

	end_time = time.time()
	time_taken = end_time - start_time

	memory_consumed = process_memory()
	final_output = alignment1_left + " " + alignment1_right + "\n" + alignment2_left + " " + alignment2_right + "\n" + str(mismatch_penalty) + "\n" + str(time_taken) + "\n" + str(memory_consumed)

	with open('output.txt', "w") as myfile:
		myfile.write(final_output)

