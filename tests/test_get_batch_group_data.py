"""
Run tests for get_batch_group_data
"""
import json

from jps2sm.batch import get_batch_group_data
from jps2sm.myloginsession import LoginParameters


def test_get_batch_group_data(requests_mock, mocker):
    """
    Test for get_batch_group_data
    """
    # We mock this as it saves an extra set of request_mocks and this is already being tested in test_get_group_description_bbcode()
    mocker.patch("jps2sm.get_data.get_group_description_bbcode", return_value="Torrent description empty mocked")
    # Sleep in get_batch_jps_group_torrent_ids()
    # TODO Consider removing the sleep as it may have no impact in the JPS Browse quota as it appears to be a counter that gets
    #  reset every 30/60 mins and not a 'per min' counter as originally thought.
    mocker.patch("time.sleep")

    batch_uploads = {'173844': '474350',  # 2014 2NE1 WORLD TOUR ~ALL OR NOTHING~ in JAPAN
                     '120274': '164403',  # AKB48 - 1830m 	[ISO / DVD / Freeleech!] [2012.11.28]
                     '219216': '375899',  # Buono! Festa 2016
                     '212853': '300250',  # Buono single - gets excluded
                     '369725': '546224',  # Bad V.A. torrent
                     }

    excluded_category = "Single"

    with open("tests/group-page-173844", "r", encoding="utf-8") as group_page_173844_file:
        group_page_173844 = group_page_173844_file.read()
    with open("tests/group-page-120274", "r", encoding="utf-8") as group_page_120274_file:
        group_page_120274 = group_page_120274_file.read()
    with open("tests/group-page-219216", "r", encoding="utf-8") as group_page_219216_file:
        group_page_219216 = group_page_219216_file.read()
    with open("tests/group-page-212853", "r", encoding="utf-8") as group_page_212853_file:
        group_page_212853 = group_page_212853_file.read()
    with open("tests/group-page-369725-bad-va", "r", encoding="utf-8") as group_page_219216_bad_va_file:
        group_page_369725_bad_va = group_page_219216_bad_va_file.read()

    requests_mock.post("https://jpopsuki.eu/login.php", text=LoginParameters.jps_success)  # Mock the initial login with requestsloginsession()
    requests_mock.get("https://jpopsuki.eu/torrents.php?id=369725", text=group_page_369725_bad_va)
    requests_mock.get("https://jpopsuki.eu/torrents.php?id=212853", text=group_page_212853)
    requests_mock.get("https://jpopsuki.eu/torrents.php?id=219216", text=group_page_219216)
    requests_mock.get("https://jpopsuki.eu/torrents.php?id=120274", text=group_page_120274)
    requests_mock.get("https://jpopsuki.eu/torrents.php?id=173844", text=group_page_173844)

    with open("tests/batch-group-data", "r", encoding="utf-8") as batch_group_data_file:
        batch_group_data = batch_group_data_file.read()

    batch_results = get_batch_group_data(batch_uploads=batch_uploads, excluded_category=excluded_category)

    assert batch_results['batch_group_data'] == json.loads(batch_group_data)
    assert batch_results['batch_group_errors'] == {}
    assert batch_results['batch_groups_excluded'] == ['212853']
    assert batch_results['batch_groups_va_errors'] == ['369725']
