#from bs4 import BeautifulSoup
#import requests
#driver = webdriver.Firefox()
#driver.get("file:///home/***REMOVED***/Downloads/minjps.html")

import urllib2
from bs4 import BeautifulSoup
import re

jps_page = "file:///home/***REMOVED***/Downloads/minjps.html"
page = urllib2.urlopen(jps_page)
soup = BeautifulSoup(page, 'html5lib')

def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


#testbox = soup.find('div#h2', attrs={'class': 'thin'})
#artistline = artistlinebox.text.strip()
#print (artistline)

#testbox = soup.find('div', attrs={'id':'wrapper'})

#testbox = soup.find('div', id="wrapper")

artistline = soup.select('.thin h2')
artistlinelink = soup.select('.thin h2 a')
text = str(artistline[0])
print artistline[0]

artistlinelinktext = str(artistlinelink[0])

sqbrackets = re.findall('\[(.*?)\]', text)
print sqbrackets
category = sqbrackets[0]
date = sqbrackets[1]

print category
print date

artist = re.findall('<a[^>]+>(.*)<', artistlinelinktext)
print artist
title = re.findall('<a.*> - (.*) \[', text)
print title

release = soup.select('.torrent_table tbody tr.group_torrent td')
#print release
release_text = str(release[0])

releasedata = re.search('\\xbb.* (.*) / (.*) / (.*)</a>', release_text).groups()
mformat = releasedata[0]
bitrate = releasedata[1]
media = releasedata[2]
print mformat
print bitrate
print media

groupdescription = remove_html_tags(str(soup.select('#content .thin .main_column .box .body')[0]))
print groupdescription

image = str(soup.select('#content .thin .sidebar .box p a'))
imagelink = re.findall('<a\s+(?:[^>]*?\s+)?href=\"([^\"]*)\"', image)
print imagelink

tagsget = str(soup.select('#content .thin .sidebar .box ul.stats.nobullet li'))
tags = re.findall('searchtags=([^\"]+)', tagsget)
print tags
