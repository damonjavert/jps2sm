# jps2sm

### A project to migrate torrents from JPopSuki to SugoiMusic

jps2sm.py is a python ~~2.7~~ 3.6 script that will automatically gather data from JPS from a given group url, iterate through all the torrents in and upload them to SM.

## How to use
### Quickstart - for those familiar with python
`pip3 install -r requirements.txt`
`python3 jps2sm.py --urls group-url or release-urls`

A **group-url** looks like `https://jpopsuki.eu/torrents.php?id=111284`
A **release-url** looks like `https://jpopsuki.eu/torrents.php?id=111284&torrentid=148289`

Add your JPS and SM login credentials to **jps2sm.cfg**, using **jps2sm.cfg.example** as a template.
Go to SM and download your torrent files and add them to your torrent client. Enjoy!
#### Examples
To upload every release of AKB48 - 1830m:
`python jps2sm.py --urls https://jpopsuki.eu/torrents.php?id=111284`
To upload only the FLAC and MP3 320:
`python jps2sm.py --urls https://jpopsuki.eu/torrents.php?id=111284&torrentid=148289 https://jpopsuki.eu/torrents.php?id=111284&torrentid=147830`
### Help! I dont know all this python stuff

* Mac Users: The best method is to install [Homebrew](https://brew.sh) and then `brew install python3`. See this guide: https://wsvincent.com/install-python3-mac/
* Windows Users: If you are familiar using the shell, consider installing [cygwin](https://cygwin.com/install.html) and then select the python 3.6 packages. Or a python3 MSI installer can be found on the [offical python 3 downloads](https://www.python.org/downloads/windows/) page.

## Known limitations
* ~~Bluray torrents are not auto-detected, and these are uploaded as DVD.~~ Fixed
* The script does not automatically download your SM torrents - you need to navigate to SM and download them manually. *Perhaps this is a good idea as it forces the user to inspect the output*
* For video torrents some data is guessed as the data is not available with certainty from JPS. ~~Some extra work with pattern matching may be able work-around this.~~ *All possible logic to gather data from JPS now done*

## Known bugs
* ~~TV-Music does not currently work. *JPS uses `()` instead of `[]` to show dates.*~~
* Pictures do not work as JPS does not have a release-date for them.
* Fansubs are currently not support as these will probably be added to the group page either by adding a release type or integrating it into the group page ala BTN.

## Roadmap
* ~~Support individual torrent links~~ DONE
* ~~Support TV-Music~~ DONE
* ~~Support auto-merging / auto add to last group.~~ DONE
* ~~Migrate to using python3~~ DONE
* Use pythonic `if __name__ == "__main__":`, defs for everything and general cleanup of the code *Started, ongoing*
* ~~Support remastered - this is a depenancy of allowing full-use of --batchuser~~
* Allow some Cats to have < 3 tags, this could either be handled in gazelle or here - this is a depenancy of allowing full-use of --batchuser

See also: https://git.sugoimusic.me/Sugoimusic/jps2sm/issues

## Contributing
* Contributors are welcomed! Please see the roadmap for issues link for ideas on how to contribute!
