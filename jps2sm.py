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
import torrent_parser as tp
from pymediainfo import MediaInfo
import humanfriendly

__version__ = "1.2"


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


def getbulktorrentids(mode, user, first=1, last=None):
    """
    Iterates through a users' uploads on JPS and gathers the groupids and corresponding torrentids and returns
    a dict in the format of groupid: [torrentd1, torrentid2, ... ]

    As we add a unique group id as the key this means that all uploads from a user to the same groupid are correlated
    together so that they are uplaoded to the same group by uploadtorrent() even if they were not uploaded to JPS
    at the same time. - uploadtorrent() requires torrents uplaoded to the same group by uploaded together.

    :param mode: Area to get bulk torrent ids from, either 'uploaded' for a user's uploads or 'seeding' for torrents currently seeding
    :param user: JPS userid
    :param first: upload page number to start at
    :param last: upload page to finish at
    :return: useruploads: dict
    """
    res = s.retrieveContent(f"https://jpopsuki.eu/torrents.php?type={mode}&userid={user}")
    soup = BeautifulSoup(res.text, 'html5lib')

    linkbox = str(soup.select('#content #ajax_torrents .linkbox')[0])
    if not last:
        try:
            last = re.findall(fr'page=([0-9]*)&amp;order_by=s3&amp;order_way=DESC&amp;type={mode}&amp;userid=(?:[0-9]*)&amp;disablegrouping=1\'\);"><strong> Last &gt;&gt;</strong>', linkbox)[0]
        except:
            # There is only 1 page of uploads if the 'Last >>' link cannot be found
            last = 1

    if debug:
        print(f'Batch user is {user}, batch mode is {mode}, first page is {first}, last page is {last}')

    useruploads = {}
    useruploads = collections.defaultdict(list)

    # Parse every torrent page and add to dict, to group together releases into the same group so that they work with
    # the way that uploadtorrent() works.
    for i in range(first, int(last) + 1):
        useruploadpage = s.retrieveContent(fr"https://jpopsuki.eu/torrents.php?page=%s&order_by=s3&order_way=DESC&type={mode}&userid=%s&disablegrouping=1" % (i, user))
        print(f"https://jpopsuki.eu/torrents.php?page=%s&order_by=s3&order_way=DESC&type={mode}&userid=%s&disablegrouping=1" % (i, user))
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


def decide_music_performance(artist, multiplefiles, duration):
    """
    Return if upload should be a Music Performance or not
    A music performance is a cut from a Music TV show and is 25 mins or less long and therefore also not a TV Show artist

    We assume we are being called if Cat = TV Music

    :return:  str: 'Music Performance' or 'TV Music'
    """
    if multiplefiles is True or duration > 1500000:  # 1 500 000 ms = 25 mins
        return 'TV Music'
    else:  # Single file that is < 25 mins, decide if Music Performance
        JPSartistpage = s.retrieveContent(f"https://jpopsuki.eu/artist.php?name={artist}")
        soup = BeautifulSoup(JPSartistpage.text, 'html5lib')
        categoriesbox = str(soup.select('#content .thin .main_column .box.center'))
        categories = re.findall(r'\[(.+)\]', categoriesbox)
        if any({*Categories.NonTVCategories} & {*categories}):  # Exclude any TV Shows for being mislabeled as Music Performance
            if debug:
                print('Upload is a Music Performance as it is 25 mins or less and not a TV Show')
            return 'Music Performance'
        else:
            return 'TV Music'


