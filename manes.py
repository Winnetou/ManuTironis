#coding:utf-8
#set of functions for initial text preparation

def find_apparatus(page):
	'''Start from the bottom line
	and check where greek text ends
	and apparatus criticus starts
	'''
	return line_number


def join_word():
	'''
	Whenever a word on the end of a line
	is continued in another line
	try to join it and check
	'''
	# first, attempt to find all lines ending with -
	for line in page[:-1]: #we do not get to the final line, because its continued on another page
		line = line.strip()
		if line.endswith('-'):
			last_word = line.split()[-1]
			next_line = page[page.inex(line)+1].strip()
			first_word = next_line.split()[0]