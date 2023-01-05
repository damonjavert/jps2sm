import logging
import os
from typing import AnyStr

# Third-party modules
from pymediainfo import MediaInfo
import torrent_parser as tp
from pyunpack import Archive
from pathlib import Path
import tempfile

logger = logging.getLogger('main.' + __name__)


def get_mediainfo(jps_torrent_object, media, media_roots):
    """
    Get filename(s) of video files in the torrent and run mediainfo and capture the output, extract if DVD found (Blurays not yet supported)
    then set the appropriate fields for the upload

    :param jps_torrent_object: bytes: BytesIO object of the JPS torrent
    :param media: str Validated media from collate()
    :param media_roots: Sanitised MediaDirectories from cfg for use by get_media_location()
    :return: mediainfo, releasedataout

    mediainfo: Mediainfo text output of the file(s)
    releaseadtaout: Fields gathered from mediainfo for SM upload
    """

    def validate_container(file_extension: str) -> AnyStr:
        """
        Map known 'bad' / alternative file extensions of containers to the primary name of the container type.
        """
        extensions = {
            "TP": "TS",
            "TSV": "TS",
            "TSA": "TS",
            "M4V": "MP4",
            "MPG": "MPEG",
        }

        validated_extension = file_extension  # Default is to not validate if it is not in the known incorrect list above - let SM catch it.
        for old, new in extensions.items():
            if file_extension.upper() == old:
                validated_extension = new

        return validated_extension

    def validate_codec(codec: str) -> AnyStr:
        """
        Map known alternative names for codecs returned by mediainfo to the primary name of the codec
        """
        codecs = {
            "MPEG Video": "MPEG-2",
            "AVC": "h264",
            "HEVC": "h265",
            "MPEG-4 Visual": "DivX",  # MPEG-4 Part 2 / h263 , usually xvid / divx
            "VP09": "VP9",
            "VP08": "VP8",
        }

        validated_codec = codec  # Default is to not validate it if it is not known in the incorrect list above - let SM catch it.
        for old, new in codecs.items():
            if codec == old:
                validated_codec = new

        return validated_codec

    torrentmetadata = tp.TorrentFileParser(jps_torrent_object).parse()
    torrentname = torrentmetadata['info']['name']  # Directory if >1 file, otherwise it is filename
    # print(torrentmetadata)
    mediainfosall = ""
    releasedataout = {}
    releasedataout['duration'] = 0

    # TODO Need to cleanup the logic to create an overall filename list to parse instead of the 3-way duplication we currently have

    if 'files' in torrentmetadata['info'].keys():  # Multiple files
        directory = torrentname
        logger.info(f'According torrent metadata the dir is {directory}')
        file_path = get_media_location(directory, True, media_roots)
        logger.info(f'Path to dir: {file_path}')
        for file in torrentmetadata['info']['files']:
            if len(torrentmetadata['info']['files']) == 1:  # This might never happen, it could be just info.name if so
                filename = os.path.join(*file['path'])
            else:
                releasedataout['multiplefiles'] = True
                filename = os.path.join(*[file_path, *file['path']])  # Each file in the directory of source data for the torrent

            mediainfosall += str(MediaInfo.parse(filename, text=True))
            releasedataout['duration'] += get_mediainfo_duration(filename)
            # Get biggest file and mediainfo on this to set the fields for the release
            maxfile = max(torrentmetadata['info']['files'], key=lambda x: x['length'])  # returns {'length': int, 'path': [str]} of largest file
            fileforsmfields = Path(*[file_path, *maxfile['path']])  # Assume the largest file is the main file that should populate SM upload fields

    else:  # Single file
        releasedataout['multiplefiles'] = False
        filename = torrentname
        file_path = get_media_location(filename, False, media_roots)
        logger.debug(f'Filename for mediainfo: {file_path}')
        mediainfosall += str(MediaInfo.parse(file_path, text=True))
        releasedataout['duration'] += get_mediainfo_duration(file_path)
        fileforsmfields = file_path

    if fileforsmfields.suffix == '.iso' and media == 'DVD':
        # If DVD, extract the ISO and run mediainfo against appropriate files, if BR we skip as pyunpack (patool/7z) cannot extract them
        releasedataout['container'] = 'ISO'
        logger.info(f'Extracting ISO {fileforsmfields} to obtain mediainfo on it...')
        isovideoextensions = ('.vob', '.m2ts')
        tempdir = tempfile.TemporaryDirectory()
        Archive(fileforsmfields).extractall(tempdir.name)
        dir_files = []
        for root, subFolder, files in os.walk(tempdir.name):
            for item in files:
                filenamewithpath = os.path.join(root, item)
                dir_files.append(filenamewithpath)
                if list(filter(filenamewithpath.lower().endswith,
                               isovideoextensions)):  # Only gather mediainfo for DVD video files (BR when supported)
                    mediainfosall += str(MediaInfo.parse(filenamewithpath, text=True))
                    releasedataout['duration'] += get_mediainfo_duration(filenamewithpath)

        filesize = lambda f: os.path.getsize(f)
        fileforsmfields = sorted(dir_files, key=filesize)[-1]  # Assume the largest file is the main file that should populate SM upload fields

    # Now we have decided which file will have its mediainfo parsed for SM fields, parse its mediainfo
    mediainforeleasedata = MediaInfo.parse(fileforsmfields)
    # Remove path to file in case it reveals usernames etc.
    replacement = str(Path(file_path).parent)
    mediainfosall = mediainfosall.replace(replacement, '')

    if Path(fileforsmfields).suffix == '.iso' and media == 'DVD':
        tempdir.cleanup()

    for track in mediainforeleasedata.tracks:
        if track.track_type == 'General':
            # releasedataout['language'] = track.audio_language_list  # Will need to check if this is reliable
            if 'container' not in releasedataout:  # Not an ISO, only set container if we do not already know its an ISO
                releasedataout['container'] = validate_container(track.file_extension.upper())
            else:  # We have ISO - get category data based Mediainfo if we have it
                if track.file_extension.upper() == 'VOB':
                    releasedataout['category'] = 'DVD'
                elif track.file_extension.upper() == 'M2TS':  # Not used yet as we cannot handle Bluray / UDF
                    releasedataout['category'] = 'Bluray'

        if track.track_type == 'Video':
            releasedataout['codec'] = validate_codec(track.format)

            standardresolutions = {
                "3840": "1920",
                "1920": "1080",
                "1280": "720",
                "720": "480",
            }
            for width, height in standardresolutions.items():
                if str(track.width) == width and str(track.height) == height:
                    releasedataout['ressel'] = height

            if 'ressel' in releasedataout.keys():  # Known resolution type, try to determine if interlaced
                if track.scan_type == "Interlaced" or track.scan_type == "MBAFF":
                    releasedataout['ressel'] += "i"
                else:
                    releasedataout['ressel'] += "p"  # Sometimes a Progressive encode has no field set
            else:  # Custom resolution
                releasedataout['ressel'] = 'Other'
                releasedataout['resolution'] = str(track.width) + "x" + str(track.height)

        if track.track_type == 'Audio' or track.track_type == 'Audio #1':  # Handle multiple audio streams, we just get data from the first for now
            if track.format in ["AAC", "DTS", "PCM", "AC3", "Vorbis", "Opus"]:
                releasedataout['audioformat'] = track.format
            elif track.format == "AC-3":
                releasedataout['audioformat'] = "AC3"
            elif track.format == "MPEG Audio" and track.format_profile == "Layer 3":
                releasedataout['audioformat'] = "MP3"
            elif track.format == "MPEG Audio" and track.format_profile == "Layer 2":
                releasedataout['audioformat'] = "MP2"

    logger.debug(f'Mediainfo interpreted data: {releasedataout}')

    return mediainfosall, releasedataout


