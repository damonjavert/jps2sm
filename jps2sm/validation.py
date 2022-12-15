# Standard library packages
import logging
import re

from jps2sm.myloginsession import jpopsuki
from jps2sm.constants import Categories, VideoOptions
from jps2sm.utils import GetArgs

# Third-party packages
from bs4 import BeautifulSoup
import torrent_parser as tp

logger = logging.getLogger('main.' + __name__)


def decide_music_performance(artists, multiplefiles, duration):
    """
    Return if upload should be a Music Performance or not
    A music performance is a cut from a Music TV show and is 25 mins or less long and therefore also not a TV Show artist

    We assume we are being called if Cat = TV Music

    :return:  str: 'Music Performance' or 'TV Music'
    """
    if multiplefiles is True or duration > 1500000:  # 1 500 000 ms = 25 mins
        return 'TV Music'
    else:  # Single file that is < 25 mins, decide if Music Performance
        if len(artists) > 1:  # Multiple artists
            logger.debug('Upload is a Music Performance as it has derived multiple artists and is 25 mins or less')
            return 'Music Performance'  # JPS TV Show artists never have multiple artists
        JPSartistpage = jpopsuki(f"https://jpopsuki.eu/artist.php?name={artists[0]}")
        soup = BeautifulSoup(JPSartistpage.text, 'html5lib')
        categoriesbox = str(soup.select('#content .thin .main_column .box.center'))
        categories = re.findall(r'\[(.+)\]', categoriesbox)
        if any({*Categories.NonTVCategories} & {*categories}):  # Exclude any TV Shows for being mislabeled as Music Performance
            logger.debug('Upload is a Music Performance as it is 25 mins or less and not a TV Show')
            return 'Music Performance'
        else:
            logger.debug('Upload is not a Music Performance')
            return 'TV Music'


def get_alternate_fansub_category_id(artist, group_name):
    """
    Attempts to detect the actual category for JPS Fansubs category torrents and if not ask the user to select an alternate category.
    If it is a TV show, this TV show category type is detected and returned, else query the user from a list of potential categories.

    :param artist: str artist name
    :return: int alternative category ID based on Categories.SM()
    """
    JPSartistpage = jpopsuki(f"https://jpopsuki.eu/artist.php?name={artist}")
    soup = BeautifulSoup(JPSartistpage.text, 'html5lib')
    categoriesbox = str(soup.select('#content .thin .main_column .box.center'))
    categories = re.findall(r'\[(.+)\]', categoriesbox)

    if not any({*Categories.NonTVCategories} & {*categories}) and " ".join(categories).count('TV-') == 1:
        # Artist has no music and only 1 TV Category, artist is a TV show and we can auto detect the category for FanSub releases
        autodetectcategory = re.findall(r'(TV-(?:[^ ]+))', " ".join(categories))[0]
        logger.debug(f'Autodetected SM category {autodetectcategory} for JPS Fansubs torrent')
        return autodetectcategory
    else:  # Cannot autodetect
        AlternateFanSubCategoriesIDs = (5, 6, 7, 8, 9, 11)  # Matches indices in Categories()
        logger.warning(f'Cannot auto-detect correct category for torrent group {group_name}.')
        print('Select Category:')
        option = 1
        optionlookup = {}
        for alternativefansubcategoryid in AlternateFanSubCategoriesIDs:
            for cat, catid in Categories.SM.items():
                if alternativefansubcategoryid == catid:
                    print(f'({option}) {cat}')
                    optionlookup[option] = alternativefansubcategoryid
                    option += 1
        alternatecategoryoption = input('Choose alternate category or press ENTER to skip: ')
        if alternatecategoryoption == "":
            logger.error('No alternate Fansubs category chosen.')
            return "Fansubs"  # Allow upload to fail
        else:
            category = optionlookup[int(alternatecategoryoption)]
            logger.info(f'Alternate Fansubs category {category} chosen')
            return category


def validate_jps_video_data(releasedata, categorystatus):
    """
    Validate and process dict supplied by getreleasedata() via collate() to extract all available data
    from JPS for video torrents, whilst handling weird cases where VideoTorrent is uploaded as a Music category

    :param releasedata:
    :param categorystatus: str: good or bad. good for correct category assigned and bad if this is a Music Torrent
    mistakenly uploaded as a non-VC category!
    :return: releasedataout{} validated container, codec, media, audioformat
    """
    releasedataout = {}
    # JPS uses the audioformat field (represented as releasedata[0] here) for containers and codecs in video torrents

    # If a known container is used as audioformat set it as the container on SM
    if releasedata[0] in VideoOptions.badcontainers:
        releasedataout['container'] = releasedata[0]
    else:
        releasedataout['container'] = 'CHANGEME'
    # If a known codec is used as audioformat set it as the codec on SM
    if releasedata[0] in VideoOptions.badcodecs:
        if releasedata[0] == "MPEG2":  # JPS uses 'MPEG2' for codec instead of the correct 'MPEG-2'
            releasedataout['codec'] = "MPEG-2"
        else:
            releasedataout['codec'] = releasedata[0]
    else:
        releasedataout['codec'] = 'CHANGEME'  # assume default

    if categorystatus == "good":
        releasedataout['media'] = releasedata[1]
    else:
        releasedataout['media'] = releasedata[2]

    if releasedata[0] == 'AAC':  # For video torrents, the only correct audioformat in JPS is AAC
        releasedataout['audioformat'] = "AAC"
    else:
        releasedataout['audioformat'] = "CHANGEME"

    return releasedataout


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
    elif media == args.parsed.excmedia:
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
            logger.debug(f"Deciding if EP with torrent with these tracks: {file['path'][-1]}")
            track_count += 1
            track_extensions.add(file_path.split('.')[-1])

    if has_cue and track_extensions == {'flac'}:
        logger.debug(f'Upload is not an EP as it has a .cue file and only .flac files')
        return 'Album'

    if track_count < 7:
        logger.debug(f'Upload is an EP as it has {track_count} standard tracks')
        return 'EP'
    else:
        logger.debug(f'Upload is not an EP as it has {track_count} tracks')
        return 'Album'
