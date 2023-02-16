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
import configparser
import json
import io

# Third-party packages
from bs4 import BeautifulSoup
import humanfriendly
from pathlib import Path
from loguru import logger
from datasize import DataSize

# jps2sm modules
from jps2sm.get_data import GetGroupData, get_release_data, GetJPSUser, GetSMUser
from jps2sm.save_data import save_sm_html_debug_output, download_sm_uploaded_torrents, download_sm_torrent, get_jps_torrent, download_jps_torrent
from jps2sm.batch import batch_mode
from jps2sm.utils import fatal_error, GetConfig, GetArgs, decide_duplicate
from jps2sm.myloginsession import jpopsuki, sugoimusic
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


def setorigartist(artist, origartist):
    """
    Set an artist's original artist with the string origartist, currently used for contrib artists
    # TODO Consider using this for main orig artist

    :param artist: string: String of the artist that needs it's original artist set
    :param origartist: string: Original artist
    """
    if origartist == "":  # If there is no origartist at JPS do not bother trying to set it here
        return

    SMartistpage = sugoimusic(f"https://sugoimusic.me/artist.php?artistname={artist}")

    if re.findall("Your search did not match anything", SMartistpage.text):
        logger.debug(f"Artist {artist} does not yet exist at SM so origartist cannot be set")
        return

    soup = BeautifulSoup(SMartistpage.text, 'html5lib')
    linkbox = str(soup.select('#content .thin .header .linkbox'))
    artistid = re.findall(r'href="artist\.php\?action=edit&amp;artistid=([0-9]+)"', linkbox)[0]

    sm_user = GetSMUser()

    data = {
        'action': 'edit',
        'auth': sm_user.auth_key(),
        'artistid': artistid,
        'name_jp': origartist
    }

    SMeditartistpage = sugoimusic(f'https://sugoimusic.me/artist.php?artistname={artist}', 'post', data)
    logger.debug(f'Set artist {artist} original artist to {origartist}')


def uploadtorrent(jps_torrent_object, torrentgroupdata, **uploaddata):
    """
    Prepare POST data for the SM upload, performs additional validation, reports errors and performs the actual upload to
    SM whilst saving the html result to investigate any errors if they are not reported correctly.

    :param jps_torrent_object: bytes: BytesIO object of the JPS torrent
    :param groupid: groupid to upload to - allows to upload torrents to the same group
    :param uploaddata: dict of collated / validated release data from collate()
    """
    config = GetConfig()
    args = GetArgs()
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

    sm_user = GetSMUser()

    if not args.parsed.dryrun:
        data['auth'] = sm_user.auth_key()

    logger.debug(uploaddata)

    # TODO Most of this can be in getmediainfo()
    if args.parsed.mediainfo:
        try:
            data['mediainfo'], releasedatamediainfo = get_mediainfo(jps_torrent_object, uploaddata['media'], config.media_roots)
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
        data['type'] = Categories.JPStoSM[decide_ep(jps_torrent_object, uploaddata)]

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

    try:
        data['artist_jp'] = torrentgroupdata.originalartist
        data['title_jp'] = torrentgroupdata.originaltitle
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

    jps_torrent_object.seek(0)

    postDataFiles = {
        # We need to specify a filename  now we are using BytesIO and SM will validate files without a .torrent extension
        'file_input': ('blah.torrent', jps_torrent_object)
    }

    if args.parsed.dryrun or args.parsed.debug:
        dataexcmediainfo = {x: data[x] for x in data if x not in 'mediainfo'}
        dataexcmediainfo['auth'] = '<scrubbed>'
        logger.info(json.dumps(dataexcmediainfo, indent=2))  # Mediainfo shows too much data
    if not args.parsed.dryrun:
        SMres = sugoimusic(uploadurl, "post", data, postDataFiles)

        SMerrorTorrent = re.findall('red; text-align: center;">(.*)</p>', SMres.text)
        if SMerrorTorrent:
            raise Exception(SMerrorTorrent[0])

        SMerrorLogon = re.findall('<p>Invalid (.*)</p>', SMres.text)
        if SMerrorLogon:
            raise Exception(f'Invalid {SMerrorLogon[0]}')

        html_debug_output_path = save_sm_html_debug_output(SMres.text, torrentgroupdata, uploaddata['jpstorrentid'])

        groupid = re.findall('<input type="hidden" name="groupid" value="([0-9]+)" />', SMres.text)
        if not groupid:
            # Find groupid if private torrent warning
            groupid = re.findall(
                r'Your torrent has been uploaded; however, you must download your torrent from <a href="torrents\.php\?id=([0-9]+)">here</a>',
                SMres.text)
            if not groupid:
                unknown_error_msg = f'Cannot find groupid in SM response - there was probably an unknown error. See {html_debug_output_path} for potential errors'
                raise RuntimeError(unknown_error_msg)

        if groupid:
            logger.info(f'Torrent uploaded successfully as groupid {groupid[0]}  See https://sugoimusic.me/torrents.php?id={groupid[0]}')


