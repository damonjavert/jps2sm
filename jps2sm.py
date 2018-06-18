#from bs4 import BeautifulSoup
#import requests
#driver = webdriver.Firefox()
#driver.get("file:///home/***REMOVED***/Downloads/minjps.html")

import urllib2
from bs4 import BeautifulSoup
import re

jps_page = "file:///home/***REMOVED***/Downloads/sgbuono.html"
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

rel2 = str(soup.select('#content .thin .main_column .torrent_table tbody')[0])
#print rel2
rel2data = re.findall('\\xbb.* (.*) / (.*) / (.*)</a>', rel2)
#print rel2data[0]

torrentlinks = re.findall('href="(.*)" title="Download"', rel2)
#print torrentlinks[0]

for releasedata, torrentlink in zip(rel2data, torrentlinks):
    print releasedata[0] , releasedata[1], releasedata[2]
    print torrentlink

"""
release = soup.select('.torrent_table tbody tr.group_torrent td')
#print release
release_text = str(release[0])
print release_text


releasedata = re.findall('\\xbb.* (.*) / (.*) / (.*)</a>', release_text)
mformat = releasedata[0]
bitrate = releasedata[1]
media = releasedata[2]
print mformat
print bitrate
print media
"""

groupdescription = remove_html_tags(str(soup.select('#content .thin .main_column .box .body')[0]))
print groupdescription

image = str(soup.select('#content .thin .sidebar .box p a'))
imagelink = re.findall('<a\s+(?:[^>]*?\s+)?href=\"([^\"]*)\"', image)
print imagelink

tagsget = str(soup.select('#content .thin .sidebar .box ul.stats.nobullet li'))
tags = re.findall('searchtags=([^\"]+)', tagsget)
print tags
