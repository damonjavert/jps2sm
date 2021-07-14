# Standard library packages
import logging
import re
import itertools
import time
import json

from jps2sm.myloginsession import jpopsuki, sugoimusic
from jps2sm.constants import Categories
from jps2sm.utils import remove_html_tags

# Third-party packages
from bs4 import BeautifulSoup

logger = logging.getLogger('main.' + __name__)


class GetGroupData:
    """
    Retrieve group data of the group supplied from args.parsed.urls
    Group data is defined as data that is constant for every release, eg category, artist, title, groupdescription, tags etc.
    Each property is gathered by calling a method of the class
    """

    def __init__(self, jpsurl):
        self.jpsurl = jpsurl
        logger.debug(f'Processing JPS URL: {jpsurl}')
        self.getdata(jpsurl)

    def getdata(self, jpsurl):
        date_regex = r'[12]\d{3}\.(?:0[1-9]|1[0-2])\.(?:0[1-9]|[12]\d|3[01])'  # YYYY.MM.DD format
        # YYYY.MM.DD OR YYYY format, for Pictures only
        date_regex2 = r'(?:[12]\d{3}\.(?:0[1-9]|1[0-2])\.(?:0[1-9]|[12]\d|3[01])|(?:19|20)\d\d)'

        res = jpopsuki(self.jpsurl.split()[0])  # If there are multiple urls only the first url needs to be parsed

        self.groupid = re.findall(r"(?!id=)\d+", self.jpsurl)[0]

        soup = BeautifulSoup(res.text, 'html5lib')

        artistline = soup.select('.thin h2')
        artistlinelink = soup.select('.thin h2 a')
        originaltitleline = soup.select('.thin h3')
        text = str(artistline[0])
        logger.debug(artistline[0])

        sqbrackets = re.findall('\[(.*?)\]', text)
        self.category = sqbrackets[0]
        logger.info(f'Category: {self.category}')

        try:
            artistlinelinktext = str(artistlinelink[0])
            artist_raw = re.findall('<a[^>]+>(.*)<', artistlinelinktext)[0]
            self.artist = split_bad_multiple_artists(artist_raw)
        except IndexError:  # Cannot find artist
            if self.category == "Pictures":
                # JPS allows Picture torrents to have no artist set, in this scenario try to infer the artist by examining the text
                # immediately after the category string up to a YYYY.MM.DD string if available as this should be the magazine title
                try:
                    self.artist = re.findall(fr'\[Pictures\] ([A-Za-z\. ]+) (?:{date_regex2})', text)
                except IndexError:
                    logger.exception('Cannot find artist')
                    raise
            elif self.category == "Misc":
                # JPS has some older groups with no artists set, uploaders still used the "Artist - Group name" syntax though
                try:
                    artist_raw = re.findall(r'\[Misc\] ([A-Za-z\, ]+) - ', text)[0]
                except IndexError:
                    logger.exception('Cannot find artist')
                    raise
                self.artist = split_bad_multiple_artists(artist_raw)
            else:
                logger.exception('JPS upload appears to have no artist set and artist cannot be autodetected')
                raise

        logger.info(f'Artist(s): {self.artist}')

        # Extract date without using '[]' as it allows '[]' elsewhere in the title and it works with JPS TV-* categories
        try:
            self.date = re.findall(date_regex, text)[0].replace(".", "")
        except IndexError:  # Handle YYYY dates, creating extra regex as I cannot get it working without causing issue #33
            try:
                self.date = re.findall(r'[^\d]((?:19|20)\d{2})[^\d]', text)[0]

            # Handle if cannot find date in the title, use upload date instead from getreleasedata() but error if the category should have it
            except IndexError:
                if self.category not in Categories.NonDate:
                    logger.exception(f'Group release date not found and not using upload date instead as {self.category} torrents should have it set')
                else:
                    logger.warning('Date not found from group data, will use upload date as the release date')
                self.date = None
                pass

        logger.info(f'Release date: {self.date}')

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
                except IndexError:
                    if self.category == "Pictures":  # Pictures non-artist upload - for magazines
                        # Fallback to all the text after the category, we need to include the date stamp as magazines are often titled
                        # with the same numbers each year - the first magazine each year appears to always be 'No. 1' for example
                        try:
                            self.title = re.findall(fr'\[Pictures\] (?:[A-Za-z\. ]+) ({date_regex2}(?:.*))</h2>', text)[0]
                        except IndexError:
                            logger.exception('Cannot find title from the JPS upload')
                            raise
                    elif self.category == "Misc":
                        try:
                            self.title = re.findall(r'\[Misc\] (?:[A-Za-z\, ]+) - (.+)</h2>', text)[0]
                        except IndexError:
                            logger.exception('Cannot find title from the JPS upload')
                            raise
                    else:
                        logger.exception('Cannot find title from the JPS upload')
                        raise
            else:
                self.title = titlemerged

        logger.info(f'Title: {self.title}')
        try:
            originalchars = re.findall(r'<a href="artist.php\?id=(?:[0-9]+)">(.+)</a> - (.+)\)</h3>', str(originaltitleline))[0]
            self.originalartist = originalchars[0]
            self.originaltitle = originalchars[1]
            logger.info(f"Original artist: {self.originalartist} Original title: {self.originaltitle}")
        except IndexError:  # Do nothing if group has no original artist/title
            pass

        self.rel2 = str(soup.select('#content .thin .main_column .torrent_table tbody')[0])

        # print rel2
        # fakeurl = 'https://jpopsuki.eu/torrents.php?id=181558&torrentid=251763'
        # fakeurl = 'blah'

        # Get description with BB Code if user has group edit permissions on JPS, if not just use stripped html text.
        try:
            self.groupdescription = get_group_descrption_bbcode(self.groupid)  # Requires PU+ at JPS
        except:
            self.groupdescription = remove_html_tags(str(soup.select('#content .thin .main_column .box .body')[0]))

        logger.info(f"Group description:\n{self.groupdescription}")

        image = str(soup.select('#content .thin .sidebar .box p a'))
        try:
            self.imagelink = "https://jpopsuki.eu/" + re.findall('<a\s+(?:[^>]*?\s+)?href=\"([^\"]*)\"', image)[0]
            logger.info(f'Image link: {self.imagelink}')
        except IndexError:  # No image for the group
            self.imagelink = None

        tagsget = str(soup.select('#content .thin .sidebar .box ul.stats.nobullet li'))
        tags = re.findall('searchtags=([^\"]+)', tagsget)
        logger.info(f'Tags: {tags}')
        self.tagsall = ",".join(tags)

        try:
            contribartistsget = str(soup.select('#content .thin .sidebar .box .body ul.stats.nobullet li'))
            contribartistslist = re.findall(r'<li><a href="artist\.php\?id=(?:[0-9]+?)" title="([^"]*?)">([\w .-]+)</a>', contribartistsget)
            self.contribartists = {}
            for artistpair in contribartistslist:
                self.contribartists[artistpair[1]] = artistpair[0] # Creates contribartists[artist] = origartist

            logger.info(f'Contributing artists: {self.contribartists}')
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