def collate(torrentids, torrentgroupdata, max_size=None):
    """
    Collate and validate data ready for upload to SM

    Validate and process dict supplied by getreleasedata() with format, bitrate, media, container, codec, and remaster data to extract
    all available data from JPS
    Perform validation on some fields
    Download JPS torrent
    Apply filters via decide_exc_filter()
    Send data to setorigartists()

    :param torrentids: list of JPS torrentids to be processed
            Always a single torrentid unless specifying a group url in --url mode
    :param torrentgroupdata: dictionary with torrent group data from getgroupdata[]
    :param max_size: str: Maximum size with unit specified, currently only used by recent mode
    """
    config = GetConfig()
    args = GetArgs()

    jps_torrent_downloaded_count = skipped_max_size = skipped_low_seeders = skipped_exc_filter = skipped_dupe_torrent_hash = 0
    dupe_jps_ids = []
    dupe_sm_ids = []
    jps_torrent_collated_data = {}

    for jps_torrent_id, release_data in get_release_data(torrentids, torrentgroupdata.torrent_table, torrentgroupdata.date).items():

        logger.info(f'Now processing: {jps_torrent_id} {release_data}')

        if max_size:
            good_jps_format = release_data['size_units'][:1] + "i" + release_data['size_units'][1:]  # JPS uses 'GB' when it means 'GiB' etc.
            jps_torrent_size_in_bytes = DataSize(release_data['size_no_units'] + good_jps_format)
            cfg_max_size_in_bytes = DataSize(max_size)
            if jps_torrent_size_in_bytes > cfg_max_size_in_bytes:
                skipped_max_size += 1
                logger.debug(f"Skipping as torrent is > {max_size}")
                continue

        if int(release_data['seeders']) < config.jps_min_seeders:
            logger.debug(f'Skipping as torrent has < {config.jps_min_seeders} seeder(s)')
            skipped_low_seeders += 1
            continue

        slash_data = release_data['slashdata']
        uploaddatestr = release_data['uploaddate']
        release_data_collated = {'jpstorrentid': jps_torrent_id}
        remaster_data = False  # Set default

        # JPS uses the audioformat field (represented as slash_data[0] here) for containers and codecs in video torrents,
        # and when combined with VideoMedias we can perform VideoTorrent detection.
        if slash_data[0] in VideoOptions.badformats and slash_data[1] in VideoOptions.VideoMedias:
            # VideoCategory torrent, this also detects VideoCategories in a non-VC group
            # container / media
            release_data_collated['videotorrent'] = True  # For processing by uploadtorrent()
            release_data_collated['categorystatus'] = "good"

            #videoreleasedatavalidated = validate_jps_video_data(slash_data, release_data_collated['categorystatus'])
            for field, data in validate_jps_video_data(slash_data, release_data_collated['categorystatus']).items():
                release_data_collated[field] = data

            if len(slash_data) == 3:  # Remastered
                remaster_data = slash_data[2]

        elif slash_data[0] in VideoOptions.badformats and slash_data[2] in VideoOptions.VideoMedias:
            # Video torrent mistakenly uploaded as an Album/Single
            # container / 'bitrate' / media   Bitrate is meaningless, users usually select Lossless
            release_data_collated['videotorrent'] = True  # For processing by uploadtorrent()
            release_data_collated['categorystatus'] = "bad"

            videoreleasedatavalidated = validate_jps_video_data(slash_data, release_data_collated['categorystatus'])
            for field, data in videoreleasedatavalidated.items():
                release_data_collated[field] = data

            if len(slash_data) == 4:  # Remastered
                remaster_data = slash_data[3]

        elif torrentgroupdata.category in Categories.Music:  # Music torrent
            # format / bitrate / media
            release_data_collated['videotorrent'] = False
            release_data_collated['categorystatus'] = "good"

            release_data_collated['media'] = slash_data[2]
            release_data_collated['audioformat'] = slash_data[0]
            release_data_collated['bitrate'] = validate_jps_bitrate(slash_data[1])

            if decide_exc_filter(release_data_collated['audioformat'], release_data_collated['media'], slash_data):
                skipped_exc_filter += 1
                continue

            if len(slash_data) == 4:  # Remastered
                remaster_data = slash_data[3]

        elif torrentgroupdata.category in Categories.Video:  # Probably Music in a VC group
            # format / media
            release_data_collated['videotorrent'] = False
            release_data_collated['categorystatus'] = "bad"

            release_data_collated['audioformat'] = slash_data[0]
            release_data_collated['media'] = slash_data[1]

            if decide_exc_filter(release_data_collated['audioformat'], release_data_collated['media'], slash_data):
                skipped_exc_filter += 1
                continue

            if len(slash_data) == 3:  # Remastered
                remaster_data = slash_data[2]

        elif torrentgroupdata.category in Categories.NonReleaseData:  # Pictures or Misc Category torrents
            release_data_collated['videotorrent'] = False
            release_data_collated['categorystatus'] = "good"

        else:  # We should never reach here
            logger.error('Could not handle release data')
            raise RuntimeError('Could not handle release data')

        if remaster_data:
            try:
                remaster_text = re.findall('(.*) - (.*)$', remaster_data)[0]
                release_data_collated['remastertitle'] = remaster_text[0]
                remaster_year = remaster_text[1]
            except IndexError:  # Torrent is remastered and only has year set
                remaster_year = remaster_data  # The whole string is just the year

            # Year is mandatory on JPS so most remastered releases have current year set as year. This looks ugly on SM (and JPS) so if the
            # year is the groupdata['year'] we will not set it.
            year = re.findall('([0-9]{4})(?:.*)', torrentgroupdata.date)[0]
            if year != remaster_year:
                release_data_collated['remasteryear'] = remaster_year

        if 'WEB' in slash_data:  # Media validation
            release_data_collated['media'] = 'Web'
        elif 'Blu-Ray' in slash_data:
            release_data_collated['media'] = 'Bluray'  # JPS may actually be calling it the correct official name, but modern usage differs.

        # uploadtorrent() will use the upload date as release date if the torrent has no release date, usually for
        # Picture Category torrents and some TV-Variety.
        release_data_collated['uploaddate'] = datetime.datetime.strptime(uploaddatestr, '%b %d %Y, %H:%M').strftime('%Y%m%d')

        jps_torrent_file = get_jps_torrent(jps_torrent_id, torrentgroupdata)
        jps_torrent_object = io.BytesIO(jps_torrent_file.content)  # Keep file in memory as it could be processed and deleted by a torrent client

        if dupe_sugoimusic_torrent_id := decide_duplicate(jps_torrent_object):
            skipped_dupe_torrent_hash += 1

        if dupe_sugoimusic_torrent_id and config.skip_dupes:
            logger.debug(f'Not downloading JPS torrent {jps_torrent_id} as it is a duplicate on SM as torrent {dupe_sugoimusic_torrent_id}'
                         f' and SkipDuplicates is true in cfg.')
        else:
            download_jps_torrent(jps_torrent_file, torrentgroupdata, slash_data)
            logger.debug(f'downloaded jps torrent {jps_torrent_id}')
            jps_torrent_downloaded_count += 1

        if not args.parsed.dryrun and dupe_sugoimusic_torrent_id:
            if not config.skip_dupes:
                dupe_file_path = download_sm_torrent(dupe_sugoimusic_torrent_id, torrentgroupdata.artist, torrentgroupdata.title)
                # torrentgroupdata.artist and torrentgroupdata.title is just to generate a pretty filename
                logger.warning(
                    f'This torrent already exists on SugoiMusic - https://sugoimusic.me/torrents.php?torrentid={dupe_sugoimusic_torrent_id} '
                    f'The .torrent has been downloaded with name "{dupe_file_path}"'
                )
            dupe_error_msg = f'The exact same torrent file already exists on the site! See: https://sugoimusic.me/torrents.php?torrentid={dupe_sugoimusic_torrent_id} JPS torrent id: {jps_torrent_id}'
            logger.warning(dupe_error_msg)
            dupe_jps_ids.append(int(jps_torrent_id))
            dupe_sm_ids.append(int(dupe_sugoimusic_torrent_id))
            continue

        jps_torrent_collated_data[jps_torrent_id] = {}
        jps_torrent_collated_data[jps_torrent_id]['jps_torrent_object'] = jps_torrent_object
        jps_torrent_collated_data[jps_torrent_id]['torrentgroupdata'] = torrentgroupdata
        jps_torrent_collated_data[jps_torrent_id]['release_data_collated'] = release_data_collated

    if not args.parsed.dryrun:
        # Add original artists for contrib artists
        if torrentgroupdata.contribartists:
            for artist, origartist in torrentgroupdata.contribartists.items():
                # For every artist, go to its artist page to get artist ID, then use this to go to artist.php?action=edit with the orig artist
                try:
                    setorigartist(artist, origartist)
                except IndexError:  # Do not let a setorigartist error affect stats
                    logger.debug(f'Error in setting artist {artist} origartist {origartist}')
                    pass

    collate_torrent_info = {
        'jps_torrent_collated_data': jps_torrent_collated_data,
        'jps_torrents_downloaded_count': jps_torrent_downloaded_count,
        'skipped_torrents_max_size': skipped_max_size,
        'skipped_torrents_low_seeders': skipped_low_seeders,
        'skipped_torrents_exc_filter': skipped_exc_filter,
        'skipped_torrents_duplicate': skipped_dupe_torrent_hash,
        'dupe_jps_ids': dupe_jps_ids,
        'dupe_sm_ids': dupe_sm_ids,
    }

    return collate_torrent_info


