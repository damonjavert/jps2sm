# Third-party packages
from requestsloginsession import RequestsLoginSession

# jps2sm modules
from jps2sm.utils import GetConfig


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

    jps_session = RequestsLoginSession(jps_login_url, login_data, jps_test_url, jps_success, test_login)

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

    sm_login_url = "https://sugoimusic.me/login.php"
    sm_test_url = "https://sugoimusic.me/"
    sm_success = "Enabled users"
    login_data = {'username': config.sm_user, 'password': config.sm_pass}

    sm_session = RequestsLoginSession(sm_login_url, login_data, sm_test_url, sm_success, test_login)

    return sm_session.retrieve_content(url, method, post_data, post_data_files)

