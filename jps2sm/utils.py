# Standard library packages
import logging
import re
from typing import AnyStr
import sys
import configparser
import argparse
import torrent_parser as tp
import tempfile
import bencoding, hashlib
import json
import os

from jps2sm.constants import JPSTorrentView, Categories

# Third-party packages
from pathlib import Path

logger = logging.getLogger('main.' + __name__)

__version__ = "1.5.1"


def get_valid_filename(s: str) -> AnyStr:
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.

    :param s: str: A string that needs to be converted
    :return: str: A string with a clean filename
    """

    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def count_values_dict(dict):
    """
    Count the values in a dictionary.
    """
    return sum([len(dict[x]) for x in dict])


def fatal_error(msg):
    """
    Immediately exit and show an error to stderr and not log it
    Usually used argument, file or other simple errors that should not be logged as otherwise it creates noise

    :param msg: str
    :return:
    """

    print(msg, file=sys.stderr)
    sys.exit(1)


class GetArgs:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
        parser.add_argument('-d', '--debug', help='Enable debug mode', action='store_true')
        parser.add_argument("-u", "--urls", help="JPS URL for a group, or multiple individual releases URLs from the same group", type=str)
        parser.add_argument("-n", "--dryrun", help="Just parse url and show the output, do not add the torrent to SM", action="store_true")
        parser.add_argument("-b", "--batchuser", help="User id for batch user operations, default is user id of SM Username specified in jps2sm.cfg")
        parser.add_argument("-U", "--batchuploaded", help="(Batch mode only) Upload all releases uploaded by you or, if provided, user id specified by --batchuser", action="store_true")
        parser.add_argument("-S", "--batchseeding", help="(Batch mode only) Upload all releases currently seeding by you or, if provided, user id specified by --batchuser", action="store_true")
        parser.add_argument("-R", "--batchrecent", help="(Batch mode only) Upload recent releases uploaded to JPS that are under 1Gb in size", action="store_true")
        parser.add_argument("-SN", "--batchsnatched", help="(Batch mode only) Upload all releases snatched by you or, if provided, user id specified by --batchuser", action="store_true")
        parser.add_argument("-bs", "--batchsort", help=f"(Batch mode only) Sort for batch upload, must be one of: {','.join(JPSTorrentView.sort_by.keys())}")
        parser.add_argument("-bso", "--batchsortorder", help="(Batch mode only) Sort order for batch upload, either ASC or DESC.")
        parser.add_argument("-s", "--batchstart", help="(Batch mode only) Start at this page", type=int)
        parser.add_argument("-e", "--batchend", help="(Batch mode only) End at this page", type=int)
        parser.add_argument("-exc", "--exccategory", help="(Batch mode only) Exclude a JPS category from upload", type=str)
        parser.add_argument("-exf", "--excaudioformat", help="(Batch mode only) Exclude an audioformat from upload", type=str)
        parser.add_argument("-exm", "--excmedia", help="(Batch mode only) Exclude a media from upload", type=str)
        parser.add_argument("-m", "--mediainfo", help="Search and get mediainfo data from the source file(s) in the directories specified by MediaDirectories. Extract data to set codec, resolution, audio format and container fields as well as the mediainfo field itself.", action="store_true")
        self.parsed = parser.parse_args()

        # Handle bag args
        # TODO move all bad arg logic to here

        if self.parsed.batchsort is not None and self.parsed.batchsort not in JPSTorrentView.sort_by.keys():
            fatal_error(f'Error: Incorrect --batchsort mode specified, sort mode must be one of {",".join(JPSTorrentView.sort_by.keys())}')
        if self.parsed.batchsortorder is not None and str(self.parsed.batchsortorder).upper() not in ("ASC", "DESC"):
            fatal_error(f'Error: Incorrect --batchsortorder specified, order must be wither ASC or DESC')
        if self.parsed.exccategory is not None and str(self.parsed.exccategory) not in Categories.JPS:
            fatal_error(f'Error: Incorrect --exccategory specified, it must match a JPS category, these are: {",".join(Categories.JPS)}')


class GetConfig:
    def __init__(self):
        script_dir = Path(__file__).parent.parent

        # Get configuration
        config = configparser.ConfigParser()
        configfile = Path(script_dir, 'jps2sm.cfg')
        try:
            open(configfile)
        except FileNotFoundError:
            fatal_error(
                f'Error: config file {configfile} not found - enter your JPS/SM credentials in jps2sm.cfg and check jps2sm.cfg.example to see the syntax.')

        config.read(configfile)
        self.jps_user = config.get('JPopSuki', 'User')
        self.jps_pass = config.get('JPopSuki', 'Password')
        self.sm_user = config.get('SugoiMusic', 'User')
        self.sm_pass = config.get('SugoiMusic', 'Password')
        self.media_roots = [x.strip() for x in config.get('Media', 'MediaDirectories').split(',')]  # Remove whitespace after comma if any
        self.directories = config.items('Directories')
        try:
            self.skip_dupes = config.getboolean('SugoiMusic', 'SkipDuplicates')
        except configparser.NoOptionError:
            self.skip_dupes = False

    def __getattr__(self, item):
        return self.item


class HandleCfgOutputDirs:
    """
    Handle all config dir logic

    Get data, decide if relative or absolute path and create dir if required

    :param config_file_dirs_section: dict: Contents of 'Directories' section in jps2sm.cfg
    """

    def __init__(self, config_file_dirs_section):
        self.config_file_dirs_section = config_file_dirs_section
        self.file_dir = {}
        for (cfg_key, cfg_value) in config_file_dirs_section:
            if Path(cfg_value).is_absolute():
                self.file_dir[cfg_key] = cfg_value
            else:
                self.file_dir[cfg_key] = Path(Path.home(), cfg_value)
            if not Path(self.file_dir[cfg_key]).is_dir():
                Path(self.file_dir[cfg_key]).mkdir(parents=True, exist_ok=True)


def remove_html_tags(text):
    """
    Strip html tags, used by GetGroupData() on the group description if unable to get bbcode

    """
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def decide_duplicate(jps_torrent_object):
    from jps2sm.myloginsession import sugoimusic
    """
    Detect if a torrent is a duplicate by crafting the torrent hash and then sending this to SM.

    This is useful for mediainfo (-m) uploads as it avoids the need to search for the file(s) and
    the mediainfo data before doing the upload, only having to find that it is a duplicate anyway.

    jps_torrent_object: bytes: BytesIO object of the JPS torrent
    """

    torrent_hashcheckdata = tp.TorrentFileParser(jps_torrent_object).parse()
    torrent_hashcheckdata["info"]["source"] = 'SugoiMusic'
    fd, temp_torrent_file = tempfile.mkstemp()
    tp.create_torrent_file(temp_torrent_file, torrent_hashcheckdata)

    with open(temp_torrent_file, "rb") as f:
        data = bencoding.bdecode(f.read())
        info = data[b'info']
        hashed_info = hashlib.sha1(bencoding.bencode(info)).hexdigest()
        f.close()
    os.close(fd)

    # tempfile is supposed to delete it but with me at least it does not
    os.remove(temp_torrent_file)

    logger.debug(hashed_info)

    hashcheckjson = sugoimusic('https://sugoimusic.me/ajax.php?action=torrent&hash=' + hashed_info)

    if hashcheckjson.text == '{"status":"failure","error":"bad hash parameter"}':
        logger.debug('Duplicate not detected via torrent hash')
        return False, None
    elif str(hashcheckjson.text).startswith('{"status":"success"'):
        logger.debug('Duplicate detected via torrent hash')
        dupe_jps_torrent_json = json.loads(hashcheckjson.text)
        dupe_jps_torrent_id = dupe_jps_torrent_json['response']['torrent']['id']
        logger.debug(f'Dupe torrent: {dupe_jps_torrent_id}')
        return True, dupe_jps_torrent_id
    else:
        raise Exception('Bad response from SugoiMusic hashcheck')


