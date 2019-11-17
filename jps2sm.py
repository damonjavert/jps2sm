# jps2sm.py is a python script that will automatically gather data from JPS from a given group url, release url,
# or a user's uploaded torrents and iterate through them and upload them to SM.

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
import json
import traceback

# Third-party packages
import requests
from bs4 import BeautifulSoup
from django.utils.text import get_valid_filename

__version__ = "0.9.0"


class MyLoginSession:
    """
    Taken from: https://stackoverflow.com/a/37118451/2115140
    New features added in jps2sm originally by: https://stackoverflow.com/users/1150303/domtomcat

    a class which handles and saves login sessions. It also keeps track of proxy settings.
    It does also maintains a cache-file for restoring session data from earlier
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
                 debug=False,
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
        if res.text.lower().find(self.loginTestString.lower()) < 0:
            if args.debug:
                print(res.text)
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
    """
    Iterates through a users' uploads on JPS and gathers the groupids and corresponding torrentids and returns
    a dict in the format of groupid: [torrentd1, torrentid2, ... ]

    As we add a unique group id as the key this means that all uploads from a user to the same groupid are correlated
    together so that they are uplaoded to the same group by uploadtorrent() even if they were not uploaded to JPS
    at the same time. - uploadtorrent() requires torrents uplaoded to the same group by uploaded together.

    :param user: JSP userid
    :param first: upload page number to start at
    :param last: upload page to finish at
    :return: useruploads: dict
    """
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


def removehtmltags(text):
    """
    Strip html tags, used by GetGroupData() on the group description

    """
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def getauthkey():
    """
    Get SM session authkey for use by uploadtorrent() data dict.
    Uses SM login data

    :return: authkey
    """
    smpage = sm.retrieveContent("https://sugoimusic.me/torrents.php?id=118")  # Arbitrary page on JPS that has authkey
    soup = BeautifulSoup(smpage.text, 'html5lib')
    rel2 = str(soup.select('#content .thin .main_column .torrent_table tbody'))
    authkey = re.findall('authkey=(.*)&amp;torrent_pass=', rel2)
    return authkey


def setorigartist(artist, origartist):
    """
    Set an artist's original artist with the string origartist, currently used for contrib artists
    # TODO Consider using this for main orig artist

    :param artist: string: String of the artist that needs it's original artist set
    :param origartist: string: Original artist
    """
    SMartistpage = sm.retrieveContent(f"https://sugoimusic.me/artist.php?artistname={artist}")
    soup = BeautifulSoup(SMartistpage.text, 'html5lib')
    linkbox = str(soup.select('#content .thin .header .linkbox'))
    artistid = re.findall(r'href="artist\.php\?action=edit&amp;artistid=([0-9]+)"', linkbox)[0]

    data = {
        'action': 'edit',
        'auth': authkey,
        'artistid': artistid,
        'name_jp': origartist
    }

    SMeditartistpage = sm.retrieveContent(f'https://sugoimusic.me/artist.php?artistname={artist}', 'post', data)
    if debug:
        print(f'Set artist {artist} original artist to {origartist}')

def filterlist(string, substr):
    """
    Returns a filtered list where only items containing substr are returned.

    :param string:
    :param substr:
    :return: filteredlist
    """
    return [str for str in string if
            any(sub in str for sub in substr)]


def gettorrentlink(torrentid):
    """
    Extract a torrent link for a given torrentid

    :param torrentid:
    :return: torrentlink: URI of torrent link
    """
    torrentlink = re.findall(rf'torrents\.php\?action=download&amp;id={torrentid}&amp;authkey=(?:[^&]+)&amp;torrent_pass=(?:[^"]+)', torrentgroupdata.rel2)[0]
    return torrentlink


def getreleasedata(torrentids):
    """
    Retrieve all torrent id and release data (slash separated data) whilst coping with 'noise' from FL torrents,
    and either return all data if using a group URL or only return the relevant data if release url(s) were used

    :param torrentids: list of torrentids to be processed
    :return: releasedata: dict of release data in the format of torrentid: slashdata , with 1 sublist for each release
    """
    freeleechtext = '<strong>Freeleech!</strong>'
    slashdata = re.findall(r"swapTorrent\('([0-9]+)'\);\">» (.*)</a>", torrentgroupdata.rel2)
    if debug:
        print(f'Entire group contains: {slashdata}')

    releasedata = {}
    for release in slashdata:
        torrentid = release[0]
        slashlist = ([i.split(' / ') for i in [release[1]]])[0]
        releasedata[torrentid] = slashlist

    removetorrents = []
    for torrentid, release in releasedata.items():
        if len(torrentids) != 0 and torrentid not in torrentids:
            # If len(torrentids) != 0 then user has supplied a group url and every release is processed,
            # otherwise iterate through releasedata{} and remove what is not needed
            removetorrents.append(torrentid)
        if freeleechtext in release:
            release.remove(freeleechtext)  # Remove Freeleech so it does not interfere with Remastered
    for torrentid in removetorrents:
        del(releasedata[torrentid])
    print(f'Selected for upload: {releasedata}')

    return releasedata


def uploadtorrent(filename, groupid=None, **uploaddata):
    """
    Prepare POST data for the SM upload, performs additional validation, reports errors and performs the actual upload to
    SM whilst saving the html result to investigate any errors if they are not reported correctly.

    :param filename: filename of the JPS torrent to be uploaded
    :param groupid: groupid to upload to - allows to upload torrents to the same group
    :param uploaddata: dict of collated / validated release data from collate()
    :return: groupid: groupid used in the upload, used by collate() in case of uploading several torrents to the same group
    """
    uploadurl = 'https://sugoimusic.me/upload.php'
    languages = ('Japanese', 'English', 'Korean', 'Chinese', 'Vietnamese')
    data = {
        'submit': 'true',
        'type': Categories[torrentgroupdata.category],
        # TODO Add feature to request category as parameter as JPS cats do not all = SM cats
        #  ^^ will probably never need to do this now due to improved validation logic
        'title': torrentgroupdata.title,
        'year': torrentgroupdata.date,
        'media': uploaddata['media'],
        'audioformat': uploaddata['audioformat'],
        'tags': torrentgroupdata.tagsall,
        'image': torrentgroupdata.imagelink,
        'album_desc': torrentgroupdata.groupdescription,
        # 'release_desc': releasedescription
    }
    if not dryrun:
        data['auth'] = authkey

    if debug:
        print(uploaddata)

    if uploaddata['videotorrent']:
        if Categories[torrentgroupdata.category] == "DVD" and uploaddata['media'] == 'Bluray':
            data['type'] = 'Bluray'  # JPS has no Bluray category
        data['codec'] = uploaddata['codec']
        data['ressel'] = 'Other'
        data['container'] = uploaddata['container']
        data['sub'] = 'NoSubs'  # assumed default
        data['lang'] = 'CHANGEME'
        for language in languages:  # If we have a language tag, set the language field
            if language.lower() in torrentgroupdata.tagsall:
                data['lang'] = language
    else:
        data['bitrate'] = uploaddata['bitrate']

    if 'remastertitle' in uploaddata.keys():
        data['remaster'] = 'remaster'
        data['remastertitle'] = uploaddata['remastertitle']
    if 'remasteryear' in uploaddata.keys():
        data['remasteryear'] = uploaddata['remasteryear']

    if groupid:
        data['groupid'] = groupid  # Upload torrents into the same group

    try:
        data['artist_jp'], data['title_jp'] = torrentgroupdata.originalchars()
    except AttributeError:  # If no originalchars do nothing
        pass

    try:
        contribartistsenglish = []
        for artist, origartist in torrentgroupdata.contribartists.items():
            contribartistsenglish.append(artist)
        data['contrib_artists[]'] = contribartistsenglish
    except AttributeError:  # If no contrib artists do nothing
        pass

    if torrentgroupdata.artist == "V.A.":  # At JPS Various Artists torrents have their artists as contrib artists
        # TODO Recognise torrents that have >4 artists and keep them as contrib artists, this probably requires
        # a Gazelle code change to handle torrent groups with no main artist
        del data['contrib_artists[]']  # Error if null as if there is a V.A. torrent group with no contrib artists something is wrong
        data['idols[]'] = contribartistsenglish
        if debug:
            print(f'Various Artists torrent, setting main artists to {contribartistsenglish}')
    else:
        data['idols[]'] = torrentgroupdata.artist  # Set the artist normally

    postDataFiles = {
        'file_input': open(filename, 'rb')
    }

    if dryrun or debug:
        print(json.dumps(data, indent=2))
    if not dryrun:
        SMres = sm.retrieveContent(uploadurl, "post", data, postDataFiles)

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
            print(f'OK - groupid {groupid[0]}')

        with open("SMuploadresult." + filename + ".html", "w") as f:
            f.write(str(SMres.content))

    return groupid


class GetGroupData:
    """
    Retrieve group data of the group supplied from jpsurl
    Group data is defined as data that is constant for every release, eg category, artist, title, groupdescription, tags etc.
    Each property is gathered by calling a method of the class
    """
    def __init__(self, jpsurl):
        self.jpsurl = jpsurl

        self.getdata(jpsurl)

    def getdata(self, jpsurl):
        res = s.retrieveContent(self.jpsurl.split()[0])  # If there are multiple urls only the first url needs to be parsed

        soup = BeautifulSoup(res.text, 'html5lib')
        #soup = BeautifulSoup(open("1830.html"), 'html5lib')

        artistline = soup.select('.thin h2')
        artistlinelink = soup.select('.thin h2 a')
        originaltitleline = soup.select('.thin h3')
        text = str(artistline[0])
        print(artistline[0])

        artistlinelinktext = str(artistlinelink[0])

        sqbrackets = re.findall('\[(.*?)\]', text)
        print(sqbrackets)
        self.category = sqbrackets[0]

        # Extract date without using '[]' as it allows '[]' elsewhere in the title and it works with JPS TV-* categories
        self.date = re.findall('([12]\d{3}\.(?:0[1-9]|1[0-2])\.(?:0[1-9]|[12]\d|3[01]))', text)[0].replace(".", "")

        print(self.category)
        print(self.date)

        self.artist = re.findall('<a[^>]+>(.*)<', artistlinelinktext)[0]
        print(self.artist)

        if self.category not in TVCategories:
            self.title = re.findall('<a.*> - (.*) \[', text)[0]
        else:
            # Using two sets of findall() as I cannot get the OR regex operator "|" to work
            title1 = re.findall('<a.*> - (?:[12]\d{3}\.(?:0[1-9]|1[0-2])\.(?:0[1-9]|[12]\d|3[01])) - (.*)</h2>', text)
            title2 = re.findall('<a.*> - (.*) \((.*) (?:[12]\d{3}\.(?:0[1-9]|1[0-2])\.(?:0[1-9]|[12]\d|3[01]))', text)
            # title1 has 1 matching group, title2 has 2
            titlemerged = [title1, " ".join(itertools.chain(*title2))]
            self.title = "".join(itertools.chain(*titlemerged))

        print(self.title)
        try:
            originalchars = re.findall(r'<a href="artist.php\?id=(?:[0-9]+)">(.+)</a> - (.+)\)</h3>', str(originaltitleline))[0]
            self.originalartist = originalchars[0]
            self.originaltitle = originalchars[1]
            print(f"Original artist: {self.originalartist} Original title: {self.originaltitle}")
        except IndexError:  # Do nothing if group has no original artist/title
            pass

        self.rel2 = str(soup.select('#content .thin .main_column .torrent_table tbody')[0])

        # print rel2
        # fakeurl = 'https://jpopsuki.eu/torrents.php?id=181558&torrentid=251763'
        # fakeurl = 'blah'

        self.groupdescription = removehtmltags(str(soup.select('#content .thin .main_column .box .body')[0]))
        print(f"Group description:\n{self.groupdescription}")

        image = str(soup.select('#content .thin .sidebar .box p a'))
        self.imagelink = "https://jpopsuki.eu/" + re.findall('<a\s+(?:[^>]*?\s+)?href=\"([^\"]*)\"', image)[0]
        print(self.imagelink)

        tagsget = str(soup.select('#content .thin .sidebar .box ul.stats.nobullet li'))
        tags = re.findall('searchtags=([^\"]+)', tagsget)
        print(tags)
        self.tagsall = ",".join(tags)

        try:
            contribartistsget = str(soup.select('#content .thin .sidebar .box .body ul.stats.nobullet li'))
            contribartistslist = re.findall(r'<li><a href="artist\.php\?id=(?:[0-9]+?)" title="(.*?)">([\w ]+)</a>', contribartistsget)
            self.contribartists = {}
            for artistpair in contribartistslist:
                self.contribartists[artistpair[1]] = artistpair[0] # Creates contribartists[artist] = origartist

            print(f'Contributing artists: {self.contribartists}')
        except IndexError:  # Do nothing if group has no contrib artists
            pass

    def category(self):
        return self.category()

    def date(self):
        return self.date()

    def artist(self):
        return self.artist()

    def title(self):
        return self.title()

    def originalchars(self):
        return self.originalartist, self.originaltitle

    def rel2(self):
        return self.rel2()

    def groupdescription(self):
        return self.groupdescription()

    def imagelink(self):
        return self.imagelink()

    def tagsall(self):
        return self.tagsall()

    def contribartists(self):
        return self.contribartists


def collate(torrentids):
    """
    Collate and validate data ready for upload to SM

    Validate and process dict supplied by getreleasedata() with format, bitrate, media, container, codec, and remaster data to extract all available data from JPS
    Perform validation on some fields
    Download JPS torrent
    Apply filters
    Send data to uploadtorrent()

    :param torrentids: list of JPS torrentids to be processed
    :param groupdata: dictionary with torrent group data from getgroupdata[]
    """
    groupid = None
    for torrentid, releasedata in getreleasedata(torrentids).items():

        print(f'Now processing: {torrentid} {releasedata}')

        releasedataout = {}

        # JPS uses the audioformat field (represented as releasedata[0] here) for containers and codecs in video torrents,
        # and when combined with VideoMedias we can perform VideoTorrent detection.
        VideoMedias = ('DVD', 'Blu-Ray', 'VHS', 'VCD', 'TV', 'HDTV', 'WEB')
        badcontainers = ('ISO', 'VOB', 'MPEG', 'AVI', 'MKV', 'WMV', 'MP4')
        badcodecs = ('MPEG2', 'h264')
        badformats = badcontainers + badcodecs
        if releasedata[0] in badformats and releasedata[1] in VideoMedias:  # VideoCategory torrent, this also detects VideoCategories in a non-VC group
            # container / media
            releasedataout['videotorrent'] = True  # For processing by uploadtorrent()
            # If a known container is used as audioformat set it as the container on SM
            if releasedata[0] in badcontainers:
                releasedataout['container'] = releasedata[0]
            else:
                releasedataout['container'] = 'CHANGEME'
            # If a known codec is used as audioformat set it as the codec on SM
            if releasedata[0] in badcodecs:
                if releasedata[0] == "MPEG2":  # JPS uses 'MPEG2' for codec instead of the correct 'MPEG-2'
                    releasedataout['codec'] = "MPEG-2"
                else:
                    releasedataout['codec'] = releasedata[0]
            else:
                releasedataout['codec'] = 'CHANGEME'  # assume default

            releasedataout['media'] = releasedata[1]

            if releasedata[0] != 'AAC':  # For video torrents, the only correct audioformat is AAC
                releasedataout['audioformat'] = "CHANGEME"

            if len(releasedata) == 3:  # Remastered
                remasterdata = releasedata[2]
            else:
                remasterdata = False

        else:
            # format / bitrate / media
            releasedataout['videotorrent'] = False

            releasedataout['media'] = releasedata[2]
            releasedataout['audioformat'] = releasedata[0]

            if releasedata[1].startswith('24bit'):
                releasedataout['bitrate'] = '24bit Lossless'
            else:
                releasedataout['bitrate'] = releasedata[1]

            if releasedataout['audioformat'] == excfilteraudioformat:  # Exclude filters
                print(f'Excluding {releasedata} as exclude audioformat {excfilteraudioformat} is set')
                continue
            elif releasedataout['media'] == excfiltermedia:
                print(f'Excluding {releasedata} as exclude  {excfiltermedia} is set')
                continue

            if len(releasedata) == 4:  # Remastered
                remasterdata = releasedata[3]
            else:
                remasterdata = False

        if remasterdata:
            remastertext = re.findall('(.*) - (.*)$', remasterdata)[0]  # TODO Handle when there is year but no edition data
            releasedataout['remastertitle'] = remastertext[0]
            # Year is mandatory on JPS so most releases have current year. This looks ugly on SM (and JPS) so if the
            # year is the groupdata['year'] we will not set it.
            year = re.findall('([0-9]{4})(?:.*)', torrentgroupdata.date)[0]
            if year != remastertext[1]:
                releasedataout['remasteryear'] = remastertext[1]

        if 'WEB' in releasedata:  # Media validation
            releasedataout['media'] = 'Web'
        elif 'Blu-Ray' in releasedata:
            releasedataout['media'] = 'Bluray'  # JPS may actually be calling it the correct official name, but modern usage differs.

        torrentlink = html.unescape(gettorrentlink(torrentid))

        torrentfile = s.retrieveContent("https://jpopsuki.eu/%s" % torrentlink)  # Download JPS torrent
        torrentfilename = get_valid_filename(
            "JPS %s - %s - %s.torrent" % (torrentgroupdata.artist, torrentgroupdata.title, "-".join(releasedata)))
        with open(torrentfilename, "wb") as f:
            f.write(torrentfile.content)

        # Upload torrent to SM
        # If groupid was returned from a previous call of uploadtorrent() then use it to allow torrents
        # to be uploaded to the same group, else get the groupid from the first run of uploadtorrent()
        if groupid is None:
            groupid = uploadtorrent(torrentfilename, **releasedataout)
        else:
            uploadtorrent(torrentfilename, groupid, **releasedataout)

    if not dryrun:
        # Add original artists for contrib artists
        if torrentgroupdata.contribartists:
            for artist, origartist in torrentgroupdata.contribartists.items():
                # For every artist, go to its artist page to get artist ID, then use this to go to artist.php?action=edit with the orig artist
                setorigartist(artist, origartist)


if __name__ == "__main__":
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

    s = MyLoginSession(loginUrl, loginData, loginTestUrl, successStr, debug=args.debug)

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
        'Bluray', 'DVD', 'PV', 'TV-Music', 'TV-Variety', 'TV-Drama', 'Music Performance']

    TVCategories = [
        'TV-Music', 'TV-Variety', 'TV-Drama']

    if not dryrun:
        sm = MyLoginSession(SMloginUrl, SMloginData, SMloginTestUrl, SMsuccessStr, debug=args.debug)
        authkey = getauthkey()  # We only want this run ONCE per instance of the script

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
                torrentgroupdata = GetGroupData("https://jpopsuki.eu/torrents.php?id=%s" % groupid)
            except KeyboardInterrupt:  # Allow Ctrl-C to exit without showing the error multiple times and polluting the final error dict
                raise
            except Exception as exc:
                print('Error with retrieving group data for groupid %s trorrentid(s) %s, skipping upload' % (groupid, ",".join(torrentids)))
                useruploadsgrouperrors[groupid] = torrentids
                if debug:
                    print(exc)
                    traceback.print_exc()
                continue

            try:
                collate(torrentids)
            except KeyboardInterrupt:  # Allow Ctrl-C to exit without showing the error multiple times and polluting the final error dict
                raise
            except Exception as exc:
                print('Error with collating/retrieving release data for groupid %s torrentid(s) %s, skipping upload' % (groupid, ",".join(torrentids)))
                useruploadscollateerrors[groupid] = torrentids
                if debug:
                    print(exc)
                    traceback.print_exc()
                continue

        if useruploadsgrouperrors:
            print('The following groupid(s) (torrentid(s) shown for reference) had errors in retrieving group data, '
                  'keep this data safe and you can possibly retry with it in a later version:')
            print(useruploadsgrouperrors)
        if useruploadscollateerrors:
            print('The following groupid(s) and corresponding torrentid(s) had errors either in collating/retrieving '
                  'release data or in performing the actual upload to SM (although group data was retrieved OK), '
                  'keep this data safe and you can possibly retry with it in a later version:')
            print(useruploadscollateerrors)

    else:
        # Standard non-batch upload using --urls
        torrentgroupdata = GetGroupData(jpsurl)
        torrentids = re.findall('torrentid=([0-9]+)', jpsurl)
        collate(torrentids)

