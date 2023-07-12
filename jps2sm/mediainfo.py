"""
mediainfo processing
"""
# pylint: disable=no-name-in-module,import-error
# pylint appears to have a bug where it cannot import despite python itself being able to
# pylint: disable=fixme

# Standard library packages
import os
from io import BytesIO
from typing import List, Tuple, Dict, Union
from pathlib import Path
import tempfile

# Third-party modules
from pymediainfo import MediaInfo
import torrent_parser as tp
from pyunpack import Archive
from loguru import logger

# jps2sm modules
from jps2sm.utils import GetConfig


def validate_container(file_extension: str) -> str:
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


def validate_codec(codec: str) -> str:
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


def get_mediainfo(jps_torrent_object: BytesIO, media: str) -> Tuple[str, Dict[str, str]]:
    """
    Get filename(s) of video files in the torrent and run mediainfo and capture the output, extract if DVD found (Blurays not yet supported)
    then set the appropriate fields for the upload

    :param jps_torrent_object: bytes: BytesIO object of the JPS torrent
    :param media: str Validated media from collate()
    :return: mediainfo, releasedataout
            mediainfo: Mediainfo text output of the file(s)
            releaseadtaout: Fields gathered from mediainfo for SM upload
    """

    config = GetConfig()
    torrent_metadata = tp.TorrentFileParser(jps_torrent_object).parse()
    torrent_name = torrent_metadata['info']['name']  # Directory if >1 file, otherwise it is filename
    # print(torrentmetadata)
    mediainfo_whole_str = ""
    release_data_from_mediainfo = {'duration': 0}

    # TODO Need to cleanup the logic to 3^H2-way duplication we currently have between ISO and non-ISO

    torrent_has_directory = bool('files' in torrent_metadata['info'].keys())

    logger.info(f'According to torrent metadata the dir/file is is {torrent_name}')
    file_path = get_media_location(torrent_name, torrent_has_directory, config.media_roots)
    if not torrent_has_directory:
        release_data_from_mediainfo['multiplefiles'] = False
        mediainfo_whole_str += str(MediaInfo.parse(file_path, text=True))
        release_data_from_mediainfo['duration'] += get_mediainfo_duration(file_path)
        file_for_sm_upload_video_fields = file_path
    else:
        release_data_from_mediainfo['multiplefiles'] = True
        for file in torrent_metadata['info']['files']:
            file_name = os.path.join(*[file_path, *file['path']])  # Each file in the directory of source data for the torrent
            mediainfo_whole_str += str(MediaInfo.parse(file_name, text=True))
            release_data_from_mediainfo['duration'] += get_mediainfo_duration(file_name)  # TODO should this reference file_path directly?
        # Get biggest file and mediainfo on this to set the fields for the release
        max_file = max(torrent_metadata['info']['files'], key=lambda x: x['length'])  # returns {'length': int, 'path': [str]} of largest file
        # Assume the largest file is the main file that should populate SM upload fields
        file_for_sm_upload_video_fields = Path(*[file_path, *max_file['path']])

    if file_for_sm_upload_video_fields is None:
        raise RuntimeError("Error in parsing torrent meta data to get the filename used for populating the SM media fields.")

    if file_for_sm_upload_video_fields.suffix == '.iso' and media == 'DVD':
        # If DVD, extract the ISO and run mediainfo against appropriate files, if BR we skip as pyunpack (patool/7z) cannot extract them
        release_data_from_mediainfo['container'] = 'ISO'
        logger.info(f'Extracting ISO {file_for_sm_upload_video_fields} to obtain mediainfo on it...')
        isovideoextensions = ('.vob', '.m2ts')
        tempdir = tempfile.TemporaryDirectory()
        Archive(file_for_sm_upload_video_fields).extractall(tempdir.name)
        dir_files = []
        for root, sub_folder, files in os.walk(tempdir.name):
            for item in files:
                filenamewithpath = os.path.join(root, item)
                dir_files.append(filenamewithpath)
                if list(filter(filenamewithpath.lower().endswith,
                               isovideoextensions)):  # Only gather mediainfo for DVD video files (BR when supported)
                    mediainfo_whole_str += str(MediaInfo.parse(filenamewithpath, text=True))
                    release_data_from_mediainfo['duration'] += get_mediainfo_duration(filenamewithpath)

        filesize = lambda f: os.path.getsize(f)
        file_for_sm_upload_video_fields = sorted(dir_files, key=filesize)[-1]  # Assume the largest file is the main file that should populate SM upload fields

    # Now we have decided which file will have its mediainfo parsed for SM fields, parse its mediainfo
    mediainfo_release_data = MediaInfo.parse(file_for_sm_upload_video_fields)
    # Remove path to file in case it reveals usernames etc.
    replacement = str(Path(file_path).parent)
    mediainfo_whole_str = mediainfo_whole_str.replace(replacement, '')

    if Path(file_for_sm_upload_video_fields).suffix == '.iso' and media == 'DVD':
        tempdir.cleanup()  # TODO This looks like it can be moved to the if block above

    mediainfo_general = mediainfo_video = mediainfo_audio = None

    for track in mediainfo_release_data.tracks:
        if track.track_type == 'General':
            mediainfo_general = track.__dict__
        if track.track_type == 'Video':
            mediainfo_video = track.__dict__
        if track.track_type in ('Audio', 'Audio #1'):  # Handle multiple audio streams, we just get data from the first for now
            mediainfo_audio = track.__dict__

    if mediainfo_general is None:
        raise RuntimeError('Bad mediainfo presented to get_mediainfo_duration. Missing "General" track type')
    if mediainfo_video is None:
        raise RuntimeError('Bad mediainfo presented to get_mediainfo_duration. Missing "Video" track type')
    if mediainfo_audio is None:
        raise RuntimeError('Bad mediainfo presented to get_mediainfo_duration. Missing "Audio" track type')

    video_fields_from_mediainfo = get_video_fields_from_mediainfo(general=mediainfo_general, video=mediainfo_video, audio=mediainfo_audio)
    release_data_from_mediainfo.update(video_fields_from_mediainfo)

    logger.debug(f'Mediainfo interpreted data: {release_data_from_mediainfo}')
    return mediainfo_whole_str, release_data_from_mediainfo


