"""
Perform batch processing functions for the --batch* arguments
"""
# pylint: disable=no-name-in-module,import-error
# pylint appears to have a bug where it cannot import despite python itself being able to
# pylint: disable=fixme

# Standard library packages
import collections
import time
import re
import sys

# Third-party packages
from bs4 import BeautifulSoup
from loguru import logger

# jps2sm modules
from jps2sm.get_data import GetGroupData, get_jps_group_data_class
from jps2sm.myloginsession import jpopsuki
from jps2sm.save_data import download_sm_uploaded_torrents
from jps2sm.utils import GetArgs, count_values_dict, GetConfig
from jps2sm.constants import JPSTorrentView


def batch_mode(mode, user, start=1, end=None, sort=None, order=None):
    """
    Operate batch upload mode
    """
    from jps2sm.jps2sm import collate, prepare_torrent, set_original_artists
    args = GetArgs()

    def batch_stats(final_stats, media_info_mode, dry_run):
        """
        Return statistics from a batch upload.
        If using --recent mode it returns initial statistics after JPS torrents have been scraped, followed by final_stats after the
        SM upload.

        TODO: Needs some cleaning up, but this is better than the stats being completely duplicated as it was before
        """
        print(f'--------------------------------------------------------\nOverall stats:'
              f'\nTorrents found at JPS: {batch_uploads_found}'
              f'\nJPS Group data errors: {count_values_dict(batch_uploads_group_errors)}'
              f'\nJPS Groups excluded by user: {len(batch_groups_excluded)}'
              f'\nJPS "V.A." Groups with no contributing artists: {len(batch_groups_va_errors)}'
              f'\nJPS Release data errors: {count_values_dict(batch_upload_collate_errors)}'
              f'\nTorrents skipped due to max_size filter: {batch_torrent_info["skipped_torrents_max_size"]}'
              f'\nTorrents skipped due to low seeders: {batch_torrent_info["skipped_torrents_low_seeders"]}'  
              f'\nTorrents excluded by user: {batch_torrent_info["skipped_torrents_exc_filter"]}'
              f'\nDuplicates found with torrent hash: {batch_torrent_info["skipped_torrents_duplicate"]}'
              f'\nJPS Torrents downloaded: {batch_torrent_info["jps_torrents_downloaded_count"]}'
              )
        if final_stats:
            if media_info_mode:
                print(f'MediaInfo source data missing: {len(batch_upload_source_data_not_found)}')
            if not dry_run:
                logger.info(f'MediaInfo not submitted errors (use \"--mediainfo\" to fix): {batch_upload_mediainfo_not_submitted}'
                            f'\n\nSM upload errors: {sm_upload_errors}'
                            f'\nNew uploads successfully created: {sm_torrents_uploaded_count}'
                            )

    batch_uploads = get_batch_jps_group_torrent_ids(mode=mode, user=user, first=start, last=end, sort=sort, order=order)

    # batch_uploads = { '362613': ['535927'], '354969': ['535926'], '362612': ['535925'], '362611': ['535924'], '181901': ['535923'], '181902': ['535922'] }

    batch_upload_collate_errors = collections.defaultdict(list)
    batch_upload_source_data_not_found = []
    batch_upload_mediainfo_not_submitted = 0
    sm_upload_errors = 0
    sm_torrents_uploaded_count = 0

    batch_uploads_found = count_values_dict(batch_uploads)

    batch_torrent_info = {
        'skipped_torrents_max_size': 0,
        'skipped_torrents_low_seeders': 0,
        'jps_torrents_downloaded_count': 0,
        'skipped_torrents_exc_filter': 0,
        'skipped_torrents_duplicate': 0,
        'dupe_jps_ids': [],
        'dupe_sm_ids': [],
    }

    logger.info(f'Now attempting to upload {batch_uploads_found} torrents.')

    batch_group_data, batch_uploads_group_errors, batch_groups_excluded, batch_groups_va_errors = get_batch_group_data(batch_uploads, args.parsed.exccategory)
    # print(json.dumps(batch_group_data, indent=2))

    max_size = None

    if mode == "recent":
        config = GetConfig()
        max_size = config.max_size_recent_mode

    batch_collate_torrent_info = {}
    for jps_group_id, jps_torrent_ids in batch_uploads.items():
        if jps_group_id in batch_uploads_group_errors or jps_group_id in batch_groups_excluded or jps_group_id in batch_groups_va_errors:
            # Skip group if GetGroupData() failed or the group is being excluded by the '-exc' parameter, or if it is a 'V.A.' group and
            # no contrib artists were set
            # TODO Should the jps_group_ids be deleted within get_batch_group_data() ?
            continue

        jps_group_data = get_jps_group_data_class(batch_group_data, jps_group_id)

        try:
            collate_torrent_info = collate(torrentids=jps_torrent_ids, torrentgroupdata=jps_group_data, max_size=max_size)
            #logger.debug(f'collate_torrent_info: {json.dumps(collate_torrent_info, indent=2)}')
            for collate_result_item, value in collate_torrent_info.items():
                if isinstance(value, int):
                    batch_torrent_info[collate_result_item] += value
                elif isinstance(value, list):
                    for item in value:
                        batch_torrent_info[collate_result_item].append(item)
                elif isinstance(value, dict):
                    if collate_result_item != "jps_torrent_collated_data":
                        raise RuntimeError('Expected only a dict with a parent dicts value of jps_torrent_collated_data')
                    for jps_torrent_id, collate_torrent_info in collate_torrent_info['jps_torrent_collated_data'].items():
                        batch_collate_torrent_info[jps_torrent_id] = {}
                        batch_collate_torrent_info[jps_torrent_id]['jps_torrent_object'] = collate_torrent_info['jps_torrent_object']
                        batch_collate_torrent_info[jps_torrent_id]['torrentgroupdata'] = collate_torrent_info['torrentgroupdata']
                        batch_collate_torrent_info[jps_torrent_id]['release_data_collated'] = collate_torrent_info['release_data_collated']
                else:
                    raise RuntimeError('Expected either int, list or dict in collate_torrent_info.items() from collate()')
        except KeyboardInterrupt:  # Allow Ctrl-C to exit without showing the error multiple times and polluting the final error dict
            break  # Still continue to get error dicts and dupe list so far
        except Exception as exc:
            # Catch all for any collate() exception
            logger.exception(f'Error with collating/retrieving release data for JPS group id {jps_group_id} torrentid(s) {",".join(jps_torrent_ids)}, skipping upload')
            batch_upload_collate_errors[jps_group_id] = jps_torrent_ids
            continue

    #logger.debug(f'batch_collate_torrent_info: {pprint.pprint(batch_collate_torrent_info, indent=2, compact=True)}')

    if mode == "recent":
        logger.info('Interim stats')
        batch_stats(final_stats=False, media_info_mode=args.parsed.mediainfo, dry_run=args.parsed.dryrun)
        input('When these files have been downloaded press enter to continue...')

    for jps_torrent_id, collate_torrent_info in batch_collate_torrent_info.items():
        try:
            prepare_torrent(collate_torrent_info['jps_torrent_object'], collate_torrent_info['torrentgroupdata'], **collate_torrent_info['release_data_collated'])
        except KeyboardInterrupt:  # Allow Ctrl-C to exit without showing the error multiple times and polluting the final error dict
            break  # Still continue to get error dicts and dupe list so far
        except Exception as exc:
            # TODO These should all be custom exceptions
            if str(exc).startswith('Mediainfo error - file/directory not found'):
                # Need to get filename that was not found
                missing_file = re.findall(r'Mediainfo error - file/directory not found: (.+) in any of the MediaDirectories', str(exc))
                batch_upload_source_data_not_found.append(missing_file)
            elif str(exc).startswith('You do not appear to have entered any MediaInfo data for your video upload.'):
                batch_upload_mediainfo_not_submitted += 1
            else:
                # Catch all for any upload_torrent() exception
                logger.exception(f"SM upload error with JPS torrent id {jps_torrent_id} - {collate_torrent_info['torrentgroupdata'].title}")
                sm_upload_errors += 1
            continue
        if not args.parsed.dryrun:
            set_original_artists(collate_torrent_info['torrentgroupdata'].contribartists)
            download_sm_uploaded_torrents(torrentcount=1, artist=collate_torrent_info['torrentgroupdata'].artist,
                                          title=collate_torrent_info['torrentgroupdata'].title)
            sm_torrents_uploaded_count += 1

    if batch_uploads_group_errors:
        logger.error('The following JPS groupid(s) (torrentid(s) shown for reference) had errors in retrieving group data, '
                     'keep this data safe and you can possibly retry with it in a later version:')
        logger.error(batch_uploads_group_errors)
        logger.error(f'Total: {count_values_dict(batch_uploads_group_errors)}')
    if batch_groups_excluded:
        logger.info('The following groups were excluded due to user-specified filters:')
        logger.info(f'{batch_groups_excluded}\nTotal: {len(batch_groups_excluded)}')
    if batch_groups_va_errors:
        logger.warning('The following JPS groupid(s) were "bad V.A." groups - they are Various Artist groups with the artist set as "V.A." and'
                       ' the contributing artists should be set as the actual list of artists, however these are missing:')
        logger.warning(batch_groups_va_errors)
        logger.warning(f'Total: {len(batch_groups_va_errors)}')
    if batch_upload_collate_errors:
        logger.error('The following JPS groupid(s) and corresponding torrentid(s) had errors either in collating/retrieving '
                     'release data or in performing the actual upload to SM (although group data was retrieved OK), '
                     'keep this data safe and you can possibly retry with it in a later version:')
        logger.error(batch_upload_collate_errors)
        logger.error(f'Total: {count_values_dict(batch_upload_collate_errors)}')
    if batch_torrent_info['dupe_sm_ids']:  # Dupes found by decide_duplicate()
        logger.warning('The following torrents have already been uploaded to the site, and were found by searching for the torrent hash on SM, the SM torrents were download so you can cross seed:')
        logger.warning(f'SM duplicate torrent ids: {batch_torrent_info["dupe_sm_ids"]}\nJPS duplicate torrent ids: {batch_torrent_info["dupe_jps_ids"]}'
                       f'\nTotal: {len(batch_torrent_info["dupe_sm_ids"])}')
    if batch_upload_source_data_not_found:
        logger.error('The following file(s)/dir(s) were not found in your MediaDirectories specified in jps2sm.cfg and the upload was skipped:')
        logger.error(batch_upload_source_data_not_found)
        logger.error(f'Total: {len(batch_upload_source_data_not_found)}')

    logger.info('Finished batch upload')
    batch_stats(final_stats=True, media_info_mode=args.parsed.mediainfo, dry_run=args.parsed.dryrun)


