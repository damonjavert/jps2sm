#!/bin/bash
#Very basic tests, do not complain how badly these are written without submitting a PR to improve it.

echo "Running tests on $(git rev-parse --verify HEAD)"

interpreter="python3.8"

diff -u tests/group-111284 <(python3.8 jps2sm.py --urls "https://jpopsuki.eu/torrents.php?id=111284" -dn || echo "jps2sm exited non-zero!")
echo ---------------------------------
diff -u tests/group-321079-torrent-472015 <(${interpreter} jps2sm.py --urls "https://jpopsuki.eu/torrents.php?id=321079&torrentid=472015" -dn || echo "jps2sm exited non-zero!")
echo ---------------------------------
diff -u tests/group-251299-torrent-358233 <(python3.8 jps2sm.py --urls "https://jpopsuki.eu/torrents.php?id=251299&torrentid=358233" -dn || echo "jps2sm exited non-zero!")
echo ---------------------------------
echo "Tests complete"


