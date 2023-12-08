"""
Perform validation of JPS data
"""
# pylint: disable=no-name-in-module,import-error
# pylint appears to have a bug where it cannot import despite python itself being able to

# Standard library packages
import re

# Third-party packages
from bs4 import BeautifulSoup
import torrent_parser as tp
from loguru import logger

# jps2sm modules
from jps2sm.myloginsession import jpopsuki
from jps2sm.constants import Categories, VideoOptions
from jps2sm.utils import GetArgs


def decide_music_performance(artists, multiple_files, duration):
    """
    Return if upload should be a Music Performance or not
    A music performance is a cut from a Music TV show and is 25 mins or less long and therefore also not a TV Show artist

    We assume we are being called if Cat = TV Music

    :return:  str: 'Music Performance' or 'TV Music'
    """
    if multiple_files is True or duration > 1500000:  # 1 500 000 ms = 25 mins
        return 'TV Music'

    # Single file that is < 25 mins, decide if Music Performance
    if len(artists) > 1:  # Multiple artists
        logger.debug('Upload is a Music Performance as it has derived multiple artists and is 25 mins or less')
        return 'Music Performance'  # JPS TV Show artists never have multiple artists

    # Single file
    jps_artist_page = jpopsuki(f"https://jpopsuki.eu/artist.php?name={artists[0]}")
    soup = BeautifulSoup(jps_artist_page.text, 'html5lib')
    categories_box = str(soup.select('#content .thin .main_column .box.center'))
    categories = re.findall(r'\[(.+)\]', categories_box)
    if any({*Categories.NonTVCategories} & {*categories}):  # Exclude any TV Shows for being mislabeled as Music Performance
        logger.debug('Upload is a Music Performance as it is 25 mins or less and not a TV Show')
        return 'Music Performance'

    logger.debug('Upload is not a Music Performance')
    return 'TV Music'


def get_alternate_fansub_category_id(artist, group_name):
    """
    Attempts to detect the actual category for JPS Fansubs category torrents and if not ask the user to select an alternate category.
    If it is a TV show, this TV show category type is detected and returned, else query the user from a list of potential categories.

    :param artist: str artist name
    :param group_name: str JPS group name
    :return: int alternative category ID based on Categories.SM()
    """
    jps_artist_page = jpopsuki(f"https://jpopsuki.eu/artist.php?name={artist}")
    soup = BeautifulSoup(jps_artist_page.text, 'html5lib')
    categories_box = str(soup.select('#content .thin .main_column .box.center'))
    categories = re.findall(r'\[(.+)\]', categories_box)

    if not any({*Categories.NonTVCategories} & {*categories}) and " ".join(categories).count('TV-') == 1:
        # Artist has no music and only 1 TV Category, artist is a TV show and we can auto detect the category for FanSub releases
        autodetect_category = re.findall(r'(TV-(?:[^ ]+))', " ".join(categories))[0]
        logger.debug(f'Autodetected SM category {autodetect_category} for JPS Fansubs torrent')
        return autodetect_category

    # Cannot autodetect
    alternate_fansub_categories_ids = (5, 6, 7, 8, 9, 11)  # Matches indices in Categories()
    logger.warning(f'Cannot auto-detect correct category for torrent group {group_name}.')
    print('Select Category:')
    option = 1
    option_lookup = {}
    for alternative_fansub_category_id in alternate_fansub_categories_ids:
        for cat, catid in Categories.SM.items():
            if alternative_fansub_category_id == catid:
                print(f'({option}) {cat}')
                option_lookup[option] = alternative_fansub_category_id
                option += 1
    alternate_category_option = input('Choose alternate category or press ENTER to skip: ')

    # User did not choose an option
    if alternate_category_option == "":
        logger.error('No alternate Fansubs category chosen.')
        return "Fansubs"  # Allow upload to fail

    # User chose an option
    category = option_lookup[int(alternate_category_option)]
    logger.info(f'Alternate Fansubs category {category} chosen')
    return category


def validate_jps_video_data(slash_data, category_status):
    """
    Validate and process dict supplied by get_release_data() via collate() to extract all available data
    from JPS for video torrents, whilst handling weird cases where VideoTorrent is uploaded as a Music category

    :param slash_data: list: 'slash data' from collate()
    :param category_status: str: good or bad. good for correct category assigned and bad if this is a Music Torrent
    mistakenly uploaded as a non-VC category!
    :return: jps_video_data{} validated container, codec, media, audioformat
    """
    jps_video_data = {}
    # JPS uses the audioformat field (represented as slash_data[0] here) for containers and codecs in video torrents

    # If a known container is used as audioformat set it as the container on SM
    if slash_data[0] in VideoOptions.badcontainers:
        jps_video_data['container'] = slash_data[0]
    else:
        jps_video_data['container'] = 'CHANGEME'
    # If a known codec is used as audioformat set it as the codec on SM
    if slash_data[0] in VideoOptions.badcodecs:
        if slash_data[0] == "MPEG2":  # JPS uses 'MPEG2' for codec instead of the correct 'MPEG-2'
            jps_video_data['codec'] = "MPEG-2"
        else:
            jps_video_data['codec'] = slash_data[0]
    else:
        jps_video_data['codec'] = 'CHANGEME'  # assume default

    if category_status == "good":
        jps_video_data['media'] = slash_data[1]
    else:
        jps_video_data['media'] = slash_data[2]

    if slash_data[0] == 'AAC':  # For video torrents, the only correct audioformat in JPS is AAC
        jps_video_data['audioformat'] = "AAC"
    else:
        jps_video_data['audioformat'] = "CHANGEME"

    return jps_video_data


