"""
Tests for validate_container()
"""
from jps2sm.mediainfo import validate_container


def test_validate_container():
    """
    Test for validate_container()
    """

    assert validate_container("TP") == "TS"
    assert validate_container("M4V") == "MP4"
    assert validate_container("MPG") == "MPEG"
    assert validate_container("5608759367590759683") == "5608759367590759683"  # Test that it leaves unknown strings alone
