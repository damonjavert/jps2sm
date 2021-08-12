# Standard library packages
import logging
import datetime
import os
import pickle
from urllib.parse import urlparse
import requests

from jps2sm.utils import GetConfig

logger = logging.getLogger('main.' + __name__)


def jpopsuki(url, test_login=False):
    """
    Get content from JPS

    :param url:
    :param test_login: Disable test login
    :return: data
    """
    config = GetConfig()

    jps_login_url = "https://jpopsuki.eu/login.php"
    jps_test_url = "https://jpopsuki.eu"
    jps_success = '<div id="extra1"><span></span></div>'
    login_data = {'username': config.jps_user, 'password': config.jps_pass}

    jps_session = MyLoginSession(jps_login_url, login_data, jps_test_url, jps_success, test_login)

    return jps_session.retrieveContent(url)


def sugoimusic(url, method="get", post_data=None, post_data_files=None, test_login=False):
    """
    Get/Post content to SM

    :param post_data_files: Files to send in POST
    :param post_data: Parameters to send in POST
    :param method: HTML method
    :param url: URL to parse
    :param test_login: Disable test login
    :return: data
    """

    config = GetConfig()

    sm_login_url = "https://sugoimusic.me/login.php"
    sm_test_url = "https://sugoimusic.me/"
    sm_success = "Enabled users"
    login_data = {'username': config.sm_user, 'password': config.sm_pass}

    sm_session = MyLoginSession(sm_login_url, login_data, sm_test_url, sm_success, test_login)

    return sm_session.retrieveContent(url, method, post_data, post_data_files)


class MyLoginSession:
    """
    Taken from: https://stackoverflow.com/a/37118451/2115140
    New features added in jps2sm
    Originally by: https://stackoverflow.com/users/1150303/domtomcat

    a class which handles and saves login sessions. It also keeps track of proxy settings.
    It does also maintains a cache-file for restoring session data from earlier
    script executions.
    """

    def __init__(self,
                 loginUrl,
                 loginData,
                 loginTestUrl,
                 loginTestString,
                 test_login=False,
                 sessionFileAppendix='_session.dat',
                 maxSessionTimeSeconds=30 * 60,
                 proxies=None,
                 userAgent='Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
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

        self.login(forceLogin, test_login, **kwargs)

    def modification_date(self, filename):
        """
        return last file modification date as datetime object
        """
        t = os.path.getmtime(filename)
        return datetime.datetime.fromtimestamp(t)

    def login(self, forceLogin=False, test_login=False, **kwargs):
        """
        login to a session. Try to read last saved session from cache file. If this fails
        do proper login. If the last cache access was too old, also perform a proper login.
        Always updates session cache file.
        """
        wasReadFromCache = False
        # logger.debug('loading or generating session...')
        if os.path.exists(self.sessionFile) and not forceLogin:
            time = self.modification_date(self.sessionFile)

            # only load if file less than 30 minutes old
            lastModification = (datetime.datetime.now() - time).seconds
            if lastModification < self.maxSessionTime:
                with open(self.sessionFile, "rb") as f:
                    self.session = pickle.load(f)
                    wasReadFromCache = True
                    # logger.debug("loaded session from cache (last access %ds ago) " % lastModification)
        if not wasReadFromCache:
            self.session = requests.Session()
            self.session.headers.update({'user-agent': self.userAgent})
            res = self.session.post(self.loginUrl, data=self.loginData,
                                    proxies=self.proxies, **kwargs)
            logger.debug('created new session with login')
            self.saveSessionToCache()

        if test_login:
            # test login
            logger.debug('Loaded session from cache and testing login...')
            res = self.session.get(self.loginTestUrl)
            if res.text.lower().find(self.loginTestString.lower()) < 0:
                os.remove(self.sessionFile) # delete the session file if login fails
                logger.debug(res.text)
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
            logger.debug('updated session cache-file %s' % self.sessionFile)

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
