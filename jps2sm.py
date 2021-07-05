# jps2sm.py is a python script that will automatically gather data from JPS from a given group url, release url,
# or a user's uploaded / seeding torrents and iterate through them and upload them to SM.

# Catch python2 being run here to get a relatively graceful error message, rather than a syntax error later on which causes confusion.
error_x, *error_y = 1, 2, 3, 4  # jps2sm requires requires python3.8, a SyntaxError here means you are running it in python2!

# Catch python < 3.8 being run here to get a relatively graceful error message, rather than a syntax error later on which causes confusion.
print(walrus := "", end='')  # jps2sm requires python3.8, a SyntaxError here means you are running it in python <= 3.7!

# Standard version check that for now it pretty useless
import sys
if sys.version_info < (3, 8):
    print("Error: jps2sm requires python 3.8 to run.", file=sys.stderr)
    exit(1)

# Standard library packages
import re
import os
import datetime
import itertools
import collections
import time
import argparse
import configparser
import html
import json
import logging
from logging.handlers import RotatingFileHandler

# Third-party packages
from bs4 import BeautifulSoup
import torrent_parser as tp
import humanfriendly
from pathlib import Path

# jps2sm modules
from modules.utils import get_valid_filename, count_values_dict, fatal_error, GetConfig
from modules.myloginsession import MyLoginSession, jpopsuki
from modules.constants import Categories, VideoOptions
from modules.mediainfo import get_mediainfo

__version__ = "1.5.1"


def detect_display_swapped_names(userid):
    """
    Detect if the user has original (Japanese/Chinese characters) names shown for Artists and Torrent groups in their torrents.php views
    :param userid:
    :return: True if enabled (bad) or False if disabled (OK)
    """
    user_profile_page = jpopsuki(f"https://jpopsuki.eu/user.php?action=edit&userid={userid}")
    soup = BeautifulSoup(user_profile_page.text, 'html5lib')
    user_form = str(soup.select('#content .thin #userform'))

    # We do both string matches to be extra safe due to the havoc it causes if the user has original characters in torrent lists switched on
    good_setting = user_form.find('<input id="browsejp" name="browsejp" type="checkbox"/>')
    bad_setting = user_form.find('<input checked="checked" id="browsejp" name="browsejp" type="checkbox"/>')

    if (good_setting != -1) and (bad_setting == -1):
        # OK!
        return False
    else:
        # Not OK!
        return True


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
    res = jpopsuki(f"https://jpopsuki.eu/torrents.php?type={mode}&userid={user}")
    soup = BeautifulSoup(res.text, 'html5lib')

    time.sleep(5)  # Sleep as otherwise we hit JPS browse quota

    linkbox = str(soup.select('#content #ajax_torrents .linkbox')[0])
    if not last:
        try:
            last = re.findall(fr'page=([0-9]*)&amp;order_by=s3&amp;order_way=DESC&amp;type={mode}&amp;userid=(?:[0-9]*)&amp;disablegrouping=1(?:\'\);|&amp;action=advanced)"><strong> Last &gt;&gt;</strong>', linkbox)[0]
        except:
            # There is only 1 page of uploads if the 'Last >>' link cannot be found
            last = 1

    logger.debug(f'Batch user is {user}, batch mode is {mode}, first page is {first}, last page is {last}')

    useruploads = {}
    useruploads = collections.defaultdict(list)

    # Parse every torrent page and add to dict, to group together releases into the same group so that they work with
    # the way that uploadtorrent() works.
    for i in range(first, int(last) + 1):
        useruploadurl = fr"https://jpopsuki.eu/torrents.php?page={i}&order_by=s1&order_way=ASC&type={mode}&userid={user}&disablegrouping=1"
        useruploadpage = jpopsuki(useruploadurl)
        logger.info(useruploadurl)
        # print useruploadpage.text
        soup2 = BeautifulSoup(useruploadpage.text, 'html5lib')
        try:
            torrenttable = str(soup2.select('#content #ajax_torrents .torrent_table tbody')[0])
        except IndexError:
            # TODO: Need to add this to every request so it can be handled everywhere, for now it can exist here
            quotaexceeded = re.findall('<title>Browse quota exceeded :: JPopsuki 2.0</title>', useruploadpage.text)
            if quotaexceeded:
                logger.error('Browse quota exceeded :: JPopsuki 2.0')
                sys.exit(1)
            else:
                raise
        alltorrentlinksidsonly = re.findall('torrents.php\?id=([0-9]+)\&amp;torrentid=([0-9]+)', torrenttable)
        logger.info(alltorrentlinksidsonly)
        for groupid, torrentid in alltorrentlinksidsonly:
            useruploads[groupid].append(torrentid)
        time.sleep(5)  # Sleep as otherwise we hit JPS browse quota
    logger.debug(useruploads)
    return useruploads


