class VideoOptions:
    """
    Store Video option constants
    """

    VideoMedias = ('DVD', 'Blu-Ray', 'VHS', 'VCD', 'TV', 'HDTV', 'WEB')
    badcontainers = ('ISO', 'VOB', 'MPEG', 'AVI', 'MKV', 'WMV', 'MP4')
    badcodecs = ('MPEG2', 'h264')
    badformats = badcontainers + badcodecs
    resolutions = ('720p', '1080i', '1080p')


class Categories:
    """
    Store category constants
    """

    # Store JPS to SM Category translation, defines which JPS Cat gets uploaded to which SM Cat
    # key: JPS category name
    # value: SM category ID
    JPStoSM = {
        'Album': 0,
        'EP': 1,  # Does not exist on JPS
        'Single': 2,
        'Bluray': 3,  # Does not exist on JPS
        'DVD': 4,
        'PV': 5,
        'Music Performance': 6,  # Does not exist on JPS
        'TV-Music': 7,  # Music Show
        'TV-Variety': 8,  # Talk Show
        'TV-Drama': 9,  # TV Drama
        'Pictures': 10,
        'Misc': 11,
    }

    SM = {
        'Album': 0,
        'EP': 1,  # Does not exist on JPS
        'Single': 2,
        'Bluray': 3,  # Does not exist on JPS
        'DVD': 4,
        'PV': 5,
        'Music Performance': 6,  # Does not exist on JPS
        'TV Music': 7,  # TV-Music
        'TV Variety': 8,  # TV-Variety
        'TV Drama': 9,  # TV-Drama
        'Pictures': 10,
        'Misc': 11,
    }

    Video = ('Bluray', 'DVD', 'PV', 'TV-Music', 'TV-Variety', 'TV-Drama', 'Music Performance')

    # JPS Categories where release date cannot be entered and therefore need to be processed differently
    NonDate = ('TV-Music', 'TV-Variety', 'TV-Drama', 'Fansubs', 'Pictures', 'Misc')
    # JPS Categories where no release data is present and therefore need to be processed differently
    NonReleaseData = ('Pictures', 'Misc')
    # Music and Music Video Torrents, for category validation. This must match the cateogry headers in JPS for an artist, hence they are in plural
    NonTVCategories = ('Albums', 'Singles', 'DVDs', 'PVs')
    # Categories that should have some of their mediainfo stripped if present, must match indices in Categories.SM
    SM_StripAllMediainfo = (0, 1, 2, 11)  # Album, EP, Single, Misc - useful to have duration if we have it added to the description
    SM_StripAllMediainfoExcResolution = 10  # Pictures - useful to have resolution if we have it
