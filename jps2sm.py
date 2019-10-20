# jps2sm.py is a python script that will automatically gather data from JPS from a given group url,
# iterate through all the torrents and upload them to SM.

# Standard library packages
import re
import os
import sys
import datetime
import itertools
import collections
import time
import argparse
import configparser
import pickle
import html
from urllib.parse import urlparse

# Third-party packages
import requests
import html5lib
from bs4 import BeautifulSoup
from django.utils.text import get_valid_filename

__version__ = "0.6.6.3"

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
                 sessionFileAppendix='_session.dat',
                 maxSessionTimeSeconds=30 * 60,
                 proxies=None,
                 userAgent='Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
                 debug=True,
                 forceLogin=False,
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

    def login(self, forceLogin=False, **kwargs):
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
            self.session.headers.update({'user-agent': self.userAgent})
            res = self.session.post(self.loginUrl, data=self.loginData,
                                    proxies=self.proxies, **kwargs)

            if self.debug:
                print('created new session with login')
            self.saveSessionToCache()

        # test login
        res = self.session.get(self.loginTestUrl)
        # print res.text
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

    def retrieveContent(self, url, method="get", postData=None, postDataFiles=None, **kwargs):
        """
        return the content of the url with respect to the session.

        If 'method' is not 'get', the url will be called with 'postData'
        as a post request.
        """
        if method == 'get':
            res = self.session.get(url, proxies=self.proxies, **kwargs)
        else:
            res = self.session.post(url, data=postData, proxies=self.proxies, files=postDataFiles, **kwargs)

        # the session has been updated on the server, so also update in cache
        self.saveSessionToCache()

        return res


def getbulktorrentids(user, first=1, last=None):
    res = s.retrieveContent("https://jpopsuki.eu/torrents.php?type=uploaded&userid=%s" % (user))
    soup = BeautifulSoup(res.text, 'html5lib')

    linkbox = str(soup.select('#content #ajax_torrents .linkbox')[0])
    if not last:
        try:
            last = re.findall('page=([0-9]*)&amp;order_by=s3&amp;order_way=DESC&amp;type=uploaded&amp;userid=(?:[0-9]*)&amp;disablegrouping=1\'\);"><strong> Last &gt;&gt;</strong>', linkbox)[0]
        except:
            # There is only 1 page of uploads if the 'Last >>' link cannot be found
            last = 1

    if debug:
        print(f'First page is {first}, last page is {last}')

    useruploads = {}
    useruploads = collections.defaultdict(list)

    # Parse every torrent page and add to dict, to group together releases into the same group so that they work with
    # the way that uploadtorrent() works.
    for i in range(first, int(last) + 1):
        useruploadpage = s.retrieveContent("https://jpopsuki.eu/torrents.php?page=%s&order_by=s3&order_way=DESC&type=uploaded&userid=%s&disablegrouping=1" % (i, user))
        print("https://jpopsuki.eu/torrents.php?page=%s&order_by=s3&order_way=DESC&type=uploaded&userid=%s&disablegrouping=1" % (i, user))
        # print useruploadpage.text
        soup2 = BeautifulSoup(useruploadpage.text, 'html5lib')
        try:
            torrenttable = str(soup2.select('#content #ajax_torrents .torrent_table tbody')[0])
        except IndexError:
            # TODO: Need to add this to every request so it can be handled everywhere, for now it can exist here
            quotaexceeded = re.findall('<title>Browse quota exceeded :: JPopsuki 2.0</title>', useruploadpage.text)
            if quotaexceeded:
                print('Browse quota exceeded :: JPopsuki 2.0')
                sys.exit(0)
            else:
                raise
        alltorrentlinksidsonly = re.findall('torrents.php\?id=([0-9]+)\&amp;torrentid=([0-9]+)', torrenttable)
        print(alltorrentlinksidsonly)
        for groupid, torrentid in alltorrentlinksidsonly:
            useruploads[groupid].append(torrentid)
        time.sleep(5)  # Sleep as otherwise we hit JPS browse quota
    print(useruploads)
    return useruploads


