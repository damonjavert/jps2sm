# jps2sm

### A project to migrate torrents from JPopSuki to SugoiMusic

jps2sm will automatically gather data from JPS from a given group url, release url(s) or userid's uploads/seeding torrents and iterate through all the data in and upload them to SM.

## Features
* Create upload to SM by automatically retrieving all data on JPS, including english and original titles, group description, release information (format / meida / bitrate etc.), group images, contributing artists, original titles, mediainfo data and remaster information if applicable.
* Upload all torrents in a torrent group or specify 1 or more release urls.
* Upload all your personally uploaded or currently seeding torrents at JPS with `--batchuser` mode
* Run [Mediainfo](https://mediaarea.net/en/MediaInfo) against your media files and save the output to the 'mediainfo' field and parse the data to populate the codec, container, audioformat and resolution fields. DVD ISOs are automatically extracted and Mediainfo is run againdst the VOB files, BR ISO images are not currently supported.
* Exclude certain audioformats or medias with `--excfilteraudioformat` and `--excfiltermedia`
* Test your uploads with `--dryrun` mode.

## How to use
Windows and Mac users can use the latest compiled binary on the releases page: https://git.sugoimusic.me/Sugoimusic/jps2sm/releases

### Quickstart
Download the binary release for your platform: https://git.sugoimusic.me/Sugoimusic/jps2sm/releases

Extract the contents of the zip, add your JPS and SM login credentials to **jps2sm.cfg**

    jps2sm --help

See Command line usge below

The SM torrents are automatically downloaded to the $HOME/SMTorrents, or My Documents\SMTorrents if on Windows by default. Enjoy!

### Quickstart - for those familiar with python
**jps2sm** requires python 3.8

The latest Dev release can be used instead by cloning the repo:

    git clone https://git.sugoimusic.me/Sugoimusic/jps2sm

Add your JPS and SM login credentials to **jps2sm.cfg**, using **jps2sm.cfg.example** as a template.

Install modules and run the script:

    pip3 install -r requirements.txt
    python3 jps2sm.py --urls <group-url or release-url(s)>

* A **group-url** looks like https://jpopsuki.eu/torrents.php?id=111284
* A **release-url** looks like https://jpopsuki.eu/torrents.php?id=111284&torrentid=148289
* See Command line usage for batch processing options.

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
    -m, --mediainfo       Get mediainfo data from the torrent download file(s) in
                          the current working dir and extract data to set codec,
                          resolution, audio format and container fields

    usage: jps2sm.py [-h] [-v] [-d] [-u URLS] [-n] [-b BATCHUSER] [-U] [-S]
                 [-s BATCHSTART] [-e BATCHEND] [-f EXCFILTERAUDIOFORMAT]
                 [-F EXCFILTERMEDIA]

## Development
Pull requests are welcome!

It is strongly recommended to create a python virtual environment for your development. 

See https://git.sugoimusic.me/Sugoimusic/jps2sm/issues for areas that you can contribute to.

### Windows
Windows 10 users can setup a Dev environment using [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10). Windows 7 users can install [cygwin](https://cygwin.com/install.html) and then select the python 3.8 packages. Or a python3 MSI installer can be found on the [offical python 3 downloads](https://www.python.org/downloads/windows/) page.

### Mac OSX
Install [Homebrew](https://brew.sh) if you do not have it already and then `brew install python3`. See this guide: https://wsvincent.com/install-python3-mac/

### Linux

Your distro's primary repos may not include packages for python3.8. Using apt-get indtall python3 for example may only install python3.6 and due to the use of the walrus operator jps2sm requires python 3.8. Debian  and Fedora based distros can follow this guide: https://docs.python-guide.org/starting/install3/linux/

