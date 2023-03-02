# Standard library packages
import sys
import re
import os
import configparser

# Third-party packages
from bs4 import BeautifulSoup
from loguru import logger

# jps2sm modules
from jps2sm.get_data import GetGroupData, GetJPSUser
from jps2sm.prepare_data import collate, prepare_torrent
from jps2sm.save_data import download_sm_uploaded_torrents
from jps2sm.batch import batch_mode
from jps2sm.upload_data import set_original_artists
from jps2sm.utils import fatal_error, GetConfig, GetArgs
from jps2sm.myloginsession import jpopsuki


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
        prepare_torrent(data['jps_torrent_object'], data['torrentgroupdata'], **data['release_data_collated'])
        if not dry_run:
            download_sm_uploaded_torrents(torrentcount=1, artist=jps_group_data.artist, title=jps_group_data.title)

    if not dry_run:
        set_original_artists(jps_group_data.contribartists)


if __name__ == "__main__":
    main()