parser = argparse.ArgumentParser()
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
parser.add_argument('-d', '--debug', help='Enable debug mode', action='store_true')
parser.add_argument("-u", "--urls", help="JPS URL for a group, or multiple individual releases URLs to be added to the same group", type=str)
parser.add_argument("-n", "--dryrun", help="Just parse url and show the output, do not add the torrent to SM", action="store_true")
parser.add_argument("-b", "--batchuser", help="Upload all releases uploaded by a particular user id")
parser.add_argument("-s", "--batchstart", help="(Batch mode only) Start at this page", type=int)
parser.add_argument("-e", "--batchend", help="(Batch mode only) End at this page", type=int)
parser.add_argument("-f", "--excfilteraudioformat", help="Exclude an audioformat from upload", type=str)
parser.add_argument("-F", "--excfiltermedia", help="Exclude a media from upload", type=str)
args = parser.parse_args()

# TODO consider calling args[] directly, we will then not need this line
dryrun = debug = excfilteraudioformat = excfiltermedia = usermode = batchstart = batchend = None

if args.dryrun:
    dryrun = True

if args.debug:
    debug = True
else:
    sys.tracebacklimit = 0

if args.excfilteraudioformat:
    excfilteraudioformat = args.excfilteraudioformat

if args.excfiltermedia:
    excfiltermedia = args.excfiltermedia

if args.urls is None and args.batchuser is None:
    print('JPS URL(s) nor batchuser specified')
    sys.exit()
elif args.urls:
    jpsurl = args.urls
elif args.batchuser:
    if bool(args.batchstart) ^ bool(args.batchend):
        print('You have specified an incomplete page range.')
        sys.exit()
    elif bool(args.batchstart) and bool(args.batchend):
        batchstart = args.batchstart
        batchend = args.batchend
    usermode = True
    batchuser = args.batchuser

# Get credentials from cfg file
scriptdir = os.path.dirname(os.path.abspath(sys.argv[0]))
config = configparser.ConfigParser()
configfile = scriptdir + '/jps2sm.cfg'
try:
    open(configfile)
except FileNotFoundError:
    print('Error: cannot read cfg - enter your JPS/SM credentials in jps2sm.cfg and check jps2sm.cfg.example to see the syntax.')
    raise

config.read(configfile)
jpsuser = config.get('JPopSuki', 'User')
jpspass = config.get('JPopSuki', 'Password')
smuser = config.get('SugoiMusic', 'User')
smpass = config.get('SugoiMusic', 'Password')

# JPS MyLoginSession vars
loginUrl = "https://jpopsuki.eu/login.php"
loginTestUrl = "https://jpopsuki.eu"
successStr = "Latest 5 Torrents"
loginData = {'username': jpsuser, 'password': jpspass}

# SM MyLoginSession vars
SMloginUrl = "https://sugoimusic.me/login.php"
SMloginTestUrl = "https://sugoimusic.me/"
SMsuccessStr = "Enabled users"
SMloginData = {'username': smuser, 'password': smpass}

s = MyLoginSession(loginUrl, loginData, loginTestUrl, successStr)

Categories = {
    'Album': 0,
    # 'EP': 1, #Does not exist on JPS
    'Single': 2,
    'Bluray': 3,  # Does not exist on JPS
    'DVD': 4,
    'PV': 5,
    'Music Performance': 6,  # Does not exist on JPS
    'TV-Music': 7,  # Music Show
    'TV-Variety': 8,  # Talk Show
    'TV-Drama': 9,  # TV Drama
    'Pictures': 10,
    'Misc': 11,
}

VideoCategories = [
    'Bluray', 'DVD', 'PV', 'TV-Music', 'TV-Variety', 'TV-Drama', 'Music Performace']

TVCategories = [
    'TV-Music', 'TV-Variety', 'TV-Drama']


def removehtmltags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def getauthkey():
    SMshome = MyLoginSession(SMloginUrl, SMloginData, SMloginTestUrl, SMsuccessStr)
    SMreshome = SMshome.retrieveContent("https://sugoimusic.me/torrents.php?id=118")
    soup = BeautifulSoup(SMreshome.text, 'html5lib')
    rel2 = str(soup.select('#content .thin .main_column .torrent_table tbody'))
    authkey = re.findall('authkey=(.*)&amp;torrent_pass=', rel2)
    return authkey


def filterlist(string, substr):
    return [str for str in string if
            any(sub in str for sub in substr)]


def gettorrentlinks(torrentids):
    alltorrentlinks = re.findall('href="(.*)" title="Download"', groupdata['rel2'])
    if len(torrentids) != 0:  # We have specific torrent (release) url(s)
        # No ultra complex regex is needed here, we simply parse the array looking for the torrent url(s) that have
        # the torrentid(s) in it
        torrentlinks = filterlist(alltorrentlinks, torrentids)
        return torrentlinks
    else:  # We have group url
        return alltorrentlinks


