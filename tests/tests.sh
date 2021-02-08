#!/bin/bash
#Very basic tests, do not complain how badly these are written without submitting a PR to improve it.

echo "Running tests on $(git rev-parse --verify HEAD)"

interpreter="python3.8"

#Test if start page specified but no end page error
diff -u tests/arg-check-batchuser-no-end-page <(${interpreter} jps2sm.py -d --batchuser 194033 --batchuploaded -s 10 -n 2>&1 && echo "jps2sm exited OK but it should have errored!")
echo ---------------------------------
#Test general whole group AKB48 - 1830m
diff -u tests/group-111284 <(${interpreter} jps2sm.py --urls "https://jpopsuki.eu/torrents.php?id=111284" -dn || echo "jps2sm exited non-zero!")
echo ---------------------------------
#Test specific torrent in a group that has Hi-Res FLAC
diff -u tests/group-321079-torrent-472015 <(${interpreter} jps2sm.py --urls "https://jpopsuki.eu/torrents.php?id=321079&torrentid=472015" -dn || echo "jps2sm exited non-zero!")
echo ---------------------------------
#Test V.A. group that has contrib artists with no original character name
diff -u tests/group-251299-torrent-358233 <(${interpreter} jps2sm.py --urls "https://jpopsuki.eu/torrents.php?id=251299&torrentid=358233" -dn || echo "jps2sm exited non-zero!")
echo ---------------------------------
echo "Tests complete"


