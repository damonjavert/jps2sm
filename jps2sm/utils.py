# Standard library packages
import logging
import re
from typing import AnyStr
import sys
import configparser
import argparse

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
        parser.add_argument("-u", "--urls", help="JPS URL for a group, or multiple individual releases URLs to be added to the same group", type=str)
        parser.add_argument("-n", "--dryrun", help="Just parse url and show the output, do not add the torrent to SM", action="store_true")
        parser.add_argument("-b", "--batchuser", help="User id for batch user operations, default is user id of SM Username specified in jps2sm.cfg")
        parser.add_argument("-U", "--batchuploaded", help="(Batch mode only) Upload all releases uploaded by you or, if provided, user id specified by --batchuser", action="store_true")
        parser.add_argument("-S", "--batchseeding", help="(Batch mode only) Upload all releases currently seeding by you or, if provided, user id specified by --batchuser", action="store_true")
        parser.add_argument("--batchsnatched", help="(Batch mode only) Upload all releases snatched by you or, if provided, user id specified by --batchuser", action="store_true")
        parser.add_argument("-s", "--batchstart", help="(Batch mode only) Start at this page", type=int)
        parser.add_argument("-e", "--batchend", help="(Batch mode only) End at this page", type=int)
        parser.add_argument("-exc", "--exccategory", help="(Batch mode only) Exclude a JPS category from upload", type=str)
        parser.add_argument("-exf", "--excaudioformat", help="(Batch mode only) Exclude an audioformat from upload", type=str)
        parser.add_argument("-exm", "--excmedia", help="(Batch mode only) Exclude a media from upload", type=str)
        parser.add_argument("-m", "--mediainfo", help="Search and get mediainfo data from the source file(s) in the directories specified by MediaDirectories. Extract data to set codec, resolution, audio format and container fields as well as the mediainfo field itself.", action="store_true")
        self.parsed = parser.parse_args()


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