def getreleasedata(category, torrentids):
    slashlist = []
    freeleechtext = '<strong>Freeleech!</strong>'
    if len(torrentids) == 0:  # Group url
        slashdata = re.findall('\\xbb (.*)<\/a>',  groupdata['rel2'])
        slashlist = [i.split(' / ') for i in slashdata]
    else:  # Release url(s) given
        for torrentid in torrentids:
            slashdata = re.findall('swapTorrent(?:.*)%s(?:.*)\\xbb (.*)<\/a>' % (torrentid), groupdata['rel2'])
            slashlist.extend([i.split(' / ') for i in slashdata])

    if freeleechtext in slashlist:
        slashlist.remove(freeleechtext)  # Remove Freeleech so it does not interfere with Remastered

    print(slashlist)
    return slashlist


# Send data to SugoiMusic upload!
def uploadtorrent(category, artist, title, date, tagsall, imagelink, groupdescription,
                  filename, groupid=None, **releasedata):
    uploadurl = 'https://sugoimusic.me/upload.php'
    languages = ('Japanese', 'English', 'Korean', 'Chinese', 'Vietnamese')
    data = {
        'submit': 'true',
        'auth': getauthkey(),
        'type': Categories[category],
        # TODO Add feature to request cateogry as parameter as JPS cats do not all = SM cats
        'title': title,
        # 'title_jp': title_jp, #TODO Extract Japanese title
        'idols[]': artist,
        'year': date,
        'media': releasedata['media'],  # releasedata[2]
        'audioformat': releasedata['audioformat'],  # releasedata[0]
        'tags': tagsall,
        'image': imagelink,
        'album_desc': groupdescription,
        # 'release_desc': releasedescription
    }
    if category in VideoCategories:
        data['codec'] = releasedata['codec']
        data['ressel'] = 'Other'
        data['container'] = releasedata['container']
        data['sub'] = 'NoSubs'  # assumed default
        data['lang'] = 'CHANGEME'
        for language in languages:  # If we have language set, set the language field
            if language.lower() in groupdata['tagsall']:
                data['lang'] = language
    else:
        data['bitrate'] = releasedata['bitrate']  # releasedata[1]

    if 'remastertitle' in releasedata.keys():
        data['remaster'] = 'remaster'
        data['remastertitle'] = releasedata['remastertitle']
    if 'remasteryear' in releasedata.keys():
        data['remasteryear'] = releasedata['remasteryear']

    if groupid:
        data['groupid'] = groupid  # Upload torrents into the same group

    postDataFiles = {
        'file_input': open(filename, 'rb')
    }

    if dryrun:
        print(data)
    else:
        SMs = MyLoginSession(SMloginUrl, SMloginData, SMloginTestUrl, SMsuccessStr)
        SMres = SMs.retrieveContent(uploadurl, "post", data, postDataFiles)

        SMerrorTorrent = re.findall('red; text-align: center;">(.*)</p>', SMres.text)
        if SMerrorTorrent:
            dupe = re.findall('torrentid=([0-9]+)">The exact same torrent file already exists on the site!</a>$', SMerrorTorrent[0])
            if dupe:
                raise Exception(f'The exact same torrent file already exists on the site! See: https://sugoimusic.me/torrents.php?torrentid={dupe[0]}')
            else:
                raise Exception(SMerrorTorrent[0])

        SMerrorLogon = re.findall('<p>Invalid (.*)</p>', SMres.text)
        if SMerrorLogon:
            raise Exception(f'Invalid {SMerrorLogon[0]}')

        groupid = re.findall('<input type="hidden" name="groupid" value="(.*)" />', SMres.text)
        if not groupid:
            raise Exception('Error')
        else:
            print('OK - groupid %s' % groupid)

        with open("SMuploadresult." + filename + ".html", "w") as f:
            f.write(str(SMres.content))

    return groupid


