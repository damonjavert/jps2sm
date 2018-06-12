<?php

ini_set("error_reporting", E_ALL);
function GET($url,$referer = "",$proxy="", $header=false) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL,"$url");
    curl_setopt($ch, CURLOPT_COOKIEJAR, 'curl_cookiejar');  
    curl_setopt($ch, CURLOPT_COOKIEFILE, 'curl_cookiejar');
    if ($referer != "")
        curl_setopt ($ch, CURLOPT_REFERER, $referer);
    if ($proxy != "")
    {
        curl_setopt($ch, CURLOPT_PROXY, "");
        curl_setopt($ch, CURLOPT_HTTPPROXYTUNNEL,true);
    }
    if ($header) {
        curl_setopt($ch, CURLOPT_HEADER, true);
    }
    curl_setopt($ch, CURLOPT_USERAGENT,
        "Mozilla/5.0 (Windows; U; Windows NT 6.0; nl; rv:1.9.1) Gecko/20090612 Firefox/ 3.5");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $result = curl_exec($ch);
    curl_close($ch);
    return $result;
}

function POST($url,$data,$referer = "",$proxy="") {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL,"$url");
    if ($referer != "")
        curl_setopt ($ch, CURLOPT_REFERER, $referer);
        
    curl_setopt($ch, CURLOPT_USERAGENT,
        "Mozilla/5.0 (Windows; U; Windows NT 6.0; nl; rv:1.9.1) Gecko/20090612 Firefox/ 3.5");
    if ($proxy != "") {
        curl_setopt($ch, CURLOPT_PROXY, "");
        curl_setopt($ch, CURLOPT_HTTPPROXYTUNNEL,true);
    }
    curl_setopt($ch, CURLOPT_COOKIEJAR, 'curl_cookiejar');
    curl_setopt($ch, CURLOPT_COOKIEFILE, 'curl_cookiejar');
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true );
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data );
    curl_setopt($ch, CURLOPT_HEADER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array('Expect:'));
    $result = curl_exec($ch);
    curl_close($ch);
    return $result;
}

$res = GET("upload.php", "", "", true);

if (strstr($res, 'Location: login.php'))
    POST("login.php", "username=YOURUSERNAMEHERE&password=YOURPASSWORDHERE&keeplogged=1");

$data = array(
    'submit'        => 'true',
    'file_input'    => '@___TORRENTFILE___',
    'type'          => 'TV-Music',
    'artist'        => '___ARTIST___',
    'artistjp'      => '',
    'title'         => '___TITLE___',
    'format'        => '___FORMAT___',
    'media'         => 'HDTV',
    'tags'          => '___TAGS___',
    'genre_tags'    => '---',
    'image'         => '',
    'userfile'      => '',
    'album_desc'    =>
        "Note that this is a completely automated upload made by a script without human intervention;"
        ." please excuse any errors.\nFeel free to remove this text and post a real description here.",
    'release_desc'  => 'Untouched transport stream; only null packets, control messages'
        .'and superfluous streams have been stripped. May contain ads. Resolution and codec are in filename.',
    'freeleech'     => 'on',
);
$p = POST("upload.php", $data, "upload.php");
if (preg_match('/<a href="torrents\.php\?id=(\d+)>here<\/a>/', $p, $m))
    $tid = $m[1];
else
    die('failed');

$tp = GET("torrents.php?id=".$tid, "upload.php");
if (!preg_match(
        '/<a href="(torrents.php\?action=download&authkey=.*?&torrent_pass=.*?)"\s+title="Download">DL<\/a>/',
        $tp, $m2))
    die("failed");

$urlkey = $m2[1];
str_replace('&', '&', $urlkey);

$turl      = '' . $urlkey;
$torrent   = GET($turl, "torrents.php?id=".$tid);
$tname     = '/tmp/jpopsuki-tid-'.$tid . time() . '.torrent';
$f = fopen($tname, 'w');
fwrite($f, $torrent);
fclose($f);
echo $tname;

?>
