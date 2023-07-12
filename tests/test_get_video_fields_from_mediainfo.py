"""
Tests for get_video_fields_from_mediainfo
"""
from jps2sm.mediainfo import get_video_fields_from_mediainfo


def test_mediainfo_get_sm_video_fields():
    """
    Test for get_video_fields_from_mediainfo
    """

    mediainfo_general = {'track_type': 'General', 'count': '331', 'count_of_stream_of_this_kind': '1', 'kind_of_stream': 'General',
         'other_kind_of_stream': ['General'], 'stream_identifier': '0', 'count_of_video_streams': '1', 'count_of_audio_streams': '1',
         'count_of_menu_streams': '2', 'video_format_list': 'AVC', 'video_format_withhint_list': 'AVC', 'codecs_video': 'AVC',
         'audio_format_list': 'AAC LC', 'audio_format_withhint_list': 'AAC LC', 'audio_codecs': 'AAC LC', 'menu_format_list': 'txet / ',
         'menu_format_withhint_list': 'txet / ', 'menu_codecs': 'txet / ', 'menu_language_list': 'English / ',
         'complete_name': '/file/+(KR)ystalEyes - Cherry Talk (THE SHOW 2023.07.04)@shrghkqud.mp4',
         'folder_name': '/file', 'file_name_extension': '+(KR)ystalEyes - Cherry Talk (THE SHOW 2023.07.04)@shrghkqud.mp4',
         'file_name': '+(KR)ystalEyes - Cherry Talk (THE SHOW 2023.07.04)@shrghkqud', 'file_extension': 'mp4', 'format': 'MPEG-4',
         'other_format': ['MPEG-4'],
         'format_extensions_usually_used': 'braw mov mp4 m4v m4a m4b m4p m4r 3ga 3gpa 3gpp 3gp 3gpp2 3g2 k3g jpm jpx mqv ismv isma ismt f4a f4b f4v',
         'commercial_name': 'MPEG-4', 'format_profile': 'Base Media', 'internet_media_type': 'video/mp4', 'codec_id': 'isom',
         'other_codec_id': ['isom (isom/iso2/avc1/mp41)'], 'codec_id_url': 'http://www.apple.com/quicktime/download/standalone.html',
         'codecid_compatible': 'isom/iso2/avc1/mp41', 'file_size': 454797043,
         'other_file_size': ['434 MiB', '434 MiB', '434 MiB', '434 MiB', '433.7 MiB'], 'duration': 178734,
         'other_duration': ['2 min 58 s', '2 min 58 s 734 ms', '2 min 58 s', '00:02:58.734', '00:02:58:44', '00:02:58.734 (00:02:58:44)'],
         'overall_bit_rate_mode': 'CBR', 'other_overall_bit_rate_mode': ['Constant'], 'overall_bit_rate': 20356375,
         'other_overall_bit_rate': ['20.4 Mb/s'], 'frame_rate': '60.000', 'other_frame_rate': ['60.000 FPS'], 'frame_count': '10724',
         'stream_size': 460519, 'other_stream_size': ['450 KiB (0%)', '450 KiB', '450 KiB', '450 KiB', '449.7 KiB', '450 KiB (0%)'],
         'proportion_of_this_stream': '0.00101', 'headersize': '460488', 'datasize': '454336555', 'footersize': '0', 'isstreamable': 'Yes',
         'file_last_modification_date': 'UTC 2023-07-12 23:51:03', 'file_last_modification_date__local': '2023-07-13 00:51:03',
         'writing_application': 'VideoReDo (Lavf58.29.100)', 'other_writing_application': ['VideoReDo (Lavf58.29.100)']}
    mediainfo_video = {'track_type': 'Video', 'count': '379', 'count_of_stream_of_this_kind': '1', 'kind_of_stream': 'Video',
                       'other_kind_of_stream': ['Video'],
         'stream_identifier': '0', 'streamorder': '0', 'track_id': 1, 'other_track_id': ['1'], 'format': 'AVC', 'other_format': ['AVC'],
         'format_info': 'Advanced Video Codec', 'format_url': 'http://developers.videolan.org/x264.html', 'commercial_name': 'AVC',
         'format_profile': 'High@L4.2', 'format_settings': 'CABAC / 2 Ref Frames', 'format_settings__cabac': 'Yes',
         'other_format_settings__cabac': ['Yes'], 'format_settings__reference_frames': 2, 'other_format_settings__reference_frames': ['2 frames'],
         'internet_media_type': 'video/H264', 'codec_id': 'avc1', 'codec_id_info': 'Advanced Video Coding', 'duration': 178734,
         'other_duration': ['2 min 58 s', '2 min 58 s 734 ms', '2 min 58 s', '00:02:58.734', '00:02:58:44', '00:02:58.734 (00:02:58:44)'],
         'bit_rate_mode': 'CBR', 'other_bit_rate_mode': ['Constant'], 'bit_rate': '20000000 / 20055000', 'other_bit_rate': ['20.0 Mb/s / 20.1 Mb/s'],
         'width': 1920, 'other_width': ['1 920 pixels'], 'height': 1080, 'other_height': ['1 080 pixels'], 'stored_height': '1088',
         'sampled_width': '1920', 'sampled_height': '1080', 'pixel_aspect_ratio': '1.000', 'display_aspect_ratio': '1.778',
         'other_display_aspect_ratio': ['16:9'], 'rotation': '0.000', 'frame_rate_mode': 'CFR', 'other_frame_rate_mode': ['Constant'],
         'frame_rate': '60.000', 'other_frame_rate': ['60.000 FPS'], 'frame_count': '10724', 'color_space': 'YUV', 'chroma_subsampling': '4:2:0',
         'other_chroma_subsampling': ['4:2:0'], 'bit_depth': 8, 'other_bit_depth': ['8 bits'], 'scan_type': 'Progressive',
         'other_scan_type': ['Progressive'], 'bits__pixel_frame': '0.161', 'stream_size': 447162176,
         'other_stream_size': ['426 MiB (98%)', '426 MiB', '426 MiB', '426 MiB', '426.4 MiB', '426 MiB (98%)'],
         'proportion_of_this_stream': '0.98321', 'writing_library': 'x264 - core 160 r3000', 'other_writing_library': ['x264 core 160 r3000'],
         'encoded_library_name': 'x264', 'encoded_library_version': 'core 160 r3000',
         'encoding_settings': 'cabac=1 / ref=2 / deblock=1:0:0 / analyse=0x3:0x113 / me=hex / subme=4 / psy=1 / psy_rd=1.00:0.00 / mixed_ref=0 / me_range=16 / chroma_me=1 / trellis=1 / 8x8dct=1 / cqm=0 / deadzone=21,11 / fast_pskip=1 / chroma_qp_offset=0 / threads=20 / lookahead_threads=5 / sliced_threads=0 / nr=0 / decimate=1 / interlaced=0 / bluray_compat=0 / constrained_intra=0 / bframes=3 / b_pyramid=2 / b_adapt=1 / b_bias=0 / direct=1 / weightb=1 / open_gop=0 / weightp=1 / keyint=60 / keyint_min=6 / scenecut=0 / intra_refresh=0 / rc_lookahead=20 / rc=cbr / mbtree=1 / bitrate=20055 / ratetol=1.0 / qcomp=0.60 / qpmin=0 / qpmax=69 / qpstep=4 / vbv_maxrate=20055 / vbv_bufsize=20000 / nal_hrd=none / filler=0 / ip_ratio=1.40 / aq=1:1.00',
         'buffer_size': '20000000', 'colour_description_present': 'Yes', 'colour_description_present_source': 'Stream', 'color_range': 'Full',
         'colour_range_source': 'Stream', 'color_primaries': 'BT.709', 'colour_primaries_source': 'Stream', 'transfer_characteristics': 'BT.709',
         'transfer_characteristics_source': 'Stream', 'matrix_coefficients': 'BT.709', 'matrix_coefficients_source': 'Stream', 'menus': '3',
         'codec_configuration_box': 'avcC'}
    mediainfo_audio = {'track_type': 'Audio', 'count': '281', 'count_of_stream_of_this_kind': '1', 'kind_of_stream': 'Audio',
                       'other_kind_of_stream': ['Audio'],
         'stream_identifier': '0', 'streamorder': '1', 'track_id': 2, 'other_track_id': ['2'], 'format': 'AAC', 'other_format': ['AAC LC'],
         'format_info': 'Advanced Audio Codec Low Complexity', 'commercial_name': 'AAC', 'format_settings__sbr': 'No (Explicit)',
         'other_format_settings__sbr': ['No (Explicit)'], 'format_additionalfeatures': 'LC', 'codec_id': 'mp4a-40-2', 'duration': 178689,
         'other_duration': ['2 min 58 s', '2 min 58 s 689 ms', '2 min 58 s', '00:02:58.689', '00:02:58:11', '00:02:58.689 (00:02:58:11)'],
         'duration_lastframe': -21, 'other_duration_lastframe': ['-21 ms', '-21 ms', '-21 ms', '-00:00:00.021'], 'bit_rate_mode': 'CBR',
         'other_bit_rate_mode': ['Constant'], 'bit_rate': 321201, 'other_bit_rate': ['321 kb/s'], 'channel_s': 2, 'other_channel_s': ['2 channels'],
         'channel_positions': 'Front: L R', 'other_channel_positions': ['2/0/0'], 'channel_layout': 'L R', 'samples_per_frame': '1024',
         'sampling_rate': 48000, 'other_sampling_rate': ['48.0 kHz'], 'samples_count': '8577072', 'frame_rate': '46.875',
         'other_frame_rate': ['46.875 FPS (1024 SPF)'], 'frame_count': '8377', 'compression_mode': 'Lossy', 'other_compression_mode': ['Lossy'],
         'stream_size': 7174348, 'other_stream_size': ['6.84 MiB (2%)', '7 MiB', '6.8 MiB', '6.84 MiB', '6.842 MiB', '6.84 MiB (2%)'],
         'proportion_of_this_stream': '0.01577', 'default': 'Yes', 'other_default': ['Yes'], 'alternate_group': 1, 'other_alternate_group': ['1'],
         'menus': '3'}

    assert get_video_fields_from_mediainfo(general=mediainfo_general, video=mediainfo_video, audio=mediainfo_audio)\
           == {'container': 'MP4', 'codec': 'h264', 'ressel': '1080p', 'audioformat': 'AAC'}