def getgroupdata(jpsurl):
    groupdata = {}
    # If there are multiple urls only the first url needs to be parsed
    res = s.retrieveContent(jpsurl.split()[0])

    soup = BeautifulSoup(res.text, 'html5lib')

    artistline = soup.select('.thin h2')
    artistlinelink = soup.select('.thin h2 a')
    text = str(artistline[0])
    print(artistline[0])

    artistlinelinktext = str(artistlinelink[0])

    sqbrackets = re.findall('\[(.*?)\]', text)
    print(sqbrackets)
    groupdata['category'] = sqbrackets[0]

    # Extract date without using '[]' as it allows '[]' elsewhere in the title and it works with JPS TV-* categories
    groupdata['date'] = re.findall('([12]\d{3}\.(?:0[1-9]|1[0-2])\.(?:0[1-9]|[12]\d|3[01]))', text)[0].replace(".", "")

    print(groupdata['category'])
    print(groupdata['date'])

    groupdata['artist'] = re.findall('<a[^>]+>(.*)<', artistlinelinktext)[0]
    print(groupdata['artist'])

    if groupdata['category'] not in TVCategories:
        groupdata['title'] = re.findall('<a.*> - (.*) \[', text)[0]
    else:
        # Using two sets of findall() as I cannot get the OR regex operator "|" to work
        title1 = re.findall('<a.*> - (?:[12]\d{3}\.(?:0[1-9]|1[0-2])\.(?:0[1-9]|[12]\d|3[01])) - (.*)</h2>', text)
        title2 = re.findall('<a.*> - (.*) \((.*) (?:[12]\d{3}\.(?:0[1-9]|1[0-2])\.(?:0[1-9]|[12]\d|3[01]))', text)
        # title1 has 1 matching group, title2 has 2
        titlemerged = [title1, " ".join(itertools.chain(*title2))]
        groupdata['title'] = "".join(itertools.chain(*titlemerged))

    print(groupdata['title'])

    groupdata['rel2'] = str(soup.select('#content .thin .main_column .torrent_table tbody')[0])

    # print rel2
    # fakeurl = 'https://jpopsuki.eu/torrents.php?id=181558&torrentid=251763'
    # fakeurl = 'blah'

    groupdata['groupdescription'] = removehtmltags(str(soup.select('#content .thin .main_column .box .body')[0]))
    print(groupdata['groupdescription'])

    image = str(soup.select('#content .thin .sidebar .box p a'))
    groupdata['imagelink'] = "https://jpopsuki.eu/" + re.findall('<a\s+(?:[^>]*?\s+)?href=\"([^\"]*)\"', image)[0]
    print(groupdata['imagelink'])

    tagsget = str(soup.select('#content .thin .sidebar .box ul.stats.nobullet li'))
    tags = re.findall('searchtags=([^\"]+)', tagsget)
    print(tags)
    groupdata['tagsall'] = ",".join(tags)

    # Try to find torrentid(s) in the url(s) to determine if this is a group url or a specific torrent url(s).
    # groupdata['torrentids'] = re.findall('torrentid=([0-9]+)', jpsurl)

    return groupdata