def main():
    args = GetArgs()

    if args.parsed.debug:
        stderr_log_level = "DEBUG"
    else:
        stderr_log_level = "INFO"
    logger.remove()
    logger.add(sys.stderr, format="<lvl>{message}</>", level=stderr_log_level)
    logger.add("jps2sm.log", level="DEBUG", rotation="1 MB")

    if not args.parsed.debug:
        sys.tracebacklimit = 0

    if args.parsed.mediainfo:
        config = GetConfig()
        try:
            for media_dir in config.media_roots:
                if not os.path.exists(media_dir):
                    fatal_error(f'Error: Media directory {media_dir} does not exist. Check your configuration in jps2sm.cfg.')
                if not os.path.isdir(media_dir):
                    fatal_error(f'Error: Media directory {media_dir} is a file and not a directory. Check your configuration in jps2sm.cfg.')
        except configparser.NoSectionError:
            fatal_error('Error: --mediainfo requires you to configure MediaDirectories in jps2sm.cfg for mediainfo to find your file(s).')

    jps_user = GetJPSUser()
    jps_user_id = jps_user.user_id()
    logger.debug(f"JPopsuki user id is {jps_user_id}")

    if detect_display_swapped_names(jps_user_id):
        fatal_error("Error: 'Display original Artist/Album titles' is enabled in your JPS user profile. This must be disabled for jps2sm to run.")

    if args.parsed.torrentid:
        non_batch_upload(jps_torrent_id=args.parsed.torrentid, dry_run=args.parsed.dryrun, wait_for_jps_dl=args.parsed.wait_for_jps_dl)
        return

    if args.parsed.urls:
        non_batch_upload(jps_urls=args.parsed.urls, dry_run=args.parsed.dryrun, wait_for_jps_dl=args.parsed.wait_for_jps_dl)
        return

    if args.batch_modes == 1:
        batch_mode_user = args.parsed.batchuser or jps_user_id
        batch_mode(mode=args.batch_mode, user=batch_mode_user, start=args.parsed.batchstart,
                   end=args.parsed.batchend, sort=args.parsed.batchsort, order=args.parsed.batchsortorder)
    else:
        # If we reach here something has gone very wrong with parsing args
        raise RuntimeError('Argument handling error')


