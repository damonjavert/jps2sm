"""
Run tests for validate_jps_video_data()
"""
# pylint: disable=duplicate-code

import pytest

from jps2sm.validation import validate_jps_video_data

def test_validate_jps_video_data_good_category() -> None:
    """
    Test for a simple correct JPS video group
    """
    slash_data_get_codec = ['MPEG2', 'HDTV', 'M-ON! HD - 2019']
    category_status = "good"
    assert validate_jps_video_data(slash_data=slash_data_get_codec, category_status=category_status)\
           == {'container': 'CHANGEME', 'codec': 'MPEG-2', 'media': 'HDTV', 'audioformat': 'CHANGEME'}

    slash_data_get_container = ['MP4', 'WEB', 'YouTube (1080p) - 2019']
    assert validate_jps_video_data(slash_data=slash_data_get_container, category_status=category_status)\
           == {'container': 'MP4', 'codec': 'CHANGEME', 'media': 'WEB', 'audioformat': 'CHANGEME'}


def test_validate_jps_video_data_bad_category() -> None:
    """
    Test for a video torrent uploaded at a non-video category:
    """
    slash_data = ['ISO', 'Lossless', 'DVD']
    category_status = "bad"

    assert validate_jps_video_data(slash_data=slash_data, category_status=category_status)\
           == {'container': 'ISO', 'codec': 'CHANGEME', 'media': 'DVD', 'audioformat': 'CHANGEME'}