def get_batch_jps_group_torrent_ids(mode, user, first=1, last=None, sort=None, order=None):
    """
    Iterates through pages of uploads on JPS and gathers the jps_group_ids and corresponding jps_torrent_id and returns
    a dict in the format of jps_group_id: [jps_torrent_id]

    :param mode: Area to get batch torrent ids from:
        'uploaded' for a user's uploads,
        'seeding' for the user's currently seeding torrents,
        'snatched' for a user's snatched torrents and
        'recent' for uploads recently uploaded to JPS from ANY user,
    :param user: JPS userid, defined by --batchuser or the SM user specified in jps2sm.cfg
    :param first: upload page number to start at
    :param last: upload page to finish at
    :param sort: Sort the JPS torrents page by a specific column, one of: {",".join(JPSTorrentView.sort_by.keys())}
    :param order: Order by ASC or DESC
    :return: batch_uploads: dict
    """

    # sort_by = {
    #    'name': 's1',
    #    'year': 's2',
    #    'time': 's3',  # snatched time for snatched, seeding time for seeding, added for uploaded and recent
    #    'size': 's4',
    #    'snatches': 's5',
    #    'seeders':  's6',
    #    'leechers': 's7'
    # }

    def get_sort_mode(user_sort):
        # By default:
        # uploaded mode: sort by uploaded time ASC
        # snatched mode: sort by uploaded time ASC
        # seeding mode: sort by name ASC - it is pointless to sort by seeded time as this random on whenever your torrent client
        #   last announced to the tracker
        # recent mode: sort by uploaded DESC - to upload all items recent uploaded to JPS

        default_sort_order_init = "ASC"
        if user_sort is not None:
            return JPSTorrentView.sort_by[user_sort], default_sort_order_init
        if mode == 'snatched' or mode == 'uploaded':
            return JPSTorrentView.sort_by['time'], default_sort_order_init
        elif mode == 'seeding':
            return JPSTorrentView.sort_by['name'], default_sort_order_init
        elif mode == 'recent':
            default_sort_order_init = "DESC"
            return JPSTorrentView.sort_by['time'], default_sort_order_init

    sort_mode, default_sort_order = get_sort_mode(sort)

    if order is not None:
        order_way = str(order).upper()  # Use --batchsortorder specified by user if present
    else:
        order_way = default_sort_order  # Else use sensible default defined in get_sort_mode()

    if not last and mode != 'recent':
        # Ascertain last page if not provided for seeding and snatched modes

        res = jpopsuki(f"https://jpopsuki.eu/torrents.php?type={mode}&userid={user}")
        soup = BeautifulSoup(res.text, 'html5lib')
        linkbox = str(soup.select('#content #ajax_torrents .linkbox')[0])
        try:
            last = re.findall(
                fr'page=([0-9]*)&amp;order_by=s3&amp;order_way=DESC&amp;type={mode}&amp;userid=(?:[0-9]*)&amp;disablegrouping=1(?:\'\);|&amp;action=advanced)"><strong> Last &gt;&gt;</strong>',
                linkbox)[0]
        except IndexError:
            # There is only 1 page of uploads if the 'Last >>' link cannot be found
            last = 1
    elif not last and mode == 'recent':
        # We do not need to ascertain the last page for recent mode as we never use this - we are not trying to jps2sm
        # *every* torrent!
        last = 1

    # Just for debugging purposes - get the jps_sort_name from the key when specifying the value in JPSTorrentView.sort_by{}
    jps_sort_name = list(JPSTorrentView.sort_by.keys())[list(JPSTorrentView.sort_by.values()).index(sort_mode)]
    if not first:
        first = 1
    logger.debug(f'Batch user is {user}, batch mode is {mode}, '
                 f'sort is {sort}, JPS sort column is {sort_mode} - {jps_sort_name}, '
                 f'order by is {order_way} '
                 f'first page is {first}, last page is {last}')

    batch_uploads = collections.defaultdict(list)

    # Parse every torrent page and add to dict
    for i in range(first, int(last) + 1):
        if mode == 'snatched' or mode == 'uploaded' or mode == 'seeding':
            batch_upload_url = f"https://jpopsuki.eu/torrents.php?page={i}&order_by={sort_mode}&order_way={order_way}&type={mode}&userid={user}&disablegrouping=1"
        elif mode == 'recent':
            batch_upload_url = f"https://jpopsuki.eu/torrents.php?page={i}&order_by={sort_mode}&order_way={order_way}&disablegrouping=1"
        else:
            raise RuntimeError("Unknown batch mode set")

        batch_upload_page = jpopsuki(batch_upload_url)
        logger.info(batch_upload_url)
        # print batch_upload_page.text
        soup2 = BeautifulSoup(batch_upload_page.text, 'html5lib')
        try:
            torrent_table = str(soup2.select('#content #ajax_torrents .torrent_table tbody')[0])
        except IndexError:
            quota_exceeded = re.findall('<title>Browse quota exceeded :: JPopsuki 2.0</title>', batch_upload_page.text)
            if quota_exceeded:
                logger.error('Browse quota exceeded :: JPopsuki 2.0')
                sys.exit(1)
            else:
                raise
        # Find all jps_group_id/jps_torrent_id pairs and returns a list of tuples
        all_jps_group_ids_and_torrent_ids = re.findall('torrents.php\?id=([0-9]+)&amp;torrentid=([0-9]+)', torrent_table)
        logger.info(f'jps_group_ids and jps_torrent_ids found on page: {all_jps_group_ids_and_torrent_ids}')

        for jps_group_id, jps_torrent_id in all_jps_group_ids_and_torrent_ids:
            batch_uploads[jps_group_id].append(jps_torrent_id)
        time.sleep(5)  # Sleep as otherwise we hit JPS browse quota

    logger.debug(f'jps_group_ids and jps_torrent_ids found on all pages: {batch_uploads}')
    return batch_uploads


