import logging
import re
from typing import AnyStr
import sys
import configparser

# Third-party packages
from pathlib import Path

logger = logging.getLogger('main.' + __name__)


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
