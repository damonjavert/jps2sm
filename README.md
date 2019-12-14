# jps2sm

### A project to migrate torrents from JPopSuki to SugoiMusic

jps2sm.py is a python3 script that will automatically gather data from JPS from a given group url, release url(s) or userid's uploads/seeding torrents and iterate through all the data in and upload them to SM.

## Features
* Create upload to SM by automatically retrieving all data on JPS, including english and original titles, group description, release information (format / meida / bitrate etc.), group images, contributing artists, original titles, mediainfo data and remaster information if applicable.
* Upload all torrents in a torrent group or specify 1 or more release urls.
* Upload all your personally uploaded or currently seeding torrents at JPS with `--batchuser` mode
* Run [Mediainfo](https://mediaarea.net/en/MediaInfo) against your media files and save the output to the 'mediainfo' field and parse the data to populate the codec, container, audioformat and resolution fields. DVD/BR ISO images are not currently supported.
* Exclude certain audioformats or medias with `--excfilteraudioformat` and `--excfiltermedia`
* Test your uploads with `--dryrun` mode.

## How to use
### Quickstart - for those familiar with python

Add your JPS and SM login credentials to **jps2sm.cfg**, using **jps2sm.cfg.example** as a template.

Install modules and run the script:

    pip3 install -r requirements.txt
    python3 jps2sm.py --urls <group-url or release-url(s)>

A **group-url** looks like https://jpopsuki.eu/torrents.php?id=111284
A **release-url** looks like https://jpopsuki.eu/torrents.php?id=111284&torrentid=148289

Go to SM and download your torrent files and add them to your torrent client. Enjoy!
#### Examples
To upload every release of AKB48 - 1830m:

    python3 jps2sm.py --urls "https://jpopsuki.eu/torrents.php?id=111284"

To upload only the FLAC and MP3 320:

    python3 jps2sm.py --urls "https://jpopsuki.eu/torrents.php?id=111284&torrentid=148289 https://jpopsuki.eu/torrents.php?id=111284&torrentid=147830"

To upload every release of AKB48 - 1830m, excluding the ISOs *(in JPS ISO is considered an audio format)*:

    python3 jps2sm.py --urls "https://jpopsuki.eu/torrents.php?id=111284" --excfilteraudioformat ISO

To *test* upload all your personal uploads, `<userid>` is your JPS userid:

    python3 jps2sm.py --batchuser <userid> --batchuploaded --dryrun

Once everything looks ok, to upload all your personal uploads, `<userid>` is your JPS userid:

    python3 jps2sm.py --batchuser <userid> --batchuploaded


**Please only upload torrents you intend to SEED.**
## Usage

    usage: jps2sm.py [-h] [-v] [-d] [-u URLS] [-n] [-b BATCHUSER] [-U] [-S]
                 [-s BATCHSTART] [-e BATCHEND] [-f EXCFILTERAUDIOFORMAT]
                 [-F EXCFILTERMEDIA]

arguments:

    -h, --help            show this help message and exit
    -v, --version         show program's version number and exit
    -d, --debug           Enable debug mode
    -u URLS, --urls URLS  JPS URL for a group, or multiple individual releases
                          URLs to be added to the same group
    -n, --dryrun          Just parse url and show the output, do not add the
                          torrent to SM
    -b BATCHUSER, --batchuser BATCHUSER
                          User id for batch user operations
    -U, --batchuploaded   Upload all releases uploaded by user id specified by
                          --batchuser
    -S, --batchseeding    Upload all releases currently seeding by user id
                          specified by --batchuser
    -s BATCHSTART, --batchstart BATCHSTART
                          (Batch mode only) Start at this page
    -e BATCHEND, --batchend BATCHEND
                          (Batch mode only) End at this page
    -f EXCFILTERAUDIOFORMAT, --excfilteraudioformat EXCFILTERAUDIOFORMAT
                          Exclude an audioformat from upload
    -F EXCFILTERMEDIA, --excfiltermedia EXCFILTERMEDIA
                          Exclude a media from upload
    -m, --mediainfo       Get mediainfo data and extract data to set codec,
                          resolution, audio format and container fields

## Help! I dont know all this python stuff
* Mac Users: The best method is to install [Homebrew](https://brew.sh) and then `brew install python3`. See this guide: https://wsvincent.com/install-python3-mac/
* Windows Users: If you are familiar using the shell, consider installing [cygwin](https://cygwin.com/install.html) and then select the python 3.6 packages. Or a python3 MSI installer can be found on the [offical python 3 downloads](https://www.python.org/downloads/windows/) page.

## Roadmap

See: https://git.sugoimusic.me/Sugoimusic/jps2sm/issues

## Contributing
* Contributors are welcomed! Please see the roadmap for issues link for ideas on how to contribute!
