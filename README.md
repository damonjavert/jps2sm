# jps2sm

### A project to migrate torrents from JPopSuki to SugoiMusic

jps2sm will automatically gather data from JPS from a given group url, release url(s) or userid's uploaded/seeding torrents and iterate through all the data in and upload them to SM.

## Features
* Create upload to SM by automatically retrieving all data on JPS, including english and original titles, group description, release information (format / media / bitrate etc.), group images, contributing artists, original titles, mediainfo data and remaster information if applicable.
* Upload by specifiyng a JPS group or release `--url`
* Upload all your (or someone elses) personally uploaded / seeding / snatched torrents with `--batchupload` / `--batchseeding` / `--batchsnatched`
* Contribute to SM  by uploading ALL non-large recent torrents to SM with `--batchrecent` mode. Note: This mode will prompt you to continue once the JPS data has been downloaded. Torrents over 1Gb are skipped.
* Search for your media files specified in `MediaDirectories` and run [Mediainfo](https://mediaarea.net/en/MediaInfo) against them and save the output to the 'mediainfo' field and parse the data to populate the codec, container, audioformat and resolution fields. DVD ISOs are automatically extracted and Mediainfo is run against the VOB files, BR ISO images are not currently supported in the pyunpack module.
* Exclude certain audioformats, medias or categories with `--excaudioformat` , `--excmedia` and `--exccategory`
* Test your uploads with `--dryrun` mode.

## How to use
Windows, Mac and Linux users can use the latest compiled binary on the releases page: https://git.sugoimusic.me/Sugoimusic/jps2sm/releases
The current compile binaries are out of date, with some features missing, if you can for now, use the python code.

### Quickstart
Download the binary release for your platform: https://git.sugoimusic.me/Sugoimusic/jps2sm/releases

Extract the contents of the zip, add your JPS & SM login credentials and the directories where your media is stored to **jps2sm.cfg**

    jps2sm --help

See Command line usage below

The SM torrents are automatically downloaded to the $HOME/SMTorrents, or My Documents\SMTorrents if on Windows by default. All video torrents MUST have mediainfo extracted to be uploaded - you must setup `MediaDirectories` as below in order for jps2sm to find your media files:

```text
    [Media]
    MediaDirectories: d:\Music, e:\BR-Rips, .....
```

or use Linux/Mac OSX ecquivalent paths. The MediaInfo library is bundled with the Windows and Mac OSX releases, if using the Linux release you will need to install MediaInfo, jps2sm/pymediainfo will locate the library. Enjoy!

### Quickstart - for those familiar with python
**jps2sm** requires python 3.8

The latest Dev release can be used instead by cloning the repo:

    git clone https://git.sugoimusic.me/Sugoimusic/jps2sm

Add your JPS & SM login credentials and the directories where your media is stored to **jps2sm.cfg**, using **jps2sm.cfg.example** as a template.

Install modules and run the script, adjusting the exact commands if required by your environment:

    pip3 install -r requirements.txt
    python3 jps2sm.py --urls <group-url or release-url(s)>

* A **group-url** looks like https://jpopsuki.eu/torrents.php?id=111284
* A **release-url** looks like https://jpopsuki.eu/torrents.php?id=111284&torrentid=148289
* See Command line usage for batch processing options.

### Command line usage Examples
To upload all your current seeding torrents, whilst automatically retrieving mediainfo data:

    python3 jps2sm.py --batchseeding --mediainfo

To upload the latest 50 torrents uploaded to JPS, prompting the user to continue once JPS data has been downloaded:

    python3 jps2sm.py --batchrecent --mediainfo

To upload the most recent 50 torrents you uploaded:

    python3 jps2sm.py --batchuploaded

To upload your 100 most popular uploads, based on snatches:

    python3 jps2sm.py --batchuploaded --batchsort snatches --batchsortorder desc --batchstart 1 --batchend 2

To upload every release of AKB48 - 1830m:

    python3 jps2sm.py --urls "https://jpopsuki.eu/torrents.php?id=111284"

To upload only the FLAC and MP3 320:

    python3 jps2sm.py --urls "https://jpopsuki.eu/torrents.php?id=111284&torrentid=148289 https://jpopsuki.eu/torrents.php?id=111284&torrentid=147830"

To upload every release of AKB48 - 1830m, excluding the ISOs *(in JPS ISO is considered an audio format)*:

    python3 jps2sm.py --urls "https://jpopsuki.eu/torrents.php?id=111284" --excaudioformat ISO

To *test* upload all your personal uploads:

    python3 jps2sm.py --batchuploaded --dryrun

Once everything looks ok, to upload all your personal uploads:

    python3 jps2sm.py --batchuploaded


**Please only upload torrents you intend to SEED.** Never-seeded torrents are deleted after 48 hours.
## Usage

```text
usage: jps2sm.py [--help] [--version] [--debug] [--dryrun] [--mediainfo] [--wait-for-jps-dl]

Single group / release mode arguments:

  --urls URLS

Single torrent id:

  --torrentid JPSTORRENTID

Batch processing mode arguments:

  --batchuser BATCHUSER (--batchuploaded | --batchseeding | --batchsnatched | --batchrecent) [-s BATCHSTART] [-e BATCHEND]
  [--exccategory EXCCATEGORY] [--excaudioformat EXCAUDIOFORMAT] [--excmedia EXCMEDIA]


Help for arguments for group/release uploads:

  -t JPSTORRENTID, --torrentid JPSTORRENTID
                        Specify a JPS torrent id to upload
  -u URLS, --urls URLS  JPS URL for a group, or multiple individual releases URLs from the same group, space delimited
                        in quotes


Help for arguments for batch processing:

  -b BATCHUSER, --batchuser BATCHUSER
                        User id for batch user operations, default is user id of SM Username specified in jps2sm.cfg
  -U, --batchuploaded   Upload all releases personally uploaded
        **or**
  -S, --batchseeding    Upload all releases currently seeding
        **or**
  -SN, --batchsnatched  Upload all releases that have been snatched
        **or**
  -R, --batchrecent     Upload ALL recent releases uploaded to JPS that are under 1Gb in size.
                        This mode will prompt you to continue once the JPS data has been downloaded, by default it parses
                        the first page at JPS - the last 50 torrents shown on the main page: https://jpopsuki.eu/torrents.php .
                        This mode is designed to contribute to SM even if you do not have much activity at JPS and/or ensure
                        that we have the very latest torrents!


Help for optional arguments for batch processing:

  -s BATCHSTART, --batchstart BATCHSTART
                    Start at this page
  -e BATCHEND, --batchend BATCHEND
                    End at this page
  -bs BATCHSORT, --batchsort BATCHSORT
                    Sort for batch upload, must be one of: name,year,time,size,snatches,seeders,leechers
  -bso BATCHSORTORDER, --batchsortorder BATCHSORTORDER
                    Sort order for batch upload, either ASC or DESC.
  -exc EXCCATEGORY, --exccategory EXCCATEGORY
                    Exclude a JPS category from upload
  -exf EXCAUDIOFORMAT, --excaudioformat EXCAUDIOFORMAT
                    Exclude an audioformat from upload
  -exm EXCMEDIA, --excmedia EXCMEDIA
                    Exclude a media from upload


Help for optional arguments:

  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -d, --debug           Enable debug mode. Run your command with this before submitting bugs.
  -n, --dryrun          Just parse data and show the output, do not add the torrent to SM
  -m, --mediainfo       Search and get mediainfo data from the source file(s) in the directories
                        specified by MediaDirectories. Extract data to set codec, resolution,
                        audio format and container fields as well as the mediainfo field itself.
  -w --wait-for-jps-dl  (Non-batch mode only) Show a prompt for the user to continue after scraping JPS torrent data and the
                        torrent, to allow for the file to be downloaded before adding it to SM
```

## Development
Pull requests are welcome!

It is strongly recommended to create a python virtual environment for your development.

See https://git.sugoimusic.me/Sugoimusic/jps2sm/issues for areas that you can contribute to.

### Windows
Windows 10 users can setup a Dev environment using [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10). Windows 7 users can install [cygwin](https://cygwin.com/install.html) and then select the python 3.8 packages. Or a python3 MSI installer can be found on the [offical python 3 downloads](https://www.python.org/downloads/windows/) page.

### Mac OSX
Install [Homebrew](https://brew.sh) if you do not have it already and then `brew install python3`. See this guide: https://wsvincent.com/install-python3-mac/

### Linux
Your distro's primary repos may not include packages for python3.8. Using `apt-get install python3` for example may only install python3.6 (or even earlier) and due to the use of the walrus operator jps2sm requires python 3.8. Debian and Fedora based distros can follow this guide: https://docs.python-guide.org/starting/install3/linux/ .
