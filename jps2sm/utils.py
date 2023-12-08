"""
Util functions
"""
# pylint: disable=no-name-in-module,import-error
# pylint appears to have a bug where it cannot import despite python itself being able to

# Standard library packages
import re
from typing import AnyStr
import sys
import configparser
import argparse
import tempfile
import hashlib
import json
import os

# Third-party packages
from pathlib import Path
from loguru import logger
import torrent_parser as tp
import bencoding

# jps2sm modules
from jps2sm.constants import JPSTorrentView, Categories
from jps2sm.__init__ import __version__


def get_valid_filename(bad_filename: str) -> AnyStr:
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.

    :param bad_filename: str: A string that needs to be converted
    :return: str: A string with a clean filename
    """

    bad_filename = str(bad_filename).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', bad_filename)


def count_values_dict(dict_counted):
    """
    Count the values in a dictionary.
    """
    return sum([len(dict_counted[x]) for x in dict_counted])


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
    """
    Handle command-line arguments
    """
    __args_parsed = None

    def __init__(self):
        # pylint: disable=line-too-long
        # It is actually easier to read the arguments without wrapping the lines

        if GetArgs.__args_parsed is not None:
            return

        GetArgs.__args_parsed = True
        batch_modes = ['uploaded', 'seeding', 'snatched', 'recent']
        parser = argparse.ArgumentParser()

        jps2sm_core_args = parser.add_argument_group(title="jps2sm actions", description="Choose ONE action for jps2sm to migrate data from")
        jps2sm_core_args = jps2sm_core_args.add_mutually_exclusive_group(required=True)
        jps2sm_core_args.add_argument("-u", "--urls", help="JPS URL for a group, or multiple individual releases URLs from the same group", type=str)
        jps2sm_core_args.add_argument("-t", "--torrentid", help="JPS torrent id", type=int)
        jps2sm_core_args.add_argument("-bm", "--batch",
                                      help="Batch mode: Upload all releases either uploaded, seeding, snatched by you or, if provided, user id specified by --batchuser. OR all recent uploads to JPS.",
                                      type=str, choices=batch_modes)
        jps2sm_core_args.add_argument("-U", "--batchuploaded", help="alias to --batch upload", dest="batch", const="uploaded", action="store_const")
        jps2sm_core_args.add_argument("-S", "--batchseeding", help="alias to --batch seeding", dest="batch", const="seeding", action="store_const")
        jps2sm_core_args.add_argument("-SN", "--batchsnatched", help="alias to --batch snatched", dest="batch", const="snatched", action="store_const")
        jps2sm_core_args.add_argument("-R", "--batchrecent", help="alias to --batch recent", dest="batch", const="recent", action="store_const")

        batch_mode_args = parser.add_argument_group(title="Batch mode (--batch MODE) optional arguments")
        batch_mode_args.add_argument("-b", "--batchuser", help="User id for batch user operations, default is user id of SM Username specified in jps2sm.cfg", type=int)
        batch_mode_args.add_argument("-bs", "--batchsort", help=f"Sort for batch upload, must be one of: {','.join(JPSTorrentView.sort_by.keys())}", choices=JPSTorrentView.sort_by.keys())
        batch_mode_args.add_argument("-bso", "--batchsortorder", help="Sort order for batch upload, either ASC or DESC.", choices=['asc', 'desc'], type=str.lower)
        batch_mode_args.add_argument("-s", "--batchstart", help="Start at this page", type=int)
        batch_mode_args.add_argument("-e", "--batchend", help="End at this page", type=int)
        batch_mode_args.add_argument("-exc", "--exccategory", help="Exclude a JPS category from upload", type=str, choices=Categories.JPS)
        batch_mode_args.add_argument("-exf", "--excaudioformat", help="Exclude an audioformat from upload", type=str)
        batch_mode_args.add_argument("-exm", "--excmedia", help="Exclude a media from upload", type=str)
        batch_mode_args.add_argument("-fl", "--freeleech-only", help="Include only freeleech torrents", action="store_true")

        parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
        parser.add_argument('-d', '--debug', help='Enable debug mode', action='store_true')
        parser.add_argument("-n", "--dryrun", help="Just parse JPS data and show the output, do not upload the torrent(s) to SM", action="store_true")
        parser.add_argument("-w", "--wait-for-jps-dl", help="Wait for JPS file to be downloaded", action="store_true")
        parser.add_argument("-m", "--mediainfo",
                            help="Search and get mediainfo data from the source file(s) in the directories specified by MediaDirectories. Extract data to set codec, resolution, audio format and container fields as well as the mediainfo field itself.",
                            action="store_true")
        parser.add_argument("-c", "--cfg-file", help="Use a custom config file location", type=str)

        GetArgs.parsed = parser.parse_args()

        if GetArgs.parsed.debug:
            print(GetArgs.parsed)

        if GetArgs.parsed.batch:
            if bool(GetArgs.parsed.batchstart) ^ bool(GetArgs.parsed.batchend):
                parser.error('Error: You have specified an incomplete page range. See --help')

    def __getattr__(self, item):
        return GetArgs.item


def locate_cfg_file() -> Path:
    """
    Locate jps2sm.cfg file is not provided by --cfg-file parameter

    return: config_file: Path
    """

    cfg_file_name = 'jps2sm.cfg'
    script_dir = Path(__file__).parent.parent

    config_file_locations = [Path(script_dir, cfg_file_name),
                             Path(Path.home(), '.config', 'jps2sm', cfg_file_name),
                             Path(Path.home(), '.local', 'etc', cfg_file_name),
                             Path(Path.home(), cfg_file_name),
                             ]

    config_file = None
    for config_file_location in config_file_locations:
        try:
            open(config_file_location, "r", encoding="utf-8")
        except FileNotFoundError:
            continue
        config_file = config_file_location
        break
    if config_file is None:
        config_file_locations_str = list(map(str, config_file_locations))
        fatal_error(f'Error: configuration file not found. jps2sm searches for the config file following locations: {config_file_locations_str}'
                    f'\nSee: https://github.com/damonjavert/jps2sm/blob/master/jps2sm.cfg.example for example configuration.')

    return config_file


class GetConfig:
    """
    Handle jps2sm.cfg
    """
    __config_parsed = None

    def __init__(self):
        args = GetArgs()

        if GetConfig.__config_parsed is not None:
            return

        if args.parsed.cfg_file:
            config_file = Path(args.parsed.cfg_file)
        else:
            config_file = locate_cfg_file()

        try:
            open(config_file, "r", encoding="utf-8")
        except FileNotFoundError:
            fatal_error(f'Error: Config file {config_file} not found.')
        jps = 'JPopSuki'
        sugoi = 'SugoiMusic'
        config = configparser.ConfigParser()
        config.read(config_file)
        GetConfig.jps_user = config.get(jps, 'User')
        GetConfig.jps_pass = config.get(jps, 'Password')
        GetConfig.sm_user = config.get(sugoi, 'User')
        GetConfig.sm_pass = config.get(sugoi, 'Password')
        GetConfig.media_roots = [x.strip() for x in config.get('Media', 'MediaDirectories').split(',')]  # Remove whitespace after comma if any
        GetConfig.directories = config.items('Directories')
        GetConfig.skip_dupes = config.getboolean(sugoi, 'SkipDuplicates', fallback=False)
        GetConfig.jps_min_seeders = config.getint(jps, 'MinSeeders', fallback=1)
        GetConfig.max_size_recent_mode = config.get(jps, 'MaxSizeRecentMode', fallback=None)
        GetConfig.wait_time_recent_mode = config.get(jps, 'WaitTimeRecentModeMins', fallback=20)

        logger.debug(f"Config file used: {config_file}")

        GetConfig.__config_parsed = True

    def __getattr__(self, item):
        return GetConfig.item


class HandleCfgOutputDirs:
    """
    Handle all config dir logic

    Get data, decide if relative or absolute path and create dir if required

    :param config_file_dirs_section: dict: Contents of 'Directories' section in jps2sm.cfg
    """
    __output_dirs_handled = None

    def __init__(self, config_file_dirs_section):

        if HandleCfgOutputDirs.__output_dirs_handled is not None:
            return

        HandleCfgOutputDirs.file_dir = {}
        for (cfg_key, cfg_value) in config_file_dirs_section:
            if Path(cfg_value).is_absolute():
                HandleCfgOutputDirs.file_dir[cfg_key] = cfg_value
            else:
                HandleCfgOutputDirs.file_dir[cfg_key] = Path(Path.home(), cfg_value)
            if not Path(HandleCfgOutputDirs.file_dir[cfg_key]).is_dir():
                Path(HandleCfgOutputDirs.file_dir[cfg_key]).mkdir(parents=True, exist_ok=True)

    def __getattr__(self, item):
        return HandleCfgOutputDirs.item


def handle_cfg_media_roots() -> None:
    """
    Sanitise media_roots cfg, check they are dirs and not files and report error if they do not exist.
    """

    config = GetConfig()
    try:
        for media_dir in config.media_roots:
            if not os.path.exists(media_dir):
                fatal_error(f'Error: Media directory {media_dir} does not exist. Check your configuration in jps2sm.cfg.')
            if not os.path.isdir(media_dir):
                fatal_error(f'Error: Media directory {media_dir} is a file and not a directory. Check your configuration in jps2sm.cfg.')
    except configparser.NoSectionError:
        fatal_error('Error: --mediainfo requires you to configure MediaDirectories in jps2sm.cfg for mediainfo to find your file(s).')


def decide_duplicate(jps_torrent_object):
    """
    Detect if a torrent is a duplicate by crafting the torrent hash and then sending this to SM.

    This is useful for mediainfo (-m) uploads as it avoids the need to search for the file(s) and
    the mediainfo data before doing the upload, only having to find that it is a duplicate anyway.

    jps_torrent_object: bytes: BytesIO object of the JPS torrent
    """
    from jps2sm.myloginsession import sugoimusic

    torrent_hashcheckdata = tp.TorrentFileParser(jps_torrent_object).parse()
    torrent_hashcheckdata["info"]["source"] = 'SugoiMusic'
    file_descriptor, temp_torrent_file = tempfile.mkstemp()
    tp.create_torrent_file(temp_torrent_file, torrent_hashcheckdata)

    with open(temp_torrent_file, "rb") as file:
        data = bencoding.bdecode(file.read())
        info = data[b'info']
        hashed_info = hashlib.sha1(bencoding.bencode(info)).hexdigest()
        file.close()
    os.close(file_descriptor)

    # tempfile is supposed to delete it but with me at least it does not
    os.remove(temp_torrent_file)

    logger.debug(hashed_info)

    hashcheckjson = sugoimusic('https://sugoimusic.me/ajax.php?action=torrent&hash=' + hashed_info)

    if hashcheckjson.text == '{"status":"failure","error":"bad hash parameter"}':
        logger.debug('Duplicate not detected via torrent hash')
        return None
    if str(hashcheckjson.text).startswith('{"status":"success"'):
        logger.debug('Duplicate detected via torrent hash')
        dupe_jps_torrent_json = json.loads(hashcheckjson.text)
        dupe_jps_torrent_id = dupe_jps_torrent_json['response']['torrent']['id']
        logger.debug(f'Dupe torrent: {dupe_jps_torrent_id}')
        return dupe_jps_torrent_id

    # If we reach here something has gone wrong with the hash check
    raise Exception('Bad response from SugoiMusic hashcheck')


def setup_logging(debug: bool):
    """
    Setup logging, using loguru, assumes that loguru has already been imported as 'logger'
    """

    if debug:
        stderr_log_level = "DEBUG"
    else:
        stderr_log_level = "INFO"

    logger.remove()
    logger.add(sys.stderr, format="<lvl>{message}</>", level=stderr_log_level)
    logger.add("jps2sm.log", level="DEBUG", rotation="1 MB")

    if not debug:
        sys.tracebacklimit = 0
