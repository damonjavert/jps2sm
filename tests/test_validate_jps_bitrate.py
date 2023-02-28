"""
Run tests for validate_jps_bitrate()
"""
import pytest

from jps2sm.validation import validate_jps_bitrate

def test_validate_jps_bitrate_bad_bitrate_hires() -> None:
    """
    Test for known bad JPS bitrate
    """
    assert validate_jps_bitrate("24/48") == "24bit Lossless 48kHz"
    assert validate_jps_bitrate("24bit/96kHz") == "24bit Lossless 96kHz"
    assert validate_jps_bitrate("Scans") == ""


def test_validate_jps_bitrate_good_bitrate() -> None:
    """
    Test for known correct JPS bitrates
    """
    assert validate_jps_bitrate("320") == "320"
    assert validate_jps_bitrate("256") == "256"
    assert validate_jps_bitrate("192") == "192"