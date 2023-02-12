import json

from jps2sm.get_data import GetGroupData, GetSMUser
from jps2sm.myloginsession import sugoimusic, jpopsuki
from jps2sm.utils import get_valid_filename, GetConfig, HandleCfgOutputDirs
from typing import Type

from pathlib import Path
from loguru import logger

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


def downloaduploadedtorrents(torrentcount: int, artist: str, title: str) -> None:
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


def download_sm_torrent(torrent_id: str, artist: str, title: str) -> str:
    """
    Downloads the SM torrent if it is a dupe, in this scenario we cannot use downloaduploadedtorrents() as the user
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
    path = Path(output_dir, name)
    with open(path, "wb") as f:
        f.write(file.content)

    return name
