# Standard library packages
import logging
import re
import itertools
import time
import json
from dataclasses import dataclass
from typing import Optional
import collections

from jps2sm.myloginsession import jpopsuki, sugoimusic
from jps2sm.constants import Categories
from jps2sm.utils import remove_html_tags

# Third-party packages
from html2phpbbcode.parser import HTML2PHPBBCode
from bs4 import BeautifulSoup

logger = logging.getLogger('main.' + __name__)


@dataclass
class JPSGroup:
    groupid: int
    category: str
    artist: str
    date: str
    title: str
    originalartist: str
    originaltitle: str
    rel2: str
    groupdescription: str
    imagelink: str
    tagsall: str
    contribartists: str


def get_jps_group_data_class(batch_group_data, jps_group_id):
    """
    Extract a JPS group's data from batch_group_data{} and present it as a JPSGroup dataclass.
    In the future this can potentially be used to provide validation, or collate() and uploadtorrent() may
    be refactored to just use a dict.

    :param batch_group_data: dict
    :param jps_group_id: int
    :returns: torrent_group_data: class
    """

    torrent_group_data = JPSGroup(
        groupid=batch_group_data[jps_group_id]['groupid'],
        category=batch_group_data[jps_group_id]['category'],
        artist=batch_group_data[jps_group_id]['artist'],
        date=batch_group_data[jps_group_id]['date'],
        title=batch_group_data[jps_group_id]['title'],
        originalartist=batch_group_data[jps_group_id]['originalartist'],
        originaltitle=batch_group_data[jps_group_id]['originaltitle'],
        rel2=batch_group_data[jps_group_id]['rel2'],
        groupdescription=batch_group_data[jps_group_id]['groupdescription'],
        imagelink=batch_group_data[jps_group_id]['imagelink'],
        tagsall=batch_group_data[jps_group_id]['tagsall'],
        contribartists=batch_group_data[jps_group_id]['contribartists']
    )

    return torrent_group_data


