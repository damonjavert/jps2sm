import functools
import re
from typing import List, AnyStr


def split_artists(artist: str) -> List[str]:
    replacements = ('-', ',', 'x', '&')
    artists = functools.reduce(lambda s, sep: s.replace(sep, ' '), replacements, artist)
    return artists.split()


def get_valid_filename(s: str) -> AnyStr:
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)
