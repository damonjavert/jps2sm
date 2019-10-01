from bs4 import BeautifulSoup
import re
import pickle
import datetime
import os
from urlparse import urlparse
import requests
import HTMLParser
from django.utils.text import get_valid_filename
import sys
import ConfigParser

class MyLoginSession:
    """
    https://stackoverflow.com/a/37118451/2115140
    Added some features myself, originally by https://stackoverflow.com/users/1150303/domtomcat

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

    def retrieveContent(self, url, method = "get", postData = None, postDataFiles = None, **kwargs):
        """
        return the content of the url with respect to the session.

        If 'method' is not 'get', the url will be called with 'postData'
        as a post request.
        """
        if method == 'get':
            res = self.session.get(url , proxies = self.proxies, **kwargs)
        else:
            res = self.session.post(url , data = postData, proxies = self.proxies, files = postDataFiles, **kwargs)

        # the session has been updated on the server, so also update in cache
        self.saveSessionToCache()            

        return res

url = sys.argv[1]

#Get credentials from cfg file
scriptdir = os.path.dirname(os.path.abspath(sys.argv[0]))
config = ConfigParser.ConfigParser()
configfile = scriptdir + '/jps2sm.cfg'
try:
    open(configfile)
except IOError:
    print 'Error: cannot read cfg - enter your JPS/SM credentials in jps2sm.cfg and check jps2sm.cfg.example to see the syntax.'
    raise

config.read(configfile)
jpsuser = config.get('JPopSuki', 'User')
jpspass = config.get('JPopSuki', 'Password')
smuser = config.get('SugoiMusic', 'User')
smpass = config.get('SugoiMusic', 'Password')

#JPS MyLoginSession vars
loginUrl = "https://jpopsuki.eu/login.php"
loginTestUrl = "https://jpopsuki.eu"
successStr = "Latest 5 Torrents"
loginData = {'username' : jpsuser, 'password' : jpspass }

#SM MyLoginSession vars
SMloginUrl = "https://sugoimusic.me/login.php"
SMloginTestUrl = "https://sugoimusic.me/"
SMsuccessStr = "Enabled users"
SMloginData = {'username' : smuser, 'password' : smpass }

def getauthkey():
    SMshome = MyLoginSession(SMloginUrl, SMloginData, SMloginTestUrl, SMsuccessStr)
    SMreshome = SMshome.retrieveContent("https://sugoimusic.me/torrents.php?id=118")
    soup = BeautifulSoup(SMreshome.text, 'html5lib')
    rel2 = str(soup.select('#content .thin .main_column .torrent_table tbody')[0])
    authkey = re.findall('authkey=(.*)&amp;torrent_pass=', rel2)[0]
    return authkey

s = MyLoginSession(loginUrl, loginData, loginTestUrl, successStr)

res = s.retrieveContent(url) #TODO: Proper argument parsing

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

#Extract date even if square brackets are used elsewhere in the title
datepattern = re.compile("[12][09][0-9][0-9].*")
date = filter(datepattern.match, sqbrackets)[0].replace(".","")

print category
print date

artist = re.findall('<a[^>]+>(.*)<', artistlinelinktext)[0]
print artist
title = re.findall('<a.*> - (.*) \[', text)[0]
print title

VideoCategories = [
    'Bluray', 'DVD', 'PV', 'TV-Music', 'TV-Variety', 'TV-Drama', 'Music Performace']

rel2 = str(soup.select('#content .thin .main_column .torrent_table tbody')[0])

#print rel2
#fakeurl = 'https://jpopsuki.eu/torrents.php?id=181558&torrentid=251763'
#fakeurl = 'blah'

def gettorrentlinks(torrentid):
    torrentlinks = re.findall('href="(.*)" title="Download"', rel2)
    if torrentid is not None: #We have specific torrent url
        #No ultra complex regex is needed here, we simply parse the array looking for the torrent url that has the torrentid in it
        torrentlink = [i for i in torrentlinks if torrentid in i]
        return torrentlink
    else: #We have group url
        return torrentlinks

#Try to find torrentid in the url to determine if this is a group url or a specific torrent url.
try:
    torrentid = re.findall('torrentid=(.*)$', url)[0]
except:
    torrentid = None

torrentlinks = gettorrentlinks(torrentid)

#For single torrent urls use the swapTorrent JS to find the exact torrent release data, for group urls just find all of them in sequence
if category in VideoCategories and torrentid is not None:
    rel2data = re.findall('swapTorrent(?:.*)%s(?:.*)\xbb (\w+) / (\w+)' % (torrentid),rel2)
elif category in VideoCategories and torrentid is None:
    rel2data = re.findall('\\xbb (\w+) / (\w+)', rel2) #Support Freeleach
elif category not in VideoCategories and torrentid is not None:
    rel2data = re.findall('swapTorrent(?:.*)%s(?:.*)\xbb (.*) / (.*) / (.*)</a>' % (torrentid),rel2)
elif category not in VideoCategories and torrentid is None:
    rel2data = re.findall('\\xbb.* (.*) / (.*) / (.*)</a>', rel2)

print rel2data
#print torrentlinks

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
tagsall = ",".join(tags)

authkey = getauthkey()

#Send data to SugoiMusic upload!
def uploadtorrent(category, artist, title, date, media, audioformat, bitrate, tagsall, imagelink, groupdescription, filename, **kwargs):
    uploadurl = 'https://sugoimusic.me/upload.php'
    data =  {
        'submit': 'true',
        'auth': authkey,
        'type': Categories[category], #TODO Add feature to request cateogry as parameter as JPS cats do not all = SM cats
        'title': title,
        #'title_jp': title_jp, #TODO Extract Japanese title
        'idols[]': artist,
        'year': date,
        #'remaster': true,
        #'remasteryear': remasterdate,
        #'remastertitle': remastertitle,
        'media': media, #releasedata[2]
        'audioformat': audioformat, #releasedata[0]
        'bitrate': bitrate, #releasedata[1]
        'tags': tagsall,
        'image': imagelink,
        'album_desc': groupdescription,
        #'release_desc': releasedescription
    }
    if category in VideoCategories:
        data['codec'] = 'h264' #assumed default
        data['ressel'] = 'SD' #assumed default
        data['container'] = audioformat #In JPS container and audioformat are the same field
        data['sub'] = 'NoSubs' #assumed default
        data['audioformat'] = 'AAC' #assumed default
        data['lang'] = 'Japanese' #assumed default
        del data['bitrate']

    postDataFiles = {
        'file_input': open(filename,'rb')
    }
 
    SMs = MyLoginSession(SMloginUrl, SMloginData, SMloginTestUrl, SMsuccessStr)
    SMres = SMs.retrieveContent(uploadurl,"post",data,postDataFiles)

    try:
        SMerrorTorrent = re.findall('red; text-align: center;">(.*)</p>', SMres.text)[0]
        print SMerrorTorrent
        groupid = re.findall('<input type="hidden" name="groupid" value="(.*)" />', SMres.text)[0]
        print groupid
    except:
        try:
            SMerrorLogon = re.findall('<p>Invalid(.*)</p>', SMres.text)[0]
            print 'Invalid ' + SMerrorLogon
        except:
            groupid = re.findall('<input type="hidden" name="groupid" value="(.*)" />', SMres.text)[0]
            print 'OK - groupid %s' % (groupid)

    with open("results." + torrentfilename + ".html", "w") as f:
        f.write(SMres.content)

Categories = {
    'Album': 0,
    #'EP': 1, #Does not exist on JPS
    'Single': 2,
    'Bluray': 3, #Does not exist on JPS
    'DVD': 4,
    'PV': 5,
    'Music Performance': 6, #Does not exist on JPS
    'TV-Music': 7, #Music Show
    'TV-Variety': 8, #Talk Show
    'TV-Drama': 9, #TV Drama
    'Pictures': 10,
    'Misc': 11,
}

for releasedata, torrentlinkescaped in zip(rel2data, torrentlinks):
    print releasedata
    if category in VideoCategories:
        media = releasedata[1]
        audioformat = releasedata[0]
        bitrate = "---"
    else:
        media = releasedata[2]
        audioformat = releasedata[0]
        bitrate = releasedata[1]

    torrentlink = HTMLParser.HTMLParser().unescape(torrentlinkescaped)
    #Download JPS torrents
    torrentfile = s.retrieveContent("https://jpopsuki.eu/%s" % torrentlink)
    torrentfilename = get_valid_filename("%s - %s - %s.torrent" % (artist, title, "-".join(releasedata)))
    #print torrentfile.text
    #torrentdata = torrentfile.text.Value()
    with open(torrentfilename, "wb") as f:
        f.write(torrentfile.content)
        
    uploadtorrent(category, artist, title, date, media, audioformat, bitrate, tagsall, imagelink, groupdescription, torrentfilename)

