# Standard library packages
import re
import itertools
import time
import json
from dataclasses import dataclass
from typing import Optional, Dict, List, Any, Union, Tuple
import collections

from jps2sm.myloginsession import jpopsuki, sugoimusic
from jps2sm.constants import Categories
from jps2sm.utils import remove_html_tags

# Third-party packages
from bs4 import BeautifulSoup

from loguru import logger


@dataclass
class JPSGroup:
    groupid: int
    category: str
    artist: str
    date: str
    title: str
    originalartist: str
    originaltitle: str
    torrent_table: str
    groupdescription: str
    imagelink: str
    tagsall: str
    contribartists: str


def get_jps_group_data_class(batch_group_data: dict, jps_group_id: int) -> dataclass(JPSGroup):
    """
    Extract a JPS group's data from batch_group_data{} and present it as a JPSGroup dataclass.
    In the future this can potentially be used to provide validation, or collate() and uploadtorrent() may
    be refactored to just use a dict.

    :param batch_group_data: dict
    :param jps_group_id: int
    :returns: torrent_group_data: dataclass JPSGroup
    """

    torrent_group_data = JPSGroup(
        groupid=batch_group_data[jps_group_id]['groupid'],
        category=batch_group_data[jps_group_id]['category'],
        artist=batch_group_data[jps_group_id]['artist'],
        date=batch_group_data[jps_group_id]['date'],
        title=batch_group_data[jps_group_id]['title'],
        originalartist=batch_group_data[jps_group_id]['originalartist'],
        originaltitle=batch_group_data[jps_group_id]['originaltitle'],
        torrent_table=batch_group_data[jps_group_id]['torrent_table'],
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
        self.torrent_table: str = str()
        self.groupdescription: str = str()
        self.imagelink: str = str()
        self.tagsall: str = str()
        self.contribartists: str = str()

        self.getdata()

    def getdata(self) -> None:
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

        self.torrent_table = str(soup.select('#content .thin .main_column .torrent_table tbody')[0])

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

    def originalchars(self) -> Tuple[str, str]:
        return self.originalartist, self.originaltitle

    def all(self) -> Dict[str, Union[str, Tuple[str, str]]]:
        return {
            'groupid': self.groupid,
            'category': self.category,
            'artist': self.artist,
            'date': self.date,
            'title': self.title,
            'originalartist': self.originalartist,
            'originaltitle': self.originaltitle,
            'torrent_table': self.torrent_table,
            'groupdescription': self.groupdescription,
            'imagelink': self.imagelink,
            'tagsall': self.tagsall,
            'contribartists': self.contribartists,
            'originalchars': self.originalchars()
        }

    def __getattr__(self, item):
        return self.item


def split_bad_multiple_artists(artists: str) -> List[str]:
    # TODO When upgrading to 3.9+ the type can be changed to list[str] See PEP 585
    return re.split(', | x | & ', artists)


def get_release_data(torrentids: List[str], torrent_table: str, date: str) -> Dict[str, Dict[str, Union[List[str], str]]]:
    # TODO When upgrading to 3.9+ the 'List[str]' can be changed to 'list[str]' and  'Union[list, str]' can be 'list | str'. See PEP 585
    """
    Retrieve all torrent id and release data (slash separated data, upload date torrent size, snatch count, seeders, leechers)
    whilst coping with 'noise' from FL torrents, and either return all data if using a group URL or only return the relevant
    releases if release url(s) were used

    :param torrentids: list of torrentids to be processed, empty list if a group URL is being used.
    :param torrent_table: contents of .torrent_table tbody of the JPS group page
    :param date: Date for the JPS group in YYYYMMDD format or YYYY
    :return: releasedata: 2d dict of release data in the format of :
                torrentid: { "slashdata" : [ slashdatalist ] ,
                          "uploaddate": uploaddate,
                          "size_no_units": size_no_units,
                          "size_units" : size_units,
                          "completed" : completed,
                          "seeders" : seeders,
                         "leechers": leechers, }
                        ,
                       ...
    """

    # print(torrent_table)
    freeleechtext = '<strong>Freeleech!</strong>'
    releasedatapre = re.findall(r"swapTorrent\('([0-9]+)'\);\">» (.+?(?=</a>))</a>(?:\s*)</td>(?:\s*)<td class=\"nobr\">(\d*(?:\.)?(?:\d{0,2})?) (\w{2})</td>(?:\s*)<td>([0-9,]{1,6})</td>(?:\s*)<td>([0-9,]{1,6})</td>(?:\s*)<td>([0-9,]{1,6})</td>.*?<blockquote>(?:\s*)Uploaded by <a href=\"user.php\?id=(?:[0-9]+)\">(?:[\S]+)</a>  on <span title=\"(?:[^\"]+)\">([^<]+)</span>", torrent_table, re.DOTALL)
    # logger.debug(f'Pre-processed releasedata: {json.dumps(releasedatapre, indent=2)}')

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
        uploadeddate = release[7]
        releasedata[torrentid] = {}
        releasedata[torrentid]['slashdata'] = slashlist
        releasedata[torrentid]['uploaddate'] = uploadeddate
        releasedata[torrentid]['size_no_units'] = size_no_units
        releasedata[torrentid]['size_units'] = size_units
        releasedata[torrentid]['completed'] = completed
        releasedata[torrentid]['seeders'] = seeders
        releasedata[torrentid]['leechers'] = leechers

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


def get_group_descrption_bbcode(groupid: str) -> str:
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


class GetJPSUser:

    __jps_user_id = None

    def __init__(self):
        if GetJPSUser.__jps_user_id is None:
            GetJPSUser.__jps_user_id = get_jps_user_id()

    def user_id(self) -> str:
        return GetJPSUser.__jps_user_id


def get_jps_user_id() -> int:
    """
    Returns the JPopSuki user id
    :return: int: user id
    """

    res = jpopsuki("https://jpopsuki.eu/", True)
    soup = BeautifulSoup(res.text, 'html5lib')
    href = soup.select('.username')[0]['href']
    jps_user_id = re.match(r"user\.php\?id=(\d+)", href).group(1)

    return int(str(jps_user_id))


class GetSMUser:

    __authkey = None
    __torrent_password_key = None

    def __init__(self):
        if GetSMUser.__authkey is None:
            userkeys = get_user_keys()
            GetSMUser.__authkey = userkeys['authkey']
            GetSMUser.__torrent_password_key = userkeys['torrent_password_key']

    def auth_key(self) -> str:
        return GetSMUser.__authkey

    def torrent_password_key(self) -> str:
        return GetSMUser.__torrent_password_key


def get_user_keys() -> Dict[str, str]:
    """
    Get SM session authkey and torrent_password_key for use by uploadtorrent()|download_sm_torrent() data dict.
    Uses SM login data
    """

    smpage = sugoimusic("https://sugoimusic.me/torrents.php?id=118", test_login=True)  # Arbitrary page on SM that has authkey
    soup = BeautifulSoup(smpage.text, 'html5lib')
    sm_torrent_link = str(soup.select_one('#torrent_details .group_torrent > td > span > .tooltip'))

    return {
        'authkey': re.findall('authkey=(.*)&amp;torrent_pass=', sm_torrent_link)[0],
        'torrent_password_key': re.findall(r"torrent_pass=(.+)\" title", sm_torrent_link)[0]
    }


def get_torrent_link(torrentid: str, torrent_table: str) -> str:
    """
    Extract a torrent link for a given torrentid

    :param torrentid:
    :param torrent_table: str of torrent_table in JPS group page
    :return: torrentlink: URI of torrent link
    """
    torrentlink = re.findall(rf'torrents\.php\?action=download&amp;id={torrentid}&amp;authkey=(?:[^&]+)&amp;torrent_pass=(?:[^"]+)', torrent_table)[0]
    return torrentlink
