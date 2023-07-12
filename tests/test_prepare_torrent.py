"""
Run tests for prepare_torrent()
"""

from jps2sm.prepare_data import prepare_torrent


class AttributeDict(dict):
    """
    Convert a dict into attributes so prepare_torrent() can access GetGroupData
    """
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value


def test_prepare_torrent():
    """
    Test for Run tests for prepare_torrent()

    """

    # jps_torrent_id = 95129  # 2011.05.25 - Everyday, Kachuusha  FLAC / Lossless / CD / Type-A - 2011

    release_data_collated = {'jpstorrentid': '95129',
                             'videotorrent': False,
                             'categorystatus': 'good',
                             'media': 'CD',
                             'audioformat': 'FLAC',
                             'bitrate': 'Lossless',
                             'remastertitle': 'Type-A',
                             'uploaddate': '20110526'}

    torrent_group_data_dict = {'groupid': '72951',
                               'category': 'Single',
                               'artist': ['AKB48'],
                               'date': '20110525',
                               'title': 'Everyday, Kachuusha',
                               'originalartist': 'AKB48',
                               'originaltitle': 'Everyday、カチューシャ',
                               'groupdescription': 'AKB48 21stシングル「Everyday、カチューシャ」\n2011.5.25（水）発売\n\n女の子たちが集まると、とっておきの夏が来る\n国民的アイドルとなったAKB48が今年も年に一度のお祭りを開催！\n「AKB48\u300022 ndシングル選抜総選挙」投票用シリアルナンバーカード封入！選抜メンバーは最多の26名！\nmusic clipはグアムで撮影！夏にぴったりのアイドルソング！\n今年もやります！選抜総選挙！！\n\n\n\n通常盤Type A\nCD\n1. Everyday、カチューシャ (Everyday, Kachuusha)\n2. これからWonderland (Kore kara Wonderland)\n3. ヤンキーソウル (Yankee Soul)\n4. Everyday、カチューシャ (off vocal ver.)\n5. これからWonderland (off vocal ver.)\n6. ヤンキーソウル (off vocal ver.)\nDVD\n1. Everyday、カチューシャ\u3000Music Clip\n2. これからWonderland\u3000Music Clip\n3. ヤンキーソウル\u3000Music Clip\n4. Everyday 、カチューシャ\u3000Music Clip＜Drama ver.＞\n5. 特典映像 Type-A\n\n\n通常盤Type B\nCD\n1. Everyday、カチューシャ\n2. これからWonderland\n3. 人の力 (Hito no chikara)\n4. Everyday、カチューシャ (off vocal ver.)\n5. これからWonderland (off vocal ver.)\n6．人の力 (off vocal ver.)\nDVD\n1. Everyday、カチューシャ\u3000Music Clip\n2. これからWonderland\u3000Music Clip\n3. 人の力\u3000Music Clip\n4. Everyday 、カチューシャ\u3000Music Clip＜Dance ver.＞\n5．特典映像 Type-B\n\n\n劇場盤 CD\n1. Everyday、カチューシャ\n2. これからWonderland\n3. アンチ (Anti)\n4. Everyday、カチューシャ (off vocal ver.)\n5. これからWonderland (off vocal ver.)\n6. アンチ (off vocal ver.)',
                               'imagelink': 'https://jpopsuki.eu/static/images/torrents/72951.jpg',
                               'tagsall': 'japanese,pop,female.vocalist,idol',
                               'contribartists': {}}

    torrent_group_data = AttributeDict(torrent_group_data_dict)
    jps_torrent_object = ""
    sugoimusic_upload_data = {'submit': 'true',
                              'title': 'Everyday, Kachuusha',
                              'tags': 'japanese,pop,female.vocalist,idol',
                              'album_desc': 'AKB48 21stシングル「Everyday、カチューシャ」\n2011.5.25（水）発売\n\n女の子たちが集まると、とっておきの夏が来る\n国民的アイドルとなったAKB48が今年も年に一度のお祭りを開催！\n「AKB48\u300022 ndシングル選抜総選挙」投票用シリアルナンバーカード封入！選抜メンバーは最多の26名！\nmusic clipはグアムで撮影！夏にぴったりのアイドルソング！\n今年もやります！選抜総選挙！！\n\n\n\n通常盤Type A\nCD\n1. Everyday、カチューシャ (Everyday, Kachuusha)\n2. これからWonderland (Kore kara Wonderland)\n3. ヤンキーソウル (Yankee Soul)\n4. Everyday、カチューシャ (off vocal ver.)\n5. これからWonderland (off vocal ver.)\n6. ヤンキーソウル (off vocal ver.)\nDVD\n1. Everyday、カチューシャ\u3000Music Clip\n2. これからWonderland\u3000Music Clip\n3. ヤンキーソウル\u3000Music Clip\n4. Everyday 、カチューシャ\u3000Music Clip＜Drama ver.＞\n5. 特典映像 Type-A\n\n\n通常盤Type B\nCD\n1. Everyday、カチューシャ\n2. これからWonderland\n3. 人の力 (Hito no chikara)\n4. Everyday、カチューシャ (off vocal ver.)\n5. これからWonderland (off vocal ver.)\n6．人の力 (off vocal ver.)\nDVD\n1. Everyday、カチューシャ\u3000Music Clip\n2. これからWonderland\u3000Music Clip\n3. 人の力\u3000Music Clip\n4. Everyday 、カチューシャ\u3000Music Clip＜Dance ver.＞\n5．特典映像 Type-B\n\n\n劇場盤 CD\n1. Everyday、カチューシャ\n2. これからWonderland\n3. アンチ (Anti)\n4. Everyday、カチューシャ (off vocal ver.)\n5. これからWonderland (off vocal ver.)\n6. アンチ (off vocal ver.)',
                              'year': '20110525',
                              'media': 'CD',
                              'audioformat': 'FLAC',
                              'image': 'https://jpopsuki.eu/static/images/torrents/72951.jpg',
                              'bitrate': 'Lossless',
                              'remaster': 'remaster',
                              'remastertitle': 'Type-A',
                              'type': 2,
                              'artist_jp': 'AKB48',
                              'title_jp': 'Everyday、カチューシャ',
                              'contrib_artists[]': [],
                              'idols[]': ['AKB48'],
                              'jps_torrent_id': '95129'}

    assert prepare_torrent(jps_torrent_object=jps_torrent_object,
                           torrent_group_data=torrent_group_data,
                           mediainfo=False,
                           release_data_collated=release_data_collated) == sugoimusic_upload_data
