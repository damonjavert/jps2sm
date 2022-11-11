# Standard library packages
import logging
import collections

from jps2sm.get_data import GetGroupData

logger = logging.getLogger('main.' + __name__)


def get_batch_group_data(batch_uploads, excluded_category):
    """
    Iterate through batch_uploads and run GetGroupData on each group and store the data in batch_group_data{}

    :param: batch_uploads: dict: Contains jps_group_id: jps_torrent_id of all uploads
    :param: excluded_category: str: String of JPS Category name to be excluded
    :return: batch_group_data: dict: multi dimensional dict contain group data of all uploads
    :return: batch_group_errors: list: All JPS jps_group_ids where GetGroupData failed
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