def getalternatefansubcategoryid(artist):
    """
    Attempts to detect the actual category for JPS Fansubs category torrents and if not ask the user to select an alternate category.
    If it is a TV show, this TV show category type is detected and returned, else query the user from a list of potential categories.

    :param artist: str artist name
    :return: int alternative category ID based on Categories.SM()
    """
    JPSartistpage = s.retrieveContent(f"https://jpopsuki.eu/artist.php?name={artist}")
    soup = BeautifulSoup(JPSartistpage.text, 'html5lib')
    categoriesbox = str(soup.select('#content .thin .main_column .box.center'))
    categories = re.findall(r'\[(.+)\]', categoriesbox)

    if not any({*Categories.NonTVCategories} & {*categories}) and " ".join(categories).count('TV-') == 1:
        # Artist has no music and only 1 TV Category, artist is a TV show and we can auto detect the category for FanSub releases
        autodetectcategory = re.findall(r'(TV-(?:[^ ]+))', " ".join(categories))[0]
        if debug:
            print(f'Autodetected SM category {autodetectcategory} for JPS Fansubs torrent')
        return autodetectcategory
    else:  # Cannot autodetect
        AlternateFanSubCategoriesIDs = (5, 6, 7, 8, 9)  #Matches indices in Categories()
        print(f'Cannot auto-detect correct category for torrent group {torrentgroupdata.title}.\nSelect Category:')
        option = 1
        optionlookup = {}
        for alternativefansubcategoryid in AlternateFanSubCategoriesIDs:
            for cat, catid in Categories.SM.items():
                if alternativefansubcategoryid == catid:
                    print(f'({option}) {cat}')
                    optionlookup[option] = alternativefansubcategoryid
                    option += 1
        alternatecategoryoption = input('Choose alternate category or press ENTER to skip: ')
        if alternatecategoryoption == "":
            return "Fansubs"  # Allow upload to fail
        else:
            return optionlookup[int(alternatecategoryoption)]


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
    Retrieve all torrent id and release data (slash separated data and upload date) whilst coping with 'noise' from FL torrents,
    and either return all data if using a group URL or only return the relevant releases if release url(s) were used

    :param torrentids: list of torrentids to be processed, NULL if group is used
    :return: releasedata: 2d dict of release data in the format of torrentid: { "slashdata" : [ slashdatalist ] , "uploaddate": uploaddate } .
    """

    freeleechtext = '<strong>Freeleech!</strong>'
    releasedatapre = re.findall(r"swapTorrent\('([0-9]+)'\);\">» (.*?)</a>.*?<blockquote>(?:\s*)Uploaded by <a href=\"user.php\?id=(?:[0-9]+)\">(?:[\S]+)</a>  on <span title=\"(?:[^\"]+)\">([^<]+)</span>", torrentgroupdata.rel2, re.DOTALL)
    # if debug:
    #     print(f'Pre-processed releasedata: {json.dumps(releasedatapre, indent=2)}')

    releasedata = {}
    for release in releasedatapre:
        torrentid = release[0]
        slashlist = ([i.split(' / ') for i in [release[1]]])[0]
        uploadeddate = release[2]
        releasedata[torrentid] = {}
        releasedata[torrentid]['slashdata'] = slashlist
        releasedata[torrentid]['uploaddate'] = uploadeddate

    if debug:
        print(f'Entire group contains: {json.dumps(releasedata, indent=2)}')

    removetorrents = []
    for torrentid, release in releasedata.items():  # Now release is a dict!
        if len(torrentids) != 0 and torrentid not in torrentids:
            # If len(torrentids) != 0 then user has supplied a group url and every release is processed,
            # otherwise iterate through releasedata{} and remove what is not needed
            removetorrents.append(torrentid)
        if freeleechtext in release['slashdata']:
            release['slashdata'].remove(freeleechtext)  # Remove Freeleech so it does not interfere with Remastered
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

    if torrentgroupdata.date is None:  # If release date cannot be derived use upload date
        date = uploaddata['uploaddate']
    else:
        date = torrentgroupdata.date

    data = {
        'submit': 'true',
        'title': torrentgroupdata.title,
        'year': date,
        'tags': torrentgroupdata.tagsall,
        'album_desc': torrentgroupdata.groupdescription,
        # 'release_desc': releasedescription
    }

    if not dryrun:
        data['auth'] = authkey

    if debug:
        print(uploaddata)

    if args.mediainfo:
        data['mediainfo'], releasedatamediainfo = getmediainfo(filename)
        data.update(releasedatamediainfo)
        if 'duration' in data.keys():
            duration_friendly_format = humanfriendly.format_timespan(datetime.timedelta(seconds=int(data['duration']/1000)))
            data['album_desc'] += f"\n\nDuration: {duration_friendly_format}"

    if torrentgroupdata.category not in Categories.NonReleaseData:
        data['media'] = uploaddata['media']
        if 'audioformat' not in data.keys():  # If not supplied by getmediainfo() use audioformat guessed by collate()
            data['audioformat'] = uploaddata['audioformat']

    if torrentgroupdata.imagelink is not None:
        data['image'] = torrentgroupdata.imagelink

    if uploaddata['videotorrent']:
        if torrentgroupdata.category == "DVD" and uploaddata['media'] == 'Bluray':
            data['type'] = Categories.JPStoSM['Bluray']  # JPS has no Bluray category
        if uploaddata['categorystatus'] == 'bad':  # Need to set a correct category
            if uploaddata['media'] == 'Bluray':
                data['type'] = Categories.JPStoSM['Bluray']
            else:  # Still need to change the category to something, if not a Bluray then even if it is not a DVD the most sensible category is DVD in a music torrent group
                data['type'] = Categories.JPStoSM['DVD']
        if torrentgroupdata.category == "TV-Music" and args.mediainfo:
            data['type'] = Categories.JPStoSM[decide_music_performance(torrentgroupdata.artist, data['multiplefiles'], data['duration'])]

        # If not supplied by getmediainfo() use codec found by collate()
        if 'codec' not in data.keys():
            data['codec'] = uploaddata['codec']

        # If not supplied by getmediainfo() try to detect resolution by searching the group description for resolutions
        if 'ressel' not in data.keys():
            foundresolutions720 = re.findall('1080 ?x ?720', torrentgroupdata.groupdescription)
            foundresolutions1080 = re.findall('1920 ?x ?1080', torrentgroupdata.groupdescription)
            if len(foundresolutions720) != 0:
                data['ressel'] = "720p"
            elif len(foundresolutions1080) != 0:
                data['ressel'] = "1080p"
            for resolution in VideoOptions.resolutions:  # Now set more specific resolutions if they are present
                if resolution in torrentgroupdata.groupdescription:  # If we can see the resolution in the group description then set it
                    data['ressel'] = resolution
                else:
                    data['ressel'] = 'CHANGEME'

        if 'container' not in data.keys():
            data['container'] = uploaddata['container']

        data['sub'] = 'NoSubs'  # assumed default
        data['lang'] = 'CHANGEME'
        for language in languages:  # If we have a language tag, set the language field
            if language.lower() in torrentgroupdata.tagsall:
                data['lang'] = language
    elif torrentgroupdata.category not in Categories.NonReleaseData:  # Music Category torrent
        data['bitrate'] = uploaddata['bitrate']

    if 'remastertitle' in uploaddata.keys():
        data['remaster'] = 'remaster'
        data['remastertitle'] = uploaddata['remastertitle']
    if 'remasteryear' in uploaddata.keys():
        data['remaster'] = 'remaster'
        data['remasteryear'] = uploaddata['remasteryear']

    # Non-BR/DVD/TV-* category validation
    # TODO Move this to a def
    if torrentgroupdata.category == "Fansubs":
        data['type'] = getalternatefansubcategoryid(torrentgroupdata.artist)
        data['sub'] = 'Hardsubs'  # We have subtitles! Subs in JPS FanSubs are usually Hardsubs so guess as this
        # TODO: Use torrent library to look for sub/srt files
    elif torrentgroupdata.category == "Album":  # Ascertain if upload is EP
        data['type'] = Categories.JPStoSM[decide_ep(filename)]

    if 'type' not in data.keys():  # Set default value after all validation has been done
        data['type'] = Categories.JPStoSM[torrentgroupdata.category]

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
        dataexcmediainfo = {x: data[x] for x in data if x not in 'mediainfo'}
        print(json.dumps(dataexcmediainfo, indent=2))  # Mediainfo shows too much data
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
        date_regex = r'[12]\d{3}\.(?:0[1-9]|1[0-2])\.(?:0[1-9]|[12]\d|3[01])'  # YYYY.MM.DD format

        res = s.retrieveContent(self.jpsurl.split()[0])  # If there are multiple urls only the first url needs to be parsed

        soup = BeautifulSoup(res.text, 'html5lib')
        #soup = BeautifulSoup(open("1830.html"), 'html5lib')

        artistline = soup.select('.thin h2')
        artistlinelink = soup.select('.thin h2 a')
        originaltitleline = soup.select('.thin h3')
        text = str(artistline[0])
        if debug:
            print(artistline[0])

        sqbrackets = re.findall('\[(.*?)\]', text)
        self.category = sqbrackets[0]
        print(self.category)

        try:
            artistlinelinktext = str(artistlinelink[0])
            self.artist = re.findall('<a[^>]+>(.*)<', artistlinelinktext)[0]
            print(f'Artist: {self.artist}')
        except IndexError:  # Cannot find artist
            if self.category == "Pictures":
                # JPS allows Picture torrents to have no artist set, in this scenario try to infer the artist by examining the text
                # immediately after the category string up to a YYYY.MM.DD string if available as this should be the magazine title
                self.artist = re.findall(fr'\[Pictures\] ([A-Za-z ]+) (?:{date_regex})', text)
            else:
                print('JPS upload appears to have no artist set and artist cannot be autodetected')
                raise


        # Extract date without using '[]' as it allows '[]' elsewhere in the title and it works with JPS TV-* categories
        try:
            self.date = re.findall(date_regex, text)[0].replace(".", "")
        except IndexError:  # Handle YYYY dates, creating extra regex as I cannot get it working without causing issue #33
            try:
                self.date = re.findall(r'[^\d]((?:19|20)\d{2})[^\d]', text)[0]
            
            # Handle if cannot find date in the title, use upload date instead from getreleasedata() but error if the category should have it
            except IndexError as dateexc:
                if self.category not in Categories.NonDate:
                    print(f'Group release date not found and not using upload date instead as {self.category} torrents should have it set')
                    if debug:
                        print(dateexc)
                        traceback.print_exc()
                if debug:
                    print('Date not found from group data, will use upload date as the release date')
                self.date = None
                pass

        print(f'Release date: {self.date}')

        if self.category not in Categories.NonDate:
            self.title = re.findall('<a.*> - (.*) \[', text)[0]
        else:
            # Using two sets of findall() as I cannot get the OR regex operator "|" to work
            title1 = re.findall('<a.*> - (?:[12]\d{3}\.(?:0[1-9]|1[0-2])\.(?:0[1-9]|[12]\d|3[01])) - (.*)</h2>', text)
            title2 = re.findall('<a.*> - (.*) \((.*) (?:[12]\d{3}\.(?:0[1-9]|1[0-2])\.(?:0[1-9]|[12]\d|3[01]))', text)
            # title1 has 1 matching group, title2 has 2
            titlemergedpre = [title1, " ".join(itertools.chain(*title2))]
            titlemerged = "".join(itertools.chain(*titlemergedpre))
            if len(titlemerged) == 0:  # Non standard title, fallback on the whole string after the "-"
                try:
                    self.title = re.findall('<a.*> - (.*)</h2>', text)[0]
                except IndexError:  # Pictures non-artist upload - for magazines
                    if self.category == "Pictures":
                        # Fallback to all the text after the category, we need to include the date stamp as magazines are often titled
                        # with the same numbers each year - the first magazine each year appears to always be 'No. 1' for example
                        self.title = re.findall(fr'\[Pictures\] (?:[A-Za-z ]+) ({date_regex} .+)</h2>', text)[0]
                    else:
                        print('Cannot find title from the JPS upload')
                        raise
            else:
                self.title = titlemerged

        print(f'Title: {self.title}')
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
        try:
            self.imagelink = "https://jpopsuki.eu/" + re.findall('<a\s+(?:[^>]*?\s+)?href=\"([^\"]*)\"', image)[0]
            print(self.imagelink)
        except IndexError:  # No image for the group
            self.imagelink = None

        tagsget = str(soup.select('#content .thin .sidebar .box ul.stats.nobullet li'))
        tags = re.findall('searchtags=([^\"]+)', tagsget)
        print(tags)
        self.tagsall = ",".join(tags)

        try:
            contribartistsget = str(soup.select('#content .thin .sidebar .box .body ul.stats.nobullet li'))
            contribartistslist = re.findall(r'<li><a href="artist\.php\?id=(?:[0-9]+?)" title="([^"]+?)">([\w ]+)</a>', contribartistsget)
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


def validatejpsvideodata(releasedata, categorystatus):
    """
    Validate and process dict supplied by getreleasedata() via collate() to extract all available data
    from JPS for video torrents, whilst handling weird cases where VideoTorrent is uploaded as a Music category

    :param releasedata:
    :param categorystatus: str: good or bad. good for correct category assigned and bad if this is a Music Torrent
    mistakenly uploaded as a non-VC category!
    :return: releasedataout{} validated container, codec, media, audioformat
    """
    releasedataout = {}
    # JPS uses the audioformat field (represented as releasedata[0] here) for containers and codecs in video torrents

    # If a known container is used as audioformat set it as the container on SM
    if releasedata[0] in VideoOptions.badcontainers:
        releasedataout['container'] = releasedata[0]
    else:
        releasedataout['container'] = 'CHANGEME'
    # If a known codec is used as audioformat set it as the codec on SM
    if releasedata[0] in VideoOptions.badcodecs:
        if releasedata[0] == "MPEG2":  # JPS uses 'MPEG2' for codec instead of the correct 'MPEG-2'
            releasedataout['codec'] = "MPEG-2"
        else:
            releasedataout['codec'] = releasedata[0]
    else:
        releasedataout['codec'] = 'CHANGEME'  # assume default

    if categorystatus == "good":
        releasedataout['media'] = releasedata[1]
    else:
        releasedataout['media'] = releasedata[2]

    if releasedata[0] == 'AAC':  # For video torrents, the only correct audioformat in JPS is AAC
        releasedataout['audioformat'] = "AAC"
    else:
        releasedataout['audioformat'] = "CHANGEME"

    return releasedataout


def collate(torrentids):
    """
    Collate and validate data ready for upload to SM

    Validate and process dict supplied by getreleasedata() with format, bitrate, media, container, codec, and remaster data to extract
    all available data from JPS
    Perform validation on some fields
    Download JPS torrent
    Apply filters
    Send data to uploadtorrent()
    Send data to setorigartists()

    :param torrentids: list of JPS torrentids to be processed
    :param groupdata: dictionary with torrent group data from getgroupdata[]
    """
    groupid = None
    torrentcount = 0
    for torrentid, releasedatafull in getreleasedata(torrentids).items():

        torrentcount += 1
        print(f'Now processing: {torrentid} {releasedatafull}')

        releasedata = releasedatafull['slashdata']
        uploaddatestr = releasedatafull['uploaddate']
        releasedataout = {}

        # JPS uses the audioformat field (represented as releasedata[0] here) for containers and codecs in video torrents,
        # and when combined with VideoMedias we can perform VideoTorrent detection.
        if releasedata[0] in VideoOptions.badformats and releasedata[1] in VideoOptions.VideoMedias:  # VideoCategory torrent, this also detects VideoCategories in a non-VC group
            # container / media
            releasedataout['videotorrent'] = True  # For processing by uploadtorrent()
            releasedataout['categorystatus'] = "good"

            videoreleasedatavalidated = validatejpsvideodata(releasedata, releasedataout['categorystatus'])
            for field, data in videoreleasedatavalidated.items():
                releasedataout[field] = data

            if len(releasedata) == 3:  # Remastered
                remasterdata = releasedata[2]
            else:
                remasterdata = False

        elif releasedata[0] in VideoOptions.badformats and releasedata[2] in VideoOptions.VideoMedias:  # Video torrent mistakenly uploaded as an Album/Single
            # container / 'bitrate' / media   Bitrate is meaningless, users usually select Lossless
            releasedataout['videotorrent'] = True  # For processing by uploadtorrent()
            releasedataout['categorystatus'] = "bad"

            videoreleasedatavalidated = validatejpsvideodata(releasedata, releasedataout['categorystatus'])
            for field, data in videoreleasedatavalidated.items():
                releasedataout[field] = data

            if len(releasedata) == 4:  # Remastered
                remasterdata = releasedata[3]
            else:
                remasterdata = False

        elif torrentgroupdata.category not in Categories.NonReleaseData:  # Music torrent  
            # format / bitrate / media
            releasedataout['videotorrent'] = False
            releasedataout['categorystatus'] = "good"
            
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

        elif torrentgroupdata.category in Categories.NonReleaseData:  # Pictures or Misc Category torrents
            releasedataout['videotorrent'] = False
            releasedataout['categorystatus'] = "good"
            remasterdata = False

        if remasterdata:
            try:
                remastertext = re.findall('(.*) - (.*)$', remasterdata)[0]
                releasedataout['remastertitle'] = remastertext[0]
                remasteryear = remastertext[1]
            except IndexError:  # Torrent is remastered and only has year set
                remasteryear = remasterdata  # The whole string is just the year

            # Year is mandatory on JPS so most remastered releases have current year set as year. This looks ugly on SM (and JPS) so if the
            # year is the groupdata['year'] we will not set it.
            year = re.findall('([0-9]{4})(?:.*)', torrentgroupdata.date)[0]
            if year != remasteryear:
                releasedataout['remasteryear'] = remasteryear

        if 'WEB' in releasedata:  # Media validation
            releasedataout['media'] = 'Web'
        elif 'Blu-Ray' in releasedata:
            releasedataout['media'] = 'Bluray'  # JPS may actually be calling it the correct official name, but modern usage differs.

        # uploadtorrent() will use the upload date as release date if the torrent has no release date, usually for
        # Picture Category torrents and some TV-Variety.
        releasedataout['uploaddate'] = datetime.datetime.strptime(uploaddatestr, '%b %d %Y, %H:%M').strftime('%Y%m%d')

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

    return torrentcount  # For use by downloaduploadedtorrents()


def downloaduploadedtorrents(torrentcount):
    """
    Get last torrentcount torrent DL links that user uploaded using SM API and download them

    :param torrentcount: count of recent torrent links to be downloaded
    :return:
    """

    if torrentcount == 0:
        return

    user_recents = sm.retrieveContent(f"https://sugoimusic.me/ajax.php?action=user_recents&limit={torrentcount}")
    user_recents_json = json.loads(user_recents.text)

    smtorrentlinks = {}
    for torrentdata in user_recents_json['response']['uploads']:  # Get list of SM torrent links
        smtorrentlinks[torrentdata['torrentid']] = torrentdata['torrentdl']

    for torrentid, torrentlink in smtorrentlinks.items():
        torrentfile = sm.retrieveContent(torrentlink)
        torrentfilename = get_valid_filename(f'SM {torrentgroupdata.artist} - {torrentgroupdata.title} - {torrentid}.torrent')
        with open(torrentfilename, "wb") as f:
            f.write(torrentfile.content)
        if debug:
            print(f'Downloaded SM torrent as {torrentfilename}')


def decide_ep(torrentfilename):
    """
    Return if Album upload should be an EP or not.
    EPs are considered to have < 7 tracks, excluding off-vocals and uploaded to JPS as an Album

    We assume we are being called only if Cat = Album

    :param torrentfilename:
    :return: str: 'EP' or 'Album'
    """

    torrent_metadata = tp.parse_torrent_file(torrentfilename)
    music_extensions = ['.flac', '.mp3', '.ogg', '.alac', '.m4a', '.wav', '.wma', '.ra']
    off_vocal_phrases = ['off-vocal', 'offvocal', 'off vocal', 'inst.', 'instrumental', 'english ver', 'japanese ver', 'korean ver']
    track_count = 0
    for file in torrent_metadata['info']['files']:
        if list(filter(file['path'][-1].lower().endswith, music_extensions)) and \
                not any(substring in file['path'][-1].lower() for substring in off_vocal_phrases):
            #  Count music files which are not an off-vocal or instrumental
            print(file['path'][-1])
            track_count += 1

    if track_count < 7:
        if debug:
            print(f'Upload is an EP as it has {track_count} standard tracks')
        return 'EP'
    else:
        print(f'Upload is not an EP as it has {track_count} tracks')
        return 'Album'


def getmediainfo(torrentfilename):
    """
    Get filename(s) of video files in the torrent and run mediainfo and capture the output, then set the appropriate fields for the upload

    :param torrentfilename: str filename of torrent to parse from collate()
    :return: mediainfo
    """

    torrentmetadata = tp.parse_torrent_file(torrentfilename)

    if 'name' in torrentmetadata['info'].keys():
        name = torrentmetadata['info']['name']  # Directory if >1 file, otherwise it is filename
    #print(torrentmetadata)

    # info = libtorrent.torrent_info(torrentfilename)
    # for f in info.files():
    #     print(f"file: {f.path} - {f.size}")

    mediainfosall = ""
    releasedataout = {}

    if 'files' in torrentmetadata['info'].keys():
        for file in torrentmetadata['info']['files']:
            if len(torrentmetadata['info']['files']) == 1:  # This might never happen, it could be just info.name if so
                filename = os.path.join(*file['path'])
            else:
                releasedataout['multiplefiles'] = True
                filename = os.path.join(*[name, *file['path']])  # Directory if >1 file

            mediainfosall += str(MediaInfo.parse(filename, text=True))
            # Get biggest file and mediainfo on this to set the fields for the release
            maxfile = max(torrentmetadata['info']['files'], key=lambda x: x['length'])  # returns {'length': int, 'path': [str]} of largest file
            fileforsmfields = os.path.join(*[name, *maxfile['path']])
    else:
        releasedataout['multiplefiles'] = False
        filename = name
        if debug:
            print(f'Filename for mediainfo: {filename}')
        mediainfosall += str(MediaInfo.parse(filename, text=True))
        fileforsmfields = torrentmetadata['info']['name']

    mediainforeleasedata = MediaInfo.parse(fileforsmfields)

    releasedataout['duration'] = 0

    for track in mediainforeleasedata.tracks:
        if track.track_type == 'General':
            releasedataout['container'] = track.file_extension.upper()
            # releasedataout['language'] = track.audio_language_list  # Will need to check if this is reliable
            releasedataout['duration'] += float(track.duration)  # time in ms

        if track.track_type == 'Video':
            validatecodec = {
                "MPEG Video": "MPEG-2",
                "AVC": "h264",
                "HEVC": "h265",
                "MPEG-4 Visual": "DivX",  # MPEG-4 Part 2 / h263 , usually xvid / divx
            }
            for old, new in validatecodec.items():
                if track.format == old:
                    releasedataout['codec'] = new

            standardresolutions = {
                "3840": "1920",
                "1920": "1080",
                "1280": "720",
                "640": "480",
            }
            for width, height in standardresolutions.items():
                if str(track.width) == width and str(track.height) == height:
                    releasedataout['ressel'] = height

            if 'ressel' in releasedataout.keys():  # Known resolution type, try to determine if interlaced
                if track.scan_type == "Interlaced" or track.scan_type == "MBAFF":
                    releasedataout['ressel'] += "i"
                else:
                    releasedataout['ressel'] += "p"  # Sometimes a Progressive encode has no field set
            else:  # Custom resolution
                releasedataout['ressel'] = str(track.width) + "x" + str(track.height)

        if track.track_type == 'Audio' or track.track_type == 'Audio #1':  # Handle multiple audio streams, we just get data from the first for now
            if track.format in ["AAC", "DTS", "PCM", "AC-3"]:
                releasedataout['audioformat'] = track.format
            elif track.format == "MPEG Audio" and track.format_profile == "Layer 3":
                releasedataout['audioformat'] = "MP3"
            elif track.format == "MPEG Audio" and track.format_profile == "Layer 2":
                releasedataout['audioformat'] = "MP2"

    if debug:
        print(f'Mediainfo interpreted data: {releasedataout}')

    return mediainfosall, releasedataout


def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-d', '--debug', help='Enable debug mode', action='store_true')
    parser.add_argument("-u", "--urls", help="JPS URL for a group, or multiple individual releases URLs to be added to the same group", type=str)
    parser.add_argument("-n", "--dryrun", help="Just parse url and show the output, do not add the torrent to SM", action="store_true")
    parser.add_argument("-b", "--batchuser", help="User id for batch user operations")
    parser.add_argument("-U", "--batchuploaded", help="Upload all releases uploaded by user id specified by --batchuser", action="store_true")
    parser.add_argument("-S", "--batchseeding", help="Upload all releases currently seeding by user id specified by --batchuser", action="store_true")
    parser.add_argument("-s", "--batchstart", help="(Batch mode only) Start at this page", type=int)
    parser.add_argument("-e", "--batchend", help="(Batch mode only) End at this page", type=int)
    parser.add_argument("-f", "--excfilteraudioformat", help="Exclude an audioformat from upload", type=str)
    parser.add_argument("-F", "--excfiltermedia", help="Exclude a media from upload", type=str)
    parser.add_argument("-m", "--mediainfo", help="Get mediainfo data and extract data to set codec, resolution, audio format and container fields", action="store_true")

    return parser.parse_args()


class VideoOptions:
    """
    Store Video option constants
    """

    VideoMedias = ('DVD', 'Blu-Ray', 'VHS', 'VCD', 'TV', 'HDTV', 'WEB')
    badcontainers = ('ISO', 'VOB', 'MPEG', 'AVI', 'MKV', 'WMV', 'MP4')
    badcodecs = ('MPEG2', 'h264')
    badformats = badcontainers + badcodecs
    resolutions = ('720p', '1080i', '1080p')


class Categories:
    """
    Store category constants
    """

    # Store JPS to SM Category translation, defines which JPS Cat gets uploaded to which SM Cat
    # key: JPS category name
    # value: SM category ID
    JPStoSM = {
        'Album': 0,
        'EP': 1,  # Does not exist on JPS
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

    SM = {
        'Album': 0,
        'EP': 1,  # Does not exist on JPS
        'Single': 2,
        'Bluray': 3,  # Does not exist on JPS
        'DVD': 4,
        'PV': 5,
        'Music Performance': 6,  # Does not exist on JPS
        'TV Music': 7,  # TV-Music
        'TV Variety': 8,  # TV-Variety
        'TV Drama': 9,  # TV-Drama
        'Pictures': 10,
        'Misc': 11,
    }

    # Video = ('Bluray', 'DVD', 'PV', 'TV-Music', 'TV-Variety', 'TV-Drama', 'Music Performance')  # was VideoCategories

    # JPS Categories where release date cannot be entered and therefore need to be processed differently
    NonDate = ('TV-Music', 'TV-Variety', 'TV-Drama', 'Fansubs', 'Pictures', 'Misc')
    # JPS Categories where no release data is present and therefore need to be processed differently
    NonReleaseData = ('Pictures', 'Misc')
    # Music and Music Video Torrents, for category validation. This must match the cateogry headers in JPS for an artist, hence they are in plural
    NonTVCategories = ('Albums', 'Singles', 'DVDs', 'PVs')


if __name__ == "__main__":
    args = getargs()
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
        if bool(args.batchuploaded) and bool(args.batchseeding):
            print('You have specified both batch modes of operation - only one can be used at the same time.')
            sys.exit()
        elif args.batchuploaded is False and args.batchseeding is False:
            print('Batch user upload mode not specified.')
            sys.exit()

        if args.batchuploaded:
            batchmode = "uploaded"
        elif args.batchseeding:
            batchmode = "seeding"

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

    if not dryrun:
        sm = MyLoginSession(SMloginUrl, SMloginData, SMloginTestUrl, SMsuccessStr, debug=args.debug)
        authkey = getauthkey()  # We only want this run ONCE per instance of the script

    if usermode:
        if batchstart and batchend:
            useruploads = getbulktorrentids(batchmode, batchuser, batchstart, batchend)
        else:
            useruploads = getbulktorrentids(batchmode, batchuser)
        useruploadsgrouperrors = collections.defaultdict(list)
        useruploadscollateerrors = collections.defaultdict(list)
        user_upload_dupes = []

        for key, value in useruploads.items():
            groupid = key
            torrentids = value
            try:
                torrentgroupdata = GetGroupData("https://jpopsuki.eu/torrents.php?id=%s" % groupid)
            except KeyboardInterrupt:  # Allow Ctrl-C to exit without showing the error multiple times and polluting the final error dict
                break  # Still continue to get error dicts and dupe list so far
            except Exception as exc:
                print('Error with retrieving group data for groupid %s trorrentid(s) %s, skipping upload' % (groupid, ",".join(torrentids)))
                useruploadsgrouperrors[groupid] = torrentids
                if debug:
                    print(exc)
                    traceback.print_exc()
                continue

            try:
                torrentcount = collate(torrentids)
                if not dryrun:
                    downloaduploadedtorrents(torrentcount)
            except KeyboardInterrupt:  # Allow Ctrl-C to exit without showing the error multiple times and polluting the final error dict
                break  # Still continue to get error dicts and dupe list so far
            except Exception as exc:
                if str(exc).startswith('The exact same torrent file already exists on the site!'):
                    print(exc)
                    sm_dupe_torrentid = re.findall(r'The exact same torrent file already exists on the site! See: https://sugoimusic\.me/torrents\.php\?torrentid=([0-9]+)', str(exc))
                    user_upload_dupes.append(sm_dupe_torrentid)
                else:
                    print('Error with collating/retrieving release data for groupid %s torrentid(s) %s, skipping upload' % (groupid, ",".join(torrentids)))
                    useruploadscollateerrors[groupid] = torrentids
                    if debug:
                        print(exc)
                        traceback.print_exc()

                continue

        if useruploadsgrouperrors:
            print('The following JPS groupid(s) (torrentid(s) shown for reference) had errors in retrieving group data, '
                  'keep this data safe and you can possibly retry with it in a later version:')
            print(useruploadsgrouperrors)
        if useruploadscollateerrors:
            print('The following JPS groupid(s) and corresponding torrentid(s) had errors either in collating/retrieving '
                  'release data or in performing the actual upload to SM (although group data was retrieved OK), '
                  'keep this data safe and you can possibly retry with it in a later version:')
            print(useruploadscollateerrors)
        if user_upload_dupes:
            print('The following SM torrentid(s) have already been uploaded to the site:')
            print(user_upload_dupes)

    else:
        # Standard non-batch upload using --urls
        torrentgroupdata = GetGroupData(jpsurl)
        torrentids = re.findall('torrentid=([0-9]+)', jpsurl)
        torrentcount = collate(torrentids)
        if not dryrun:
            downloaduploadedtorrents(torrentcount)


