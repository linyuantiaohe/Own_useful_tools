from urllib.request import urlopen
from bs4 import BeautifulSoup
 
url = 'http://www.weather.com.cn/weather/101010700.shtml'
bs = BeautifulSoup(urlopen(url),'lxml')
wt = bs.find("ul",{'class':{'t clearfix'}})
abc= wt.findAll("li")
print('昌平天气:\n')
for i in abc:
    print(i.get_text().replace('\n',' '))