class GetGroupData:
    """
    Retrieve group data of the group supplied from args.parsed.urls
    Group data is defined as data that is constant for every release, eg category, artist, title, groupdescription, tags etc.
    Each property is gathered by calling a method of the class
    """

    def __init__(self, jpsurl):
        self.jpsurl = jpsurl
        logger.debug(f'Processing JPS URL: {jpsurl}')
        self.groupid: int = int()
        self.category: str = str()
        self.artist: str = str()
        self.date: str = str()
        self.title: str = str()
        self.originalartist: str = str()
        self.originaltitle: str = str()
        self.rel2: str = str()
        self.groupdescription: str = str()
        self.imagelink: str = str()
        self.tagsall: str = str()
        self.contribartists: str = str()

        self.getdata()

    def getdata(self):
        date_regex = r'[12]\d{3}\.(?:0[1-9]|1[0-2])\.(?:0[1-9]|[12]\d|3[01])'  # YYYY.MM.DD format
        # YYYY.MM.DD OR YYYY format, for Pictures only
        date_regex2 = r'(?:[12]\d{3}\.(?:0[1-9]|1[0-2])\.(?:0[1-9]|[12]\d|3[01])|(?:19|20)\d\d)'

        res = jpopsuki(self.jpsurl.split()[0])  # If there are multiple urls only the first url needs to be parsed

        self.groupid = re.findall(r"(?!id=)\d+", self.jpsurl)[0]

        soup = BeautifulSoup(res.text, 'html5lib')
        artistlinelink = soup.select('.thin h2 a')
        originaltitleline = soup.select('.thin h3')

        logger.debug(torrent_description_page_h2_line := str(soup.select('.thin h2')[0]))

        if torrent_description_page_h2_line == "<h2>Error</h2>":
            if error := str(soup.select('.thin h3')[0]):  # Try to grab error string
                if error == "<h3>Torrent not found</h3>":
                    logger.error('JPS torrent not found')
                    raise Exception('JPS torrent not found')

            logger.error(f'Error: {error}')
            raise Exception(f'Error in GetGroupData: {error}')

        try:
            self.category = re.findall(r'\[(.*?)\]', torrent_description_page_h2_line)[0]
        except IndexError:
            logger.error(f'Error: Could not ascertain Category for group {self.groupid}, try adding --debug to see what could be wrong.')
            raise Exception('JPS Category not found')

        logger.info(f'Category: {self.category}')

        try:
            artist_raw = re.findall(r'<a[^>]+>(.*)<', str(artistlinelink[0]))[0]
            self.artist = split_bad_multiple_artists(artist_raw)
        except IndexError:  # Cannot find artist
            if self.category == "Pictures":
                # JPS allows Picture torrents to have no artist set, in this scenario try to infer the artist by examining the text
                # immediately after the category string up to a YYYY.MM.DD string if available as this should be the magazine title
                try:
                    self.artist = re.findall(fr'\[Pictures\] ([A-Za-z\. ]+) (?:{date_regex2})', torrent_description_page_h2_line)
                except IndexError:
                    logger.exception('Cannot find artist')
                    raise
            elif self.category == "Misc":
                # JPS has some older groups with no artists set, uploaders still used the "Artist - Group name" syntax though
                try:
                    artist_raw = re.findall(r'\[Misc\] ([A-Za-z\, ]+) - ', torrent_description_page_h2_line)[0]
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
            self.date = re.findall(date_regex, torrent_description_page_h2_line)[0].replace(".", "")
        except IndexError:  # Handle YYYY dates, creating extra regex as I cannot get it working without causing issue #33
            try:
                self.date = re.findall(r'[^\d]((?:19|20)\d{2})[^\d]', torrent_description_page_h2_line)[0]

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
            self.title = re.findall(r'<a.*> - (.*) \[', torrent_description_page_h2_line)[0]
        else:
            # Using two sets of findall() as I cannot get the OR regex operator "|" to work
            title1 = re.findall(r'<a.*> - (?:[12]\d{3}\.(?:0[1-9]|1[0-2])\.(?:0[1-9]|[12]\d|3[01])) - (.*)</h2>', torrent_description_page_h2_line)
            title2 = re.findall(r'<a.*> - (.*) \((.*) (?:[12]\d{3}\.(?:0[1-9]|1[0-2])\.(?:0[1-9]|[12]\d|3[01]))', torrent_description_page_h2_line)
            # title1 has 1 matching group, title2 has 2
            titlemergedpre = [title1, " ".join(itertools.chain(*title2))]
            titlemerged = "".join(itertools.chain(*titlemergedpre))
            if len(titlemerged) == 0:  # Non standard title, fallback on the whole string after the "-"
                try:
                    self.title = re.findall(r'<a.*> - (.*)</h2>', torrent_description_page_h2_line)[0]
                except IndexError:
                    if self.category == "Pictures":  # Pictures non-artist upload - for magazines
                        # Fallback to all the text after the category, we need to include the date stamp as magazines are often titled
                        # with the same numbers each year - the first magazine each year appears to always be 'No. 1' for example
                        try:
                            self.title = re.findall(fr'\[Pictures\] (?:[A-Za-z\. ]+) ({date_regex2}(?:.*))</h2>', torrent_description_page_h2_line)[0]
                        except IndexError:
                            logger.exception('Cannot find title from the JPS upload')
                            raise
                    elif self.category == "Misc":
                        try:
                            self.title = re.findall(r'\[Misc\] (?:[A-Za-z\, ]+) - (.+)</h2>', torrent_description_page_h2_line)[0]
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

        # Get description with BB Code if user has group edit permissions on JPS, if not just use stripped html text.
        try:
            self.groupdescription = get_group_descrption_bbcode(self.groupid)  # Requires PU+ at JPS
        except:
            logger.exception('Could not get group description BBCode. Are you a Power User+ at JPS?')
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


        contribartistsget = str(soup.select('#content .thin .sidebar .box .body ul.stats.nobullet li'))
        contribartistslist = re.findall(r'<li><a href="artist\.php\?id=(?:[0-9]+?)" title="([^"]*?)">([\w .-]+)</a>', contribartistsget)
        self.contribartists = {}
        for artistpair in contribartistslist:
            self.contribartists[artistpair[1]] = artistpair[0]  # Creates contribartists[artist] = origartist

        logger.info(f'Contributing artists: {self.contribartists}')
        if self.contribartists == {}:
            # No contrib artists found, we need to error here if it is a V.A. torrent
            if self.artist == ['V.A.']:
                raise Exception("V.A. torrent with to contrib artists set - torrent has no valid artists so this cannot be uploaded.")


    def originalchars(self):
        return self.originalartist, self.originaltitle

    def all(self):
        return {
            'groupid': self.groupid,
            'category': self.category,
            'artist': self.artist,
            'date': self.date,
            'title': self.title,
            'originalartist': self.originalartist,
            'originaltitle': self.originaltitle,
            'rel2': self.rel2,
            'groupdescription': self.groupdescription,
            'imagelink': self.imagelink,
            'tagsall': self.tagsall,
            'contribartists': self.contribartists,
            'originalchars': self.originalchars()
        }

    def __getattr__(self, item):
        return self.item


