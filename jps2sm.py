# jps2sm.py is a python script that will automatically gather data from JPS from a given group url, release url,
# or a user's uploaded / seeding torrents and iterate through them and upload them to SM.

# Catch python2 being run here to get a relatively graceful error message, rather than a syntax error later on which causes confusion.
from typing import List, Any

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
import collections
import time
import configparser
import html
import json
import logging
from logging.handlers import RotatingFileHandler

# Third-party packages
from bs4 import BeautifulSoup
import humanfriendly
from pathlib import Path

# jps2sm modules
from jps2sm.get_data import GetGroupData, get_user_keys, get_jps_user_id, get_torrent_link, get_release_data
from jps2sm.utils import get_valid_filename, count_values_dict, fatal_error, GetConfig, GetArgs, HandleCfgOutputDirs
from jps2sm.myloginsession import MyLoginSession, jpopsuki, sugoimusic
from jps2sm.constants import Categories, VideoOptions
from jps2sm.mediainfo import get_mediainfo
from jps2sm.validation import decide_music_performance, get_alternate_fansub_category_id, validate_jps_video_data, validate_jps_bitrate, \
    decide_exc_filter, decide_ep


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

    :param mode: Area to get bulk torrent ids from, 'uploaded' for a user's uploads, 'seeding' for torrents currently seeding and 'snatched' for a user's snatched torrents
    :param user: JPS userid
    :param first: upload page number to start at
    :param last: upload page to finish at
    :return: useruploads: dict
    """

    sort_by = {
        'name': 's1',
        'year': 's2',
        'time': 's3', # snatched time for snatched, seeding time for seeding, added for uploaded
        'size': 's4',
        'snatches': 's5',
        'seeders':  's6',
        'leechers': 's7'
    }

    if mode == 'snatched' or mode == 'uploaded':
        sort_mode = sort_by['time']
    elif mode == 'seeding':
        sort_mode = sort_by['name']

    res = jpopsuki(f"https://jpopsuki.eu/torrents.php?type={mode}&userid={user}")
    soup = BeautifulSoup(res.text, 'html5lib')

    time.sleep(5)  # Sleep as otherwise we hit JPS browse quota

    linkbox = str(soup.select('#content #ajax_torrents .linkbox')[0])
    if not last:
        try:
            last = re.findall(
                fr'page=([0-9]*)&amp;order_by=s3&amp;order_way=DESC&amp;type={mode}&amp;userid=(?:[0-9]*)&amp;disablegrouping=1(?:\'\);|&amp;action=advanced)"><strong> Last &gt;&gt;</strong>',
                linkbox)[0]
        except:
            # There is only 1 page of uploads if the 'Last >>' link cannot be found
            last = 1

    logger.debug(f'Batch user is {user}, batch mode is {mode}, first page is {first}, last page is {last}')

    useruploads = {}
    useruploads = collections.defaultdict(list)

    # Parse every torrent page and add to dict, to group together releases into the same group so that they work with
    # the way that uploadtorrent() works.
    for i in range(first, int(last) + 1):
        useruploadurl = fr"https://jpopsuki.eu/torrents.php?page={i}&order_by={sort_mode}&order_way=ASC&type={mode}&userid={user}&disablegrouping=1"
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


def download_sm_torrent(torrent_id, artist, title):
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
        "SM %s - %s - %s.torrent" % (artist, title, torrent_id)
    )
    path = Path(output.file_dir['smtorrents'], name)
    with open(path, "wb") as f:
        f.write(file.content)

    return name


def setorigartist(artist, origartist):
    """
    Set an artist's original artist with the string origartist, currently used for contrib artists
    # TODO Consider using this for main orig artist

    :param artist: string: String of the artist that needs it's original artist set
    :param origartist: string: Original artist
    """
    SMartistpage = sugoimusic(f"https://sugoimusic.me/artist.php?artistname={artist}")
    soup = BeautifulSoup(SMartistpage.text, 'html5lib')
    linkbox = str(soup.select('#content .thin .header .linkbox'))
    artistid = re.findall(r'href="artist\.php\?action=edit&amp;artistid=([0-9]+)"', linkbox)[0]

    data = {
        'action': 'edit',
        'auth': authkey,
        'artistid': artistid,
        'name_jp': origartist
    }

    SMeditartistpage = sugoimusic(f'https://sugoimusic.me/artist.php?artistname={artist}', 'post', data)
    logger.debug(f'Set artist {artist} original artist to {origartist}')


def uploadtorrent(torrentpath, torrentgroupdata, groupid=None, **uploaddata):
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
            data['mediainfo'], releasedatamediainfo = get_mediainfo(torrentpath, uploaddata['media'], config.media_roots)
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
        data['type'] = get_alternate_fansub_category_id(torrentgroupdata.artist, torrentgroupdata.title)  # Title just for user
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
        SMres = sugoimusic(uploadurl, "post", data, postDataFiles)

        SMerrorTorrent = re.findall('red; text-align: center;">(.*)</p>', SMres.text)
        if SMerrorTorrent:
            dupe = re.findall('torrentid=([0-9]+)">The exact same torrent file already exists on the site!</a>$', SMerrorTorrent[0])
            if dupe:
                dupe_file_name = download_sm_torrent(dupe[0], torrentgroupdata.artist, torrentgroupdata.title)
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
            groupid = re.findall(
                r'Your torrent has been uploaded; however, you must download your torrent from <a href="torrents\.php\?id=([0-9]+)">here</a>',
                SMres.text)
            if not groupid:
                unknown_error_msg = f'Cannot find groupid in SM response - there was probably an unknown error. See {smuploadresultfilename} for potential errors'
                raise RuntimeError(unknown_error_msg)

        if groupid:
            logger.info(f'Torrent uploaded successfully as groupid {groupid[0]}  See https://sugoimusic.me/torrents.php?id={groupid[0]}')

    return groupid


def collate(torrentids, torrentgroupdata):
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
    for torrentid, releasedatafull in get_release_data(torrentids, torrentgroupdata.rel2, torrentgroupdata.date).items():

        torrentcount += 1
        logger.info(f'Now processing: {torrentid} {releasedatafull}')

        releasedata = releasedatafull['slashdata']
        uploaddatestr = releasedatafull['uploaddate']
        releasedataout = {}
        releasedataout['jpstorrentid'] = torrentid  # Not needed for uploadtorrent(), purely for logging purposes
        remasterdata = False  # Set default

        # JPS uses the audioformat field (represented as releasedata[0] here) for containers and codecs in video torrents,
        # and when combined with VideoMedias we can perform VideoTorrent detection.
        if releasedata[0] in VideoOptions.badformats and releasedata[
            1] in VideoOptions.VideoMedias:  # VideoCategory torrent, this also detects VideoCategories in a non-VC group
            # container / media
            releasedataout['videotorrent'] = True  # For processing by uploadtorrent()
            releasedataout['categorystatus'] = "good"

            videoreleasedatavalidated = validate_jps_video_data(releasedata, releasedataout['categorystatus'])
            for field, data in videoreleasedatavalidated.items():
                releasedataout[field] = data

            if len(releasedata) == 3:  # Remastered
                remasterdata = releasedata[2]

        elif releasedata[0] in VideoOptions.badformats and releasedata[
            2] in VideoOptions.VideoMedias:  # Video torrent mistakenly uploaded as an Album/Single
            # container / 'bitrate' / media   Bitrate is meaningless, users usually select Lossless
            releasedataout['videotorrent'] = True  # For processing by uploadtorrent()
            releasedataout['categorystatus'] = "bad"

            videoreleasedatavalidated = validate_jps_video_data(releasedata, releasedataout['categorystatus'])
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

        torrentlink = html.unescape(get_torrent_link(torrentid, torrentgroupdata.rel2))
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
                release_group_id = uploadtorrent(torrentpath, torrentgroupdata, **releasedataout)
            else:
                uploadtorrent(torrentpath, torrentgroupdata, release_group_id, **releasedataout)
        except Exception:
            logger.exception('Error in uploadtorrent()')
            raise RuntimeError('Error in uploadtorrent()')

    return torrentcount  # For use by downloaduploadedtorrents()


def downloaduploadedtorrents(torrentcount, artist, title):
    """
    Get last torrentcount torrent DL links that user uploaded using SM API and download them

    :param torrentcount: count of recent torrent links to be downloaded
    :return:
    """

    if torrentcount == 0:
        return

    user_recents = sugoimusic(f"https://sugoimusic.me/ajax.php?action=user_recents&limit={torrentcount}")
    user_recents_json = json.loads(user_recents.text)

    smtorrentlinks = {}
    for torrentdata in user_recents_json['response']['uploads']:  # Get list of SM torrent links
        smtorrentlinks[torrentdata['torrentid']] = torrentdata['torrentdl']

    for torrentid, torrentlink in smtorrentlinks.items():
        torrentfile = sugoimusic(torrentlink)
        torrentfilename = get_valid_filename(f'SM {artist} - {title} - {torrentid}.torrent')
        torrentpath = Path(output.file_dir['smtorrents'], torrentfilename)

        with open(torrentpath, "wb") as f:
            f.write(torrentfile.content)
        logger.debug(f'Downloaded SM torrent as {torrentpath}')


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    # console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = RotatingFileHandler(log_file, maxBytes=1048576)
    file_handler.setFormatter(FORMATTER)
    return file_handler


def main():
    """
    This code was formally in if __name__ == "__main__" and was moved to eventually find and remove all globals

    TODO: Split up this def into separate defs

    :return:
    """

    usermode = None

    if args.parsed.urls is None and not (bool(args.parsed.batchuploaded) or bool(args.parsed.batchseeding) or bool(args.parsed.batchsnatched)):
        fatal_error('Error: Neither any JPS URL(s) (--urls) or batch parameters (--batchsnatched, --batchuploaded or --batchseeding) have been specified. See --help')
    elif args.parsed.urls is not None and (bool(args.parsed.batchuploaded) or bool(args.parsed.batchseeding) or bool(args.parsed.batchsnatched)):
        fatal_error(
            'Error: Both the JPS URL(s) (--urls) and batch parameters (--batchsnatched,--batchuploaded or --batchseeding) have been specified, but only one is allowed.')
    elif bool(args.parsed.batchuploaded) or bool(args.parsed.batchseeding) or bool(args.parsed.batchsnatched):

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
        if bool(args.parsed.batchuploaded) and (bool(args.parsed.batchseeding) or bool(args.parsed.batchsnatched)) or \
           (bool(args.parsed.batchseeding) and bool(args.parsed.batchsnatched)): # https://stackoverflow.com/a/3076081
            fatal_error('Error: Multiple batch modes of operation specified - only one can be used at the same time. See --help')
        if args.parsed.batchuploaded:
            batchmode = "uploaded"
        elif args.parsed.batchseeding:
            batchmode = "seeding"
        elif args.parsed.batchsnatched:
            batchmode = "snatched"
        else:
            raise RuntimeError("Expected some batch mode to be set")

        usermode = True

    if args.parsed.mediainfo:
        try:
            for media_dir in config.media_roots:
                if not os.path.exists(media_dir):
                    fatal_error(f'Error: Media directory {media_dir} does not exist. Check your configuration in jps2sm.cfg.')
                if not os.path.isdir(media_dir):
                    fatal_error(f'Error: Media directory {media_dir} is a file and not a directory. Check your configuration in jps2sm.cfg.')
        except configparser.NoSectionError:
            fatal_error('Error: --mediainfo requires you to configure MediaDirectories in jps2sm.cfg for mediainfo to find your file(s).')

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
                logger.exception(
                    'Error with retrieving group data for groupid %s trorrentid(s) %s, skipping upload' % (groupid, ",".join(torrentids)))
                useruploadsgrouperrors[groupid] = torrentids
                continue

            group_torrents_count = 0

            for jps_torrent_id in torrentids:
                try:
                    group_torrents_count += collate([jps_torrent_id], torrentgroupdata)
                except KeyboardInterrupt:  # Allow Ctrl-C to exit without showing the error multiple times and polluting the final error dict
                    break  # Still continue to get error dicts and dupe list so far
                except Exception as exc:
                    if str(exc).startswith('The exact same torrent file already exists on the site!'):
                        sm_dupe_torrentid, jps_dupe_torrentid = re.findall(
                            r'The exact same torrent file already exists on the site! See: https://sugoimusic\.me/torrents\.php\?torrentid=([0-9]+) JPS torrent id\: ([0-9]+)',
                            str(exc))[0]
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
                        logger.exception(
                            f'Error with collating/retrieving release data for {groupid} torrentid(s) {",".join(torrentids)}, skipping upload')
                        useruploadscollateerrors[groupid] = torrentids

                    continue

            if not args.parsed.dryrun:
                downloaduploadedtorrents(group_torrents_count, torrentgroupdata.artist, torrentgroupdata.title)
                user_uploads_done += group_torrents_count

                # Add original artists for contrib artists
                if torrentgroupdata.contribartists:
                    for artist, origartist in torrentgroupdata.contribartists.items():
                        # For every artist, go to its artist page to get artist ID, then use this to go to
                        # artist.php?action=edit with the orig artist
                        setorigartist(artist, origartist)

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
            logger.warning(
                'The following SM torrentid(s) have already been uploaded to the site, but the SM torrents were downloaded so you can cross seed:')
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
        torrentcount = collate(torrentids, torrentgroupdata)

        if not args.parsed.dryrun:
            downloaduploadedtorrents(torrentcount, torrentgroupdata.artist, torrentgroupdata.title)

            if torrentgroupdata.contribartists:
                for artist, origartist in torrentgroupdata.contribartists.items():
                    # For every artist, go to its artist page to get artist ID, then use this to go to
                    # artist.php?action=edit with the orig artist
                    setorigartist(artist, origartist)


if __name__ == "__main__":
    args = GetArgs()
    config = GetConfig()
    output = HandleCfgOutputDirs(config.directories)  # Get config dirs config, handle absolute/relative paths and create if not exist

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

    if not args.parsed.dryrun:
        # We only want this run ONCE per instance of the script
        # TODO Move to a class
        userkeys = get_user_keys()
        authkey = userkeys['authkey']
        torrent_password_key = userkeys['torrent_password_key']

    if not args.parsed.debug:
        sys.tracebacklimit = 0

    main()
