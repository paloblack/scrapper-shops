from bs4 import BeautifulSoup
import urllib.request
import re

url="https://www.momocshoes.com/es/producto/felin-noir-vegan/"
data=urllib.request.urlopen(url)


searched_word = 'in-stock'

soup = BeautifulSoup(data, 'html.parser')
results = soup.findAll(string=re.compile('.*{0}.*'.format(searched_word)), recursive=True)

print ('Found the word "{0}" {1} times\n'.format(searched_word, len(results)))
