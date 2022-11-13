# Standard library packages
import logging
import collections
import time
import re
import sys

from jps2sm.get_data import GetGroupData
from jps2sm.myloginsession import jpopsuki

# Third-party packages
from bs4 import BeautifulSoup

logger = logging.getLogger('main.' + __name__)


def get_batch_jps_group_torrent_ids(mode, user, first=1, last=None):
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
    :return: batch_uploads: dict
    """

    sort_by = {
        'name': 's1',
        'year': 's2',
        'time': 's3',  # snatched time for snatched, seeding time for seeding, added for uploaded and recent
        'size': 's4',
        'snatches': 's5',
        'seeders':  's6',
        'leechers': 's7'
    }

    if mode == 'snatched' or mode == 'uploaded':
        sort_mode = sort_by['time']
    elif mode == 'seeding':
        sort_mode = sort_by['name']
    elif mode == 'recent':
        sort_mode = sort_by['time']

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

    logger.debug(f'Batch user is {user}, batch mode is {mode}, first page is {first}, last page is {last}')

    batch_uploads = collections.defaultdict(list)

    # Parse every torrent page and add to dict
    for i in range(first, int(last) + 1):
        if mode == 'snatched' or mode == 'uploaded' or mode == 'seeding':
            batch_upload_url = f"https://jpopsuki.eu/torrents.php?page={i}&order_by={sort_mode}&order_way=ASC&type={mode}&userid={user}&disablegrouping=1"
        elif mode == 'recent':
            batch_upload_url = f"https://jpopsuki.eu/torrents.php?page={i}&order_by={sort_mode}&order_way=DESC&disablegrouping=1"
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
    """

    batch_group_errors = collections.defaultdict(list)
    batch_groups_excluded = []
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
        except Exception:
            # Catch all for any exception
            logger.exception(
                'Error with retrieving group data for jps_group_id %s jps_torrent_id %s, skipping upload' % (jps_group_id, ",".join(jps_torrent_id)))
            batch_group_errors[jps_group_id] = jps_torrent_id
            continue

    return batch_group_data, batch_group_errors, batch_groups_excluded