def non_batch_upload(jps_torrent_id=None, jps_urls=None, dry_run=None, wait_for_jps_dl=False):
    """
    Perform simple non-batch upload to SM with either a single jps_torrent_id from --torrentid or a string of --urls
    """

    if jps_torrent_id and jps_urls:
        raise RuntimeError('Expected either jps_torrent_id OR jps_url')

    if jps_torrent_id:
        jps_group_data = GetGroupData(f"https://jpopsuki.eu/torrents.php?torrentid={jps_torrent_id}")
        # This is a hack to ensure the get_release_data() works as it is designed to only parse a list of strs
        jps_torrent_ids = [str(jps_torrent_id)]
    elif jps_urls:
        jps_group_data = GetGroupData(jps_urls)
        jps_torrent_ids = re.findall('torrentid=([0-9]+)', jps_urls)
    else:
        raise RuntimeError('Expected either a jps_torrent_id or a jps_url')

    collate_torrent_info = collate(torrentids=jps_torrent_ids, torrentgroupdata=jps_group_data)

    if wait_for_jps_dl:
        input('When these files have been downloaded press enter to continue...')

    for jps_torrent_id, data in collate_torrent_info['jps_torrent_collated_data'].items():
        uploadtorrent(data['jps_torrent_object'], data['torrentgroupdata'], **data['release_data_collated'])
    if not dry_run:
        download_sm_uploaded_torrents(collate_torrent_info['sm_torrents_uploaded_count'], jps_group_data.artist, jps_group_data.title)


if __name__ == "__main__":
    main()
