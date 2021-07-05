#!/bin/bash
#Very basic tests, do not complain how badly these are written without submitting a PR to improve it.

echo "Running tests on $(git rev-parse --verify HEAD)"

jps2sm=$1

echo Test if start page specified but no end page error
diff -u tests/arg-check-batchuser-no-end-page <(${jps2sm} -d --batchuser 194033 --batchuploaded -s 10 -n 2>&1 && echo "jps2sm exited OK but it should have errored!")
echo ---------------------------------
echo Test general whole group AKB48 - 1830m
diff -u tests/group-111284 <(${jps2sm} --urls "https://jpopsuki.eu/torrents.php?id=111284" -dn || echo "jps2sm exited non-zero!")
echo ---------------------------------
echo Test specific torrent in a group that has Hi-Res FLAC
diff -u tests/group-321079-torrent-472015 <(${jps2sm} --urls "https://jpopsuki.eu/torrents.php?id=321079&torrentid=472015" -dn || echo "jps2sm exited non-zero!")
echo ---------------------------------
echo Test V.A. group that has contrib artists with no original character name
diff -u tests/group-251299-torrent-358233 <(${jps2sm} --urls "https://jpopsuki.eu/torrents.php?id=251299&torrentid=358233" -dn || echo "jps2sm exited non-zero!")
echo ---------------------------------
echo Test batchuser 194033 - zilla - batchuploaded pages 15 - 16
#This only works as we are testing against an uploader who is no longer active, if they become active this test will fail
diff -u tests/batchuser-194033-zilla-pages-15-16 <(${jps2sm} -dn --batchuser 194033 --batchuploaded -s 15 -e 16 || echo "jps2sm exited non-zero!")
echo ---------------------------------
echo Test for music in a video group
diff -u tests/group-28034-music-in-video-group <(${jps2sm} -dn --urls 'https://jpopsuki.eu/torrents.php?id=280834' || echo "jps2sm exited non-zero!")
echo ---------------------------------
echo Test for excluding audioformat
diff -u tests/group-155760-exclude-audioformat <(${jps2sm} -dn --urls 'https://jpopsuki.eu/torrents.php?id=155760' -exf MP3 || echo "jps2sm exited non-zero!")
echo "Tests complete"