def get_video_fields_from_mediainfo(general: Dict, video: Dict, audio: Dict) -> Dict:
    """
    Determine the SM video fields from mediainfo track data

    :param general: Dict from get_mediainfo() of the 'General' mediainfo track
    :param video: Dict from get_mediainfo() of the 'Video' mediainfo track
    :param audio: Dict from get_mediainfo() of the 'Audio' mediainfo track
    :return video_fields_from_mediainfo: Dict with validated SM video fields from mediainfo
    """
    video_fields_from_mediainfo = {}

    # General track
    file_extension = general['file_extension'].upper()
    video_fields_from_mediainfo['container'] = validate_container(general['file_extension'].upper())
    if file_extension == 'VOB':
        video_fields_from_mediainfo['category'] = 'DVD'
    elif file_extension == 'M2TS':  # Not used yet as we cannot handle Bluray / UDF
        video_fields_from_mediainfo['category'] = 'Bluray'

    # Video track
    video_fields_from_mediainfo['codec'] = validate_codec(video['format'])

    standard_resolutions = {
        "3840": "1920",
        "1920": "1080",
        "1280": "720",
        "720": "480",
    }
    for width, height in standard_resolutions.items():
        if str(video['width']) == width and str(video['height']) == height:
            video_fields_from_mediainfo['ressel'] = height

    if 'ressel' in video_fields_from_mediainfo:  # Known resolution type, try to determine if interlaced
        if video['scan_type'] in ('Interlaced', 'MBAFF'):
            video_fields_from_mediainfo['ressel'] += "i"
        else:
            video_fields_from_mediainfo['ressel'] += "p"  # Sometimes a Progressive encode has no field set
    else:  # Custom resolution
        video_fields_from_mediainfo['ressel'] = 'Other'
        video_fields_from_mediainfo['resolution'] = str(video['width']) + "x" + str(video['height'])

    # Audio
    if audio['format'] in ["AAC", "DTS", "PCM", "AC3", "Vorbis", "Opus"]:
        video_fields_from_mediainfo['audioformat'] = audio['format']
    elif audio['format'] == "AC-3":
        video_fields_from_mediainfo['audioformat'] = "AC3"
    elif audio['format'] == "MPEG Audio" and audio['format_profile'] == "Layer 3":
        video_fields_from_mediainfo['audioformat'] = "MP3"
    elif audio['format'] == "MPEG Audio" and audio['format_profile'] == "Layer 2":
        video_fields_from_mediainfo['audioformat'] = "MP2"

    return video_fields_from_mediainfo


def get_mediainfo_duration(filename: Union[str, Path]) -> float:
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
            logger.info(f'Mediainfo duration: {filename} {track.duration}')
            return float(track.duration)  # time in ms

    raise RuntimeError('Bad mediainfo presented to get_mediainfo_duration. Missing "General" track type')


def get_media_location(media_name: str, directory: bool, media_roots: List[str]) -> Path:
    """
    Find the location of the directory or file of the source data for get_mediainfo()

    :param media_name: str name of the file or directory
    :param directory: boolean true if dir, false if file
    :param media_roots: Sanitised MediaDirectories from cfg

    :return: full path to file/dir
    """

    # Find the file/dir and stop on the first hit, hopefully OS-side disk cache will mean this will not take too long

    media_location = None
    logger.info(f'Searching for {media_name}...')

    for media_dir_search in media_roots:
        for dir_name, dir_names, filenames in os.walk(media_dir_search):
            if directory is True:
                for sub_dir_name in dir_names:
                    if sub_dir_name == media_name:
                        media_location = os.path.join(dir_name, sub_dir_name)
                        return Path(media_dir_search, media_location)
            else:
                for filename in filenames:
                    if filename == media_name:
                        media_location = os.path.join(dir_name, filename)
                        return Path(media_dir_search, media_location)

    # If we get this far the media was not found
    media_not_found_error_msg = f'Mediainfo error - file/directory not found: {media_name} in any of the MediaDirectories specified: {media_roots}'
    logger.error(media_not_found_error_msg)
    raise RuntimeError(media_not_found_error_msg)
