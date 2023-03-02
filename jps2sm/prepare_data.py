"""
Prepare data from get_data and send it to upload_data/save_data modules
"""
# pylint: disable=no-name-in-module,import-error
# pylint appears to have a bug where it cannot import despite python itself being able to


# Standard library packages
import datetime

# Third-party packages
import io
import json
import re

import humanfriendly
from datasize import DataSize
from loguru import logger

# jps2sm modules
from jps2sm.constants import VideoOptions, Categories
from jps2sm.get_data import get_release_data, GetSMUser
from jps2sm.mediainfo import get_mediainfo
from jps2sm.save_data import get_jps_torrent, download_jps_torrent, download_sm_torrent
from jps2sm.upload_data import upload_torrent
from jps2sm.utils import GetConfig, GetArgs, decide_duplicate
from jps2sm.validation import validate_jps_video_data, validate_jps_bitrate, decide_exc_filter, decide_music_performance, \
    get_alternate_fansub_category_id, decide_ep


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
            release_data_collated['videotorrent'] = True  # For processing by prepare_torrent()
            release_data_collated['categorystatus'] = "good"

            #videoreleasedatavalidated = validate_jps_video_data(slash_data, release_data_collated['categorystatus'])
            for field, data in validate_jps_video_data(slash_data, release_data_collated['categorystatus']).items():
                release_data_collated[field] = data

            if len(slash_data) == 3:  # Remastered
                remaster_data = slash_data[2]

        elif slash_data[0] in VideoOptions.badformats and slash_data[2] in VideoOptions.VideoMedias:
            # Video torrent mistakenly uploaded as an Album/Single
            # container / 'bitrate' / media   Bitrate is meaningless, users usually select Lossless
            release_data_collated['videotorrent'] = True  # For processing by prepare_torrent()
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

        # prepare_torrent() will use the upload date as release date if the torrent has no release date, usually for
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


