# jps2sm

![PyPI](https://img.shields.io/pypi/v/jps2sm) ![PyPI - Status](https://img.shields.io/pypi/status/jps2sm) ![PyPI - Downloads](https://img.shields.io/pypi/dw/jps2sm) ![Code Climate maintainability](https://img.shields.io/codeclimate/maintainability/damonjavert/jps2sm) ![Code Climate technical debt](https://img.shields.io/codeclimate/tech-debt/damonjavert/jps2sm) ![Pylint score](https://img.shields.io/badge/pylint-9.53-green) ![Code Climate coverage](https://img.shields.io/codeclimate/coverage/damonjavert/jps2sm)
 ![Tests status](https://github.com/damonjavert/jps2sm/actions/workflows/tests.yml/badge.svg) ![GitHub last commit](https://img.shields.io/github/last-commit/damonjavert/jps2sm) ![License](https://img.shields.io/github/license/damonjavert/jps2sm) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

### A project to migrate torrents from JPopSuki to SugoiMusic

jps2sm will automatically gather and validate data from JPS and transfer it to SM. jps2sm does not download any data using torrents themselves and is not a torrent client.

## Features
* Create upload on SM by automatically retrieving all data on JPS, including english and original titles, group description, release information (format / media / bitrate etc.), group images, contributing artists, original titles, mediainfo data and remaster information if applicable.
* Upload by specifiyng a JPS group or release `--url` or a `--torrentid`
* Upload all your (or someone elses) personally uploaded / seeding / snatched torrents with `--batch upload` / `--batch seeding` / `--batch snatched`
* Contribute to SM  by uploading ALL recent torrents to JPS with `--batch recent` mode. A maximum size can be configured with `MaxSizeRecentMode`, a minimum number of seeders with `MinSeeders` and an amount of time to wait for JPS files to be downloaded with `WaitTimeRecentModeMins` in jps2sm.cfg
* Search for your media files specified in `MediaDirectories` and run [Mediainfo](https://mediaarea.net/en/MediaInfo) against them and save the output to the 'mediainfo' field and parse the data to populate the codec, container, audioformat and resolution fields. DVD ISOs are automatically extracted and Mediainfo is run against the VOB files, BR ISO images are not currently supported in the pyunpack module.
* Exclude certain audioformats, medias or categories with `--excaudioformat` , `--excmedia` and `--exccategory`
* Test your uploads with `--dryrun` mode.

## Install
From PyPi:
```
pip install jps2sm
```
Or use the latest commit:
```
git clone https://github.com/damonjavert/jps2sm.git
cd jps2sm
python setup.py install
```

**jps2sm** requires python >=3.10

## Quickstart
* Install the latest release of python: https://www.python.org/downloads/
* Launch your favourite terminal emulator, if you are not familiar with command-line usage or tools, on Windows: Type Win+R and run 'cmd'. On Mac: Go > Utilities > Terminal.
* Install the package as above `pip install jps2sm` and add your JPS & SM login credentials and the directories where your media is stored to **jps2sm.cfg**, using **jps2sm.cfg.example** as a template.

The SM torrents are automatically downloaded to the $HOME/SMTorrents, or My Documents\SMTorrents if on Windows by default. All video torrents MUST have mediainfo extracted to be uploaded - you must setup `MediaDirectories` as below in order for jps2sm to find your media files:

```text
[Media]
MediaDirectories: d:\Music, e:\BR-Rips, .....
```
MediaInfo will also need to be installed.

To upload an single release or a whole group:
```
jps2sm --urls <group-url or release-url(s)>
```

* A **group-url** looks like https://jpopsuki.eu/torrents.php?id=111284
* A **release-url** looks like https://jpopsuki.eu/torrents.php?id=111284&torrentid=148289
* See Command line usage for batch processing options.

## Command line usage Examples
To upload all your current seeding torrents, whilst automatically retrieving mediainfo data:

    jps2sm --batch seeding --mediainfo

To upload the latest 50 torrents uploaded to JPS, prompting the user to continue once JPS data has been downloaded:

    jps2sm --batch recent --mediainfo

To *test* upload all your JPS uploads:

    jps2sm --batch uploaded --dryrun

To upload all your JPS uploads:

    jps2sm --batch uploaded

To upload the most recent 50 torrents you uploaded at JPS:

    jps2sm --batch uploaded --batchsort time --batchsortorder desc --batchstart 1 --batchend 1

To upload your 100 most popular uploads, based on snatches:

    jps2sm --batch uploaded --batchsort snatches --batchsortorder desc --batchstart 1 --batchend 2

To upload every release of AKB48 - 1830m:

    jps2sm --urls "https://jpopsuki.eu/torrents.php?id=111284"

To upload only the FLAC and MP3 320:

    jps2sm --urls "https://jpopsuki.eu/torrents.php?id=111284&torrentid=148289 https://jpopsuki.eu/torrents.php?id=111284&torrentid=147830"

To upload every release of AKB48 - 1830m, excluding the ISOs *(in JPS ISO is considered an audio format)*:

    jps2sm --urls "https://jpopsuki.eu/torrents.php?id=111284" --excaudioformat ISO


**Please only upload torrents you intend to SEED.** Never-seeded torrents are deleted after 48 hours.
## Usage

```text
usage: jps2sm (--urls URLS | --torrentid TORRENTID | --batch {uploaded,seeding,snatched,recent} | -U | -S | -SN | -R)
[--batchuser BATCHUSER] [--batchsort {name,year,time,size,snatches,seeders,leechers}]
[--batchsortorder {asc,desc}] [--batchstart PAGESTART] [--batchend PAGEEND]
[--exccategory {Album,Single,PV,DVD,TV-Music,TV-Variety,TV-Drama,Fansubs,Pictures,Misc}]
[-excaudoiformat EXCAUDIOFORMAT] [--excmedia EXCMEDIA]
[--help] [--version] [--debug] [--dryrun] [--mediainfo] [--wait-for-jps-dl]


jps2sm actions:
  Choose ONE action for jps2sm to migrate data from

  -u URLS, --urls URLS  JPS URL for a group, or multiple individual releases URLs from the same group
  -t TORRENTID, --torrentid TORRENTID
                        JPS torrent id
  -bm {uploaded,seeding,snatched,recent}, --batch {uploaded,seeding,snatched,recent}
                        Batch mode: Upload all releases either uploaded, seeding, snatched by you or, if provided, user id specified by --batchuser. OR all
                        recent uploads to JPS.
  -U, --batchuploaded   alias to --batch upload
  -S, --batchseeding    alias to --batch seeding
  -SN, --batchsnatched  alias to --batch snatched
  -R, --batchrecent     alias to --batch recent


Batch mode (--batch MODE) optional arguments:
  -b BATCHUSER, --batchuser BATCHUSER
                        User id for batch user operations, default is user id of SM Username specified in jps2sm.cfg
  -bs {name,year,time,size,snatches,seeders,leechers}, --batchsort {name,year,time,size,snatches,seeders,leechers}
                        Sort for batch upload, must be one of: name,year,time,size,snatches,seeders,leechers
  -bso {asc,desc}, --batchsortorder {asc,desc}
                        Sort order for batch upload, either ASC or DESC.
  -s BATCHSTART, --batchstart BATCHSTART
                        Start at this page
  -e BATCHEND, --batchend BATCHEND
                        End at this page
  -exc {Album,Single,PV,DVD,TV-Music,TV-Variety,TV-Drama,Fansubs,Pictures,Misc}, --exccategory {Album,Single,PV,DVD,TV-Music,TV-Variety,TV-Drama,Fansubs,Pictures,Misc}
                        Exclude a JPS category from upload
  -exf EXCAUDIOFORMAT, --excaudioformat EXCAUDIOFORMAT
                        Exclude an audioformat from upload
  -exm EXCMEDIA, --excmedia EXCMEDIA
                        Exclude a media from upload


optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -d, --debug           Enable debug mode
  -n, --dryrun          Just parse JPS data and show the output, do not upload the torrent(s) to SM
  -w, --wait-for-jps-dl
                        (Non-batch mode only) Show a prompt for the user to continue after scraping JPS torrent data and the
                        torrent, to allow for the file to be downloaded before adding it to SM
  -m, --mediainfo       Search and get mediainfo data from the source file(s) in the directories specified by MediaDirectories. Extract data to set codec,
                        resolution, audio format and container fields as well as the mediainfo field itself.
```

## Development
Pull requests are welcome!
See https://github.com/damonjavert/jps2sm/issues for areas that you can contribute to.

To setup your Dev environment for Mac/Linux:
```shell
git clone https://github.com/damonjavert/jps2sm.git
cd jps2sm
python3 -m venv .venv  # or whatever
. .venv/bin/activate
pip install -r requirements_dev.txt
```
This will install the runtime and dev dependancies and jps2sm itself in editable mode.

To run tests:
```shell
# Run from the repo root, else the required files will not be found
pytest
```
### Windows
Windows 10 users can setup a Dev environment using [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10). Windows 7 users can install [cygwin](https://cygwin.com/install.html) and then select the python 3.8 packages. Or a python3 MSI installer can be found on the [offical python 3 downloads](https://www.python.org/downloads/windows/) page.

### Mac OSX
Install [Homebrew](https://brew.sh) if you do not have it already and then `brew install python3`. See this guide: https://wsvincent.com/install-python3-mac/

### Linux
Your distro's primary repos may not include packages for python3.8. Using `apt-get install python3` for example may only install python3.6 (or even earlier) and due to the use of the walrus operator jps2sm requires python 3.8. The recommended approach to workaround this is to install [LinuxBrew](https://docs.brew.sh/Homebrew-on-Linux) and then `brew install python3` as also shown above. Otherwise Debian and Fedora based distros can follow this guide: https://docs.python-guide.org/starting/install3/linux/ .

## Legal Disclaimer
Use of jps2sm is not illegal but piracy probably is in your country. Data transferred using jps2sm should be used to maintain backup copies on JPopSuki and SugoiMusic.

The developers of jps2sm are assuming that you own the original file and hold NO RESPONSIBILITY if further to the use of this software the files are misused in any way and cannot be held responsible for what uploads are created on SugoiMusic as a result.

jps2sm is not a torrent client and only migrates and validates metadata and not the actual data/files themselves.
