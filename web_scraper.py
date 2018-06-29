'''
run with: python web_scraper.py <query> <rmv stop words?>

<query> should be subject of wikipedia page

most frequently used words on <query>'s page will be reported
'''
#pull, parse data from html, xml files
from bs4 import BeautifulSoup
#lib for dealing w web data
import requests
#deal w regular expressions
import re
#wrapper for existing funcs
import operator
#format for pulling data from web
import json
#make table from 2d list
from tabulate import tabulate
#system calls (user input)
import sys
#inconsequential strings
from stop_words import get_stop_words

def getWordList(url):
	word_list = []
	#retrieve raw data
	source_code = requests.get(url)
	#convert to text
	plain_text = source_code.text
	#format into lxml
	soup = BeautifulSoup(plain_text, 'lxml')

	#find words in paragraph tag
	for text in soup.findAll('p'):
		if text.text is None:
			continue
		#content
		content = text.text
		words = content.lower().split()

		#each string
		for word in words:
			#remove non-chars
			cleaned_word = clean_word(word)
			#in case nothing left after cleaning
			if len(cleaned_word) > 0:
				word_list.append(cleaned_word)

	return word_list

def clean_word(word):
	cleaned_word = re.sub('[^A-Za-z]+', '', word)
	return cleaned_word
	
def createFrequencyTable(word_list):
	#word count is roster of words seen
	word_count = {}
	for word in word_list:
		#index is the word
		if word in word_count:
			word_count[word] += 1
		else:
			word_count[word] = 1

	return word_count

def remove_stop_words(freq_list):
	stop_words = get_stop_words('en')

	#new list w no stop words
	clean_list = []
	#key = word, value = frequency
	for key, value in freq_list:
		if key not in stop_words:
			clean_list.append([key, value])

	return clean_list

#link to web data
wikipedia_api_link = "https://en.wikipedia.org/w/api.php?format=json&action=query&list=search&srsearch="
wikipedia_link = "https://en.wikipedia.org/wiki/"

#catch query too short
if(len(sys.argv) < 2):
	print('Enter valid string')
	exit()

#hold search key
string_query = sys.argv[1]


if(len(sys.argv) > 2):
	search_mode = True
else:
	search_mode = False

#concat strings, create URL
url = wikipedia_api_link + string_query

try:
	#store article
	response = requests.get(url)
	#load, decode, format data in response
	data = json.loads(response.content.decode('utf-8'))

	#first link in article list
	wikipedia_page_tag = data['query']['search'][0]['title']

	#holds page, all strings
	url = wikipedia_link + wikipedia_page_tag

	page_word_list = getWordList(url)

	#table of word counts
	page_word_count = createFrequencyTable(page_word_list)

	#sort strings
	sorted_word_freq_list = sorted(page_word_count.items(), key=operator.itemgetter(1), reverse=True)

	if(search_mode):
		sorted_word_freq_list = remove_stop_words(sorted_word_freq_list)

	#sum total words, calc frequencies
	total_words_sum = 0
	for key, value in sorted_word_freq_list:
		total_words_sum = total_words_sum + value

	#get top 20 words
	if len(sorted_word_freq_list) > 20:
		sorted_word_freq_list = sorted_word_freq_list[:20]

	#final word list + frequency + percentage
	final_list = []
	for key, value in sorted_word_freq_list:
		percentage_value = float(value * 100) / total_words_sum
		final_list.append([key, value, round(percentage_value, 4)])

	print_headers = ['Word', 'Frequency', 'Freq. %']

	print(tabulate(final_list, headers=print_headers, tablefmt='orgtbl'))

except requests.exceptions.Timeout:
	print("The server didn't respond. Please, try again later.")