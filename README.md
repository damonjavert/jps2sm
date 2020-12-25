# jps2sm

### A project to migrate torrents from JPopSuki to SugoiMusic

jps2sm will automatically gather data from JPS from a given group url, release url(s) or userid's uploaded/seeding torrents and iterate through all the data in and upload them to SM.

## Features
* Create upload to SM by automatically retrieving all data on JPS, including english and original titles, group description, release information (format / meida / bitrate etc.), group images, contributing artists, original titles, mediainfo data and remaster information if applicable.
* Upload all torrents in a torrent group or specify 1 or more release urls in a gorup.
* Upload all your (or someone elses) personally uploaded or currently seeding torrents at JPS with `--batchuser` mode
* Run [Mediainfo](https://mediaarea.net/en/MediaInfo) against your media files and save the output to the 'mediainfo' field and parse the data to populate the codec, container, audioformat and resolution fields. DVD ISOs are automatically extracted and Mediainfo is run againdst the VOB files, BR ISO images are not currently supported in the pyunpack module.
* Exclude certain audioformats, medias or categories with `--excaudioformat` , `--excmedia` and `--exccategory`
* Test your uploads with `--dryrun` mode.

## How to use
Windows, Mac and Linux users can use the latest compiled binary on the releases page: https://git.sugoimusic.me/Sugoimusic/jps2sm/releases

### Quickstart
Download the binary release for your platform: https://git.sugoimusic.me/Sugoimusic/jps2sm/releases

Extract the contents of the zip, add your JPS and SM login credentials to **jps2sm.cfg**

    jps2sm --help

See Command line usge below

The SM torrents are automatically downloaded to the $HOME/SMTorrents, or My Documents\SMTorrents if on Windows by default. If uploading video torrents please consider using the **mediainfo** option `-m`; this will extract mediainfo from the source file(s) in the ***current directory***. Enjoy!

### Quickstart - for those familiar with python
**jps2sm** requires python 3.8

The latest Dev release can be used instead by cloning the repo:

    git clone https://git.sugoimusic.me/Sugoimusic/jps2sm

Add your JPS and SM login credentials to **jps2sm.cfg**, using **jps2sm.cfg.example** as a template.

Install modules and run the script, adjusting the exact commands if required by your environment:

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

    python3 jps2sm.py --urls "https://jpopsuki.eu/torrents.php?id=111284" --excaudioformat ISO

To *test* upload all your personal uploads, `<userid>` is your JPS userid:

    python3 jps2sm.py --batchuser <userid> --batchuploaded --dryrun

Once everything looks ok, to upload all your personal uploads, `<userid>` is your JPS userid:

    python3 jps2sm.py --batchuser <userid> --batchuploaded


**Please only upload torrents you intend to SEED.**
## Usage

```text
usage: jps2sm.py [--help] [--version] [--debug] [--dryrun] [--mediainfo]
                 
Single group / release mode arguments:

  --urls URLS

Batch processing mode arguments:

  --batchuser BATCHUSER (--batchuploaded | --batchseeding) [-s BATCHSTART] [-e BATCHEND]
  [--exccategory EXCCATEGORY] [--excaudioformat EXCAUDIOFORMAT] [--excmedia EXCMEDIA]


Help for arguments for group/release uploads:

  -u URLS, --urls URLS  JPS URL for a group, or multiple individual releases URLs, space delimited
                        in quotes to be added to the same group


Help for required arguments for batch processing:

  -b BATCHUSER, --batchuser BATCHUSER
                        User id for batch user operations
  -U, --batchuploaded   Upload all releases uploaded by user id specified by --batchuser
        **or**
  -S, --batchseeding    Upload all releases currently seeding by user id specified by --batchuser


Help for optional arguments for batch processing:

  -s BATCHSTART, --batchstart BATCHSTART
                    Start at this page
  -e BATCHEND, --batchend BATCHEND
                    End at this page
  -exc EXCCATEGORY, --exccategory EXCCATEGORY
                    Exclude a JPS category from upload
  -exf EXCAUDIOFORMAT, --excaudioformat EXCAUDIOFORMAT
                    Exclude an audioformat from upload
  -exm EXCMEDIA, --excmedia EXCMEDIA
                    Exclude a media from upload


Help for optional arguments:

  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -d, --debug           Enable debug mode
  -n, --dryrun          Just parse data and show the output, do not add the torrent to SM
  -m, --mediainfo       Get mediainfo data from the source file(s) in the current directory.
                        Extract data to set codec, resolution, audio format and container fields
                        as well as the mediainfo field itself.
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
Your distro's primary repos may not include packages for python3.8. Using `apt-get install python3` for example may only install python3.6 (or even earlier) and due to the use of the walrus operator jps2sm requires python 3.8. Debian and Fedora based distros can follow this guide: https://docs.python-guide.org/starting/install3/linux/ . Or you can complain and we might make jps2sm python3.6 compatible, we are actively considering this as linux non-Devs prefer to use the source and not anything compiled.

