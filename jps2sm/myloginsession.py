"""
Handle login sessions for JPS and SM
"""
# pylint: disable=no-name-in-module,import-error
# pylint appears to have a bug where it cannot import despite python itself being able to

# Third-party packages
from requestsloginsession import RequestsLoginSession

# jps2sm modules
from jps2sm.utils import GetConfig
from jps2sm.constants import LoginParameters


def jpopsuki(url, test_login=False):
    """
    Get content from JPS

    :param url:
    :param test_login: Disable test login
    :return: data
    """

    config = GetConfig()
    login_data = {'username': config.jps_user, 'password': config.jps_pass}
    jps_session = RequestsLoginSession(LoginParameters.jps_login_url, login_data, LoginParameters.jps_test_url, LoginParameters.jps_success, test_login)

    return jps_session.retrieve_content(url)


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
    login_data = {'username': config.sm_user, 'password': config.sm_pass}
    sm_session = RequestsLoginSession(LoginParameters.sm_login_url, login_data, LoginParameters.sm_test_url, LoginParameters.sm_success, test_login)

    return sm_session.retrieve_content(url, method, post_data, post_data_files)