def collate(torrentids, groupdata):
    groupid = None
    for releasedata, torrentlinkescaped in zip(getreleasedata(groupdata['category'], torrentids),
                                               gettorrentlinks(torrentids)):

        print(releasedata)
        # The collate logic here should probably be moved to getreleasedata() in the future for ease-of-use - collate
        # should be more 'dumb' for improved readability.
        releasedataout = {}
        if groupdata['category'] in VideoCategories:
            # container / media
            # JPS uses the audioformat field for containers and codecs, if we have a known codec or container set as
            # media we can also set the container and codec here.
            badcontainers = ('ISO', 'VOB', 'MPEG', 'AVI', 'MKV', 'WMV', 'MP4')
            badcodecs = ('MPEG2', 'h264')
            if releasedata[0] in badcontainers:
                releasedataout['container'] = releasedata[0]
            else:
                releasedataout['container'] = 'CHANGEME'
            if releasedata[0] in badcodecs:
                releasedataout['codec'] = releasedata[0]
            else:
                releasedataout['codec'] = 'CHANGEME'  # assume default

            releasedataout['media'] = releasedata[1]

            if releasedata[0] == 'AAC':
                releasedataout['audioformat'] == 'AAC'
            else:
                releasedataout['audioformat'] = "CHANGEME"
                
        else:
            # format / bitrate / media
            releasedataout['media'] = releasedata[2]
            releasedataout['audioformat'] = releasedata[0]
            releasedataout['bitrate'] = releasedata[1]

            if releasedataout['audioformat'] == excfilteraudioformat:  # Exclude filters
                print(f'Excluding {releasedata} as exclude audioformat {excfilteraudioformat} is set')
                continue
            elif releasedataout['media'] == excfiltermedia:
                print(f'Excluding {releasedata} as exclude  {excfiltermedia} is set')
                continue

            if len(releasedata) == 4:  # Remastered
                remastertext = re.findall('(.*) - (.*)$', releasedata[3])[0]
                releasedataout['remastertitle'] = remastertext[0]
                # Year is mandatory on JPS so most releases have current year. This looks ugly on SM (and JPS) so if the
                # year is the groupdata['year'] we will not set it.
                year = re.findall('([0-9]{4})(?:.*)', groupdata['date'])[0]
                if year != remastertext[1]:
                    releasedataout['remasteryear'] = remastertext[1]

        if 'WEB' in releasedata:  # Media validation
            releasedataout['media'] = 'Web'
        elif 'Blu-Ray' in releasedata:
            releasedataout['media'] = 'Bluray'  # JPS may actually be calling it the correct official name, but modern usage differs.
            groupdata['category'] = 'Bluray'  # JPS only has a DVD category

        torrentlink = html.unescape(torrentlinkescaped)
        # Download JPS torrent
        torrentfile = s.retrieveContent("https://jpopsuki.eu/%s" % torrentlink)
        torrentfilename = get_valid_filename(
            "JPS %s - %s - %s.torrent" % (groupdata['artist'], groupdata['title'], "-".join(releasedata)))
        with open(torrentfilename, "wb") as f:
            f.write(torrentfile.content)

        # Upload torrent to SM
        # If groupid was returned from a previous call of uploadtorrent() then use it to allow torrents
        # to be uploaded to the same group, else get the groupid from the first run of uploadtorrent()
        if groupid is None:
            # TODO Use **groupdata and refactor uploadtorrent() to use it
            groupid = uploadtorrent(groupdata['category'], groupdata['artist'], groupdata['title'], groupdata['date'],
                                    groupdata['tagsall'], groupdata['imagelink'],
                                    groupdata['groupdescription'], torrentfilename, **releasedataout)
        else:
            uploadtorrent(groupdata['category'], groupdata['artist'], groupdata['title'], groupdata['date'],
                          groupdata['tagsall'], groupdata['imagelink'],
                          groupdata['groupdescription'], torrentfilename, groupid, **releasedataout)


if usermode:
    if batchstart and batchend:
        useruploads = getbulktorrentids(batchuser, batchstart, batchend)
    else:
        useruploads = getbulktorrentids(batchuser)
    useruploadsgrouperrors = collections.defaultdict(list)
    useruploadscollateerrors = collections.defaultdict(list)

    for key, value in useruploads.items():
        groupid = key
        torrentids = value
        try:
            groupdata = getgroupdata("https://jpopsuki.eu/torrents.php?id=%s" % groupid)
        except KeyboardInterrupt:  # Allow Ctrl-C to exit without showing the error multiple times and polluting the final error dict
            raise
        except:
            print('Error with retrieving group data for groupid %s trorrentid(s) %s, skipping upload' % (groupid, ",".join(torrentids)))
            useruploadsgrouperrors[groupid] = torrentids
            continue

        print(groupdata)

        try:
            collate(torrentids, groupdata)
        except KeyboardInterrupt:  # Allow Ctrl-C to exit without showing the error multiple times and polluting the final error dict
            raise
        except:
            print('Error with collating/retrieving release data for groupid %s torrentid(s) %s, skipping upload' % (groupid, ",".join(torrentids)))
            useruploadscollateerrors[groupid] = torrentids
            continue

    if useruploadsgrouperrors:
        print('The following groupid(s) (torrentid(s) shown for reference) had errors in retrieving group data, keep this data safe and you can possibly retry with it in a later version:')
        print(useruploadsgrouperrors)
    if useruploadscollateerrors:
        print('The following groupid(s) and corresponding torrentid(s) had errors either in collating/retrieving release data or in performing the actual upload to SM (although group data was retrieved OK), keep this data safe and you can possibly retry with it in a later version:')
        print(useruploadscollateerrors)

else:
    # Standard non-batch upload using --urls
    groupdata = getgroupdata(jpsurl)
    torrentids = re.findall('torrentid=([0-9]+)', jpsurl)
    collate(torrentids, groupdata)
