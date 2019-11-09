# deletetorrentid.py
# Delete a particular torrentid

# from jps2sm import MyLoginSession needs overhual before we can import it
# TODO use __name__ == "__main__" in jps2sm so that it can be imported

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

__version__ = "0.1.0"


class MyLoginSession:
    """
    https://stackoverflow.com/a/37118451/2115140
    Added some features myself, originally by https://stackoverflow.com/users/1150303/domtomcat

    a class which handles and saves login sessions. It also keeps track of proxy settings.
    It does also maintine a cache-file for restoring session data from earlier
    script executions.
    """

    def __init__(self,
                 loginUrl,
                 loginData,
                 loginTestUrl,
                 loginTestString,
                 sessionFileAppendix='_session.dat',
                 maxSessionTimeSeconds=30 * 60,
                 proxies=None,
                 userAgent='Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
                 debug=True,
                 forceLogin=False,
                 **kwargs):
        """
        save some information needed to login the session

        you'll have to provide 'loginTestString' which will be looked for in the
        responses html to make sure, you've properly been logged in

        'proxies' is of format { 'https' : 'https://user:pass@server:port', 'http' : ...
        'loginData' will be sent as post data (dictionary of id : value).
        'maxSessionTimeSeconds' will be used to determine when to re-login.
        """
        urlData = urlparse(loginUrl)

        self.proxies = proxies
        self.loginData = loginData
        self.loginUrl = loginUrl
        self.loginTestUrl = loginTestUrl
        self.maxSessionTime = maxSessionTimeSeconds
        self.sessionFile = urlData.netloc + sessionFileAppendix
        self.userAgent = userAgent
        self.loginTestString = loginTestString
        self.debug = debug

        self.login(forceLogin, **kwargs)

    def modification_date(self, filename):
        """
        return last file modification date as datetime object
        """
        t = os.path.getmtime(filename)
        return datetime.datetime.fromtimestamp(t)

    def login(self, forceLogin=False, **kwargs):
        """
        login to a session. Try to read last saved session from cache file. If this fails
        do proper login. If the last cache access was too old, also perform a proper login.
        Always updates session cache file.
        """
        wasReadFromCache = False
        if self.debug:
            print('loading or generating session...')
        if os.path.exists(self.sessionFile) and not forceLogin:
            time = self.modification_date(self.sessionFile)

            # only load if file less than 30 minutes old
            lastModification = (datetime.datetime.now() - time).seconds
            if lastModification < self.maxSessionTime:
                with open(self.sessionFile, "rb") as f:
                    self.session = pickle.load(f)
                    wasReadFromCache = True
                    if self.debug:
                        print("loaded session from cache (last access %ds ago) "
                              % lastModification)
        if not wasReadFromCache:
            self.session = requests.Session()
            self.session.headers.update({'user-agent': self.userAgent})
            res = self.session.post(self.loginUrl, data=self.loginData,
                                    proxies=self.proxies, **kwargs)

            if self.debug:
                print('created new session with login')
            self.saveSessionToCache()

        # test login
        res = self.session.get(self.loginTestUrl)
        # print res.text
        if res.text.lower().find(self.loginTestString.lower()) < 0:
            raise Exception("could not log into provided site '%s'"
                            " (did not find successful login string)"
                            % self.loginUrl)

    def saveSessionToCache(self):
        """
        save session to a cache file
        """
        # always save (to update timeout)
        with open(self.sessionFile, "wb") as f:
            pickle.dump(self.session, f)
            if self.debug:
                print('updated session cache-file %s' % self.sessionFile)

    def retrieveContent(self, url, method="get", postData=None, postDataFiles=None, **kwargs):
        """
        return the content of the url with respect to the session.

        If 'method' is not 'get', the url will be called with 'postData'
        as a post request.
        """
        if method == 'get':
            res = self.session.get(url, proxies=self.proxies, **kwargs)
        else:
            res = self.session.post(url, data=postData, proxies=self.proxies, files=postDataFiles, **kwargs)

        # the session has been updated on the server, so also update in cache
        self.saveSessionToCache()

        return res


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
    parser.add_argument('-t', '--torrentid', help='SugoiMusic torrentid', type=str)
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

    data = {
        'action': 'takedelete',
        'auth': getauthkey(),
        'torrentid': args.torrentid,
        'reason': 'Other',
        'extra': f'Mass delete from deletetorrent.py'
    }

    s = MyLoginSession(SMloginUrl, SMloginData, SMloginTestUrl, SMsuccessStr)
    res = s.retrieveContent("https://sugoimusic.me/torrents.php", "post", data)

    deletesuccess = re.findall('Torrent was successfully (.*)\.', res.text)
    if deletesuccess:
        print(f'Torrent was successfully {deletesuccess[0]}')
    else:
        print(f'Unknown error, check https://sugoimusic.me/log.php?search=Torrent+{args.torrentid}')