def validate_jps_bitrate(jps_bitrate):
    """
    Validate JPS bad bitrates to sensible bitrates ready for upload to SM

    :param jps_bitrate:
    :return: sm_bitrate
    """

    bitrates = {
        "Hi-Res 96/24": "24bit Lossless 96kHz",
        "24bit/48kHz": "24bit Lossless 48kHz",
        "Hi-Res": "24bit Lossless",
        "24/44.1": "24bit Lossless",
        "Hi-Res 48/24": "24bit Lossless 48kHz",
        "Hi-Res 96-24": "24bit Lossless 96kHz",
        "24bit/96kHz": "24bit Lossless 96kHz",
        "24bit/48Khz": "24bit Lossless 48kHz",
        "24bit/96Khz": "24bit Lossless 96kHz",
        "24bit/48khz": "24bit Lossless 48kHz",
        "24/48": "24bit Lossless 48kHz",
        "24/96": "24bit Lossless 96kHz",
        "Hi-Res Lossless": "24bit Lossless",
        "160": "Other",
        "Variable": "Other",
        "320 (VBR)": "Other",
        "Scans": "",
        "Booklet": "",
        "1080p": "",
        "720p": "",
        "256 (VBR)": "APS (VBR)",
        "155": "Other"
    }

    sm_bitrate = jps_bitrate  # Default is to leave bitrate alone if not mentioned here, such as bitrates that are OK on both JPS and SM
    for old, new in bitrates.items():
        if jps_bitrate == old:
            sm_bitrate = new

    return sm_bitrate


def decide_exc_filter(audioformat, media, releasedata):
    """
    Implement audioformat and media exclusion filters
    :return: boolean: True or False
    """
    args = GetArgs()

    if audioformat == args.parsed.excaudioformat:
        logger.info(f'Excluding {releasedata} as exclude audioformat {args.parsed.excaudioformat} is set')
        return True
    if media == args.parsed.excmedia:
        logger.info(f'Excluding {releasedata} as exclude media {args.parsed.excmedia} is set')
        return True

    return False


def decide_ep(jps_torrent_object, uploaddata):
    """
    Return if Album upload should be an EP or not.
    EPs are considered to have < 7 tracks, excluding off-vocals and uploaded to JPS as an Album

    We assume we are being called only if Cat = Album

    :param jps_torrent_object: bytes: BytesIO object of the JPS torrent
    :param uploaddata:
    :return: str: 'EP' or 'Album'
    """

    if uploaddata['media'].lower() == 'bluray' or uploaddata['media'].lower() == 'dvd':
        return 'Album'

    torrent_metadata = tp.TorrentFileParser(jps_torrent_object).parse()
    music_extensions = ['.flac', '.mp3', '.ogg', '.alac', '.m4a', '.wav', '.wma', '.ra']
    off_vocal_phrases = ['off-vocal', 'offvocal', 'off vocal', 'inst.', 'instrumental', 'english ver', 'japanese ver', 'korean ver']
    track_count = 0
    has_cue = False
    track_extensions = set()
    for file in torrent_metadata['info']['files']:
        file_path = file['path'][-1].lower()

        if file_path.endswith('.iso'):
            return 'Album'

        if file_path.endswith('.cue'):
            has_cue = True

        if list(filter(file_path.endswith, music_extensions)) and \
                not any(substring in file_path for substring in off_vocal_phrases):
            #  Count music files which are not an off-vocal or instrumental
            logger.trace(f"Deciding if EP with torrent with these tracks: {file['path'][-1]}")
            track_count += 1
            track_extensions.add(file_path.split('.')[-1])

    if has_cue and track_extensions == {'flac'}:
        logger.debug('Upload is not an EP as it has a .cue file and only .flac files')
        return 'Album'

    if track_count < 7:
        logger.debug(f'Upload is an EP as it has {track_count} standard tracks')
        return 'EP'

    # 7 or more tracks
    logger.debug(f'Upload is not an EP as it has {track_count} tracks')
    return 'Album'
