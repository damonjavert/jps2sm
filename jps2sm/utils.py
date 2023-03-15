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

__version__ = "1.15.5"


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
    __args_parsed = None

    def __init__(self):
        # pylint: disable=line-too-long
        # It is actually easier to read the arguments without wrapping the lines and using lots of vars for the help texts
        # would unnecessary extra code.

        if GetArgs.__args_parsed is not None:
            return

        GetArgs.__args_parsed = True
        parser = argparse.ArgumentParser()
        parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
        parser.add_argument('-d', '--debug', help='Enable debug mode', action='store_true')
        parser.add_argument("-u", "--urls", help="JPS URL for a group, or multiple individual releases URLs from the same group", type=str)
        parser.add_argument("-t", "--torrentid", help="JPS torrent id", type=int)
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
        parser.add_argument("-w", "--wait-for-jps-dl", help="Wait for JPS file to be downloaded", action="store_true")
        parser.add_argument("-exc", "--exccategory", help="(Batch mode only) Exclude a JPS category from upload", type=str)
        parser.add_argument("-exf", "--excaudioformat", help="(Batch mode only) Exclude an audioformat from upload", type=str)
        parser.add_argument("-exm", "--excmedia", help="(Batch mode only) Exclude a media from upload", type=str)
        parser.add_argument("-m", "--mediainfo", help="Search and get mediainfo data from the source file(s) in the directories specified by MediaDirectories. Extract data to set codec, resolution, audio format and container fields as well as the mediainfo field itself.", action="store_true")
        GetArgs.parsed = parser.parse_args()

        # Handle bag args
        GetArgs.batch_modes = sum([bool(GetArgs.parsed.batchuploaded),
                                   bool(GetArgs.parsed.batchseeding),
                                   bool(GetArgs.parsed.batchsnatched),
                                   bool(GetArgs.parsed.batchrecent)])
        if GetArgs.batch_modes > 1:
            fatal_error('Error: Multiple batch modes of operation specified - only one can be used at the same time. See --help')

        if GetArgs.parsed.urls is not None and GetArgs.parsed.torrentid is not None:
            fatal_error('Error: Both JPS URL(s) (--urls) and a JPS torrent id (--torrentid) have been specified '
                        '- only one can be used at the same time. See --help')
        if GetArgs.parsed.urls is None and GetArgs.parsed.torrentid is None and GetArgs.batch_modes == 0:
            fatal_error('Error: Neither any JPS URL(s) (--urls) '
                        'nor a JPS torrent id (--torrentid) '
                        'nor any batch parameters (--batchsnatched, --batchuploaded, --batchseeding or --batchrecent) have been specified. See --help')
        elif (GetArgs.parsed.urls is not None or GetArgs.parsed.torrentid is not None) and GetArgs.batch_modes == 1:
            fatal_error(
                'Error: Both the JPS URL(s) (--urls) or torrent id (--torrentid) and batch parameters '
                '(--batchsnatched,--batchuploaded, --batchseeding or --batchrecent) have been specified, but only one is allowed.')

        if GetArgs.parsed.batchsort is not None and GetArgs.parsed.batchsort not in JPSTorrentView.sort_by.keys():
            fatal_error(f'Error: Incorrect --batchsort mode specified, sort mode must be one of {",".join(JPSTorrentView.sort_by.keys())}')
        if GetArgs.parsed.batchsortorder is not None and str(GetArgs.parsed.batchsortorder).upper() not in ("ASC", "DESC"):
            fatal_error(f'Error: Incorrect --batchsortorder specified, order must be wither ASC or DESC')
        if GetArgs.parsed.exccategory is not None and str(GetArgs.parsed.exccategory) not in Categories.JPS:
            fatal_error(f'Error: Incorrect --exccategory specified, it must match a JPS category, these are: {",".join(Categories.JPS)}')

        if GetArgs.batch_modes == 1:  # Handle bad batch args TODO this should be handles as part of proper sub args if possible
            if GetArgs.parsed.batchuser:
                if GetArgs.parsed.batchuser.isnumeric() is False:
                    fatal_error('Error: "--batchuser" or short "-b" should be a JPS profile ID. See --help')

            if bool(GetArgs.parsed.batchstart) ^ bool(GetArgs.parsed.batchend):
                fatal_error('Error: You have specified an incomplete page range. See --help')

            if GetArgs.parsed.batchuploaded:
                GetArgs.batch_mode = "uploaded"
            elif GetArgs.parsed.batchseeding:
                GetArgs.batch_mode = "seeding"
            elif GetArgs.parsed.batchsnatched:
                GetArgs.batch_mode = "snatched"
            elif GetArgs.parsed.batchrecent:
                GetArgs.batch_mode = "recent"
            else:
                raise RuntimeError("Expected some batch mode to be set")

    def __getattr__(self, item):
        return GetArgs.item


class GetConfig:
    __config_parsed = None

    def __init__(self):
        if GetConfig.__config_parsed is not None:
            return

        GetConfig.__config_parsed = True
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
                open(config_file_location)
            except FileNotFoundError:
                continue
            config_file = config_file_location
            break
        if config_file is None:
            config_file_locations_str = list(map(str, config_file_locations))
            fatal_error(f'Error: configuration file not found. jps2sm searches for the config file following locations: {config_file_locations_str}'
                        f'\nSee: https://github.com/damonjavert/jps2sm/blob/master/jps2sm.cfg.example for example configuration.')

        open(config_file)
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
    from jps2sm.myloginsession import sugoimusic
    """
    Detect if a torrent is a duplicate by crafting the torrent hash and then sending this to SM.

    This is useful for mediainfo (-m) uploads as it avoids the need to search for the file(s) and
    the mediainfo data before doing the upload, only having to find that it is a duplicate anyway.

    jps_torrent_object: bytes: BytesIO object of the JPS torrent
    """

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
    elif str(hashcheckjson.text).startswith('{"status":"success"'):
        logger.debug('Duplicate detected via torrent hash')
        dupe_jps_torrent_json = json.loads(hashcheckjson.text)
        dupe_jps_torrent_id = dupe_jps_torrent_json['response']['torrent']['id']
        logger.debug(f'Dupe torrent: {dupe_jps_torrent_id}')
        return dupe_jps_torrent_id
    else:
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
