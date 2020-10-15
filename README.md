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

Windows users can use the latest compiled binary (exe file) on the releases page: https://git.sugoimusic.me/Sugoimusic/jps2sm/releases

### Quickstart - for those familiar with python

**jps2sm** requires python 3.4, although recent Dev and testing has been done using python 3.8, so it is storngly recommended that you use python 3.8.

Add your JPS and SM login credentials to **jps2sm.cfg**, using **jps2sm.cfg.example** as a template.

Install modules and run the script:

    pip3 install -r requirements.txt
    python3 jps2sm.py --urls <group-url or release-url(s)>

A **group-url** looks like https://jpopsuki.eu/torrents.php?id=111284
A **release-url** looks like https://jpopsuki.eu/torrents.php?id=111284&torrentid=148289

Go to SM and download your torrent files and add them to your torrent client. Enjoy!
### Command line usage Examples
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
                 [-s BATCHSTART] [-e BATCHEND] [-exc EXCCATEGORY]
                 [-exf EXCAUDIOFORMAT] [-exm EXCMEDIA] [-m]

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
    -U, --batchuploaded   (Batch mode only) Upload all releases uploaded by user
                          id specified by --batchuser
    -S, --batchseeding    (Batch mode only) Upload all releases currently
                          seeding by user id specified by --batchuser
    -s BATCHSTART, --batchstart BATCHSTART
                          (Batch mode only) Start at this page
    -e BATCHEND, --batchend BATCHEND
                          (Batch mode only) End at this page
    -exc EXCCATEGORY, --exccategory EXCCATEGORY
                          (Batch mode only) Exclude a JPS category from upload
    -exf EXCAUDIOFORMAT, --excaudioformat EXCAUDIOFORMAT
                          (Batch mode only) Exclude an audioformat from upload
    -exm EXCMEDIA, --excmedia EXCMEDIA
                          (Batch mode only) Exclude a media from upload
    -m, --mediainfo       Get mediainfo data and extract data to set codec,
                          resolution, audio format and container fields

    usage: jps2sm.py [-h] [-v] [-d] [-u URLS] [-n] [-b BATCHUSER] [-U] [-S]
                 [-s BATCHSTART] [-e BATCHEND] [-f EXCFILTERAUDIOFORMAT]
                 [-F EXCFILTERMEDIA]

## Help! I dont know all this python stuff
* Mac Users: The best method is to install [Homebrew](https://brew.sh) and then `brew install python3`. See this guide: https://wsvincent.com/install-python3-mac/
* Windows Users: Use the compiled (exe) release: https://git.sugoimusic.me/Sugoimusic/jps2sm/releases

## Development

Pull requests are welcome!

### Windows
Windows 10 users can setup a Dev environment using [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10), for Windows 7 users the best option is to install [cygwin](https://cygwin.com/install.html) and then select the python 3.8 packages. Or a python3 MSI installer can be found on the [offical python 3 downloads](https://www.python.org/downloads/windows/) page.

### Mac OSX
Install [Homebrew](https://brew.sh) if you do not have it already and then `brew install python3`. See this guide: https://wsvincent.com/install-python3-mac/ 

## Roadmap

See: https://git.sugoimusic.me/Sugoimusic/jps2sm/issues

## Contributing
* Contributors are welcomed! Please see the roadmap for issues link for ideas on how to contribute!
