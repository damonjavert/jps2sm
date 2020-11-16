Welcome to jps2sm

jps2sm allows easy migration of torrents from JPopSuki to SugoiMusic. Data is gathered from JPS and then uploads are created in SugoiMusic.

Created SugoiMusic uploads specified can either be:

* JPS Group URL - every release in the group is created
* JPS Release URL(s) - only the specified releases in the same group are created, useful if you ned to exclude some releases.
* All torrents uploaded by a given user
* All torrents seeding by a given user.

Quickstart - for those not familiar with the shell / cmd.exe etc.

1. Double-click jps2sm.cfg and add your JPS and SM login details where shown in the template.
2. Double-click jps2sm, this is a shortcut that sets up cmd.exe in the easiest to use setup and the help is shown


Command line usage Examples:

To upload every release of AKB48 - 1830m:
jps2sm.exe --urls "https://jpopsuki.eu/torrents.php?id=111284"

To upload only the FLAC and MP3 320:
jps2sm.exe --urls "https://jpopsuki.eu/torrents.php?id=111284&torrentid=148289 https://jpopsuki.eu/torrents.php?id=111284&torrentid=147830"

To upload every release of AKB48 - 1830m, excluding the ISOs (in JPS ISO is considered an audio format):
jps2sm.exe --urls "https://jpopsuki.eu/torrents.php?id=111284" --excaudioformat ISO

To test upload all your personal uploads, <userid> is your JPS userid:
jps2sm.exe --batchuser <userid> --batchuploaded --dryrun

Once everything looks ok, to upload all your personal uploads, <userid> is your JPS userid:
jps2sm.exe --batchuser <userid> --batchuploaded

To test upload all the torrents you are seeding at JPS, <userid> is your JPS userid:
jps2sm.exe --batchuser <userid> --batchseeding --dryrun

Once everything looks ok, to upload all the torrents you are seeding at JPS, <userid> is your JPS userid:
jps2sm.exe --batchuser <userid> --batchseeding

FAQ:

Help me! Its not working!
Come to the SugoiMusic Discord where someone can help.

Why are there so many files? Can everything be in one exe file?
If all the required libraries are built into one packed exe file jps2sm becomes very slow. Just ignore the extra files and run it as indicated. A nice and simple shortcut is created so you can run it from the root folder of the archive, to make it more intuitive on the command-line.

Is there a GUI?
No. It is not currently on the roadmap but it could be done in the future

Could jps2sm be web-based?
Yes it could be done potentially, using flask, and it is potentially not a particularly massive piece of work. This is actually far more likely to happen than a GUI. It is also not currently on the roadmap though.

Does jps2sm send any login credentials to a 3rd-party?
No, jps2sm only sends your JPS and SM credentials to the relevent trackers, no cloud / 3rd-party server is involved.

Bug Reports:

Visit the SugoiMusic forums or visit https://git.sugoimusic.me/Sugoimusic/jps2sm/issues