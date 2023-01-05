import sys
from resource import *
import time
import psutil


alpha_values = [[0, 110, 48, 94], [110, 0, 118, 48], [48, 118, 0, 110], [94, 48, 110, 0]]
delta_value = 30

# To generate sequence string from base string and its pattern

def generate_sequence(base_string, modifications):

	## converting string to list for better complexity as strings are immutable

	character_list = [x for x in base_string]

	for i, num in enumerate(modifications):

		if num >= len(character_list):
			return None

		character_list = character_list[0: num+1] + character_list[::] + character_list[num+1:]

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

## For DP calculation
def initialize_dp_table(a, b):

	n = len(a)
	m = len(b)

	#create a matrix of size n+1 * m+1
	dp = []
	dp = [[0 for i in range(m+1)] for j in range(n+1)]
 
	#initialize for the case where first sequence is empty
	for i in range(m+1):
		dp[0][i] = delta_value * i
 
	#initialize for the case where second sequence is empty
	for i in range(n+1):
		dp[i][0] = delta_value * i

	return dp
 
 
def fill_dp_table(a, b, dp):

	n = len(a)
	m = len(b)

	#fill in the matrix
	for i in range(1, n+1):
		for j in range(1, m+1):
			x_index = find_character_index(a[i-1])
			y_index = find_character_index(b[j-1])
			dp[i][j] = find_min(dp[i-1][j-1] + alpha_values[x_index][y_index], 
								dp[i-1][j] + delta_value, 
								dp[i][j-1] + delta_value)

	return dp
 

def generate_aligned_sequence(a, b, dp):

	n = len(a)
	m = len(b)

	#generate the strings

	a_aligned = ""
	b_aligned = ""
 
	i = n
	j = m
 
	while i >= 1 and j >= 1:

		x = a[i-1]
		y = b[j-1]
 
		x_idx = find_character_index(x)
		y_idx = find_character_index(y)

		# picking them as matched with a mismatch cost

		if dp[i][j] == dp[i-1][j-1] + alpha_values[x_idx][y_idx]:   
			a_aligned = x + a_aligned
			b_aligned = y + b_aligned
			j -= 1
			i -= 1
		
		# putting a gap in string a

		elif dp[i][j] == dp[i][j-1] + delta_value:               
			a_aligned = '_' + a_aligned
			b_aligned = y + b_aligned
			j-=1

		# putting a gap in string b

		elif dp[i][j] == dp[i-1][j] + delta_value:  
			a_aligned = x + a_aligned
			b_aligned = '_' + b_aligned
			i -= 1

 
	#add the remaining characters from a
	while i >= 1:
		a_aligned = a[i-1] + a_aligned
		b_aligned = '_' + b_aligned
		i -= 1
 
	#add the remaining characters from b
	while j >= 1:
		a_aligned = '_' + a_aligned
		b_aligned = b[j-1] + b_aligned
		j -= 1

	return [a_aligned, b_aligned, dp[n][m]]
 

def process_memory():
	process = psutil.Process()
	memory_info = process.memory_info()
	memory_consumed = memory_info.rss/1024
	return memory_consumed


if __name__ == '__main__':

	input_file = sys.argv[1]

	## Step1 : To read input and generate sequences 

	sequence1, sequence2 = input_reader(input_file)

	m = len(sequence1)
	n = len(sequence2)
	
	# Step2 : To calculate using DP algorithm, the min cost and subsequent alignments

	start_time = time.time()

	dp = initialize_dp_table(sequence1, sequence2)
	dp = fill_dp_table(sequence1, sequence2, dp)
		
	alignment1, alignment2, mismatch_penalty = generate_aligned_sequence(sequence1, sequence2, dp)

	end_time = time.time()
	time_taken = end_time - start_time

	# Step 3 : Output to output.txt
	n1 = len(alignment1)
	n2 = len(alignment2)

	# Taking first and last 50 characters of the sequences
	alignment1_left = alignment1 if len(alignment1) < 50 else alignment1[0 : 50]
	alignment1_right = alignment1 if len(alignment1) < 50 else alignment1[n1-50 : n1]
	alignment2_left = alignment2 if len(alignment2) < 50 else alignment2[0 : 50]
	alignment2_right = alignment2 if len(alignment2) < 50 else alignment2[n2-50 : n2]

	memory_consumed = process_memory()

	final_output = alignment1_left + " " + alignment1_right + "\n" + alignment2_left + " " + alignment2_right + "\n" + str(mismatch_penalty) + "\n" + str(time_taken) + "\n" + str(memory_consumed)

	with open('output.txt', "w") as myfile:
		myfile.write(final_output)	
		







