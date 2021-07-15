# bulkinvite.py
# SM bulkinviter

from jps2sm.myloginsession import MyLoginSession
#from jps2sm import getauthkey
# TODO fix getauthkey() so it can be imported

# Standard library packages
import re
import os
import sys
#import datetime
import argparse
import configparser
#import pickle
#import requests
#from urllib.parse import urlparse

# Third-party packages
#import html5lib
from bs4 import BeautifulSoup

__version__ = "0.1.0"


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
    parser.add_argument('-e', '--emailfile', help='Email addresses file', type=str)
    #parser.add_argument('-d', '--debug', help='Debug', type=str)

    args = parser.parse_args()

    # Get credentials from cfg file
    scriptdir = os.path.dirname(os.path.abspath(sys.argv[0]))
    config = configparser.ConfigParser()
    configfile = scriptdir + '/jps2sm.cfg'
    try:
        open(configfile)
    except FileNotFoundError:
        print(
            'Error: cannot read cfg - enter your SM credentials in jps2sm.cfg and check jps2sm.cfg.example to see the syntax.')
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
    print(authkey)

    with open(args.emailfile, "r") as a_file:
        for line in a_file:
            email = line.strip()

            data = {
                'action': 'take_invite',
                'auth': authkey,
                'email': email,
            }

            s = MyLoginSession(SMloginUrl, SMloginData, SMloginTestUrl, SMsuccessStr)
            res = s.retrieveContent("https://sugoimusic.me/user.php?action=invite", "post", data)

            error = re.findall('<h2>Error</h2>', res.text)
            if error:
                print(f'Error with {email}')
            else:
                good = re.findall(email, res.text)
                if good:
                    print(f'Likely ok - found email {email}')
                else:
                    print(f'No error text but no email in response either! {email}')
                #print(res.text)