def removehtmltags(text):
    """
    Strip html tags, used by GetGroupData() on the group description if unable to get bbcode

    """
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


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


def get_user_keys():
    """
    Get SM session authkey and torrent_password_key for use by uploadtorrent()|download_sm_torrent() data dict.
    Uses SM login data
    """
    smpage = sm.retrieveContent("https://sugoimusic.me/torrents.php?id=118")  # Arbitrary page on JPS that has authkey
    soup = BeautifulSoup(smpage.text, 'html5lib')
    rel2 = str(soup.select_one('#torrent_details .group_torrent > td > span > .tooltip'))

    return {
        'authkey': re.findall('authkey=(.*)&amp;torrent_pass=', rel2)[0],
        'torrent_password_key': re.findall(r"torrent_pass=(.+)\" title", rel2)[0]
    }


def download_sm_torrent(torrent_id):
    """
    Downloads the SM torrent if it is a dupe, in this scenario we cannot use downloaduploadedtorrents() as the user
    has not actually uploaded it.

    :param torrent_id: SM torrentid to be downloaded
    :return: name: int: filename of torrent downloaded
    """
    file = jpopsuki(
        'https://sugoimusic.me/torrents.php?action='
        f'download&id={torrent_id}&authkey={authkey}&torrent_pass={torrent_password_key}'
    )
    name = get_valid_filename(
        "SM %s - %s - %s.torrent" % (torrentgroupdata.artist, torrentgroupdata.title, torrent_id)
    )
    path = Path(output.file_dir['smtorrents'], name)
    with open(path, "wb") as f:
        f.write(file.content)

    return name


def decide_music_performance(artists, multiplefiles, duration):
    """
    Return if upload should be a Music Performance or not
    A music performance is a cut from a Music TV show and is 25 mins or less long and therefore also not a TV Show artist

    We assume we are being called if Cat = TV Music

    :return:  str: 'Music Performance' or 'TV Music'
    """
    if multiplefiles is True or duration > 1500000:  # 1 500 000 ms = 25 mins
        return 'TV Music'
    else:  # Single file that is < 25 mins, decide if Music Performance
        if len(artists) > 1:  # Multiple artists
            logger.debug('Upload is a Music Performance as it has derived multiple artists and is 25 mins or less')
            return 'Music Performance'  # JPS TV Show artists never have multiple artists
        JPSartistpage = jpopsuki(f"https://jpopsuki.eu/artist.php?name={artists[0]}")
        soup = BeautifulSoup(JPSartistpage.text, 'html5lib')
        categoriesbox = str(soup.select('#content .thin .main_column .box.center'))
        categories = re.findall(r'\[(.+)\]', categoriesbox)
        if any({*Categories.NonTVCategories} & {*categories}):  # Exclude any TV Shows for being mislabeled as Music Performance
            logger.debug('Upload is a Music Performance as it is 25 mins or less and not a TV Show')
            return 'Music Performance'
        else:
            logger.debug('Upload is not a Music Performance')
            return 'TV Music'


def getalternatefansubcategoryid(artist):
    """
    Attempts to detect the actual category for JPS Fansubs category torrents and if not ask the user to select an alternate category.
    If it is a TV show, this TV show category type is detected and returned, else query the user from a list of potential categories.

    :param artist: str artist name
    :return: int alternative category ID based on Categories.SM()
    """
    JPSartistpage = jpopsuki(f"https://jpopsuki.eu/artist.php?name={artist}")
    soup = BeautifulSoup(JPSartistpage.text, 'html5lib')
    categoriesbox = str(soup.select('#content .thin .main_column .box.center'))
    categories = re.findall(r'\[(.+)\]', categoriesbox)

    if not any({*Categories.NonTVCategories} & {*categories}) and " ".join(categories).count('TV-') == 1:
        # Artist has no music and only 1 TV Category, artist is a TV show and we can auto detect the category for FanSub releases
        autodetectcategory = re.findall(r'(TV-(?:[^ ]+))', " ".join(categories))[0]
        logger.debug(f'Autodetected SM category {autodetectcategory} for JPS Fansubs torrent')
        return autodetectcategory
    else:  # Cannot autodetect
        AlternateFanSubCategoriesIDs = (5, 6, 7, 8, 9, 11)  # Matches indices in Categories()
        logger.warning(f'Cannot auto-detect correct category for torrent group {torrentgroupdata.title}.')
        print('Select Category:')
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
            logger.error('No alternate Fansubs category chosen.')
            return "Fansubs"  # Allow upload to fail
        else:
            category = optionlookup[int(alternatecategoryoption)]
            logger.info(f'Alternate Fansubs category {category} chosen')
            return category


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
    logger.debug(f'Set artist {artist} original artist to {origartist}')


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
                release['slashdata'][index] = f'{remaster_freeleech_removed[0]} - {torrentgroupdata.date[:4]}'  # Use the extracted value and append group JPS release year
                logger.debug(f"Torrent {torrentid} is freeleech remastered, validated remasterdata to {release['slashdata'][index]}")
    for torrentid in removetorrents:
        del (releasedata[torrentid])

    logger.info(f'Selected for upload: {releasedata}')
    return releasedata


