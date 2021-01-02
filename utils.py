import functools
import re
from typing import List, AnyStr


def split_artists(artist: str) -> List[str]:
    """
    Splits the artist string on the specified delimiters.

            Parameters:
                    artist (str): A string containing artists
            Returns:
                    list (List(str)): List of artists
    """
    replacements = ('-', ',', 'x', '&')
    artists = functools.reduce(lambda s, sep: s.replace(sep, ' '), replacements, artist)
    return artists.split()


def get_valid_filename(s: str) -> AnyStr:
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
            Parameters:
                    s (str): A string that needs to be converted
            Returns:
                    s (str): A string with a clean filename
    """
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)