def get_batch_group_data(batch_uploads, excluded_category):
    """
    Iterate through batch_uploads and run GetGroupData on each group and store the data in batch_group_data{}

    :param batch_uploads: dict, Contains jps_group_id: jps_torrent_id of all uploads
    :param excluded_category: str, JPS Category name to be excluded
    :return batch_group_data: dict, multi dimensional dict contain group data of all uploads
    :return batch_group_errors: list, All JPS jps_group_ids where GetGroupData failed
    :return batch_groups_excluded: list, All jps_group_ids that were excluded by the user, currently --exccategory
    :return batch_groups_va_errors: list, jps_group_ids that were 'V.A.' torrents with no contrib artists set
    """

    batch_group_errors = collections.defaultdict(list)
    batch_groups_excluded = []
    batch_groups_va_errors = []
    batch_group_data = {}

    for jps_group_id, jps_torrent_id in batch_uploads.items():
        try:
            logger.info('-------------------------')
            group_data_output = GetGroupData("https://jpopsuki.eu/torrents.php?id=%s" % jps_group_id)
            batch_group_data[jps_group_id] = {}
            batch_group_data[jps_group_id] = group_data_output.all()

            if batch_group_data[jps_group_id]["category"] == excluded_category:
                logger.debug(
                    f'Excluding jps_group_id {jps_group_id} as it is {batch_group_data[jps_group_id]["category"]} group and these are being skipped')
                batch_groups_excluded.append(jps_group_id)
                continue
        except KeyboardInterrupt:  # Allow Ctrl-C to exit without showing the error multiple times and polluting the final error dict
            break  # Still continue to get error dicts and dupe list so far
        except Exception as exc:
            # Catch all for any exception
            va_no_contrib_artists_error = "V.A. torrent with to contrib artists set - torrent has no valid artists so this cannot be uploaded."
            if str(exc) == va_no_contrib_artists_error:
                logger.error(va_no_contrib_artists_error)
                batch_groups_va_errors.append(jps_group_id)
                continue
            logger.exception(
                'Error with retrieving group data for jps_group_id %s jps_torrent_id %s, skipping upload' % (jps_group_id, ",".join(jps_torrent_id)))
            batch_group_errors[jps_group_id] = jps_torrent_id
            continue

    return batch_group_data, batch_group_errors, batch_groups_excluded, batch_groups_va_errors