def split_bad_multiple_artists(artists):
    return re.split(', | x | & ', artists)


def get_release_data(torrentids, release_data, date):
    """
    Retrieve all torrent id and release data (slash separated data and upload date) whilst coping with 'noise' from FL torrents,
    and either return all data if using a group URL or only return the relevant releases if release url(s) were used

    :param torrentids: list of torrentids to be processed, NULL if group is used
    :return: releasedata: 2d dict of release data in the format of torrentid: { "slashdata" : [ slashdatalist ] , "uploaddate": uploaddate } .
    """

    freeleechtext = '<strong>Freeleech!</strong>'
    releasedatapre = re.findall(r"swapTorrent\('([0-9]+)'\);\">» (.*?)</a>.*?<blockquote>(?:\s*)Uploaded by <a href=\"user.php\?id=(?:[0-9]+)\">(?:[\S]+)</a>  on <span title=\"(?:[^\"]+)\">([^<]+)</span>", release_data, re.DOTALL)
    # if args.parsed.debug:
    #     print(f'Pre-processed releasedata: {json.dumps(releasedatapre, indent=2)}')

    releasedata = {}
    for release in releasedatapre:
        torrentid = release[0]
        slashlist = ([i.split(' / ') for i in [release[1]]])[0]
        uploadeddate = release[2]
        releasedata[torrentid] = {}
        releasedata[torrentid]['slashdata'] = slashlist
        releasedata[torrentid]['uploaddate'] = uploadeddate

    logger.debug(f'Entire group contains: {json.dumps(releasedata, indent=2)}')

    removetorrents = []
    for torrentid, release in releasedata.items():  # Now release is a dict!
        if len(torrentids) != 0 and torrentid not in torrentids:
            # If len(torrentids) != 0 then user has supplied a group url and every release is processed,
            # otherwise iterate through releasedata{} and remove what is not needed
            removetorrents.append(torrentid)
        if freeleechtext in release['slashdata']:
            release['slashdata'].remove(freeleechtext)  # Remove Freeleech whole match so it does not interfere with Remastered
        for index, slashreleaseitem in enumerate(release['slashdata']):
            if remaster_freeleech_removed := re.findall(r'(.*) - <strong>Freeleech!<\/strong>', slashreleaseitem):  # Handle Freeleech remastered torrents, issue #43
                release['slashdata'][index] = f'{remaster_freeleech_removed[0]} - {date[:4]}'  # Use the extracted value and append group JPS release year
                logger.debug(f"Torrent {torrentid} is freeleech remastered, validated remasterdata to {release['slashdata'][index]}")
    for torrentid in removetorrents:
        del (releasedata[torrentid])

    logger.info(f'Selected for upload: {releasedata}')
    return releasedata



