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
import html
import json
import logging
from logging.handlers import RotatingFileHandler
import io

# Third-party packages
from bs4 import BeautifulSoup
import humanfriendly
from pathlib import Path

# jps2sm modules
from jps2sm.get_data import GetGroupData, get_jps_group_data_class, get_user_keys, get_jps_user_id, get_torrent_link, get_release_data
from jps2sm.batch import get_batch_jps_group_torrent_ids, get_batch_group_data
from jps2sm.utils import get_valid_filename, count_values_dict, fatal_error, GetConfig, GetArgs, HandleCfgOutputDirs, decide_duplicate
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
    if origartist == "":  # If there is no origartist at JPS do not bother trying to set it here
        return

    SMartistpage = sugoimusic(f"https://sugoimusic.me/artist.php?artistname={artist}")

    if re.findall("Your search did not match anything", SMartistpage.text):
        logger.debug(f"Artist {artist} does not yet exist at SM so origartist cannot be set")
        return

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


def uploadtorrent(jps_torrent_object, torrentgroupdata, **uploaddata):
    """
    Prepare POST data for the SM upload, performs additional validation, reports errors and performs the actual upload to
    SM whilst saving the html result to investigate any errors if they are not reported correctly.

    :param jps_torrent_object: bytes: BytesIO object of the JPS torrent
    :param groupid: groupid to upload to - allows to upload torrents to the same group
    :param uploaddata: dict of collated / validated release data from collate()
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
            dupe = re.findall('torrentid=([0-9]+)">The exact same torrent file already exists on the site!</a>$', SMerrorTorrent[0])
            if dupe:
                if not config.skip_dupes:
                    dupe_file_name = download_sm_torrent(dupe[0], torrentgroupdata.artist, torrentgroupdata.title)
                    logger.warning(
                        f'This torrent already exists on SugoiMusic - https://sugoimusic.me/torrents.php?torrentid={dupe[0]} '
                        f'The .torrent has been downloaded with name "{Path(output.file_dir["smtorrents"], dupe_file_name)}"'
                    )
                dupe_error_msg = f'The exact same torrent file already exists on the site! See: https://sugoimusic.me/torrents.php?torrentid={dupe[0]} JPS torrent id: {uploaddata["jpstorrentid"]}'
                logger.info(dupe_error_msg)
                raise Exception(dupe_error_msg)
            else:
                logger.error(SMerrorTorrent[0])
                raise Exception(SMerrorTorrent[0])

        SMerrorLogon = re.findall('<p>Invalid (.*)</p>', SMres.text)
        if SMerrorLogon:
            raise Exception(f'Invalid {SMerrorLogon[0]}')

        html_debug_output_filename = f"SMuploadresult.{torrentgroupdata.artist[0]}.{torrentgroupdata.title}.{torrentgroupdata.date}.JPS_ID{uploaddata['jpstorrentid']}.html"
        html_debug_output_path = Path(output.file_dir['html'], html_debug_output_filename)

        with open(html_debug_output_path, "w") as f:
            f.write(str(SMres.content))

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


def collate(torrentids, torrentgroupdata, max_size=None, scrape_only=False):
    """
    Collate and validate data ready for upload to SM

    Validate and process dict supplied by getreleasedata() with format, bitrate, media, container, codec, and remaster data to extract
    all available data from JPS
    Perform validation on some fields
    Download JPS torrent
    Apply filters via decide_exc_filter()
    Send data to uploadtorrent()
    Send data to setorigartists()

    :param torrentids: list of JPS torrentids to be processed
            Always a single torrentid unless specifying a group url in --url mode
    :param torrentgroupdata: dictionary with torrent group data from getgroupdata[]
    :param max_size: bool: Only upload torrents < 1Gb if True
    :param scrape_only: bool: Only download JPS torrents, do not upload to SM
    """
    jps_torrent_downloaded_count = sm_torrent_uploaded_count = skipped_max_size = skipped_low_seeders = skipped_exc_filter = skipped_dupe = 0

    for torrentid, releasedatafull in get_release_data(torrentids, torrentgroupdata.rel2, torrentgroupdata.date).items():

        logger.info(f'Now processing: {torrentid} {releasedatafull}')

        if max_size and releasedatafull['size_units'] == "GB":
            # Currently only a max_size of 1Gb is supported.
            # Very simple way of just using the units, if we do not see 'GB' then it is < 1 Gb
            # TODO Add option to specify the file size
            skipped_max_size += 1
            logger.debug("Skipping as torrent is >=1Gb")
            continue

        if int(releasedatafull['seeders']) < 1:
            logger.debug('Skipping as torrent has no seeders')
            skipped_low_seeders += 1
            continue

        releasedata = releasedatafull['slashdata']
        uploaddatestr = releasedatafull['uploaddate']
        # size_no_units = releasedatafull['size_no_units']  # TODO Use this
        # size_units = releasedatafull['size_units']
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
                skipped_exc_filter += 1
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
                skipped_exc_filter += 1
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
        jps_torrent_file = jpopsuki("https://jpopsuki.eu/%s" % torrentlink)  # Download JPS torrent
        jps_torrent_filename = get_valid_filename(
            "JPS %s - %s - %s.torrent" % (torrentgroupdata.artist, torrentgroupdata.title, "-".join(releasedata)))
        jps_torrent_path = Path(output.file_dir['jpstorrents'], jps_torrent_filename)

        with open(jps_torrent_path, "wb") as f:
            f.write(jps_torrent_file.content)

        jps_torrent_downloaded_count += 1

        if scrape_only:
            continue

        jps_torrent_object = io.BytesIO(jps_torrent_file.content)  # Keep file in memory as it could be processed and deleted by a torrent client

        if not args.parsed.dryrun:
            dupe, sugoimusic_torrent_id = decide_duplicate(jps_torrent_object)
            if dupe:
                if not config.skip_dupes:
                    dupe_file_name = download_sm_torrent(sugoimusic_torrent_id, torrentgroupdata.artist, torrentgroupdata.title)
                    # torrentgroupdata.artist and torrentgroupdata.title is just to generate a pretty filename
                    logger.warning(
                        f'This torrent already exists on SugoiMusic - https://sugoimusic.me/torrents.php?torrentid={sugoimusic_torrent_id} '
                        f'The .torrent has been downloaded with name "{Path(output.file_dir["smtorrents"], dupe_file_name)}"'
                    )
                dupe_error_msg = f'The exact same torrent file already exists on the site! See: https://sugoimusic.me/torrents.php?torrentid={sugoimusic_torrent_id} JPS torrent id: {torrentid}'
                logger.warning(dupe_error_msg)
                skipped_dupe += 1
                continue
                # raise Exception(dupe_error_msg)

        # Upload torrent to SM
        uploadtorrent(jps_torrent_object, torrentgroupdata, **releasedataout)

        sm_torrent_uploaded_count += 1

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

    collate_torrent_counts = {
        'jps_torrents_downloaded_count': jps_torrent_downloaded_count,
        'sm_torrents_uploaded_count': sm_torrent_uploaded_count,  # For use by downloaduploadedtorrents() or statisics when in a batch_mode
        'skipped_torrents_max_size': skipped_max_size,
        'skipped_torrents_low_seeders': skipped_low_seeders,
        'skipped_torrents_exc_filter': skipped_exc_filter,
        'skipped_torrents_duplicate': skipped_dupe
    }

    # logger.debug(collate_torrent_counts)

    return collate_torrent_counts


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

    batch_status = None

    def batch_stats(final_stats):
        """
        Return statistics from a batch upload.
        If using --recent mode it returns initial statistics after JPS torrents have been scraped, followed by final_stats after the
        SM upload.

        TODO: Needs some cleaning up, but this is better than the stats being completely duplicated as it was before
        """
        if final_stats:
            print('Finished batch upload')
        print(f'--------------------------------------------------------\nOverall stats:'
              f'\nTorrents found at JPS: {user_uploads_found}'
              f'\nJPS Group data errors: {count_values_dict(batch_uploads_group_errors)}')

        if final_stats:
            print(f'Release data errors: {count_values_dict(useruploadscollateerrors)}')
        else:
            print(f'Release data errors: Not yet analysed')

        print(f'Torrents skipped due to max_size filter: {batch_uploads_skipped_torrents_max_size}'
              f'\nTorrents skipped due to low seeders: {batch_uploads_skipped_torrents_low_seeders}'
              f'\nJPS Torrents downloaded: {batch_uploads_jps_torrents_downloaded_count}'
              )
        if final_stats:
            if args.parsed.mediainfo:
                print(f'MediaInfo source data missing: {len(user_upload_source_data_not_found)}')
            if not args.parsed.dryrun:
                logger.info(f'MediaInfo not submitted errors (use \"--mediainfo\" to fix): {user_upload_mediainfo_not_submitted}'
                            f'\n\nNew uploads successfully created: {user_uploads_done}'
                            f'\nDuplicates found on SM (torrents downloaded for cross-seeding): {len(user_upload_dupes)}'
                            f'\nDuplicates found with torrent hash: {batch_uploads_skipped_dupe}')



    if args.parsed.urls is None and not (bool(args.parsed.batchuploaded) or bool(args.parsed.batchseeding) or bool(args.parsed.batchsnatched) or bool(args.parsed.batchrecent)):
        fatal_error('Error: Neither any JPS URL(s) (--urls) or batch parameters (--batchsnatched, --batchuploaded, --batchseeding or --batchrecent) have been specified. See --help')
    elif args.parsed.urls is not None and (bool(args.parsed.batchuploaded) or bool(args.parsed.batchseeding) or bool(args.parsed.batchsnatched) or bool(args.parsed.batchrecent)):
        fatal_error(
            'Error: Both the JPS URL(s) (--urls) and batch parameters (--batchsnatched,--batchuploaded, --batchseeding or --batchrecent) have been specified, but only one is allowed.')
    elif bool(args.parsed.batchuploaded) or bool(args.parsed.batchseeding) or bool(args.parsed.batchsnatched) or bool(args.parsed.batchrecent):

        batchuser = max_size = None
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
            batch_mode = "uploaded"
        elif args.parsed.batchseeding:
            batch_mode = "seeding"
        elif args.parsed.batchsnatched:
            batch_mode = "snatched"
        elif args.parsed.batchrecent:
            batch_mode = "recent"
            max_size = True
        else:
            raise RuntimeError("Expected some batch mode to be set")

        batch_status = True

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

    if batch_status:
        batchuser = args.parsed.batchuser or jps_user_id
        if args.parsed.batchstart and args.parsed.batchend:
            batch_uploads = get_batch_jps_group_torrent_ids(mode=batch_mode, user=batchuser, first=args.parsed.batchstart, last=args.parsed.batchend,
                                                            sort=args.parsed.batchsort, order=args.parsed.batchsortorder)
        else:
            batch_uploads = get_batch_jps_group_torrent_ids(mode=batch_mode, user=batchuser, sort=args.parsed.batchsort, order=args.parsed.batchsortorder)
        useruploadscollateerrors = collections.defaultdict(list)
        user_upload_dupes = []
        user_upload_dupes_jps = []
        user_upload_source_data_not_found = []
        user_upload_mediainfo_not_submitted = 0

        user_uploads_found = count_values_dict(batch_uploads)
        user_uploads_done = 0

        batch_uploads_skipped_torrents_max_size = batch_uploads_skipped_torrents_low_seeders = batch_uploads_jps_torrents_downloaded_count = 0
        batch_uploads_skipped_torrents_exc_filter = batch_uploads_skipped_dupe = 0

        logger.info(f'Now attempting to upload {user_uploads_found} torrents.')

        batch_group_data, batch_uploads_group_errors, batch_groups_excluded = get_batch_group_data(batch_uploads, args.parsed.exccategory)
        # print(json.dumps(batch_group_data, indent=2))

        if batch_mode == "recent":
            # Do an initial run of collate() to grab the JPS torrents only so data can be downloaded first
            # TODO Extract release data logic so that collate() does not need to be called twice.
            batch_uploads_jps_torrents_downloaded_count = 0

            for jps_group_id, jps_torrent_ids in batch_uploads.items():
                if jps_group_id in batch_uploads_group_errors or jps_group_id in batch_groups_excluded:
                    # Skip group if GetGroupData() failed or the group is being excluded by the '-exc' parameter
                    continue

                jps_group_data = get_jps_group_data_class(batch_group_data, jps_group_id)

                scrape_only = True

                try:
                    torrent_counts = collate(jps_torrent_ids, jps_group_data, max_size, scrape_only)
                    batch_uploads_jps_torrents_downloaded_count += torrent_counts["jps_torrents_downloaded_count"]
                    batch_uploads_skipped_torrents_max_size += torrent_counts['skipped_torrents_max_size']
                    batch_uploads_skipped_torrents_low_seeders += torrent_counts['skipped_torrents_low_seeders']
                    batch_uploads_skipped_torrents_exc_filter += torrent_counts['skipped_torrents_exc_filter']
                    batch_uploads_skipped_dupe += torrent_counts['skipped_torrents_duplicate']

                except Exception as exc:
                    logger.exception(f'Exception  - {exc} - in collate() on initial run with recent batch mode, however these are skipped'
                                     'as they will be handled in the next run.')
                    continue

            batch_stats(final_stats=False)

            input('When these files have been downloaded press enter to continue...')

        batch_uploads_skipped_torrents_max_size = batch_uploads_skipped_torrents_low_seeders = batch_uploads_jps_torrents_downloaded_count = 0
        batch_uploads_skipped_torrents_exc_filter = 0
        #batch_count_stats = {
        #    'batch_uploads_skipped_torrents_max_size': 0,
        #    'batch_uploads_skipped_torrents_low_seeders': 0,
        #    'batch_uploads_jps_torrents_downloaded_count': 0,
        #    'batch_uploads_skipped_torrents_exc_filter': 0
        #}

        for jps_group_id, jps_torrent_ids in batch_uploads.items():
            if jps_group_id in batch_uploads_group_errors or jps_group_id in batch_groups_excluded:
                # Skip group if GetGroupData() failed or the group is being excluded by the '-exc' parameter
                continue

            jps_group_data = get_jps_group_data_class(batch_group_data, jps_group_id)

            try:
                torrent_counts = collate(jps_torrent_ids, jps_group_data, max_size)
                #for collate_result_item, value in torrent_counts.items():
                #    if isinstance(value, int):
                #        batch_count_stats[collate_result_item] += value
                #    elif isinstance(value, list):
                #        batch_count_stats[collate_result_item].append(value)

                batch_uploads_jps_torrents_downloaded_count += torrent_counts["jps_torrents_downloaded_count"]
                batch_uploads_skipped_torrents_max_size += torrent_counts['skipped_torrents_max_size']
                batch_uploads_skipped_torrents_low_seeders += torrent_counts['skipped_torrents_low_seeders']
                batch_uploads_skipped_torrents_exc_filter += torrent_counts['skipped_torrents_exc_filter']
                batch_uploads_skipped_dupe += torrent_counts['skipped_torrents_duplicate']
                if not args.parsed.dryrun:
                    downloaduploadedtorrents(torrent_counts['sm_torrents_uploaded_count'], jps_group_data.artist, jps_group_data.title)
                    user_uploads_done += torrent_counts['sm_torrents_uploaded_count'] #  This will always be same as '+=1'
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
                        f'Error with collating/retrieving release data for {jps_group_id} torrentid(s) {",".join(jps_torrent_ids)}, skipping upload')
                    useruploadscollateerrors[jps_group_id] = jps_torrent_ids
                continue

        if batch_uploads_group_errors:
            logger.error('The following JPS groupid(s) (torrentid(s) shown for reference) had errors in retrieving group data, '
                         'keep this data safe and you can possibly retry with it in a later version:')
            logger.error(batch_uploads_group_errors)
            logger.error(f'Total: {count_values_dict(batch_uploads_group_errors)}')
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

        batch_stats(final_stats=True)

    else:
        # Standard non-batch upload using --urls
        if not args.parsed.urls:
            raise RuntimeError("Expected some JPS urls to be set")
        jps_group_data = GetGroupData(args.parsed.urls)
        jps_torrent_ids = re.findall('torrentid=([0-9]+)', args.parsed.urls)
        torrent_counts = collate(jps_torrent_ids, jps_group_data)
        if not args.parsed.dryrun:
            downloaduploadedtorrents(torrent_counts['sm_torrents_uploaded_count'], jps_group_data.artist, jps_group_data.title)


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
