#!/bin/bash

jps2sm=$1

$jps2sm --urls "https://jpopsuki.eu/torrents.php?id=111284" -dn | tee tests/group-111284
$jps2sm -d --batchuser 194033 --batchuploaded -s 10 -n 2>&1 | tee tests/arg-check-batchuser-no-end-page
$jps2sm -dn --batchuser 194033 --batchuploaded -s 15 -e 16 | tee tests/batchuser-194033-zilla-pages-15-16
$jps2sm -d --batchuser 194033 --batchuploaded -s 10 -n | tee tests/arg-check-batchuser-no-end-page
$jps2sm --urls "https://jpopsuki.eu/torrents.php?id=251299&torrentid=358233" -dn | tee tests/group-251299-torrent-358233
$jps2sm --urls "https://jpopsuki.eu/torrents.php?id=321079&torrentid=472015" -dn | tee tests/group-321079-torrent-472015
$jps2sm -dn --urls 'https://jpopsuki.eu/torrents.php?id=280834' | tee tests/group-28034-music-in-video-group
$jps2sm -dn --urls 'https://jpopsuki.eu/torrents.php?id=155760' -exf MP3 | tee tests/group-155760-exclude-audioformat
