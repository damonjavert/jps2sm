# jps2sm

### A project to migrate torrents from JPopSuki to SugoiMusic

jps2sm.py is a python 2.7 script that will automatically gather data from JPS from a given group url, iterate through all the torrents in and upload them to SM.

## How to use
### Quickstart - for those familiar with python
`pip install -r requirements.txt`
`python jps2sm.py jps-group-url`
Add your JPS and SM login credentials to **jps2sm.cfg**, using **jps2sm.cfg.example** as a template.
Go to SM and download your torrent files and add them to your torrent client. Enjoy!
### Help! I dont know all this python stuff
* Mac Users: python 2.7 is pre-installed and if you are not going to be doing any actual development of the code it should work for you just fine. Alternatively you can follow [this guide](https://docs.python-guide.org/starting/install/osx/)
* Windows Users: If you are familiar using the shell, consider installing [cygwin](https://cygwin.com/install.html) and then select the python 2.7 packages. Or a python2.7 MSI installer can be found on the [offical python 2.7 downloads](https://www.python.org/download/releases/2.7/) page.

## Known limitations
* Bluray torrents are not auto-detected, and these are uploaded as DVD.
* Torrents are not uploaded to the same group, requiring the torrents to be merged by a Staff member. *Send a Staff PM and we will do this for you*
* Only torrent group urls are supported. This is great if there is just 1 or 2 torrents in the group and you wish to upload all of them but not so good when there are 10 and you need to manually delete what you do not need afterwards.
* The script does not automatically download your SM torrrents - you need to navigate to SM and download them manually. *Perhaps this is a good idea as it forces the user to inspect the output*
* For video torrents some data is guessed as the data is not available with certainty from JPS. Some extra work with pattern matching may be able work-around this.

## Known bugs
* TV-Music does not currently work. *JPS uses `()` instead of `[]` to show dates.*

## Roadmap
* Support individual torrent links
* Support TV-Music
* Support auto-merging / auto add to last group.
* Migrate to using python3
* Use pythonic `if __name__ == "__main__":`, defs for everything and general cleanup of the code

## Contributing
* Contributors are welcomed! Please see the roadmap for ideas on how to contribute!