def get_group_descrption_bbcode(groupid):
    """
    Retrieve original bbcode from edit group url and reformat any JPS style bbcode

    :param: groupid: JPS groupid to get group description with bbcode
    :return: bbcode: group description with bbcode
    """
    edit_group_page = jpopsuki(f"https://jpopsuki.eu/torrents.php?action=editgroup&groupid={groupid}")
    soup = BeautifulSoup(edit_group_page.text, 'html5lib')
    bbcode = soup.find("textarea", {"name": "body"}).string

    bbcode_sanitised = re.sub(r'\[youtube=([^\]]+)]', r'[youtube]\1[/youtube]', bbcode)

    return bbcode_sanitised


def get_jps_user_id():
    """
    Returns the JPopSuki user id
    :return: int: user id
    """

    res = jpopsuki("https://jpopsuki.eu/", True)
    soup = BeautifulSoup(res.text, 'html5lib')
    href = soup.select('.username')[0]['href']
    jps_user_id = re.match(r"user\.php\?id=(\d+)", href).group(1)
    time.sleep(5)  # Sleep as otherwise we hit JPS browse quota

    return int(str(jps_user_id))


def get_user_keys():
    """
    Get SM session authkey and torrent_password_key for use by uploadtorrent()|download_sm_torrent() data dict.
    Uses SM login data
    """
    smpage = sugoimusic("https://sugoimusic.me/torrents.php?id=118", test_login=True)  # Arbitrary page on JPS that has authkey
    soup = BeautifulSoup(smpage.text, 'html5lib')
    rel2 = str(soup.select_one('#torrent_details .group_torrent > td > span > .tooltip'))

    return {
        'authkey': re.findall('authkey=(.*)&amp;torrent_pass=', rel2)[0],
        'torrent_password_key': re.findall(r"torrent_pass=(.+)\" title", rel2)[0]
    }


def get_torrent_link(torrentid, release_data):
    """
    Extract a torrent link for a given torrentid

    :param torrentid:
    :return: torrentlink: URI of torrent link
    """
    torrentlink = re.findall(rf'torrents\.php\?action=download&amp;id={torrentid}&amp;authkey=(?:[^&]+)&amp;torrent_pass=(?:[^"]+)', release_data)[0]
    return torrentlink