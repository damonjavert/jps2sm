#from bs4 import BeautifulSoup
#import requests
#driver = webdriver.Firefox()
#driver.get("file:///home/***REMOVED***/Downloads/minjps.html")

import urllib2
from bs4 import BeautifulSoup
import re

import pickle
import datetime
import os
from urlparse import urlparse
import requests
import HTMLParser

class MyLoginSession:
    """
    https://stackoverflow.com/a/37118451/2115140
    by https://stackoverflow.com/users/1150303/domtomcat

    a class which handles and saves login sessions. It also keeps track of proxy settings.
    It does also maintine a cache-file for restoring session data from earlier
    script executions.
    """
    def __init__(self,
                 loginUrl,
                 loginData,
                 loginTestUrl,
                 loginTestString,
                 sessionFileAppendix = '_session.dat',
                 maxSessionTimeSeconds = 30 * 60,
                 proxies = None,
                 userAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
                 debug = True,
                 forceLogin = False,
                 **kwargs):
        """
        save some information needed to login the session

        you'll have to provide 'loginTestString' which will be looked for in the
        responses html to make sure, you've properly been logged in

        'proxies' is of format { 'https' : 'https://user:pass@server:port', 'http' : ...
        'loginData' will be sent as post data (dictionary of id : value).
        'maxSessionTimeSeconds' will be used to determine when to re-login.
        """
        urlData = urlparse(loginUrl)

        self.proxies = proxies
        self.loginData = loginData
        self.loginUrl = loginUrl
        self.loginTestUrl = loginTestUrl
        self.maxSessionTime = maxSessionTimeSeconds
        self.sessionFile = urlData.netloc + sessionFileAppendix
        self.userAgent = userAgent
        self.loginTestString = loginTestString
        self.debug = debug

        self.login(forceLogin, **kwargs)

    def modification_date(self, filename):
        """
        return last file modification date as datetime object
        """
        t = os.path.getmtime(filename)
        return datetime.datetime.fromtimestamp(t)

    def login(self, forceLogin = False, **kwargs):
        """
        login to a session. Try to read last saved session from cache file. If this fails
        do proper login. If the last cache access was too old, also perform a proper login.
        Always updates session cache file.
        """
        wasReadFromCache = False
        if self.debug:
            print('loading or generating session...')
        if os.path.exists(self.sessionFile) and not forceLogin:
            time = self.modification_date(self.sessionFile)         

            # only load if file less than 30 minutes old
            lastModification = (datetime.datetime.now() - time).seconds
            if lastModification < self.maxSessionTime:
                with open(self.sessionFile, "rb") as f:
                    self.session = pickle.load(f)
                    wasReadFromCache = True
                    if self.debug:
                        print("loaded session from cache (last access %ds ago) "
                              % lastModification)
        if not wasReadFromCache:
            self.session = requests.Session()
            self.session.headers.update({'user-agent' : self.userAgent})
            res = self.session.post(self.loginUrl, data = self.loginData, 
                                    proxies = self.proxies, **kwargs)

            if self.debug:
                print('created new session with login' )
            self.saveSessionToCache()

        # test login
        res = self.session.get(self.loginTestUrl)
        #print res.text
        if res.text.lower().find(self.loginTestString.lower()) < 0:
            raise Exception("could not log into provided site '%s'"
                            " (did not find successful login string)"
                            % self.loginUrl)

    def saveSessionToCache(self):
        """
        save session to a cache file
        """
        # always save (to update timeout)
        with open(self.sessionFile, "wb") as f:
            pickle.dump(self.session, f)
            if self.debug:
                print('updated session cache-file %s' % self.sessionFile)

    def retrieveContent(self, url, method = "get", postData = None, **kwargs):
        """
        return the content of the url with respect to the session.

        If 'method' is not 'get', the url will be called with 'postData'
        as a post request.
        """
        if method == 'get':
            res = self.session.get(url , proxies = self.proxies, **kwargs)
        else:
            res = self.session.post(url , data = postData, proxies = self.proxies, **kwargs)

        # the session has been updated on the server, so also update in cache
        self.saveSessionToCache()            

        return res