def split_bad_multiple_artists(artists):
    return re.split(', | x | & ', artists)


def get_release_data(torrentids, release_data, date, jps_user_id=None):
    """
    Retrieve all torrent id and release data (slash separated data and upload date) whilst coping with 'noise' from FL torrents,
    and either return all data if using a group URL or only return the relevant releases if release url(s) were used

    :param torrentids: list of torrentids to be processed, NULL if group is used
    :return: releasedata: 2d dict of release data in the format of torrentid: { "slashdata" : [ slashdatalist ] , "uploaddate": uploaddate } .
    """

    # print(release_data)
    freeleechtext = '<strong>Freeleech!</strong>'
    releasedatapre = re.findall(r"swapTorrent\('([0-9]+)'\);\">» (.+?(?=</a>))</a>(?:\s*)</td>(?:\s*)<td class=\"nobr\">(\d*(?:\.)?(?:\d{0,2})?) (\w{2})</td>(?:\s*)<td>([0-9,]{1,6})</td>(?:\s*)<td>([0-9,]{1,6})</td>(?:\s*)<td>([0-9,]{1,6})</td>.*?<blockquote>(?:\s*)Uploaded by <a href=\"user.php\?id=([0-9]+)\">(?:[\S]+)</a>  on <span title=\"(?:[^\"]+)\">([^<]+)</span>.*?<blockquote>(.*?)</blockquote>", release_data, re.DOTALL)
    # logger.debug(f'Pre-processed releasedata: {json.dumps(releasedatapre, indent=2)}')


    #soup = BeautifulSoup(release_data,'html5lib')
    #raw_release_desc = soup.find_all("blockquote")[-1].decode_contents()
    #logging.debug(f"Raw release desc: {raw_release_desc}")
    parser = HTML2PHPBBCode()
    #release_desc = parser.feed(raw_release_desc)
    #logging.debug(f"BBCode parsed output for release desc: {release_desc}")

    releasedata = {}

    try:
        # Create exception if no release data was found, else these get silently skipped in collate() as the response is null.
        test = releasedatapre[0]
    except IndexError:
        raise RuntimeError(f'No release data found for {torrentids}')

    for release in releasedatapre:
        torrentid = release[0]
        slashlist = ([i.split(' / ') for i in [release[1]]])[0]
        size_no_units = release[2]
        size_units = release[3]
        completed = release[4]
        seeders = release[5]
        leechers = release[6]
        uploadeddate = release[8]
        releasedata[torrentid] = {}
        releasedata[torrentid]['slashdata'] = slashlist
        releasedata[torrentid]['uploaddate'] = uploadeddate
        releasedata[torrentid]['size_no_units'] = size_no_units
        releasedata[torrentid]['size_units'] = size_units
        releasedata[torrentid]['completed'] = completed
        releasedata[torrentid]['seeders'] = seeders
        releasedata[torrentid]['leechers'] = leechers
        orig_uploader_id=int(release[7])
        release_desc = parser.feed(release[9])
        logger.debug(f"Release description:{release_desc}")
        if release_desc.startswith(' New ratio after downloading'):
            release_desc = ''
        logger.debug(f"Checking if own upload. Own id: {jps_user_id}. Original uploader id: {orig_uploader_id}")
        if orig_uploader_id == jps_user_id:
            releasedata[torrentid]['release_desc'] = release_desc
        else:
            releasedata[torrentid]['release_desc'] = f'Migrated using jps2sm. Thanks to the original uploader.'
            if not release_desc == '':
                releasedata[torrentid]['release_desc']+=f"\n\n[spoiler=Original description]{release_desc}[/spoiler]"


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