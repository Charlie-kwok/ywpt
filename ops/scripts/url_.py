#coding : utf-8
from bs4 import BeautifulSoup

import  urllib.request


url="https://www.yjq.com"
html= urllib.request.urlopen(url).read()
soup =BeautifulSoup(html,"html.parser")
for line in soup.find_all('a'):
    print(line.get('href'))
