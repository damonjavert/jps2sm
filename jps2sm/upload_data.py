"""
All defs that upload data to SM
"""
# pylint: disable=no-name-in-module,import-error
# pylint appears to have a bug where it cannot import despite python itself being able to

# Standard library packages
import re

# Third-party packages
from bs4 import BeautifulSoup
from loguru import logger

# jps2sm modules
from jps2sm.get_data import GetSMUser
from jps2sm.myloginsession import sugoimusic
from jps2sm.save_data import save_sm_html_debug_output


def set_original_artists(contrib_artists) -> None:
    """
    Set a batch of original artists from the contrib artists derived from GetGroupData()
    :param contrib_artists: dict in the form of { artist: orig_artist}
    """

    def set_original_artist(artist, orig_artist) -> None:
        """
        Set an artist's original artist with the string orig_artist, currently used for contrib artists
        # TODO Consider using this for main orig artist

        :param artist: string: String of the artist that needs it's original artist set
        :param orig_artist: string: Original artist
        """
        if orig_artist == "":  # If there is no orig_artist at JPS do not bother trying to set it here
            return

        SMartistpage = sugoimusic(f"https://sugoimusic.me/artist.php?artistname={artist}")

        if re.findall("Your search did not match anything", SMartistpage.text):
            logger.debug(f"Artist {artist} does not yet exist at SM so orig_artist cannot be set")
            return

        soup = BeautifulSoup(SMartistpage.text, 'html5lib')
        linkbox = str(soup.select('#content .thin .header .linkbox'))
        artistid = re.findall(r'href="artist\.php\?action=edit&amp;artistid=([0-9]+)"', linkbox)[0]

        sm_user = GetSMUser()

        data = {
            'action': 'edit',
            'auth': sm_user.auth_key(),
            'artistid': artistid,
            'name_jp': orig_artist
        }

        sugoimusic(f'https://sugoimusic.me/artist.php?artistname={artist}', 'post', data)
        logger.debug(f'Set artist {artist} original artist to {orig_artist}')

    # Add original artists for contrib artists
    if contrib_artists is None:  # Do not do anything if the group has no contrib artists
        return
    for artist, orig_artist in contrib_artists.items():
        # For every artist, go to its artist page to get artist ID, then use this to go to artist.php?action=edit with the orig artist
        try:
            set_original_artist(artist, orig_artist)
        except IndexError:  # Do not let a set_original_artist error affect stats
            logger.debug(f'Error in setting artist {artist} orig_artist {orig_artist}')
            pass


def upload_torrent(sugoimusic_upload_data, sugoimusic_upload_files):
    """
    Perform upload to SugoiMusic and do error handling

    :param sugoimusic_upload_data: dict of all required items in the format of:

    {
      "submit": "true", # Always must be 'true'
      "title": "torrent group title",
      "year": "YYYYMMDD",
      "tags": "tag1,tag2,tag3",
      "album_desc": "torrent group description",
      "auth": user_auth_key,
      "audioformat": "FLAC",
      "image": "full-url-of-group-image",
      "bitrate": "Lossless",
      "type": 0, # SM category ID, see Categories.SM
      "artist_jp": "\u7a32\u8449\u66c7",
      "title_jp": "\u30a2\u30f3\u30c1\u30b5\u30a4\u30af\u30ed\u30f3",
      "contrib_artists[]": [
        "contribartist1",
        "contribartist2"
      ],
      "idols[]": [
        "artist1",
        "artist2"
      ],
      "jps_torrent_id": jps_torrent_id  # optional
    }

    :param sugoimusic_upload_files: dict with the torrent to upload in the format of: {'file_input': ('filename.torrent', torrent_object: bytesIO) }
    """
    upload_url = 'https://sugoimusic.me/upload.php'

    sugoimusic_upload_res = sugoimusic(upload_url, "post", sugoimusic_upload_data, sugoimusic_upload_files)

    sugoimusic_upload_error = re.findall('red; text-align: center;">(.*)</p>', sugoimusic_upload_res.text)
    if sugoimusic_upload_error:
        raise Exception(sugoimusic_upload_error[0])

    sugoimusic_data_validation_error = re.findall('<p>Invalid (.*)</p>', sugoimusic_upload_res.text)
    if sugoimusic_data_validation_error:  # Error when invalid data entered for upload, eg. Invaid bitrate
        raise Exception(f'Invalid {sugoimusic_data_validation_error[0]}')

    html_debug_output_path_filename = f"sm_upload_output_{sugoimusic_upload_data['idols[]'][0]}_" \
                                      f"{sugoimusic_upload_data['title']}_" \
                                      f"{sugoimusic_upload_data['year']}_" \
                                      f"{sugoimusic_upload_data['jps_torrent_id']}.html"
    html_debug_output_path = save_sm_html_debug_output(sugoimusic_upload_res.text, html_debug_output_path_filename)

    sugoimusic_group_id = re.findall('<input type="hidden" name="groupid" value="([0-9]+)" />', sugoimusic_upload_res.text)
    if not sugoimusic_group_id:
        # Find sugoimusic_group_id if private torrent warning
        sugoimusic_group_id = re.findall(
            r'Your torrent has been uploaded; however, you must download your torrent from <a href="torrents\.php\?id=([0-9]+)">here</a>',
            sugoimusic_upload_res.text)
        if not sugoimusic_group_id:
            unknown_error_msg = f'Cannot find groupid in SM response - there was probably an unknown error. ' \
                                f'See {html_debug_output_path} for potential errors'
            raise RuntimeError(unknown_error_msg)

    if sugoimusic_group_id:
        logger.info(f'Torrent uploaded successfully as sugoimusic_group_id {sugoimusic_group_id[0]}  '
                    f'See https://sugoimusic.me/torrents.php?id={sugoimusic_group_id[0]}')
