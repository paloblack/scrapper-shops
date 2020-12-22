from bs4 import BeautifulSoup
import urllib.request
import re
import json

url="https://www.momocshoes.com/es/producto/felin-noir-vegan/"
data=urllib.request.urlopen(url)



soup = BeautifulSoup(data, 'html.parser')
result=soup.form['data-product_variations']

res = json.loads(result)

for i in res:
        print(i['sku'])
        print(i['availability_html'])