def uploadtorrent(torrentpath, groupid=None, **uploaddata):
    """
    Prepare POST data for the SM upload, performs additional validation, reports errors and performs the actual upload to
    SM whilst saving the html result to investigate any errors if they are not reported correctly.

    :param torrentpath: filename of the JPS torrent to be uploaded, also used as save path for SM upload result html page
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

    if not args.parsed.dryrun:
        data['auth'] = authkey

    logger.debug(uploaddata)

    # TODO Most of this can be in getmediainfo()
    if args.parsed.mediainfo:
        try:
            data['mediainfo'], releasedatamediainfo = get_mediainfo(torrentpath, uploaddata['media'], media_roots)
            data.update(releasedatamediainfo)
            if 'duration' in data.keys() and data['duration'] > 1:
                duration_friendly_format = humanfriendly.format_timespan(datetime.timedelta(seconds=int(data['duration'] / 1000)))
                data['album_desc'] += f"\n\nDuration: {duration_friendly_format} - {str(data['duration'])}ms"
        except Exception as mediainfo_exc:
            if str(mediainfo_exc).startswith('Mediainfo error - file/directory not found'):
                pass
            if str(mediainfo_exc).startswith('Mediainfo error - unable to extract what appears to be a Bluray disc:'):
                pass
            if torrentgroupdata.category in Categories.Video:
                raise
            else:
                logger.debug(f'Skipping exception on mediainfo failing as {torrentgroupdata.title} is not a Video category.')

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
        if torrentgroupdata.category == "TV-Music" and args.parsed.mediainfo:
            data['type'] = Categories.SM[decide_music_performance(torrentgroupdata.artist, data['multiplefiles'], data['duration'])]

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

        # If not supplied by getmediainfo() use container found by collate()
        if 'container' not in data.keys():
            data['container'] = uploaddata['container']

        data['sub'] = 'NoSubs'  # assumed default
        data['lang'] = 'CHANGEME'
        for language in languages:  # If we have a language tag, set the language field
            if language.lower() in torrentgroupdata.tagsall:
                data['lang'] = language
    elif torrentgroupdata.category in Categories.Music:
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
        data['type'] = Categories.JPStoSM[decide_ep(torrentpath, uploaddata)]

    if 'type' not in data.keys():  # Set default value after all validation has been done
        data['type'] = Categories.JPStoSM[torrentgroupdata.category]

    # Now that all Category validation is complete decide if we should strip some mediainfo data
    mediainfo_non_resolution = ('container', 'mediainfo')
    mediainfo_resolution = ('ressel', 'resolution')
    if args.parsed.mediainfo and data['type'] in Categories.SM_StripAllMediainfo:
        for field in (mediainfo_non_resolution + mediainfo_resolution):
            data.pop(field, None)
    elif args.parsed.mediainfo and data['type'] == Categories.SM_StripAllMediainfoExcResolution:
        for field in mediainfo_non_resolution:
            data.pop(field, None)

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

    if "V.A." in torrentgroupdata.artist:  # At JPS Various Artists torrents have their artists as contrib artists
        del data['contrib_artists[]']  # Error if null as if there is a V.A. torrent group with no contrib artists something is wrong
        data['idols[]'] = contribartistsenglish
        logger.debug(f'Various Artists torrent, setting main artists to {contribartistsenglish}')
    else:
        data['idols[]'] = torrentgroupdata.artist  # Set the artist normally

    postDataFiles = {
        'file_input': open(torrentpath, 'rb')
    }

    if args.parsed.dryrun or args.parsed.debug:
        dataexcmediainfo = {x: data[x] for x in data if x not in 'mediainfo'}
        dataexcmediainfo['auth'] = '<scrubbed>'
        logger.info(json.dumps(dataexcmediainfo, indent=2))  # Mediainfo shows too much data
    if not args.parsed.dryrun:
        SMres = sm.retrieveContent(uploadurl, "post", data, postDataFiles)

        SMerrorTorrent = re.findall('red; text-align: center;">(.*)</p>', SMres.text)
        if SMerrorTorrent:
            dupe = re.findall('torrentid=([0-9]+)">The exact same torrent file already exists on the site!</a>$', SMerrorTorrent[0])
            if dupe:
                dupe_file_name = download_sm_torrent(dupe[0])
                logger.warning(
                    f'This torrent already exists on SugoiMusic - https://sugoimusic.me/torrents.php?torrentid={dupe[0]} '
                    f'The .torrent has been downloaded with name "{Path(output.file_dir["smtorrents"], dupe_file_name)}"'
                )
                dupe_error_msg = f'The exact same torrent file already exists on the site! See: https://sugoimusic.me/torrents.php?torrentid={dupe[0]} JPS torrent id: {uploaddata["jpstorrentid"]}'
                logger.error(dupe_error_msg)
                raise RuntimeError(dupe_error_msg)
            else:
                logger.error(SMerrorTorrent[0])
                raise RuntimeError(SMerrorTorrent[0])

        SMerrorLogon = re.findall('<p>Invalid (.*)</p>', SMres.text)
        if SMerrorLogon:
            raise RuntimeError(f'Invalid {SMerrorLogon[0]}')

        smuploadresultfilename = "SMuploadresult." + Path(torrentpath).stem + ".html"
        smuploadresultpath = Path(output.file_dir['html'], smuploadresultfilename)

        with open(smuploadresultpath, "w") as f:
            f.write(str(SMres.content))

        groupid = re.findall('<input type="hidden" name="groupid" value="([0-9]+)" />', SMres.text)
        if not groupid:
            # Find groupid if private torrent warning
            groupid = re.findall(r'Your torrent has been uploaded; however, you must download your torrent from <a href="torrents\.php\?id=([0-9]+)">here</a>', SMres.text)
            if not groupid:
                unknown_error_msg = f'Cannot find groupid in SM response - there was probably an unknown error. See {smuploadresultfilename} for potential errors'
                raise RuntimeError(unknown_error_msg)

        if groupid:
            logger.info(f'Torrent uploaded successfully as groupid {groupid[0]}  See https://sugoimusic.me/torrents.php?id={groupid[0]}')

    return groupid


def split_bad_multiple_artists(artists):
    return re.split(', | x | & ', artists)


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
            self.groupdescription = removehtmltags(str(soup.select('#content .thin .main_column .box .body')[0]))

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


def validate_jps_bitrate(jps_bitrate):
    """
    Validate JPS bad bitrates to sensible bitrates ready for upload to SM

    :param jps_bitrate:
    :return: sm_bitrate
    """

    bitrates = {
        "Hi-Res 96/24": "24bit Lossless 96kHz",
        "24bit/48kHz": "24bit Lossless 48kHz",
        "Hi-Res": "24bit Lossless",
        "Hi-Res 48/24": "24bit Lossless 48kHz",
        "24bit/96kHz": "24bit Lossless 96kHz",
        "24bit/48Khz": "24bit Lossless 48kHz",
        "24bit/96Khz": "24bit Lossless 96kHz",
        "24bit/48khz": "24bit Lossless 48kHz",
        "Hi-Res Lossless": "24bit Lossless",
        "160": "Other",
        "Variable": "Other",
        "320 (VBR)": "Other",
        "Scans": "",
        "Booklet": "",
        "1080p": "",
        "720p": "",
        "256 (VBR)": "APS (VBR)",
        "155": "Other"
    }

    sm_bitrate = jps_bitrate  # Default is to leave bitrate alone if not mentioned here, such as bitrates that are OK on both JPS and SM
    for old, new in bitrates.items():
        if jps_bitrate == old:
            sm_bitrate = new

    return sm_bitrate


def decide_exc_filter(audioformat, media, releasedata):
    """
    Implement audioformat and media exclusion filters
    :return: boolean: True or False
    """
    if audioformat == args.parsed.excaudioformat:
        logger.info(f'Excluding {releasedata} as exclude audioformat {args.parsed.excaudioformat} is set')
        return True
    elif media == args.parsed.excmedia:
        logger.info(f'Excluding {releasedata} as exclude media {args.parsed.excmedia} is set')
        return True

    return False


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
    release_group_id = None
    torrentcount = 0
    for torrentid, releasedatafull in getreleasedata(torrentids).items():

        torrentcount += 1
        logger.info(f'Now processing: {torrentid} {releasedatafull}')

        releasedata = releasedatafull['slashdata']
        uploaddatestr = releasedatafull['uploaddate']
        releasedataout = {}
        releasedataout['jpstorrentid'] = torrentid  # Not needed for uploadtorrent(), purely for logging purposes
        remasterdata = False  # Set default

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

        elif releasedata[0] in VideoOptions.badformats and releasedata[2] in VideoOptions.VideoMedias:  # Video torrent mistakenly uploaded as an Album/Single
            # container / 'bitrate' / media   Bitrate is meaningless, users usually select Lossless
            releasedataout['videotorrent'] = True  # For processing by uploadtorrent()
            releasedataout['categorystatus'] = "bad"

            videoreleasedatavalidated = validatejpsvideodata(releasedata, releasedataout['categorystatus'])
            for field, data in videoreleasedatavalidated.items():
                releasedataout[field] = data

            if len(releasedata) == 4:  # Remastered
                remasterdata = releasedata[3]

        elif torrentgroupdata.category in Categories.Music:  # Music torrent
            # format / bitrate / media
            releasedataout['videotorrent'] = False
            releasedataout['categorystatus'] = "good"

            releasedataout['media'] = releasedata[2]
            releasedataout['audioformat'] = releasedata[0]
            releasedataout['bitrate'] = validate_jps_bitrate(releasedata[1])

            if decide_exc_filter(releasedataout['audioformat'], releasedataout['media'], releasedata):
                continue

            if len(releasedata) == 4:  # Remastered
                remasterdata = releasedata[3]

        elif torrentgroupdata.category in Categories.Video:  # Probably Music in a VC group
            # format / media
            releasedataout['videotorrent'] = False
            releasedataout['categorystatus'] = "bad"

            releasedataout['audioformat'] = releasedata[0]
            releasedataout['media'] = releasedata[1]

            if decide_exc_filter(releasedataout['audioformat'], releasedataout['media'], releasedata):
                continue

            if len(releasedata) == 3:  # Remastered
                remasterdata = releasedata[2]

        elif torrentgroupdata.category in Categories.NonReleaseData:  # Pictures or Misc Category torrents
            releasedataout['videotorrent'] = False
            releasedataout['categorystatus'] = "good"

        else:  # We should never reach here
            logger.error('Could not handle release data')
            raise RuntimeError('Could not handle release data')

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
        torrentfile = jpopsuki("https://jpopsuki.eu/%s" % torrentlink)  # Download JPS torrent
        torrentfilename = get_valid_filename(
            "JPS %s - %s - %s.torrent" % (torrentgroupdata.artist, torrentgroupdata.title, "-".join(releasedata)))
        torrentpath = Path(output.file_dir['jpstorrents'], torrentfilename)

        with open(torrentpath, "wb") as f:
            f.write(torrentfile.content)

        # Upload torrent to SM
        # If groupid was returned from a previous call of uploadtorrent() then use it to allow torrents
        # to be uploaded to the same group, else get the groupid from the first run of uploadtorrent()
        # Update: The bug re torrent merging was fixed a long time ago, so we do not need to nest-together
        # uploads like this anymore
        try:
            if release_group_id is None:
                release_group_id = uploadtorrent(torrentpath, **releasedataout)
            else:
                uploadtorrent(torrentpath, release_group_id, **releasedataout)
        except Exception:
            logger.exception('Error in uploadtorrent()')
            raise RuntimeError('Error in uploadtorrent()')

    if not args.parsed.dryrun:
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
        torrentpath = Path(output.file_dir['smtorrents'], torrentfilename)

        with open(torrentpath, "wb") as f:
            f.write(torrentfile.content)
        logger.debug(f'Downloaded SM torrent as {torrentpath}')


def decide_ep(torrentfilename, uploaddata):
    """
    Return if Album upload should be an EP or not.
    EPs are considered to have < 7 tracks, excluding off-vocals and uploaded to JPS as an Album

    We assume we are being called only if Cat = Album

    :param torrentfilename:
    :param uploaddata:
    :return: str: 'EP' or 'Album'
    """

    if uploaddata['media'].lower() == 'bluray' or uploaddata['media'].lower() == 'dvd':
        return 'Album'

    torrent_metadata = tp.parse_torrent_file(torrentfilename)
    music_extensions = ['.flac', '.mp3', '.ogg', '.alac', '.m4a', '.wav', '.wma', '.ra']
    off_vocal_phrases = ['off-vocal', 'offvocal', 'off vocal', 'inst.', 'instrumental', 'english ver', 'japanese ver', 'korean ver']
    track_count = 0
    for file in torrent_metadata['info']['files']:
        if file['path'][-1].lower().endswith('.iso'):
            return 'Album'

        if list(filter(file['path'][-1].lower().endswith, music_extensions)) and \
                not any(substring in file['path'][-1].lower() for substring in off_vocal_phrases):
            #  Count music files which are not an off-vocal or instrumental
            logger.debug(f"Deciding if EP with torrent with these tracks: {file['path'][-1]}")
            track_count += 1

    if track_count < 7:
        logger.debug(f'Upload is an EP as it has {track_count} standard tracks')
        return 'EP'
    else:
        logger.debug(f'Upload is not an EP as it has {track_count} tracks')
        return 'Album'


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


class GetArgs:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
        parser.add_argument('-d', '--debug', help='Enable debug mode', action='store_true')
        parser.add_argument("-u", "--urls", help="JPS URL for a group, or multiple individual releases URLs to be added to the same group", type=str)
        parser.add_argument("-n", "--dryrun", help="Just parse url and show the output, do not add the torrent to SM", action="store_true")
        parser.add_argument("-b", "--batchuser", help="User id for batch user operations, default is user id of SM Username specified in jps2sm.cfg")
        parser.add_argument("-U", "--batchuploaded", help="(Batch mode only) Upload all releases uploaded by you or, if provided, user id specified by --batchuser", action="store_true")
        parser.add_argument("-S", "--batchseeding", help="(Batch mode only) Upload all releases currently seeding by you or, if provided, user id specified by --batchuser", action="store_true")
        parser.add_argument("-s", "--batchstart", help="(Batch mode only) Start at this page", type=int)
        parser.add_argument("-e", "--batchend", help="(Batch mode only) End at this page", type=int)
        parser.add_argument("-exc", "--exccategory", help="(Batch mode only) Exclude a JPS category from upload", type=str)
        parser.add_argument("-exf", "--excaudioformat", help="(Batch mode only) Exclude an audioformat from upload", type=str)
        parser.add_argument("-exm", "--excmedia", help="(Batch mode only) Exclude a media from upload", type=str)
        parser.add_argument("-m", "--mediainfo", help="Search and get mediainfo data from the source file(s) in the directories specified by MediaDirectories. Extract data to set codec, resolution, audio format and container fields as well as the mediainfo field itself.", action="store_true")
        self.parsed = parser.parse_args()


class HandleCfgOutputDirs:
    """
    Handle all config dir logic

    Get data, decide if relative or absolute path and create dir if required
    TODO: Eventually move all cfg logic to a class

    :param config_file_dirs_section: dict: Contents of 'Directories' section in jps2sm.cfg
    """

    def __init__(self, config_file_dirs_section):
        self.config_file_dirs_section = config_file_dirs_section
        self.file_dir = {}
        for (cfg_key, cfg_value) in config_file_dirs_section:
            if Path(cfg_value).is_absolute():
                self.file_dir[cfg_key] = cfg_value
            else:
                self.file_dir[cfg_key] = Path(Path.home(), cfg_value)
            if not Path(self.file_dir[cfg_key]).is_dir():
                Path(self.file_dir[cfg_key]).mkdir(parents=True, exist_ok=True)


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    # console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = RotatingFileHandler(log_file, maxBytes=1048576)
    file_handler.setFormatter(FORMATTER)
    return file_handler


if __name__ == "__main__":
    config = GetConfig()
    args = GetArgs()
    usermode = torrent_password_key = None

    FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
    scriptdir = os.path.dirname(os.path.abspath(sys.argv[0]))
    log_file = scriptdir + '/jps2sm.log'

    logger = logging.getLogger('main')
    if args.parsed.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False

    if not args.parsed.debug:
        sys.tracebacklimit = 0

    if args.parsed.urls is None and not (bool(args.parsed.batchuploaded) or bool(args.parsed.batchseeding)):
        fatal_error('Error: Neither any JPS URL(s) (--urls) or batch parameters (--batchuploaded or --batchseeding) have been specified. See --help')
    elif args.parsed.urls is not None and (bool(args.parsed.batchuploaded) or bool(args.parsed.batchseeding)):
        fatal_error('Error: Both the JPS URL(s) (--urls) and batch parameters (--batchuploaded or --batchseeding) have been specified, but only one is allowed.')
    elif bool(args.parsed.batchuploaded) or bool(args.parsed.batchseeding):

        batchuser = None
        if args.parsed.batchuser:
            if args.parsed.batchuser.isnumeric() is False:
                fatal_error('Error: "--batchuser" or short "-b" should be a JPS profile ID. See --help')
            batchuser = int(args.parsed.batchuser)

        if bool(args.parsed.batchstart) ^ bool(args.parsed.batchend):
            fatal_error('Error: You have specified an incomplete page range. See --help')
        elif bool(args.parsed.batchstart) and bool(args.parsed.batchend):
            batchstart = args.parsed.batchstart
            batchend = args.parsed.batchend
        if bool(args.parsed.batchuploaded) and bool(args.parsed.batchseeding):
            fatal_error('Error: Both batch modes of operation specified - only one can be used at the same time. See --help')
        if args.parsed.batchuploaded:
            batchmode = "uploaded"
        elif args.parsed.batchseeding:
            batchmode = "seeding"
        else:
            raise RuntimeError("Expected some batch mode to be set")

        usermode = True

    output = HandleCfgOutputDirs(config.directories)  # Get config dirs config, handle absolute/relative paths and create if not exist

    # JPS MyLoginSession vars
    loginUrl = "https://jpopsuki.eu/login.php"
    loginTestUrl = "https://jpopsuki.eu"
    successStr = '<div id="extra1"><span></span></div>'
    loginData = {'username': config.jps_user, 'password': config.jps_pass}

    # SM MyLoginSession vars
    SMloginUrl = "https://sugoimusic.me/login.php"
    SMloginTestUrl = "https://sugoimusic.me/"
    SMsuccessStr = "Enabled users"
    SMloginData = {'username': config.sm_user, 'password': config.sm_pass}

    if args.parsed.mediainfo:
        try:
            for media_dir in config.media_roots:
                if not os.path.exists(media_dir):
                    fatal_error(f'Error: Media directory {media_dir} does not exist. Check your configuration in jps2sm.cfg.')
                if not os.path.isdir(media_dir):
                    fatal_error(f'Error: Media directory {media_dir} is a file and not a directory. Check your configuration in jps2sm.cfg.')
        except configparser.NoSectionError:
            fatal_error('Error: --mediainfo requires you to configure MediaDirectories in jps2sm.cfg for mediainfo to find your file(s).')

    # s = MyLoginSession(loginUrl, loginData, loginTestUrl, successStr)

    if not args.parsed.dryrun:
        sm = MyLoginSession(SMloginUrl, SMloginData, SMloginTestUrl, SMsuccessStr)
        # We only want this run ONCE per instance of the script
        userkeys = get_user_keys()
        authkey = userkeys['authkey']
        torrent_password_key = userkeys['torrent_password_key']

    jps_user_id = get_jps_user_id()
    logger.debug(f"JPopsuki user id is {jps_user_id}")

    if detect_display_swapped_names(jps_user_id):
        fatal_error("Error: 'Display original Artist/Album titles' is enabled in your JPS user profile. This must be disabled for jps2sm to run.")

    if usermode:
        batchuser = args.parsed.batchuser or jps_user_id
        if args.parsed.batchstart and args.parsed.batchend:
            useruploads = getbulktorrentids(batchmode, batchuser, args.parsed.batchstart, args.parsed.batchend)
        else:
            useruploads = getbulktorrentids(batchmode, batchuser)
        useruploadsgrouperrors = collections.defaultdict(list)
        useruploadscollateerrors = collections.defaultdict(list)
        user_upload_dupes = []
        user_upload_dupes_jps = []
        user_upload_source_data_not_found = []
        user_upload_mediainfo_not_submitted = 0

        user_uploads_found = count_values_dict(useruploads)
        user_uploads_done = 0
        logger.info(f'Now attempting to upload {user_uploads_found} torrents.')

        for key, value in useruploads.items():
            groupid = key
            torrentids = value
            try:
                logger.info('-------------------------')
                torrentgroupdata = GetGroupData("https://jpopsuki.eu/torrents.php?id=%s" % groupid)
                if torrentgroupdata.category == args.parsed.exccategory:
                    logger.debug(f'Excluding groupid {groupid} as it is {torrentgroupdata.category} group and these are being skipped')
                    continue
            except KeyboardInterrupt:  # Allow Ctrl-C to exit without showing the error multiple times and polluting the final error dict
                break  # Still continue to get error dicts and dupe list so far
            except Exception:
                # Catch all for any exception
                logger.exception('Error with retrieving group data for groupid %s trorrentid(s) %s, skipping upload' % (groupid, ",".join(torrentids)))
                useruploadsgrouperrors[groupid] = torrentids
                continue

            try:
                torrentcount = collate(torrentids)
                if not args.parsed.dryrun:
                    downloaduploadedtorrents(torrentcount)
                    user_uploads_done += torrentcount
            except KeyboardInterrupt:  # Allow Ctrl-C to exit without showing the error multiple times and polluting the final error dict
                break  # Still continue to get error dicts and dupe list so far
            except Exception as exc:
                if str(exc).startswith('The exact same torrent file already exists on the site!'):
                    sm_dupe_torrentid, jps_dupe_torrentid = re.findall(r'The exact same torrent file already exists on the site! See: https://sugoimusic\.me/torrents\.php\?torrentid=([0-9]+) JPS torrent id\: ([0-9]+)', str(exc))[0]
                    user_upload_dupes.append(sm_dupe_torrentid)
                    user_upload_dupes_jps.append(jps_dupe_torrentid)
                elif str(exc).startswith('Mediainfo error - file/directory not found'):
                    # Need to get filename that was not found
                    missing_file = re.findall(r'Mediainfo error - file/directory not found: (.+) in any of the MediaDirectories', str(exc))
                    user_upload_source_data_not_found.append(missing_file)
                elif str(exc).startswith('You do not appear to have entered any MediaInfo data for your video upload.'):
                    user_upload_mediainfo_not_submitted += 1
                else:
                    # Catch all for any exception
                    logger.exception(f'Error with collating/retrieving release data for {groupid} torrentid(s) {",".join(torrentids)}, skipping upload')
                    useruploadscollateerrors[groupid] = torrentids

                continue

        if useruploadsgrouperrors:
            logger.error('The following JPS groupid(s) (torrentid(s) shown for reference) had errors in retrieving group data, '
                  'keep this data safe and you can possibly retry with it in a later version:')
            logger.error(useruploadsgrouperrors)
            logger.error(f'Total: {count_values_dict(useruploadsgrouperrors)}')
        if useruploadscollateerrors:
            logger.error('The following JPS groupid(s) and corresponding torrentid(s) had errors either in collating/retrieving '
                  'release data or in performing the actual upload to SM (although group data was retrieved OK), '
                  'keep this data safe and you can possibly retry with it in a later version:')
            logger.error(useruploadscollateerrors)
            logger.error(f'Total: {count_values_dict(useruploadscollateerrors)}')
        if user_upload_dupes:
            logger.warning('The following SM torrentid(s) have already been uploaded to the site, but the SM torrents were downloaded so you can cross seed:')
            logger.warning(f'SM duplicate torrent ids: {user_upload_dupes}\nJPS duplicate torrent ids: {user_upload_dupes_jps}')
            logger.warning(f'Total: {len(user_upload_dupes)}')
        if user_upload_source_data_not_found:
            logger.error('The following file(s)/dir(s) were not found in your MediaDirectories specified in jps2sm.cfg and the upload was skipped:')
            logger.error(user_upload_source_data_not_found)
            logger.error(f'Total: {len(user_upload_source_data_not_found)}')

        logger.info(f'Finished batch upload\n--------------------------------------------------------\nOverall stats:'
                    f'\nTorrents found at JPS: {user_uploads_found}\nGroup data errors: {count_values_dict(useruploadsgrouperrors)}'
                    f'\nRelease data (or any other) errors: {count_values_dict(useruploadscollateerrors)}'
                    f'\nMediaInfo source data missing: {len(user_upload_source_data_not_found)}'
                    f'\nMediaInfo not submitted errors (use \"--mediainfo\" to fix): {user_upload_mediainfo_not_submitted}')
        if not args.parsed.dryrun:
            logger.error(f'\nNew uploads successfully created: {user_uploads_done}'
                         f'\nDuplicates found (torrents downloaded for cross-seeding): {len(user_upload_dupes)}')
    else:
        # Standard non-batch upload using --urls
        if not args.parsed.urls:
            raise RuntimeError("Expected some JPS urls to be set")
        torrentgroupdata = GetGroupData(args.parsed.urls)
        torrentids = re.findall('torrentid=([0-9]+)', args.parsed.urls)
        torrentcount = collate(torrentids)
        if not args.parsed.dryrun:
            downloaduploadedtorrents(torrentcount)