def test_mediainfo_get_sm_video_fields_torrentid_558477():
    """
    Test for get_video_fields_from_mediainfo torrentid 558477
    """

    mediainfo_general = dict(track_type='General', count='333', count_of_stream_of_this_kind='1', kind_of_stream='General',
                             other_kind_of_stream=['General'], stream_identifier='0', track_id=0, other_track_id=['0 (0x0)'],
                             count_of_video_streams='1', count_of_audio_streams='1', video_format_list='MPEG Video',
                             video_format_withhint_list='MPEG Video', codecs_video='MPEG Video', audio_format_list='AAC LC',
                             audio_format_withhint_list='AAC LC', audio_codecs='AAC LC',
                             complete_name='/file/Yu Takahashi - spotlight [1440x1080i MPEG2 M-ON! HD].ts',
                             folder_name='/file',
                             file_name_extension='Yu Takahashi - spotlight [1440x1080i MPEG2 M-ON! HD].ts',
                             file_name='Yu Takahashi - spotlight [1440x1080i MPEG2 M-ON! HD]', file_extension='ts', format='MPEG-TS',
                             other_format=['MPEG-TS'], format_extensions_usually_used='ts m2t m2s m4t m4s tmf ts tp trp ty',
                             commercial_name='MPEG-TS', internet_media_type='video/MP2T', file_size=193195944,
                             other_file_size=['184 MiB', '184 MiB', '184 MiB', '184 MiB', '184.2 MiB'], duration='221424.768037',
                             other_duration=['3 min 41 s', '3 min 41 s 425 ms', '3 min 41 s', '00:03:41.425', '00:03:41;00',
                                             '00:03:41.425 (00:03:41;00)'], overall_bit_rate_mode='VBR', other_overall_bit_rate_mode=['Variable'],
                             overall_bit_rate=6980068, other_overall_bit_rate=['6 980 kb/s'], frame_rate='29.970', other_frame_rate=['29.970 FPS'],
                             frame_count='6624', file_last_modification_date='UTC 2023-07-13 18:13:39',
                             file_last_modification_date__local='2023-07-13 19:13:39', overallbitrate_precision_min='6980053',
                             overallbitrate_precision_max='6980084')
    mediainfo_video = dict(track_type='Video', count='378', count_of_stream_of_this_kind='1', kind_of_stream='Video', other_kind_of_stream=['Video'],
                           stream_identifier='0', streamorder='0-0', track_id=512, other_track_id=['512 (0x200)'], menu_id=1,
                           other_menu_id=['1 (0x1)'], format='MPEG Video', other_format=['MPEG Video'], commercial_name='MPEG-2 Video',
                           format_version='Version 2', format_profile='Main@High', format_settings='CustomMatrix / BVOP', format_settings__bvop='Yes',
                           other_format_settings__bvop=['Yes'], format_settings__matrix='Custom', other_format_settings__matrix=['Custom'],
                           format_settings_matrix_data='0810101310131616161616161A181A1B1B1B1A1A1A1A1B1B1B1D1D1D2222221D1D1D1B1B1D1D2020222225262523232223262628282830302E2E38383A454553 / 0A111112121213131313141414141415151515151516161616161616171717171717171718181819181818191A1A1A1A191B1B1B1B1B1C1C1C1C1E1E1E1F1F21',
                           format_settings__gop='Variable', internet_media_type='video/MPV', codec_id='2', duration=221021,
                           other_duration=['3 min 41 s', '3 min 41 s 21 ms', '3 min 41 s', '00:03:41.021', '00:03:40:24',
                                           '00:03:41.021 (00:03:40:24)'], bit_rate_mode='VBR', other_bit_rate_mode=['Variable'],
                           maximum_bit_rate=20000000, other_maximum_bit_rate=['20.0 Mb/s'], width=1440, other_width=['1 440 pixels'], height=1080,
                           other_height=['1 080 pixels'], sampled_width='1440', sampled_height='1080', pixel_aspect_ratio='1.333',
                           display_aspect_ratio='1.778', other_display_aspect_ratio=['16:9'], frame_rate='29.970',
                           other_frame_rate=['29.970 (30000/1001) FPS'], framerate_num='30000', framerate_den='1001', frame_count='6624',
                           standard='Component', color_space='YUV', chroma_subsampling='4:2:0', other_chroma_subsampling=['4:2:0'], bit_depth=8,
                           other_bit_depth=['8 bits'], compression_mode='Lossy', other_compression_mode=['Lossy'], delay='515.811111',
                           other_delay=['516 ms', '516 ms', '516 ms', '00:00:00.516'], delay_dropframe='No', delay__origin='Container',
                           other_delay__origin=['Container'], delay_original=0, other_delay_original=['00:00:00.000'],
                           delay_original_settings='drop_frame_flag=0 / closed_gop=1 / broken_link=0', delay_original_dropframe='No',
                           delay_original_source='Stream', time_code_of_first_frame='00:00:00:00', time_code_source='Group of pictures header',
                           buffer_size='1222656', colour_description_present='Yes', colour_description_present_source='Stream',
                           color_primaries='BT.709', colour_primaries_source='Stream', transfer_characteristics='BT.709',
                           transfer_characteristics_source='Stream', matrix_coefficients='BT.709', matrix_coefficients_source='Stream',
                           intra_dc_precision='8')
    mediainfo_audio = dict(track_type='Audio', count='280', count_of_stream_of_this_kind='1', kind_of_stream='Audio', other_kind_of_stream=['Audio'],
                           stream_identifier='0', streamorder='0-1', track_id=513, other_track_id=['513 (0x201)'], menu_id=1,
                           other_menu_id=['1 (0x1)'], format='AAC', other_format=['AAC LC'], format_info='Advanced Audio Codec Low Complexity',
                           commercial_name='AAC', format_version='Version 2', format_additionalfeatures='LC', muxing_mode='ADTS', codec_id='15-2',
                           duration=221013, other_duration=['3 min 41 s', '3 min 41 s 13 ms', '3 min 41 s', '00:03:41.013', '00:03:41.013'],
                           bit_rate_mode='VBR', other_bit_rate_mode=['Variable'], channel_s=2, other_channel_s=['2 channels'],
                           channel_positions='Front: L R', other_channel_positions=['2/0/0'], channel_layout='L R', samples_per_frame='1024',
                           sampling_rate=48000, other_sampling_rate=['48.0 kHz'], samples_count='10608624', frame_rate='46.875',
                           other_frame_rate=['46.875 FPS (1024 SPF)'], compression_mode='Lossy', other_compression_mode=['Lossy'], delay='515.811111',
                           other_delay=['516 ms', '516 ms', '516 ms', '00:00:00.516'], delay__origin='Container', other_delay__origin=['Container'],
                           delay_relative_to_video=0, other_delay_relative_to_video=['00:00:00.000'])

    assert get_video_fields_from_mediainfo(general=mediainfo_general, video=mediainfo_video, audio=mediainfo_audio)\
           == {'container': 'TS', 'codec': 'MPEG-2', 'ressel': 'Other', 'resolution': '1440x1080', 'audioformat': 'AAC'}
