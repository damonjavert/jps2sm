import json
import html

from jps2sm.get_data import GetGroupData, GetSMUser, get_torrent_link
from jps2sm.myloginsession import sugoimusic, jpopsuki
from jps2sm.utils import get_valid_filename, GetConfig, HandleCfgOutputDirs
from typing import Type, Tuple

from pathlib import Path
from loguru import logger
import requests

config = GetConfig()
output = HandleCfgOutputDirs(config.directories)


def save_sm_html_debug_output(content: str, torrent_group_data: Type[GetGroupData], jps_torrent_id: str) -> Path:
    """
    Save the html output from uploading the torrent to SM, for debug purposes

    """
    html_debug_output_filename = f"SMuploadresult." + \
                                 get_valid_filename(f"{torrent_group_data.artist[0]}.{torrent_group_data.title}.{torrent_group_data.date}."
                                                    f"JPS_ID{jps_torrent_id}") + \
                                 f".html"
    html_debug_output_path = Path(output.file_dir['html'], html_debug_output_filename)

    with open(html_debug_output_path, "w") as f:
        f.write(content)

    return html_debug_output_path


def download_sm_uploaded_torrents(torrentcount: int, artist: str, title: str) -> None:
    """
    Get last torrentcount torrent DL links that user uploaded using SM API and download them

    :param torrentcount: count of recent torrent links to be downloaded
    :param artist
    :param title

    """
    # TODO Merge this functionality into download_sm_torrent()!

    output_dir = output.file_dir['smtorrents']

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
        torrentpath = Path(output_dir, torrentfilename)

        with open(torrentpath, "wb") as f:
            f.write(torrentfile.content)
        logger.debug(f'Downloaded SM torrent as {torrentpath}')


def download_sm_torrent(torrent_id: str, artist: str, title: str) -> Path:
    """
    Downloads the SM torrent if it is a dupe, in this scenario we cannot use download_sm_uploaded_torrents() as the user
    has not actually uploaded it.

    :param torrent_id: SM torrentid to be downloaded
    :param artist: SM Artist name, for naming torrent file only
    :param title: SM group title, for naming torrent file only
    :return: name: filename of torrent downloaded
    """
    output_dir = output.file_dir['smtorrents']

    sm_user = GetSMUser()

    file = jpopsuki(
        'https://sugoimusic.me/torrents.php?action='
        f'download&id={torrent_id}&authkey={sm_user.auth_key()}&torrent_pass={sm_user.torrent_password_key()}'
    )
    name = get_valid_filename(
        "SM %s - %s - %s.torrent" % (artist, title, torrent_id)
    )
    sm_torrent_path = Path(output_dir, name)
    with open(sm_torrent_path, "wb") as f:
        f.write(file.content)

    return sm_torrent_path


def get_jps_torrent(jps_torrent_id: str, torrent_group_data: Type[GetGroupData]):
    """
    Download a JPS torrent, ascertaining the link from the torrent_table from the JPS Group

    :param jps_torrent_id: JPS torrent ID
    :param torrent_group_data: Data from the JPS Group
    """

    torrent_link = html.unescape(get_torrent_link(jps_torrent_id, torrent_group_data.rel2))
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

    with open(jps_torrent_path, "wb") as f:
        f.write(jps_torrent_file.content)