#MyLoginSession vars
loginUrl = "https://jpopsuki.eu/login.php"
loginTestUrl = "https://jpopsuki.eu"
successStr = "Latest 5 Torrents"

loginData = {'username' : '***REMOVED***', 'password' : '***REMOVED***' }

s = MyLoginSession(loginUrl, loginData, loginTestUrl, successStr)

res = s.retrieveContent("https://jpopsuki.eu/torrents.php?id=256527")

#jps_page = "file:///home/***REMOVED***/Downloads/sgbuono.html"
#page = urllib2.urlopen(jps_page)

soup = BeautifulSoup(res.text, 'html5lib')

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
date = sqbrackets[1].replace(".","")

print category
print date

artist = re.findall('<a[^>]+>(.*)<', artistlinelinktext)[0]
print artist
title = re.findall('<a.*> - (.*) \[', text)[0]
print title

rel2 = str(soup.select('#content .thin .main_column .torrent_table tbody')[0])
#print rel2
rel2data = re.findall('\\xbb.* (.*) / (.*) / (.*)</a>', rel2)
#print rel2data[0]

torrentlinks = re.findall('href="(.*)" title="Download"', rel2)
#print torrentlinks[0]

torrentfiles = []
#releasedata[0] - format
#releasedata[1] - bitrate
#releasedata[2] - source
for releasedata, torrentlinkescaped in zip(rel2data, torrentlinks):
    print releasedata[0] , releasedata[1], releasedata[2]
    #print torrentlink
    torrentlink = HTMLParser.HTMLParser().unescape(torrentlinkescaped)
    #Download JPS torrents
    torrentfile = s.retrieveContent("https://jpopsuki.eu/%s" % torrentlink)
    torrentfilename = "%s - %s - %s - %s - %s.torrent" % (artist, title, releasedata[0] , releasedata[1], releasedata[2])
    #print torrentfile.text
    #torrentdata = torrentfile.text.Value()
    with open(torrentfilename, "wb") as f:
        f.write(torrentfile.content)
	torrentfiles.append(torrentfile.content)


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
imagelink = "https://jpopsuki.eu/" + re.findall('<a\s+(?:[^>]*?\s+)?href=\"([^\"]*)\"', image)[0]
print imagelink

tagsget = str(soup.select('#content .thin .sidebar .box ul.stats.nobullet li'))
tags = re.findall('searchtags=([^\"]+)', tagsget)
print tags


"""
#Send data to SugoiMusic upload!

uploadurl = 'https://sugoimusic.me/upload.php'
data =  {
	'submit': 'true',
	'auth': '***REMOVED***',
	'file_input': torrent, 
	'type': category, #TODO Add feature to request cateogry as parameter as JPS cats do not all = SM cats
	'title': title,
	#'title_jp': title_jp, #TODO Extract Japanese title
	'idols[]': artist,
	'year': date,
	#'remaster': true,
	#'remasteryear': remasterdate,
	#'remastertitle': remastertitle,
	'media': releasedata[2],
	'audioformat': releasedata[0],
	'bitrate': releasedata[1],
	'tags': tags #Prob needs extracting into just commas
	'image': imagelink
	'album_desc': groupdescription
	#'release_desc': releasedescription
}



#SM MyLoginSession vars
SMloginUrl = "https://sugoimusic.me/login.php"
SMloginTestUrl = "https://sugoimusic.me/"
SMsuccessStr = "Enabled users"

SMloginData = {'username' : '***REMOVED***', 'password' : '***REMOVED***' }

SMs = MyLoginSession(loginUrl, loginData, loginTestUrl, successStr)

SMres = SMs.retrieveContent("https://sugoimusic.me/upload.php","post",data)

with open("results.html", "w") as f:
    f.write(SMres.read())
"""
