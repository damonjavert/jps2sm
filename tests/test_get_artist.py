"""
Run tests for get_artist()
"""
from jps2sm.get_data import get_artist


def test_get_artist_standard():
    """
    Run standard artist-link tests
    """

    group_369567_h2_line = '<h2>[PV] <a href="artist.php?id=733">BUMP OF CHICKEN</a> - Stage of the ground [2002.02.20]</h2>'
    group_369567_artist_line_link = ['<a href="artist.php?id=733">BUMP OF CHICKEN</a>']
    assert get_artist(artist_line_link=group_369567_artist_line_link,
                      torrent_description_page_h2_line=group_369567_h2_line,
                      category="PV") == ["BUMP OF CHICKEN"]

    group_369604_h2_line = '<h2>[TV-Variety] <a href="artist.php?id=434">IU</a> - Made In BS Japan (2012.03.07)</h2>'
    group_369604_artist_line_link = ['<a href="artist.php?id=434">IU</a>']
    assert get_artist(artist_line_link=group_369604_artist_line_link,
                      torrent_description_page_h2_line=group_369604_h2_line,
                      category="TV-Variety") == ['IU']


def test_get_artist_pictures():
    """
    Run pictures artistless tests
    """

    group_365309_h2_line = '<h2>[Pictures] Weekly Shounen Champion 2023 No. 7 (HKT48 Miku Tanaka)</h2>'
    assert get_artist(artist_line_link=None,
                      torrent_description_page_h2_line=group_365309_h2_line,
                      category="Pictures") == ['Weekly Shounen Champion']

    group_363525_h2_line = '<h2>[Pictures] FLASH 2022.12.20 (Hinatazaka46 Miku Kanemura, ex-SKE48 Rara Goto, others)</h2>'
    assert get_artist(artist_line_link=None,
                      torrent_description_page_h2_line=group_363525_h2_line,
                      category="Pictures") == ['FLASH']


def test_get_artist_bad_misc():
    """
    Run bad Misc torrents with no artist set
    """

    group_10956_h2_line = '<h2>[Misc] Rain - Pizza Hut Slender Lunch Cf 20 s</h2>'
    assert get_artist(artist_line_link=None,
                      torrent_description_page_h2_line=group_10956_h2_line,
                      category="Misc") == ['Rain']

    group_2353_h2_line = '<h2>[Misc] Hyori Lee - Chum Churum Soju CF CM 30 seconds</h2>'
    assert get_artist(artist_line_link=None,
                      torrent_description_page_h2_line=group_2353_h2_line,
                      category="Misc") == ['Hyori Lee']
