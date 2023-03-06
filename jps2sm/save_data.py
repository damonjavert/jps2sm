"""
All defs that save data to disk
"""
# pylint: disable=no-name-in-module,import-error
# pylint appears to have a bug where it cannot import despite python itself being able to
# pylint: disable=fixme

# Standard library packages
import json
import html
from typing import Type

# Third-party packages
from pathlib import Path
from loguru import logger

# jps2sm modules
from jps2sm.get_data import GetGroupData, GetSMUser, get_torrent_link
from jps2sm.myloginsession import sugoimusic, jpopsuki
from jps2sm.utils import get_valid_filename, GetConfig, HandleCfgOutputDirs


config = GetConfig()
output = HandleCfgOutputDirs(config.directories)


def save_sm_html_debug_output(content: str, html_debug_output_filename: str) -> Path:
    """
    Save the html output from uploading the torrent to SM, for debug purposes

    """
    html_debug_output_filename_valid = get_valid_filename(html_debug_output_filename)

    html_debug_output_path = Path(output.file_dir['html'], html_debug_output_filename_valid)

    with open(html_debug_output_path, "w") as file:
        file.write(content)

    return html_debug_output_path


def download_sm_uploaded_torrents(torrent_count: int) -> None:
    """
    Get last torrent_count torrent DL links that user uploaded using SM API and download them

    :param torrent_count: count of recent torrent links to be downloaded
    """
    # TODO Merge this functionality into download_sm_torrent()!

    output_dir = output.file_dir['smtorrents']

    if torrent_count == 0:
        return

    user_recents = sugoimusic(f"https://sugoimusic.me/ajax.php?action=user_recents&limit={torrent_count}")
    user_recents_json = json.loads(user_recents.text)

    sm_torrent_links = {}
    for torrent_data in user_recents_json['response']['uploads']:  # Get list of SM torrent links
        sm_torrent_links[torrent_data['torrentid']] = torrent_data['torrentdl']

    for torrent_id, torrent_link in sm_torrent_links.items():
        torrent_file = sugoimusic(torrent_link)
        torrent_filename = get_valid_filename(f'SM-{torrent_id}.torrent')
        sm_torrent_path = Path(output_dir, torrent_filename)

        with open(sm_torrent_path, "wb") as file:
            file.write(torrent_file.content)
        logger.debug(f'Downloaded SM torrent as {sm_torrent_path}')


def download_sm_torrent(torrent_id: str) -> Path:
    """
    Downloads the SM torrent if it is a dupe, in this scenario we cannot use download_sm_uploaded_torrents() as the user
    has not actually uploaded it.

    :param torrent_id: SM torrentid to be downloaded
    :return: name: filename of torrent downloaded
    """
    output_dir = output.file_dir['smtorrents']

    sm_user = GetSMUser()

    torrent_file = sugoimusic(
        'https://sugoimusic.me/torrents.php?action='
        f'download&id={torrent_id}&authkey={sm_user.auth_key()}&torrent_pass={sm_user.torrent_password_key()}'
    )
    torrent_filename = get_valid_filename(f'SM-{torrent_id}.torrent')
    sm_torrent_path = Path(output_dir, torrent_filename)
    with open(sm_torrent_path, "wb") as file:
        file.write(torrent_file.content)

    return sm_torrent_path


def get_jps_torrent(jps_torrent_id: str, torrent_group_data: Type[GetGroupData]):
    """
    Download a JPS torrent, ascertaining the link from the torrent_table from the JPS Group

    :param jps_torrent_id: JPS torrent ID
    :param torrent_group_data: Data from the JPS Group
    """

    torrent_link = html.unescape(get_torrent_link(jps_torrent_id, torrent_group_data.torrent_table))
    jps_torrent_file = jpopsuki(f"https://jpopsuki.eu/{torrent_link}")  # Download JPS torrent

    return jps_torrent_file


def download_jps_torrent(jps_torrent_file, torrent_group_data: Type[GetGroupData], release_data):
    """
    Save the JPS torrent

    :param jps_torrent_file: jpopsuki() of the JPS torrent
    :param torrent_group_data: Data from the JPS Group
    :param release_data: Relase data from collate()
    """

    output_dir = output.file_dir['jpstorrents']
    jps_torrent_filename = get_valid_filename(
        f"JPS {torrent_group_data.artist} - {torrent_group_data.title} - {'-'.join(release_data)}.torrent")

    jps_torrent_path = Path(output_dir, jps_torrent_filename)

    with open(jps_torrent_path, "wb") as file:
        file.write(jps_torrent_file.content)
