"""
Tests for validate_codec()
"""
from jps2sm.mediainfo import validate_codec


def test_validate_codec():
    """
    Test for validate_codec()
    """

    assert validate_codec("AVC") == "h264"
    assert validate_codec("VP09") == "VP9"
    assert validate_codec("DivX") == "DivX"
    assert validate_codec("5608759367590759683") == "5608759367590759683"  # Test that it leaves unknown strings alone
