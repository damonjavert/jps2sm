"""
Run tests for get_group_description_bbcode
"""
from jps2sm.get_data import get_group_description_bbcode
from jps2sm.myloginsession import LoginParameters


def test_get_group_description_bbcode(requests_mock):
    """
    Test for get_group_description_bbcode, with mock!
    """

    group_description_bbcode = """[img]http://i.imgur.com/LJQps.png[/img]
[img]http://i.imgur.com/oHjTw.jpg[/img]
[img]http://i.imgur.com/4ribV.jpg[/img]"""

    with open("tests/group-edit-page-121206", "r", encoding="utf-8") as group_edit_page_121206:
        requests_mock.post("https://jpopsuki.eu/login.php", text=LoginParameters.jps_success)  # Mock the initial login with requestsloginsession()
        requests_mock.get("https://jpopsuki.eu/torrents.php?action=editgroup&groupid=121206", text=group_edit_page_121206.read())
        assert group_description_bbcode == get_group_description_bbcode("121206")