def get_mediainfo_duration(filename):
    """
    Get duration in mediainfo for filename

    :param filename:
    :return: float ms
    """
    mediainfo_for_duration = MediaInfo.parse(filename)
    for track in mediainfo_for_duration.tracks:
        if track.track_type == 'General':
            if track.duration is None:
                return 0
            else:
                logger.info(f'Mediainfo duration: {filename} {track.duration}')
                return float(track.duration)  # time in ms


def get_media_location(media_name, directory, media_roots):
    """
    Find the location of the directory or file of the source data for getmediainfo()

    :param media_name: str name of the file or directory
    :param directory: boolean true if dir, false if file
    :param fall_back_file: str fall back search cor
    :param media_roots: Sanitised MediaDirectories from cfg

    :return: full path to file/dir
    """

    # Find the file/dir and stop on the first hit, hopefully OS-side disk cache will mean this will not take too long

    media_location = None
    logger.info(f'Searching for {media_name}...')

    for media_dir_search in media_roots:
        for dirname, dirnames, filenames in os.walk(media_dir_search):
            if directory is True:
                for subdirname in dirnames:
                    if subdirname == media_name:
                        media_location = os.path.join(dirname, subdirname)
                        return Path(media_dir_search, media_location)
            else:
                for filename in filenames:
                    if filename == media_name:
                        media_location = os.path.join(dirname, filename)
                        return Path(media_dir_search, media_location)

    if media_location is None:
        media_not_found_error_msg = f'Mediainfo error - file/directory not found: {media_name} in any of the MediaDirectories specified: {media_roots}'
        logger.error(media_not_found_error_msg)
        raise RuntimeError(media_not_found_error_msg)
