# deletetorrentid.py
# Delete a particular torrentid

from jps2sm import MyLoginSession
#from jps2sm import getauthkey
# TODO fix getauthkey() so it can be imported

# Standard library packages
import re
import os
import sys
import datetime
import argparse
import configparser
import pickle
import requests
from urllib.parse import urlparse

# Third-party packages
import html5lib
from bs4 import BeautifulSoup

__version__ = "0.3.0"

def getauthkey():
    SMshome = MyLoginSession(SMloginUrl, SMloginData, SMloginTestUrl, SMsuccessStr)
    SMreshome = SMshome.retrieveContent("https://sugoimusic.me/torrents.php?id=118")
    soup = BeautifulSoup(SMreshome.text, 'html5lib')
    rel = str(soup.select('#content .thin .main_column .torrent_table tbody'))
    authkey = re.findall('authkey=(.*)&amp;torrent_pass=', rel)
    return authkey


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-t', '--torrentfile', help='File with torrentids in line break delimited', type=str)
    args = parser.parse_args()

    # Get credentials from cfg file
    scriptdir = os.path.dirname(os.path.abspath(sys.argv[0]))
    config = configparser.ConfigParser()
    configfile = scriptdir + '/jps2sm.cfg'
    try:
        open(configfile)
    except FileNotFoundError:
        print(
            'Error: cannot read cfg - enter your JPS/SM credentials in jps2sm.cfg and check jps2sm.cfg.example to see the syntax.')
        raise

    config.read(configfile)
    smuser = config.get('SugoiMusic', 'User')
    smpass = config.get('SugoiMusic', 'Password')

    # SM MyLoginSession vars
    SMloginUrl = "https://sugoimusic.me/login.php"
    SMloginTestUrl = "https://sugoimusic.me/"
    SMsuccessStr = "Enabled users"
    SMloginData = {'username': smuser, 'password': smpass}

    authkey = getauthkey()

    with open(args.torrentfile, "r") as a_file:
        for line in a_file:
            torrentid = line.strip()

            data = {
                'action': 'takedelete',
                'auth': authkey,
                'torrentid': torrentid,
                'reason': 'Other',
                'extra': f'Bulk deleted with deletetorrent.py.'  # This msg goes in log.php, the user will probably not see this.
            }

            s = MyLoginSession(SMloginUrl, SMloginData, SMloginTestUrl, SMsuccessStr)
            res = s.retrieveContent("https://sugoimusic.me/torrents.php", "post", data)

            deletesuccess = re.findall('Torrent was successfully (.*)\.', res.text)
            if deletesuccess:
                print(f'Torrent was successfully {deletesuccess[0]}')
            else:
                print(f'Unknown error, check https://sugoimusic.me/log.php?search=Torrent+{args.torrentid}')