def prepare_torrent(jps_torrent_object, torrent_group_data, **release_data_collated):
    """
    Prepare POST data for the SM upload, performs additional validation, reports errors and performs the actual upload to
    SM whilst saving the html result to investigate any errors if they are not reported correctly.

    :param jps_torrent_object: bytes: BytesIO object of the JPS torrent
    :param torrent_group_data: JPSGroup data from GetGroupData
    :param release_data_collated: dict of collated / validated release data from collate()
    """
    config = GetConfig()
    args = GetArgs()
    languages = ('Japanese', 'English', 'Korean', 'Chinese', 'Vietnamese')

    sugoimusic_upload_data = {
        'submit': 'true',
        'title': torrent_group_data.title,
        'tags': torrent_group_data.tagsall,
        'album_desc': torrent_group_data.groupdescription,
        # 'release_desc': releasedescription
    }

    if torrent_group_data.date is None:  # If release date cannot be derived use upload date
        sugoimusic_upload_data['year'] = release_data_collated['uploaddate']
    else:
        sugoimusic_upload_data['year'] = torrent_group_data.date

    if not args.parsed.dryrun:
        sm_user = GetSMUser()
        sugoimusic_upload_data['auth'] = sm_user.auth_key()

    logger.debug(release_data_collated)

    # TODO Most of this can be in getmediainfo()
    if args.parsed.mediainfo:
        try:
            sugoimusic_upload_data['mediainfo'], releasedatamediainfo = get_mediainfo(jps_torrent_object, release_data_collated['media'], config.media_roots)
            sugoimusic_upload_data.update(releasedatamediainfo)
            if 'duration' in sugoimusic_upload_data.keys() and sugoimusic_upload_data['duration'] > 1:
                duration_friendly_format = humanfriendly.format_timespan(datetime.timedelta(seconds=int(sugoimusic_upload_data['duration'] / 1000)))
                sugoimusic_upload_data['album_desc'] += f"\n\nDuration: {duration_friendly_format} - {str(sugoimusic_upload_data['duration'])}ms"
        except Exception as mediainfo_exc:
            if str(mediainfo_exc).startswith('Mediainfo error - file/directory not found'):
                pass
            if str(mediainfo_exc).startswith('Mediainfo error - unable to extract what appears to be a Bluray disc:'):
                pass
            if torrent_group_data.category in Categories.Video:
                raise
            else:
                logger.debug(f'Skipping exception on mediainfo failing as {torrent_group_data.title} is not a Video category.')

    if torrent_group_data.category not in Categories.NonReleaseData:
        sugoimusic_upload_data['media'] = release_data_collated['media']
        if 'audioformat' not in sugoimusic_upload_data.keys():  # If not supplied by getmediainfo() use audioformat guessed by collate()
            sugoimusic_upload_data['audioformat'] = release_data_collated['audioformat']

    if torrent_group_data.imagelink is not None:
        sugoimusic_upload_data['image'] = torrent_group_data.imagelink

    if release_data_collated['videotorrent']:
        if torrent_group_data.category == "DVD" and release_data_collated['media'] == 'Bluray':
            sugoimusic_upload_data['type'] = Categories.JPStoSM['Bluray']  # JPS has no Bluray category
        if release_data_collated['categorystatus'] == 'bad':  # Need to set a correct category
            if release_data_collated['media'] == 'Bluray':
                sugoimusic_upload_data['type'] = Categories.JPStoSM['Bluray']
            else:  # Still need to change the category to something, if not a Bluray then even if it is not a DVD the most sensible category is DVD in a music torrent group
                sugoimusic_upload_data['type'] = Categories.JPStoSM['DVD']
        if torrent_group_data.category == "TV-Music" and args.parsed.mediainfo:
            sugoimusic_upload_data['type'] = Categories.SM[decide_music_performance(torrent_group_data.artist, sugoimusic_upload_data['multiplefiles'], sugoimusic_upload_data['duration'])]

        # If not supplied by getmediainfo() use codec found by collate()
        if 'codec' not in sugoimusic_upload_data.keys():
            sugoimusic_upload_data['codec'] = release_data_collated['codec']

        # If not supplied by getmediainfo() try to detect resolution by searching the group description for resolutions
        if 'ressel' not in sugoimusic_upload_data.keys():
            foundresolutions720 = re.findall('1080 ?x ?720', torrent_group_data.groupdescription)
            foundresolutions1080 = re.findall('1920 ?x ?1080', torrent_group_data.groupdescription)
            if len(foundresolutions720) != 0:
                sugoimusic_upload_data['ressel'] = "720p"
            elif len(foundresolutions1080) != 0:
                sugoimusic_upload_data['ressel'] = "1080p"
            for resolution in VideoOptions.resolutions:  # Now set more specific resolutions if they are present
                if resolution in torrent_group_data.groupdescription:  # If we can see the resolution in the group description then set it
                    sugoimusic_upload_data['ressel'] = resolution
                else:
                    sugoimusic_upload_data['ressel'] = 'CHANGEME'

        # If not supplied by getmediainfo() use container found by collate()
        if 'container' not in sugoimusic_upload_data.keys():
            sugoimusic_upload_data['container'] = release_data_collated['container']

        sugoimusic_upload_data['sub'] = 'NoSubs'  # assumed default
        sugoimusic_upload_data['lang'] = 'CHANGEME'
        for language in languages:  # If we have a language tag, set the language field
            if language.lower() in torrent_group_data.tagsall:
                sugoimusic_upload_data['lang'] = language
    elif torrent_group_data.category in Categories.Music:
        sugoimusic_upload_data['bitrate'] = release_data_collated['bitrate']

    if 'remastertitle' in release_data_collated.keys():
        sugoimusic_upload_data['remaster'] = 'remaster'
        sugoimusic_upload_data['remastertitle'] = release_data_collated['remastertitle']
    if 'remasteryear' in release_data_collated.keys():
        sugoimusic_upload_data['remaster'] = 'remaster'
        sugoimusic_upload_data['remasteryear'] = release_data_collated['remasteryear']

    # Non-BR/DVD/TV-* category validation
    # TODO Move this to a def
    if torrent_group_data.category == "Fansubs":
        sugoimusic_upload_data['type'] = get_alternate_fansub_category_id(torrent_group_data.artist, torrent_group_data.title)  # Title just for user
        sugoimusic_upload_data['sub'] = 'Hardsubs'  # We have subtitles! Subs in JPS FanSubs are usually Hardsubs so guess as this
        # TODO: Use torrent library to look for sub/srt files
    elif torrent_group_data.category == "Album":  # Ascertain if upload is EP
        sugoimusic_upload_data['type'] = Categories.JPStoSM[decide_ep(jps_torrent_object, release_data_collated)]

    if 'type' not in sugoimusic_upload_data.keys():  # Set default value after all validation has been done
        sugoimusic_upload_data['type'] = Categories.JPStoSM[torrent_group_data.category]

    # Now that all Category validation is complete decide if we should strip some mediainfo data
    mediainfo_non_resolution = ('container', 'mediainfo')
    mediainfo_resolution = ('ressel', 'resolution')
    if args.parsed.mediainfo and sugoimusic_upload_data['type'] in Categories.SM_StripAllMediainfo:
        for field in (mediainfo_non_resolution + mediainfo_resolution):
            sugoimusic_upload_data.pop(field, None)
    elif args.parsed.mediainfo and sugoimusic_upload_data['type'] == Categories.SM_StripAllMediainfoExcResolution:
        for field in mediainfo_non_resolution:
            sugoimusic_upload_data.pop(field, None)

    try:
        sugoimusic_upload_data['artist_jp'] = torrent_group_data.originalartist
        sugoimusic_upload_data['title_jp'] = torrent_group_data.originaltitle
    except AttributeError:  # If no originalchars do nothing
        pass

    try:
        contribartistsenglish = []
        for artist, origartist in torrent_group_data.contribartists.items():
            contribartistsenglish.append(artist)
        sugoimusic_upload_data['contrib_artists[]'] = contribartistsenglish
    except AttributeError:  # If no contrib artists do nothing
        pass

    if "V.A." in torrent_group_data.artist:  # At JPS Various Artists torrents have their artists as contrib artists
        del sugoimusic_upload_data['contrib_artists[]']  # Error if null as if there is a V.A. torrent group with no contrib artists something is wrong
        sugoimusic_upload_data['idols[]'] = contribartistsenglish
        logger.debug(f'Various Artists torrent, setting main artists to {contribartistsenglish}')
    else:
        sugoimusic_upload_data['idols[]'] = torrent_group_data.artist  # Set the artist normally

    jps_torrent_object.seek(0)

    sugoimusic_upload_files = {
        # We need to specify a filename  now we are using BytesIO and SM will validate files without a .torrent extension
        'file_input': ('blah.torrent', jps_torrent_object)
    }

    if args.parsed.dryrun or args.parsed.debug:
        dataexcmediainfo = {x: sugoimusic_upload_data[x] for x in sugoimusic_upload_data if x not in 'mediainfo'}
        dataexcmediainfo['auth'] = '<scrubbed>'
        logger.info(json.dumps(dataexcmediainfo, indent=2))  # Mediainfo shows too much data

    sugoimusic_upload_data['jps_torrent_id'] = release_data_collated['jpstorrentid']

    if not args.parsed.dryrun:
        upload_torrent(sugoimusic_upload_data, sugoimusic_upload_files)
