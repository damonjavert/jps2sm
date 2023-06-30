"""
Run tests for GetGroupData()
"""
# pylint: disable=duplicate-code

import pytest
import re
import requests
import requests_mock

from jps2sm.get_data import GetGroupData, get_group_description_bbcode
from jps2sm.myloginsession import jpopsuki, LoginParameters


def test_get_group_data(requests_mock):
    """
    Test for JPS group data class
    """
    jps_group_id = "176329"
    jps_group_page_text = """
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
        <title>Momoiro Clover Z - Momoclo Natsu no Baka Sawagi 2014 Nissan Stadium Taikai ~Tojinsai~ :: JPopsuki 2.0</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <link rel="shortcut icon" href="favicon.ico" />
        <link rel="search" type="application/opensearchdescription+xml" title="JPopsuki 2.0 - Torrents" href="/opensearch_torrents.xml" />
        <link rel="search" type="application/opensearchdescription+xml" title="JPopsuki 2.0 - Requests" href="/opensearch_requests.xml" />
        <link rel="search" type="application/opensearchdescription+xml" title="JPopsuki 2.0 - Forums" href="/opensearch_forums.xml" />
        <link rel="search" type="application/opensearchdescription+xml" title="JPopsuki 2.0 - Log" href="/opensearch_log.xml" />
        <link rel="search" type="application/opensearchdescription+xml" title="JPopsuki 2.0 - Users" href="/opensearch_users.xml" />
        <link rel="alternate" type="application/rss+xml" href="/feeds.php?feed=torrents_notify_11111111111111111111111111111111&amp;user=999999&amp;auth=00000000000000000000000000000000&amp;passkey=11111111111111111111111111111111&amp;authkey=00000000000000000000000000000000" title="JPopsuki 2.0 - P.T.N." />
        <link rel="alternate" type="application/rss+xml" href="/feeds.php?feed=torrents_notify_14056_11111111111111111111111111111111&amp;user=999999&amp;auth=00000000000000000000000000000000&amp;passkey=11111111111111111111111111111111&amp;authkey=00000000000000000000000000000000&amp;name=Artist+notifications" title="JPopsuki 2.0 - Artist notifications" />
        <link rel="alternate" type="application/rss+xml" href="/feeds.php?feed=torrents_all&amp;user=999999&amp;auth=00000000000000000000000000000000&amp;passkey=11111111111111111111111111111111&amp;authkey=00000000000000000000000000000000" title="JPopsuki 2.0 - All Torrents" />
        <link rel="alternate" type="application/rss+xml" href="/feeds.php?feed=torrents_album&amp;user=999999&amp;auth=00000000000000000000000000000000&amp;passkey=11111111111111111111111111111111&amp;authkey=00000000000000000000000000000000" title="JPopsuki 2.0 - Album Torrents" />
        <link rel="alternate" type="application/rss+xml" href="/feeds.php?feed=torrents_single&amp;user=999999&amp;auth=00000000000000000000000000000000&amp;passkey=11111111111111111111111111111111&amp;authkey=00000000000000000000000000000000" title="JPopsuki 2.0 - Single Torrents" />
        <link rel="alternate" type="application/rss+xml" href="/feeds.php?feed=torrents_pv&amp;user=999999&amp;auth=00000000000000000000000000000000&amp;passkey=11111111111111111111111111111111&amp;authkey=00000000000000000000000000000000" title="JPopsuki 2.0 - PV Torrents" />
        <link rel="alternate" type="application/rss+xml" href="/feeds.php?feed=torrents_dvd&amp;user=999999&amp;auth=00000000000000000000000000000000&amp;passkey=11111111111111111111111111111111&amp;authkey=00000000000000000000000000000000" title="JPopsuki 2.0 - DVD Torrents" />
        <link rel="alternate" type="application/rss+xml" href="/feeds.php?feed=torrents_tv-music&amp;user=999999&amp;auth=00000000000000000000000000000000&amp;passkey=11111111111111111111111111111111&amp;authkey=00000000000000000000000000000000" title="JPopsuki 2.0 - TV-Music Torrents" />
        <link rel="alternate" type="application/rss+xml" href="/feeds.php?feed=torrents_tv-variety&amp;user=999999&amp;auth=00000000000000000000000000000000&amp;passkey=11111111111111111111111111111111&amp;authkey=00000000000000000000000000000000" title="JPopsuki 2.0 - TV-Variety Torrents" />
        <link rel="alternate" type="application/rss+xml" href="/feeds.php?feed=torrents_tv-drama&amp;user=999999&amp;auth=00000000000000000000000000000000&amp;passkey=11111111111111111111111111111111&amp;authkey=00000000000000000000000000000000" title="JPopsuki 2.0 - TV-Drama Torrents" />
        <link rel="alternate" type="application/rss+xml" href="/feeds.php?feed=torrents_fansubs&amp;user=999999&amp;auth=00000000000000000000000000000000&amp;passkey=11111111111111111111111111111111&amp;authkey=00000000000000000000000000000000" title="JPopsuki 2.0 - Fansubs Torrents" />
        <link rel="alternate" type="application/rss+xml" href="/feeds.php?feed=torrents_pictures&amp;user=999999&amp;auth=00000000000000000000000000000000&amp;passkey=11111111111111111111111111111111&amp;authkey=00000000000000000000000000000000" title="JPopsuki 2.0 - Pictures Torrents" />
        <link rel="alternate" type="application/rss+xml" href="/feeds.php?feed=torrents_misc&amp;user=999999&amp;auth=00000000000000000000000000000000&amp;passkey=11111111111111111111111111111111&amp;authkey=00000000000000000000000000000000" title="JPopsuki 2.0 - Misc Torrents" />
        <link rel="alternate" type="application/rss+xml" href="/feeds.php?feed=torrents_lossless&amp;user=999999&amp;auth=00000000000000000000000000000000&amp;passkey=11111111111111111111111111111111&amp;authkey=00000000000000000000000000000000" title="JPopsuki 2.0 - Lossless Torrents" />
        <link rel="alternate" type="application/rss+xml" href="/feeds.php?feed=torrents_flac&amp;user=999999&amp;auth=00000000000000000000000000000000&amp;passkey=11111111111111111111111111111111&amp;authkey=00000000000000000000000000000000" title="JPopsuki 2.0 - FLAC Torrents" />
        <link href="static/styles/layer_cake/style.css" title="layer_cake" rel="stylesheet" type="text/css" media="screen" />
        <link href="static/styles/log.css" rel="stylesheet" type="text/css" />
        <link href="static/styles/global.css" rel="stylesheet" type="text/css" />
        <script src="static/functions/jquery.js" type="text/javascript"></script>
        <script src="static/functions/main.js" type="text/javascript"></script>
        <link rel="stylesheet" type="text/css" href="static/shadowbox-3.0.3/shadowbox.css">
        <script type="text/javascript" src="static/shadowbox-3.0.3/shadowbox.js"></script>
        <script type="text/javascript">
        Shadowbox.init();
        </script>
        <script type="text/javascript">
                function bluehorse()
                {
                        if(confirm('Would you like to see a penis?')) {
                                alert('Sick bastard. Oh well, here\'s a penis');
                        } else {
                                alert('Too bad! You\'re going to see one anyways');
                        }

                        document.location = "http://jpopsuki.eu/static/images/users/774/KICRK.png";
                }

                function penis()
                {
                        document.cookie = 'invasion=zombie_fruits; expires=Fri, 04 Mar 2011 21:29:16 GMT; path=/';
                        $('#randomfitta').css('display', 'none');
                }
        </script>

        <script src="static/functions/details.js" type="text/javascript"></script>
        <script src="static/functions/posts.js" type="text/javascript"></script>
        <script src="static/functions/jquery-ui.js" type="text/javascript"></script>

</head>
<body id="torrents">
<a name="top"></a>

<div id="wrapper">
<h1 class="hidden">JPopsuki 2.0</h1>

<div id="header">
        <div id="logo"><a href="index.php"></a></div>
        <div id="userinfo">
                <ul id="userinfo_username">
                        <li><a href="user.php?id=999999" class="username">username</a></li>
                        <li class="brackets"><a href="user.php?action=edit&amp;userid=999999">Edit</a></li>
                        <li class="brackets"><a href="logout.php?auth=00000000000000000000000000000000">Logout</a></li>
                </ul>
                <ul id="userinfo_major">
                        <li class="brackets"><strong><a href="upload.php">Upload</a></strong></li>
                        <li class="brackets"><strong><a href="user.php?action=invite">Invite (10)</a></strong></li>
                        <li class="brackets"><strong><a href="donate.php">Donate</a></strong></li>
                </ul>
                <ul id="userinfo_stats">
                        <li>Up: <span class="stat">51.87 TB</span></li>
                        <li>Down: <span class="stat">4.71 TB</span></li>
                        <li>Ratio: <span class="stat"><span class="r50">11.02</span></span></li>
                        <li><i><a href="bonus.php">Bonus: <span class="stat">2097150</span></a></i></li>
                </ul>
                <ul id="userinfo_minor">
                        <li><a href="inbox.php">Inbox</a></li>
                        <li><a href="notice.php">Notices</a></li>
                        <li><a href="torrents.php?type=uploaded&amp;userid=999999">Uploads</a></li>
                        <li><a href="bookmarks.php">Bookmarks</a></li>
</a></li>
                        <li><a href="user.php?action=notify">Notifications</a></li>
                        <li><a href="userhistory.php?action=posts&amp;userid=999999">Posts</a></li>
                        <li><a href="friends.php">Friends</a></li>
                </ul>
        </div>
        <div id="menu">
                <h4 class="hidden">Site Menu</h4>
                <ul>
                        <li id="nav_index"><a href="index.php">Home</a></li>
                        <li id="nav_torrents"><a href="torrents.php">Torrents</a></li>
                        <li id="nav_artists"><a href="artist.php">Artists</a></li>
                        <li id="nav_requests"><a href="requests.php">Requests</a></li>
                        <li id="nav_collages"><a href="collages.php">Collages</a></li>
                        <li id="nav_forums"><a href="forums.php">Forums</a></li>
                        <li id="nav_top10"><a href="top10.php">Top 10</a></li>
                        <li id="nav_irc"><a href="irc.php">IRC</a></li>
                        <li id="nav_tv"><a href="streaming.php">Radio</a></li>
                        <li id="nav_rules"><a href="rules.php">Rules</a></li>
                        <li id="nav_kb"><a href="kb2.php">Help</a></li>
                        <li id="nav_staff"><a href="staff.php">Staff</a></li>
                </ul>
        </div>
        <div id="alerts">
                <div class="alertbar">
                        <a href="torrents.php?action=notify">You have 7 new torrent notifications</a> (<a href="torrents.php?action=notify_clear&amp;auth=00000000000000000000000000000000">Delete</a>)
                </div>
        </div>
        <div id="searchbars">
                <ul>

                        <li>
                                <span class="hidden">Torrents: </span>
                                <form action="torrents.php" method="get">
                                        <input
                                                onfocus="if (this.value == 'Torrents') this.value='';"
                                                onblur="if (this.value == '') this.value='Torrents';"
                                                value="Torrents" type="text" name="searchstr" size="17"
                                        />
                                        <input value="Search" type="submit" class="hidden" />
                                </form>
                        </li>


                        <li>
                                <span class="hidden">Artist: </span>
                                <form action="artist.php" method="get">
                                        <input
                                                onfocus="if (this.value == 'Artist') this.value='';"
                                                onblur="if (this.value == '') this.value='Artist';"
                                                value="Artist" type="text" name="name" size="17"
                                        />
                                        <input value="Search" type="submit" class="hidden" />
                                </form>
                        </li>

                        <li>
                                <span class="hidden">Requests: </span>
                                <form action="requests.php" method="get">
                                        <input
                                                onfocus="if (this.value == 'Requests') this.value='';"
                                                onblur="if (this.value == '') this.value='Requests';"
                                                value="Requests" type="text" name="search" size="17"
                                        />
                                        <input value="Search" type="submit" class="hidden" />
                                </form>
                        </li>
                        <li>
                                <span class="hidden">Forums: </span>
                                <form action="forums.php" method="get">
                                        <input value="search" type="hidden" name="action" />
                                        <input
                                                onfocus="if (this.value == 'Forums') this.value='';"
                                                onblur="if (this.value == '') this.value='Forums';"
                                                value="Forums" type="text" name="search" size="17"
                                        />
                                        <input value="Search" type="submit" class="hidden" />
                                </form>
                        </li>
                        <li>
                                <span class="hidden">Log: </span>
                                <form action="log.php" method="get">
                                        <input
                                                onfocus="if (this.value == 'Log') this.value='';"
                                                onblur="if (this.value == '') this.value='Log';"
                                                value="Log" type="text" name="search" size="17"
                                        />
                                        <input value="Search" type="submit" class="hidden" />
                                </form>
                        </li>
                        <li>
                                <span class="hidden">Users: </span>
                                <form action="user.php" method="get">
                                        <input type="hidden" name="action" value="search" />
                                        <input
                                                onfocus="if (this.value == 'Peeps') this.value='';"
                                                onblur="if (this.value == '') this.value='Peeps';"
                                                value="Peeps" type="text" name="username" size="17"
                                        />
                                        <input value="Search" type="submit" class="hidden" />
                                </form>
                        </li>
                </ul>
        </div>

</div>
<br />
<div id="content">
<script type="text/javascript">
$(document).ready(function() {
        $('#lolpenis').autocomplete({
                delay: 500,
                source: "ajax.php?section=a_artist",
                minLength: 2
        });
});
</script>
<div class="thin">
        <h2>[DVD] <a href="artist.php?id=13739">Momoiro Clover Z</a> - Momoclo Natsu no Baka Sawagi 2014 Nissan Stadium Taikai ~Tojinsai~ [2015.02.25]</h2>
<h3 style="text-align:center;">(<a href="artist.php?id=13739">&#12418;&#12418;&#12356;&#12429;&#12463;&#12525;&#12540;&#12496;&#12540;Z</a> - &#12418;&#12418;&#12463;&#12525;&#22799;&#12398;&#12496;&#12459;&#39442;&#12366;2014 &#26085;&#29987;&#12473;&#12479;&#12472;&#12450;&#12512;&#22823;&#20250;&#65374;&#26691;&#31070;&#31085;&#65374;)</h3>   <div class="sidebar">
                <div class="box">
                        <div class="head"><strong>Page Options</strong></div>
                        <ul class="stats nobullet">
                                <li><a href="reports.php?action=report&amp;type=Group&amp;id=176329">Report</a></li>
                                <li><a href="torrents.php?action=editgroup&amp;groupid=176329">Edit Description</a></li>
                                <li><a href="torrents.php?action=history&amp;groupid=176329">View History</a></li>
                                <li><a href="javascript:Bookmark();">Bookmark</a></li>
                                <li><a href="upload.php?groupid=176329">Add Format</a></li>
                        </ul>
                </div>
                <div class="box">
                        <div class="head"><strong>Cover / Screenshot</strong></div>
                        <p align="center"><a href="static/images/torrents/176329.jpg" rel="shadowbox" title="Momoiro Clover Z - Momoclo Natsu no Baka Sawagi 2014 Nissan Stadium Taikai ~Tojinsai~ [2015.02.25]"><img src="static/images/torrents/176329.th.jpg" width="220" alt="Momoiro Clover Z - Momoclo Natsu no Baka Sawagi 2014 Nissan Stadium Taikai ~Tojinsai~ [2015.02.25]" title="Momoiro Clover Z - Momoclo Natsu no Baka Sawagi 2014 Nissan Stadium Taikai ~Tojinsai~ [2015.02.25]" border="0" /></a></p>
                </div>
                <div class="box">
                        <div class="head"><strong>Contributing Artists</strong></div>
                        <div class="body">
                                <ul class="stats nobullet">
                                </ul>
                                <form action="torrents.php" method="post">
                                        <input type="hidden" name="action" value="add_contrib" />
                                        <input type="hidden" name="groupid" value="176329" />
                                        <input type="text" id="lolpenis" name="artistname" size="20" />
                                        <input type="submit" value="+" />
                                </form>
                        </div>
                </div>

                <div class="box">
                        <div class="head"><strong>Tags</strong></div>
                        <ul class="stats nobullet">
<!-- 1|1|1|594 -->                              <li>
                                        <a href="torrents.php?searchtags=japanese">japanese</a>
                                        <a href="torrents.php?action=vote_tag&amp;way=up&amp;groupid=176329&amp;tagid=1&amp;auth=00000000000000000000000000000000">[+]</a>
                                        <a href="torrents.php?action=vote_tag&amp;way=down&amp;groupid=176329&amp;tagid=1&amp;auth=00000000000000000000000000000000">[-]</a>
                                </li>
                                <li>
                                        <a href="torrents.php?searchtags=pop">pop</a>
                                        <a href="torrents.php?action=vote_tag&amp;way=up&amp;groupid=176329&amp;tagid=7&amp;auth=00000000000000000000000000000000">[+]</a>
                                        <a href="torrents.php?action=vote_tag&amp;way=down&amp;groupid=176329&amp;tagid=7&amp;auth=00000000000000000000000000000000">[-]</a>
                                </li>
                                <li>
                                        <a href="torrents.php?searchtags=female.vocalist">female.vocalist</a>
                                        <a href="torrents.php?action=vote_tag&amp;way=up&amp;groupid=176329&amp;tagid=17&amp;auth=00000000000000000000000000000000">[+]</a>
                                        <a href="torrents.php?action=vote_tag&amp;way=down&amp;groupid=176329&amp;tagid=17&amp;auth=00000000000000000000000000000000">[-]</a>
                                </li>
                                <li>
                                        <a href="torrents.php?searchtags=idol">idol</a>
                                        <a href="torrents.php?action=vote_tag&amp;way=up&amp;groupid=176329&amp;tagid=175&amp;auth=00000000000000000000000000000000">[+]</a>
                                        <a href="torrents.php?action=vote_tag&amp;way=down&amp;groupid=176329&amp;tagid=175&amp;auth=00000000000000000000000000000000">[-]</a>
                                </li>
                        </ul>
                </div>
                <div class="box">
                        <div class="head"><strong>Add Tag</strong></div>
                        <div class="body">
                                <form action="torrents.php" method="post">
                                        <input type="hidden" name="action" value="add_tag" />
                                        <input type="hidden" name="groupid" value="176329" />
                                        <input type="text" name="tagname" size="20" />
                                        <input type="submit" value="+" />
                                </form>
                                <br /><br />
                                <strong><a href="rules.php?p=tag">Tagging Rules</a></strong>
                        </div>
                </div>
        </div>
        <div class="main_column">
                <table class="torrent_table" style="margin-top: 0px">
                        <tr class="colhead_dark">
                                <td width="80%"><strong>Torrents</strong></td>
                                <td><strong>Size</strong></td>
                                <td class="sign"><img src="static/styles/layer_cake/images/snatched.png" alt="Snatches" title="Snatches" /></td>
                                <td class="sign"><img src="static/styles/layer_cake/images/seeders.png" alt="Seeders" title="Seeders" /></td>
                                <td class="sign"><img src="static/styles/layer_cake/images/leechers.png" alt="Leechers" title="Leechers" /></td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=242532&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=242532" title="Report">RP</a>
                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('242532');">&raquo; MP4 / Blu-Ray / Limited Edition Day1 - 2015</a>
                                </td>
                                <td class="nobr">11.75 GB</td>
                                <td>126</td>
                                <td>0</td>
                                <td>1</td>
                        </tr>

                <tr class="pad hide" id="torrent_242532">
                <td colspan="5">
                                <div id="linkbox" style="text-align: center" >
                            <form method="post" action="">
                                <input type="hidden" id="action" name="action" value="reseed" />
                                <input type="hidden" id="gid" name="gid" value="176329" />
                                <input type="hidden" id="tid" name="tid" value="242532" />
                                                                <input type="submit" id="reseed" name="reseed" value="Request a reseed" />
                                                            </form>
                    </div>

                                                        <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">10.99</span><br />
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=164418">chewyee</a>  on <span title="8 years, 1 day, 14 hours ago">Mar 01 2015, 06:35</span>                                             <br />Last active: <span title="2 years, 4 months, 2 weeks ago">Oct 13 2020, 10:06</span>        </blockquote>
                                        <blockquote>Included both discs for Day 1 into this torrent.<br />
Credits to ici_jp for the ISO version</blockquote>                                      <table style="overflow-x:auto;"><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>Tohjinsai Day1 Disc1.mp4</td><td>4.97 GB</td></tr><tr><td>Tohjinsai Day1 Disc2 Specials.mp4</td><td>898.78 MB</td></tr><tr><td>Tohjinsai Day1 Disc2.mp4</td><td>5.90 GB</td></tr></table>                     Peer List: (<a href="#" id="swapPeer_242532" onclick="return swapPeerList('242532', '12618626711', 'Show', 'Hide');">Show</a>)<br />
                        <div id="ajax_peerlist_242532" style="text-align: center"></div><br />
                        Snatch List: (<a href="#" id="swapSnatch_242532" onclick="return swapSnatchList('242532', 'Show', 'Hide');">Show</a>)<br />
                        <div id="ajax_snatchlist_242532" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=242535&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=242535" title="Report">RP</a>
                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('242535');">&raquo; MP4 / Blu-Ray / Limited Edition Day2 - 2015</a>
                                </td>
                                <td class="nobr">11.12 GB</td>
                                <td>94</td>
                                <td>0</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_242535">
                <td colspan="5">
                                <div id="linkbox" style="text-align: center" >
                            <form method="post" action="">
                                <input type="hidden" id="action" name="action" value="reseed" />
                                <input type="hidden" id="gid" name="gid" value="176329" />
                                <input type="hidden" id="tid" name="tid" value="242535" />
                                                                <input type="submit" id="reseed" name="reseed" value="Request a reseed" />
                                                            </form>
                    </div>

                                                        <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">10.99</span><br />
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=164418">chewyee</a>  on <span title="8 years, 1 day, 12 hours ago">Mar 01 2015, 08:23</span>                                             <br />Last active: <span title="2 years, 4 months, 2 weeks ago">Oct 13 2020, 10:06</span>        </blockquote>
                                        <blockquote>Included both discs for Day 2 into this torrent.<br />
Credits to ici_jp for the ISO version</blockquote>                                      <table style="overflow-x:auto;"><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>Tohjinsai Day2 Disc1.mp4</td><td>5.44 GB</td></tr><tr><td>Tohjinsai Day2 Disc2 Specials.mp4</td><td>1.34 GB</td></tr><tr><td>Tohjinsai Day2 Disc2.mp4</td><td>4.34 GB</td></tr></table>                       Peer List: (<a href="#" id="swapPeer_242535" onclick="return swapPeerList('242535', '11941368726', 'Show', 'Hide');">Show</a>)<br />
                        <div id="ajax_peerlist_242535" style="text-align: center"></div><br />
                        Snatch List: (<a href="#" id="swapSnatch_242535" onclick="return swapSnatchList('242535', 'Show', 'Hide');">Show</a>)<br />
                        <div id="ajax_snatchlist_242535" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=242063&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=242063" title="Report" style="font-weight: bold; color: red;">Reported!</a>
                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('242063');">&raquo; ISO / Blu-Ray / Limited Edition Day1_1 - 2015</a>
                                </td>
                                <td class="nobr">34.25 GB</td>
                                <td>101</td>
                                <td>2</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_242063">
                <td colspan="5">

                                                <table style="overflow-x:auto;">
                                <tr class="colhead_dark">
                                    <td><strong>Reported on <span title="5 years, 6 months, 2 weeks ago">Aug 13 2017, 06:55</span></strong></td>
                                </tr>
                                <tr>
                                    <td>Incomplete, missing Disc 2. <br />
<br />
Rules state, &quot;If you upload a release that consists of multiple DVD&#39;s or CD&#39;s, please put all of them into one torrent and do not create separate torrents for each disc.&quot;</td>
                                </tr>
                            </table>
                                                                <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">10.94</span><br />
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=55698">ici_jp</a>  on <span title="8 years, 6 days, 14 hours ago">Feb 24 2015, 06:42</span>                                      </blockquote>
                                                                                <table style="overflow-x:auto;"><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>KIXM 90191.iso</td><td>34.25 GB</td></tr></table>                   Peer List: (<a href="#" id="swapPeer_242063" onclick="return swapPeerList('242063', '36772511744', 'Show', 'Hide');">Show</a>)<br />
                        <div id="ajax_peerlist_242063" style="text-align: center"></div><br />
                        Snatch List: (<a href="#" id="swapSnatch_242063" onclick="return swapSnatchList('242063', 'Show', 'Hide');">Show</a>)<br />
                        <div id="ajax_snatchlist_242063" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=242064&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=242064" title="Report" style="font-weight: bold; color: red;">Reported!</a>
                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('242064');">&raquo; ISO / Blu-Ray / Limited Edition Day1_2 - 2015</a>
                                </td>
                                <td class="nobr">42.92 GB</td>
                                <td>97</td>
                                <td>2</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_242064">
                <td colspan="5">

                                                <table style="overflow-x:auto;">
                                <tr class="colhead_dark">
                                    <td><strong>Reported on <span title="5 years, 6 months, 2 weeks ago">Aug 13 2017, 06:55</span></strong></td>
                                </tr>
                                <tr>
                                    <td>Incomplete, missing Disc 1. <br />
<br />
Rules state, &quot;If you upload a release that consists of multiple DVD&#39;s or CD&#39;s, please put all of them into one torrent and do not create separate torrents for each disc.&quot;</td>
                                </tr>
                            </table>
                                                                <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">10.92</span><br />
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=55698">ici_jp</a>  on <span title="8 years, 6 days, 14 hours ago">Feb 24 2015, 06:45</span>                                      </blockquote>
                                                                                <table style="overflow-x:auto;"><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>KIXM 90192.iso</td><td>42.92 GB</td></tr></table>                   Peer List: (<a href="#" id="swapPeer_242064" onclick="return swapPeerList('242064', '46083473408', 'Show', 'Hide');">Show</a>)<br />
                        <div id="ajax_peerlist_242064" style="text-align: center"></div><br />
                        Snatch List: (<a href="#" id="swapSnatch_242064" onclick="return swapSnatchList('242064', 'Show', 'Hide');">Show</a>)<br />
                        <div id="ajax_snatchlist_242064" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=242065&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=242065" title="Report" style="font-weight: bold; color: red;">Reported!</a>
                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('242065');">&raquo; ISO / Blu-Ray / Limited Edition Day2_1 - 2015</a>
                                </td>
                                <td class="nobr">37.55 GB</td>
                                <td>93</td>
                                <td>2</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_242065">
                <td colspan="5">

                                                <table style="overflow-x:auto;">
                                <tr class="colhead_dark">
                                    <td><strong>Reported on <span title="5 years, 6 months, 2 weeks ago">Aug 13 2017, 06:56</span></strong></td>
                                </tr>
                                <tr>
                                    <td>Incomplete, missing Disc 2. <br />
<br />
Rules state, &quot;If you upload a release that consists of multiple DVD&#39;s or CD&#39;s, please put all of them into one torrent and do not create separate torrents for each disc.&quot;</td>
                                </tr>
                            </table>
                                                                <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">10.93</span><br />
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=55698">ici_jp</a>  on <span title="8 years, 6 days, 14 hours ago">Feb 24 2015, 06:50</span>                                      </blockquote>
                                                                                <table style="overflow-x:auto;"><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>KIXM 90193.iso</td><td>37.55 GB</td></tr></table>                   Peer List: (<a href="#" id="swapPeer_242065" onclick="return swapPeerList('242065', '40316174336', 'Show', 'Hide');">Show</a>)<br />
                        <div id="ajax_peerlist_242065" style="text-align: center"></div><br />
                        Snatch List: (<a href="#" id="swapSnatch_242065" onclick="return swapSnatchList('242065', 'Show', 'Hide');">Show</a>)<br />
                        <div id="ajax_snatchlist_242065" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=242066&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=242066" title="Report" style="font-weight: bold; color: red;">Reported!</a>
                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('242066');">&raquo; ISO / Blu-Ray / Limited Edition Day2_2 - 2015</a>
                                </td>
                                <td class="nobr">38.86 GB</td>
                                <td>90</td>
                                <td>2</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_242066">
                <td colspan="5">

                                                <table style="overflow-x:auto;">
                                <tr class="colhead_dark">
                                    <td><strong>Reported on <span title="5 years, 6 months, 2 weeks ago">Aug 13 2017, 06:56</span></strong></td>
                                </tr>
                                <tr>
                                    <td>Incomplete, missing Disc 1. <br />
<br />
Rules state, &quot;If you upload a release that consists of multiple DVD&#39;s or CD&#39;s, please put all of them into one torrent and do not create separate torrents for each disc.&quot;</td>
                                </tr>
                            </table>
                                                                <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">10.93</span><br />
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=55698">ici_jp</a>  on <span title="8 years, 6 days, 14 hours ago">Feb 24 2015, 06:52</span>                                      </blockquote>
                                                                                <table style="overflow-x:auto;"><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>KIXM 90194.iso</td><td>38.86 GB</td></tr></table>                   Peer List: (<a href="#" id="swapPeer_242066" onclick="return swapPeerList('242066', '41727557632', 'Show', 'Hide');">Show</a>)<br />
                        <div id="ajax_peerlist_242066" style="text-align: center"></div><br />
                        Snatch List: (<a href="#" id="swapSnatch_242066" onclick="return swapSnatchList('242066', 'Show', 'Hide');">Show</a>)<br />
                        <div id="ajax_snatchlist_242066" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=335364&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=335364" title="Report">RP</a>
                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('335364');">&raquo; ISO / Blu-Ray / Day 1 - 2015</a>
                                </td>
                                <td class="nobr">77.17 GB</td>
                                <td>1</td>
                                <td>1</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_335364">
                <td colspan="5">

                                                        <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">10.84</span><br />
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=199149">dimsumli</a>  on <span title="5 years, 6 months, 2 weeks ago">Aug 13 2017, 00:36</span>                                  </blockquote>
                                                                                <table style="overflow-x:auto;"><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>&#26691;&#31070;&#31085;2014   Day 1 Disc 1.iso</td><td>34.25 GB</td></tr><tr><td>&#26691;&#31070;&#31085;2014   Day 1 Disc 2.iso</td><td>42.92 GB</td></tr></table>                  Peer List: (<a href="#" id="swapPeer_335364" onclick="return swapPeerList('335364', '82855985152', 'Show', 'Hide');">Show</a>)<br />
                        <div id="ajax_peerlist_335364" style="text-align: center"></div><br />
                        Snatch List: (<a href="#" id="swapSnatch_335364" onclick="return swapSnatchList('335364', 'Show', 'Hide');">Show</a>)<br />
                        <div id="ajax_snatchlist_335364" style="text-align: center"></div>

                                </td>
                        </tr>
                </table>
                <div class="box">
                        <div class="head"><strong>Release Info</strong></div>
                        <div class="body">2014.07.26, 27 Kanagawa Nissan Stadium<br />
<a href='http://www.momoclo.net/discography/dvd32.html' target='_blank'>http://www.momoclo.net/discography/dvd32.html</a><br />
<a href='http://www.cdjapan.co.jp/product/KIXM-90191' target='_blank'>http://www.cdjapan.co.jp/product/KIXM-90191</a><br />
<br />
<br />
Setlist<br />
---------------------------------------------------------<br />
<br />
&#9679;Day1<br />
<br />
Tojinsai no Theme(&#26691;&#31070;&#31085;&#12398;&#12486;&#12540;&#12510;)<br />
overture -Momoiro Clover Z Sanjo!!-(&#65374;&#12418;&#12418;&#12356;&#12429;&#12463;&#12525;&#12540;&#12496;&#12540;Z&#21442;&#19978;&#65281;&#65281;&#65374;)<br />
01. Ame no Tajikarao(&#22825;&#25163;&#21147;&#30007;)<br />
02. Wani to Shampoo(&#12527;&#12491;&#12392;&#12471;&#12515;&#12531;&#12503;&#12540;)<br />
03. Kuroi Shumatsu(&#40658;&#12356;&#36913;&#26411;)<br />
04. D&#39; No Junjou(D&#39;&#12398;&#32020;&#24773;)<br />
05. Doudou Heiwa Sengen(&#22530;&#12293;&#24179;&#21644;&#23459;&#35328;)<br />
06. CONTRADICTION<br />
07. Naitemo Ii n da yo(&#27875;&#12356;&#12390;&#12418;&#12356;&#12356;&#12435;&#12384;&#12424;)<br />
Omatsuri Dai Koushin(&#12362;&#31085;&#12426;&#22823;&#34892;&#36914;)<br />
08. Nippon Egao Hyakkei(&#12491;&#12483;&#12509;&#12531;&#31505;&#38996;&#30334;&#26223;)<br />
09. Momoiro Taiko Dodonga Bushi(&#12418;&#12418;&#12356;&#12429;&#22826;&#40723;&#12393;&#12393;&#12435;&#12364;&#31680;)<br />
10. Koko&#9734;Natsu(&#12467;&#12467;&#9734;&#12490;&#12484;)<br />
11. Kimi to Sekai(&#12461;&#12511;&#12392;&#12475;&#12459;&#12452;)<br />
12. Saraba, Itoshiki Kanashimi-tachi Yo(&#12469;&#12521;&#12496;&#12289;&#24859;&#12375;&#12365;&#24754;&#12375;&#12415;&#12383;&#12385;&#12424;)<br />
13. Rodo Sanka(&#21172;&#20685;&#35715;&#27468;)<br />
14. My Dear Fellow<br />
Momoclo Bon Odori(&#12418;&#12418;&#12463;&#12525;&#30406;&#36362;&#12426;)<br />
15. Neo STARGATE<br />
16. LOST CHILD<br />
17. MOON PRIDE<br />
18. Gekko(&#26376;&#34425;)<br />
19. Kono Uta(&#12467;&#12494;&#12454;&#12479;)<br />
20. DNA Rhapsody(DNA&#29378;&#35433;&#26354;)<br />
21. Hashire!(&#36208;&#12428;&#65281;)<br />
&#65308;ENCORE&#65310;<br />
22. Ikuze! Kaito Shojo(&#34892;&#12367;&#12380;&#12387;&#65281;&#24618;&#30423;&#23569;&#22899;)<br />
23. Hagane no Ishi(&#37628;&#12398;&#24847;&#24535;)<br />
24. Kimi no Ato(&#12461;&#12511;&#12494;&#12450;&#12488;)<br />
25. Mouretsu Uchuu Koukyoukyoku Dai 7 Gakushou -Mugen no Ai-(&#29467;&#28872;&#23431;&#23449;&#20132;&#38911;&#26354;&#12539;&#31532;&#19971;&#27005;&#31456;&#12300;&#28961;&#38480;&#12398;&#24859;&#12301;)<br />
<br />
Eizo Tokuten(&#26144;&#20687;&#29305;&#20856;)<br />
Tojin wo Matsuru. Sono Butaiura -Vol.2-(&#26691;&#31070;&#12434;&#31040;&#12427;&#12290;&#12381;&#12398;&#33310;&#21488;&#35023; &#65374;vol.1&#65374;)<br />
<br />
<br />
&#9679;Day2<br />
<br />
Tojinsai no Theme(&#26691;&#31070;&#31085;&#12398;&#12486;&#12540;&#12510;)<br />
overture -Momoiro Clover Z Sanjo!!-(&#65374;&#12418;&#12418;&#12356;&#12429;&#12463;&#12525;&#12540;&#12496;&#12540;Z&#21442;&#19978;&#65281;&#65281;&#65374;)<br />
01. Ame no Tajikarao(&#22825;&#25163;&#21147;&#30007;)<br />
02. Wani to Shampoo(&#12527;&#12491;&#12392;&#12471;&#12515;&#12531;&#12503;&#12540;)<br />
03. DNA Rhapsody(DNA&#29378;&#35433;&#26354;)<br />
04. D&#39; No Junjou(D&#39;&#12398;&#32020;&#24773;)<br />
05. Doudou Heiwa Sengen(&#22530;&#12293;&#24179;&#21644;&#23459;&#35328;)<br />
06. Hagane no Ishi(&#37628;&#12398;&#24847;&#24535;)<br />
07. Naitemo Ii n da yo(&#27875;&#12356;&#12390;&#12418;&#12356;&#12356;&#12435;&#12384;&#12424;)<br />
Omatsuri Dai Koushin(&#12362;&#31085;&#12426;&#22823;&#34892;&#36914;)<br />
08. Nippon Egao Hyakkei(&#12491;&#12483;&#12509;&#12531;&#31505;&#38996;&#30334;&#26223;)<br />
09. Momoiro Taiko Dodonga Bushi(&#12418;&#12418;&#12356;&#12429;&#22826;&#40723;&#12393;&#12393;&#12435;&#12364;&#31680;)<br />
10. Koko&#9734;Natsu(&#12467;&#12467;&#9734;&#12490;&#12484;)<br />
11. Tsuyoku Tsuyoku(&#12484;&#12520;&#12463;&#12484;&#12520;&#12463;)<br />
12. Chai Maxx<br />
13. My Dear Fellow<br />
14. Momoclo no Nippon Banzai!(&#12418;&#12418;&#12463;&#12525;&#12398;&#12491;&#12483;&#12509;&#12531;&#19975;&#27507;&#65281;)<br />
15. Neo STARGATE<br />
16. MOON PRIDE<br />
17. Hashire!(&#36208;&#12428;&#65281;)<br />
18. Kuroi Shumatsu(&#40658;&#12356;&#36913;&#26411;)<br />
19. Kimi no Ato(&#12461;&#12511;&#12494;&#12450;&#12488;)<br />
&#65308;ENCORE&#65310;<br />
20. Ikuze! Kaito Shojo(&#34892;&#12367;&#12380;&#12387;&#65281;&#24618;&#30423;&#23569;&#22899;)<br />
21. PUSH<br />
22. Hai to Diamond(&#28784;&#12392;&#12480;&#12452;&#12516;&#12514;&#12531;&#12489;)<br />
23. Saraba, Itoshiki Kanashimi-tachi Yo(&#12469;&#12521;&#12496;&#12289;&#24859;&#12375;&#12365;&#24754;&#12375;&#12415;&#12383;&#12385;&#12424;)<br />
<br />
Eizo Tokuten(&#26144;&#20687;&#29305;&#20856;)<br />
Tojin wo Matsuru. Sono Butaiura -Vol.2-(&#26691;&#31070;&#12434;&#31040;&#12427;&#12290;&#12381;&#12398;&#33310;&#21488;&#35023; &#65374;vol.2&#65374;)<br />
<br />
<br />
Edition<br />
---------------------------------------------------------<br />
<br />
Limited Edition(&#21021;&#22238;&#38480;&#23450;&#29256;)<br />
<br />
&#12288;KIXM-90191&#65374;90194&#12288;Day1/Day2 LIVE Blu-ray BOX (Blu-ray x 4)<br />
&#12288;KIBM-90496&#65374;90501&#12288;Day1/Day2 LIVE DVD BOX (DVD x 6)<br />
<br />
Regular Edition(&#36890;&#24120;&#29256;)<br />
<br />
&#12288;KIXM-191&#65374;192&#12288;Day1 LIVE Blu-ray (Blu-ray x 2)<br />
&#12288;KIBM-496&#65374;498&#12288;Day1 LIVE DVD (DVD x 3)<br />
&#12288;KIXM-193&#65374;194&#12288;Day2 LIVE Blu-ray (Blu-ray x 2)<br />
&#12288;KIBM-499&#65374;501&#12288;Day2 LIVE DVD (DVD x 3)</div>
                </div>
<div id="comments"></div>
<div id="ajax_tcomments">
<div class="linkbox"><strong>1-10</strong> | <a href="torrents.php?page=2&amp;id=176329" onclick="return loadHtml('tcomments', 'page=2&amp;id=176329');"><strong>11-11</strong></a> | <a href="torrents.php?page=2&amp;id=176329" onclick="return loadHtml('tcomments', 'page=2&amp;id=176329');"><strong>Next &gt;</strong></a> <a href="torrents.php?page=2&amp;id=176329" onclick="return loadHtml('tcomments', 'page=2&amp;id=176329');"><strong> Last &gt;&gt;</strong></a></div><table class="forum_post box vertical_margin" id="post381468">
    <tr class="colhead_dark">
        <td colspan="2">
            <span style="float:left;"><a href='torrents.php?page=1&amp;id=176329#post381468'>#381468</a>
            - <strong><a href="user.php?id=5693">qx123</a>  (<span class="permission_3">Member</span>)</strong>
             8 years, 6 days ago - <a href="#quickpost" onclick="Quote('381468','qx123');">[Quote]</a>
          - <a href="reports.php?action=report&amp;type=Comment&amp;id=381468">[Report]</a>
            </span>
            <span style="float: right;"><a href="#top">[Top]</a></span>
        </td>
    </tr>
    <tr>
        <td class="avatar" valign="top" height="1%">
            <img src='static/common/avatars/default.png' width='150' alt="Default avatar" />
        </td>
        <td class="body" valign="top" rowspan="2">
            <div id="content381468" class="postcontent">
                THank you very much for your sharing!            </div>
            <span id="bar381468" style="margin: 0 auto;"></span>
                                    <div class="signature"></div>
                    </td>
    </tr>
    <tr>
        <td valign="top">
            Joined: 13 years, 5 months ago<br />
            Ratio: <span class="r20">4.80</span><br />
                    Upload: 15.12 TB<br />
            Download: 3.15 TB<br />
        </td>
            </tr>
</table>

<table class="forum_post box vertical_margin" id="post381469">
    <tr class="colhead_dark">
        <td colspan="2">
            <span style="float:left;"><a href='torrents.php?page=1&amp;id=176329#post381469'>#381469</a>
            - <strong><a href="user.php?id=175589">sysyphus</a>  (<span class="permission_3">Member</span>)</strong>
             8 years, 6 days ago - <a href="#quickpost" onclick="Quote('381469','sysyphus');">[Quote]</a>
          - <a href="reports.php?action=report&amp;type=Comment&amp;id=381469">[Report]</a>
            </span>
            <span style="float: right;"><a href="#top">[Top]</a></span>
        </td>
    </tr>
    <tr>
        <td class="avatar" valign="top" height="1%">
            <img src='http://jpopsuki.eu/static/images/avatars/175589.png' width='150' alt="sysyphus's avatar" />
        </td>
        <td class="body" valign="top" rowspan="2">
            <div id="content381469" class="postcontent">
                Thank you so much! <img border='0' src='static/common/smileys/heart.gif' alt='heart.gif' />            </div>
            <span id="bar381469" style="margin: 0 auto;"></span>
                                    <div class="signature"></div>
                    </td>
    </tr>
    <tr>
        <td valign="top">
            Joined: 8 years, 5 months ago<br />
            Ratio: <span class="r10">1.56</span><br />
                    Upload: 1.16 TB<br />
            Download: 761.22 GB<br />
        </td>
            </tr>
</table>

<table class="forum_post box vertical_margin" id="post381473">
    <tr class="colhead_dark">
        <td colspan="2">
            <span style="float:left;"><a href='torrents.php?page=1&amp;id=176329#post381473'>#381473</a>
            - <strong><a href="user.php?id=173187">momoirocoverz</a>  (<span class="permission_4">Power User</span>)</strong>
             8 years, 6 days ago - <a href="#quickpost" onclick="Quote('381473','momoirocoverz');">[Quote]</a>
          - <a href="reports.php?action=report&amp;type=Comment&amp;id=381473">[Report]</a>
            </span>
            <span style="float: right;"><a href="#top">[Top]</a></span>
        </td>
    </tr>
    <tr>
        <td class="avatar" valign="top" height="1%">
            <img src='http://jpopsuki.eu/static/images/avatars/173187.jpg' width='150' alt="momoirocoverz's avatar" />
        </td>
        <td class="body" valign="top" rowspan="2">
            <div id="content381473" class="postcontent">
                <img border='0' src='static/common/smileys/nod.gif' alt='nod.gif' /> Thank you!!!            </div>
            <span id="bar381473" style="margin: 0 auto;"></span>
                                    <div class="signature"></div>
                    </td>
    </tr>
    <tr>
        <td valign="top">
            Joined: 8 years, 10 months ago<br />
            Ratio: <span class="r10">1.64</span><br />
                    Upload: 2.96 TB<br />
            Download: 1.80 TB<br />
        </td>
            </tr>
</table>

<table class="forum_post box vertical_margin" id="post381510">
    <tr class="colhead_dark">
        <td colspan="2">
            <span style="float:left;"><a href='torrents.php?page=1&amp;id=176329#post381510'>#381510</a>
            - <strong><a href="user.php?id=152958">Gaius_Baltar</a>  (<span class="permission_3">Member</span>)</strong>
             8 years, 5 days ago - <a href="#quickpost" onclick="Quote('381510','Gaius_Baltar');">[Quote]</a>
          - <a href="reports.php?action=report&amp;type=Comment&amp;id=381510">[Report]</a>
            </span>
            <span style="float: right;"><a href="#top">[Top]</a></span>
        </td>
    </tr>
    <tr>
        <td class="avatar" valign="top" height="1%">
            <img src='http://imageshack.us/a/img594/8523/fullmetaljackethartmani.jpg' width='150' alt="Gaius_Baltar's avatar" />
        </td>
        <td class="body" valign="top" rowspan="2">
            <div id="content381510" class="postcontent">
                Mega thanks!!!!            </div>
            <span id="bar381510" style="margin: 0 auto;"></span>
                                    <div class="signature"></div>
                    </td>
    </tr>
    <tr>
        <td valign="top">
            Joined: 10 years, 6 months ago<br />
            Ratio: <span class="r50">8.87</span><br />
                    Upload: 88.63 TB<br />
            Download: 9.99 TB<br />
        </td>
            </tr>
</table>

<table class="forum_post box vertical_margin" id="post381528">
    <tr class="colhead_dark">
        <td colspan="2">
            <span style="float:left;"><a href='torrents.php?page=1&amp;id=176329#post381528'>#381528</a>
            - <strong><a href="user.php?id=176127">hinokaren</a>  (<span class="permission_3">Member</span>)</strong>
             8 years, 5 days ago - <a href="#quickpost" onclick="Quote('381528','hinokaren');">[Quote]</a>
          - <a href="reports.php?action=report&amp;type=Comment&amp;id=381528">[Report]</a>
            </span>
            <span style="float: right;"><a href="#top">[Top]</a></span>
        </td>
    </tr>
    <tr>
        <td class="avatar" valign="top" height="1%">
            <img src='http://jpopsuki.eu/static/images/avatars/176127.png' width='150' alt="hinokaren's avatar" />
        </td>
        <td class="body" valign="top" rowspan="2">
            <div id="content381528" class="postcontent">
                Freeleech please <img border='0' src='static/common/smileys/sad.gif' alt='sad.gif' />            </div>
            <span id="bar381528" style="margin: 0 auto;"></span>
                                    <div class="signature"></div>
                    </td>
    </tr>
    <tr>
        <td valign="top">
            Joined: 8 years, 4 months ago<br />
            Ratio: <span class="r10">1.03</span><br />
                    Upload: 176.94 GB<br />
            Download: 171.98 GB<br />
        </td>
            </tr>
</table>

<table class="forum_post box vertical_margin" id="post381551">
    <tr class="colhead_dark">
        <td colspan="2">
            <span style="float:left;"><a href='torrents.php?page=1&amp;id=176329#post381551'>#381551</a>
            - <strong><a href="user.php?id=171385">jink12</a>  (<span class="permission_3">Member</span>)</strong>
             8 years, 5 days ago - <a href="#quickpost" onclick="Quote('381551','jink12');">[Quote]</a>
          - <a href="reports.php?action=report&amp;type=Comment&amp;id=381551">[Report]</a>
            </span>
            <span style="float: right;"><a href="#top">[Top]</a></span>
        </td>
    </tr>
    <tr>
        <td class="avatar" valign="top" height="1%">
            <img src='static/common/avatars/default.png' width='150' alt="Default avatar" />
        </td>
        <td class="body" valign="top" rowspan="2">
            <div id="content381551" class="postcontent">
                Freeleech please            </div>
            <span id="bar381551" style="margin: 0 auto;"></span>
                                    <div class="signature"></div>
                    </td>
    </tr>
    <tr>
        <td valign="top">
            Joined: 9 years, 1 month ago<br />
            Ratio: <span class="r10">1.74</span><br />
                    Upload: 9.24 TB<br />
            Download: 5.31 TB<br />
        </td>
            </tr>
</table>

<table class="forum_post box vertical_margin" id="post381562">
    <tr class="colhead_dark">
        <td colspan="2">
            <span style="float:left;"><a href='torrents.php?page=1&amp;id=176329#post381562'>#381562</a>
            - <strong><a href="user.php?id=55698">ici_jp</a>  (<span class="permission_6">VIP</span>)</strong>
             8 years, 5 days ago - <a href="#quickpost" onclick="Quote('381562','ici_jp');">[Quote]</a>
          - <a href="reports.php?action=report&amp;type=Comment&amp;id=381562">[Report]</a>
            </span>
            <span style="float: right;"><a href="#top">[Top]</a></span>
        </td>
    </tr>
    <tr>
        <td class="avatar" valign="top" height="1%">
            <img src='http://jpopsuki.eu/static/images/avatars/55698.png' width='150' alt="ici_jp's avatar" />
        </td>
        <td class="body" valign="top" rowspan="2">
            <div id="content381562" class="postcontent">
                Thank you very much.<br />
(&#12356;&#12388;&#12418;&#12354;&#12426;&#12364;&#12392;&#12358;&#12372;&#12374;&#12356;&#12414;&#12377;&#12290;)<br />
I do my best for the members of the &quot;jpopsuki&quot;.<br />
(&quot;jpopsuki&quot;&#12398;&#12513;&#12531;&#12496;&#12540;&#12398;&#12383;&#12417;&#12395;&#12364;&#12435;&#12400;&#12426;&#12414;&#12377;&#12290;)<br />
<br />
I have been to all &quot;freeleech&quot; the TV program.<br />
(&#31169;&#12399;&#12289;TV&#30058;&#32068;&#12434;&#20840;&#37096;&quot;freeleech&quot;&#12395;&#12375;&#12390;&#12356;&#12414;&#12377;&#12290;)<br />
I do not have to &quot;freeleech&quot; works that I bought myself.<br />
(&#31169;&#12399;&#33258;&#20998;&#12391;&#36023;&#12387;&#12383;&#20316;&#21697;&#12434;&quot;freeleech&quot;&#12395;&#12375;&#12390;&#12356;&#12414;&#12379;&#12435;&#12290;)<br />
Excuse me.<br />
(&#12377;&#12415;&#12414;&#12379;&#12435;&#12290;)<br />
<br />
The rules of &quot;jpopsuki&quot;, even in the same work,<br />
(&quot;jpopsuki&quot;&#12398;&#12365;&#12414;&#12426;&#12391;&#12399;&#12289;&#21516;&#12376;&#20316;&#21697;&#12391;&#12418;&#12289;)<br />
&quot;FLAC &rarr; MP3&quot; as in, if upload by converting the format,<br />
(&quot;FLAC&rarr;MP3&quot;&#12398;&#12424;&#12358;&#12395;&#12289;&#24418;&#24335;&#12434;&#22793;&#25563;&#12375;&#12390;&#12450;&#12483;&#12503;&#12525;&#12540;&#12489;&#12377;&#12428;&#12400;&#12289;)<br />
It becomes your own point.<br />
(&#12354;&#12394;&#12383;&#33258;&#36523;&#12398;&#12509;&#12452;&#12531;&#12488;&#12395;&#12394;&#12426;&#12414;&#12377;&#12290;)<br />
Therefore, everyone will have kept to be able to participate.<br />
(&#12381;&#12398;&#12383;&#12417;&#12289;&#12415;&#12394;&#12373;&#12414;&#12364;&#21442;&#21152;&#12391;&#12365;&#12427;&#12424;&#12358;&#12395;&#31354;&#12369;&#12390;&#12354;&#12426;&#12414;&#12377;&#12290;)<br />
<br />
The &quot;iso&quot; created, I&#39;ve used the &quot;DVDFab9 v8.1.8.8 all-in-one&quot; and &quot;DVDFab Passkey v8.2.3.2 lifetime&quot;.<br />
(&quot;iso&quot;&#20316;&#25104;&#12395;&#12399;&#12289;&quot;DVDFab9 v8.1.8.8 all-in-one&quot;&#12392;&quot;DVDFab Passkey v8.2.3.2 lifetime&quot;&#12434;&#20351;&#29992;&#12375;&#12414;&#12375;&#12383;&#12290;)<br />
This is the latest analysis technology.<br />
(&#12371;&#12428;&#12399;&#26368;&#26032;&#12398;&#35299;&#26512;&#25216;&#34899;&#12391;&#12377;&#12290;)<br />
But the &quot;Slysoft and CyberLink&quot; company apps, compatibility is I think bad.<br />
(&#12375;&#12363;&#12375;&quot;Slysoft&#12420;CyberLink&quot;&#31038;&#12398;&#12450;&#12503;&#12522;&#12392;&#12399;&#12289;&#30456;&#24615;&#12364;&#24746;&#12356;&#12392;&#24605;&#12356;&#12414;&#12377;&#12290;)                <br /><br />Last edited by
                <a href="user.php?id=55698">ici_jp</a>  on
                2015-02-25 05:42:00            </div>
            <span id="bar381562" style="margin: 0 auto;"></span>
                                    <div class="signature"></div>
                    </td>
    </tr>
    <tr>
        <td valign="top">
            Joined: 13 years, 3 months ago<br />
            Ratio: <span class="r50">86.40</span><br />
                    Upload: 105.96 TB<br />
            Download: 1.23 TB<br />
        </td>
            </tr>
</table>

<table class="forum_post box vertical_margin" id="post381575">
    <tr class="colhead_dark">
        <td colspan="2">
            <span style="float:left;"><a href='torrents.php?page=1&amp;id=176329#post381575'>#381575</a>
            - <strong><a href="user.php?id=172810">OM617</a>  (<span class="permission_4">Power User</span>)</strong>
             8 years, 5 days ago - <a href="#quickpost" onclick="Quote('381575','OM617');">[Quote]</a>
          - <a href="reports.php?action=report&amp;type=Comment&amp;id=381575">[Report]</a>
            </span>
            <span style="float: right;"><a href="#top">[Top]</a></span>
        </td>
    </tr>
    <tr>
        <td class="avatar" valign="top" height="1%">
            <img src='http://jpopsuki.eu/static/images/avatars/172810.jpg' width='150' alt="OM617's avatar" />
        </td>
        <td class="body" valign="top" rowspan="2">
            <div id="content381575" class="postcontent">
                Thank you!            </div>
            <span id="bar381575" style="margin: 0 auto;"></span>
                                    <div class="signature"></div>
                    </td>
    </tr>
    <tr>
        <td valign="top">
            Joined: 8 years, 10 months ago<br />
            Ratio: <span class="r20">2.98</span><br />
                    Upload: 5.39 TB<br />
            Download: 1.81 TB<br />
        </td>
            </tr>
</table>

<table class="forum_post box vertical_margin" id="post381813">
    <tr class="colhead_dark">
        <td colspan="2">
            <span style="float:left;"><a href='torrents.php?page=1&amp;id=176329#post381813'>#381813</a>
            - <strong><a href="user.php?id=33500">Ede</a>  (<span class="permission_3">Member</span>)</strong>
             8 years, 4 days ago - <a href="#quickpost" onclick="Quote('381813','Ede');">[Quote]</a>
          - <a href="reports.php?action=report&amp;type=Comment&amp;id=381813">[Report]</a>
            </span>
            <span style="float: right;"><a href="#top">[Top]</a></span>
        </td>
    </tr>
    <tr>
        <td class="avatar" valign="top" height="1%">
            <img src='static/common/avatars/default.png' width='150' alt="Default avatar" />
        </td>
        <td class="body" valign="top" rowspan="2">
            <div id="content381813" class="postcontent">
                Thanks a lot!            </div>
            <span id="bar381813" style="margin: 0 auto;"></span>
                                    <div class="signature"></div>
                    </td>
    </tr>
    <tr>
        <td valign="top">
            Joined: 13 years, 3 months ago<br />
            Ratio: <span class="r09">0.96</span><br />
            </tr>
</table>

<table class="forum_post box vertical_margin" id="post391562">
    <tr class="colhead_dark">
        <td colspan="2">
            <span style="float:left;"><a href='torrents.php?page=1&amp;id=176329#post391562'>#391562</a>
            - <strong><a href="user.php?id=98698">deadgrandma</a> <img src="static/common/symbols/donor.png" alt="Donor" style="vertical-align: bottom" /> (<span class="permission_6">VIP</span>)</strong>
             (Seiko Watcher) 7 years, 9 months ago - <a href="#quickpost" onclick="Quote('391562','deadgrandma');">[Quote]</a>
          - <a href="reports.php?action=report&amp;type=Comment&amp;id=391562">[Report]</a>
            </span>
            <span style="float: right;"><a href="#top">[Top]</a></span>
        </td>
    </tr>
    <tr>
        <td class="avatar" valign="top" height="1%">
            <img src='http://jpopsuki.eu/static/images/avatars/98698.jpg' width='150' alt="deadgrandma's avatar" />
        </td>
        <td class="body" valign="top" rowspan="2">
            <div id="content391562" class="postcontent">
                OK which one do I grab            </div>
            <span id="bar391562" style="margin: 0 auto;"></span>
                                    <div class="signature"></div>
                    </td>
    </tr>
    <tr>
        <td valign="top">
            Joined: 12 years, 6 months ago<br />
            Ratio: <span class="r50">6.00</span><br />
                    Upload: 3.35 TB<br />
            Download: 572.06 GB<br />
        </td>
            </tr>
</table>

<div class="linkbox"><strong>1-10</strong> | <a href="torrents.php?page=2&amp;id=176329" onclick="return loadHtml('tcomments', 'page=2&amp;id=176329');"><strong>11-11</strong></a> | <a href="torrents.php?page=2&amp;id=176329" onclick="return loadHtml('tcomments', 'page=2&amp;id=176329');"><strong>Next &gt;</strong></a> <a href="torrents.php?page=2&amp;id=176329" onclick="return loadHtml('tcomments', 'page=2&amp;id=176329');"><strong> Last &gt;&gt;</strong></a></div></div>
<div id="ajax_tcomments_loading" style="text-align: center; display: none"><img src="static/styles/layer_cake/images/loading.gif" alt="Loading" /><br />Loading</div>
<h3>Quick Reply</h3>
<div class="box pad" style="padding:20px 10px 10px 10px;">
    <a href="javascript:void(0);" onclick="bbcode_ins('quickpost', 'b')"><img src="static/common/bbc/bold.gif" width="23" height="22" alt="Bold" title="Bold" style="background-image: url(static/common/bbc/bbc_bg.gif);margin: 1px 2px 1px 1px; vertical-align: bottom;" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', 'u')"><img src="static/common/bbc/underline.gif" width="23" height="22" alt="Underlin" title="Underline" style="background-image: url(static/common/bbc/bbc_bg.gif);margin: 1px 2px 1px 1px; vertical-align: bottom;" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', 'i')"><img src="static/common/bbc/italicize.gif" width="23" height="22" alt="Italic" title="Italic" style="background-image: url(static/common/bbc/bbc_bg.gif);margin: 1px 2px 1px 1px; vertical-align: bottom;" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', 's')"><img src="static/common/bbc/strike.gif" width="23" height="22" alt="Strike-Through" title="Strike" style="background-image: url(static/common/bbc/bbc_bg.gif);margin: 1px 2px 1px 1px; vertical-align: bottom;" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', 'img')"><img src="static/common/bbc/img.gif" width="23" height="22" alt="Image" title="Image" style="background-image: url(static/common/bbc/bbc_bg.gif);margin: 1px 2px 1px 1px; vertical-align: bottom;" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', 'url')"><img src="static/common/bbc/url.gif" width="23" height="22" alt="URL" title="URL" style="background-image: url(static/common/bbc/bbc_bg.gif);margin: 1px 2px 1px 1px; vertical-align: bottom;" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', 'youtube')"><img src="static/common/bbc/youtube.gif" width="23" height="22" alt="YouTube" title="YouTube" style="background-image: url(static/common/bbc/bbc_bg.gif);margin: 1px 2px 1px 1px; vertical-align: bottom;" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', 'jptv')"><img src="static/common/bbc/flash.gif" width="23" height="22" alt="JPopsuki TV" title="JPopsuki.tv" style="background-image: url(static/common/bbc/bbc_bg.gif);margin: 1px 2px 1px 1px; vertical-align: bottom;" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', 'pre')"><img src="static/common/bbc/pre.gif" width="23" height="22" alt="Pre-Formated" title="Pre-Formated Text" style="background-image: url(static/common/bbc/bbc_bg.gif);margin: 1px 2px 1px 1px; vertical-align: bottom;" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', 'left')"><img src="static/common/bbc/left.gif" width="23" height="22" alt="Left Alig" title="Left align. Text" style="background-image: url(static/common/bbc/bbc_bg.gif);margin: 1px 2px 1px 1px; vertical-align: bottom;" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', 'center')"><img src="static/common/bbc/center.gif" width="23" height="22" alt="Centered" title="Centered Text" style="background-image: url(static/common/bbc/bbc_bg.gif);margin: 1px 2px 1px 1px; vertical-align: bottom;" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', 'right')"><img src="static/common/bbc/right.gif" width="23" height="22" alt="Right Alig" title="Right align. Text" style="background-image: url(static/common/bbc/bbc_bg.gif);margin: 1px 2px 1px 1px; vertical-align: bottom;" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', 'nfo')"><img src="static/common/bbc/code.gif" width="23" height="22" alt="Code" title="Code or NFO" style="background-image: url(static/common/bbc/bbc_bg.gif);margin: 1px 2px 1px 1px; vertical-align: bottom;" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', 'quote')"><img src="static/common/bbc/quote.gif" width="23" height="22" alt="Quote" title="Quote" style="background-image: url(static/common/bbc/bbc_bg.gif);margin: 1px 2px 1px 1px; vertical-align: bottom;" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', 'size')"><img src="static/common/bbc/size.gif" width="23" height="22" alt="Font Size" title="Font Size (1-10)" style="background-image: url(static/common/bbc/bbc_bg.gif);margin: 1px 2px 1px 1px; vertical-align: bottom;" /></a>
<select onchange="bbcode_ins('quickpost', value)"><option value="" selected="selected">Change Color</option>
                                                        <option value="black">Black</option>
                                                        <option value="white">White</option>
                                                        <option value="silver">Silver</option>
                                                        <option value="red">Red</option>
                                                        <option value="yellow">Yellow</option>
                                                        <option value="pink">Pink</option>
                                                        <option value="fuchsia">Fuchsia</option>
                                                        <option value="green">Green</option>
                                                        <option value="olive">Olive</option>
                                                        <option value="orange">Orange</option>
                                                        <option value="purple">Purple</option>
                                                        <option value="aqua">Aqua</option>
                                                        <option value="blue">Blue</option>
                                                        <option value="grey">Grey</option>
                                                        <option value="brown">Brown</option>
                                                        <option value="teal">Teal</option>
                                                        <option value="navy">Navy</option>
                                                        <option value="maroon">Maroon</option>
                                                        <option value="lime">LimeGreen</option>
        </select>
<br />
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :)')" /><img src="static/common/smileys/smile.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :(')" /><img src="static/common/smileys/sad.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' ;)')" /><img src="static/common/smileys/wink.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :D')" /><img src="static/common/smileys/biggrin.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :|')" /><img src="static/common/smileys/blank.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :P')" /><img src="static/common/smileys/tongue.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :angry:')" /><img src="static/common/smileys/angry.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' ;_;')" /><img src="static/common/smileys/crying.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :lol:')" /><img src="static/common/smileys/laughing.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :blush:')" /><img src="static/common/smileys/blush.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :frown:')" /><img src="static/common/smileys/frown.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :cool:')" /><img src="static/common/smileys/cool.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :unsure:')" /><img src="static/common/smileys/hmm.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :no:')" /><img src="static/common/smileys/no.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :nod:')" /><img src="static/common/smileys/nod.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :ohno:')" /><img src="static/common/smileys/ohnoes.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :omg:')" /><img src="static/common/smileys/omg.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :O')" /><img src="static/common/smileys/ohshit.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :shifty:')" /><img src="static/common/smileys/shifty.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :sick:')" /><img src="static/common/smileys/sick.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :evil:')" /><img src="static/common/smileys/evil.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :ninja:')" /><img src="static/common/smileys/ninja.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :wtf:')" /><img src="static/common/smileys/wtf.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :wub:')" /><img src="static/common/smileys/wub.gif" align="bottom" alt="Smiley" title="Smiley" /></a>
<a href="javascript:void(0);" onclick="bbcode_ins('quickpost', ' :loveflac:')" /><img src="static/common/smileys/loveflac.gif" align="bottom" alt="Smiley" title="Smiley" /></a>

<br /><br />
    <form id="quickpostform" action="" method="post" style="display: block; text-align: center; padding: 10px;">
        <div id="quickreplypreview" class="box" style="text-align: left; display: none; padding: 10px;"></div>
        <div id="quickreplytext">
            <input type="hidden" name="action" value="reply" />
            <input type="hidden" name="thread" value="176329" />
            <textarea id="quickpost" name="body"  style="width:100%" rows="8"></textarea> <br />
        </div>
        <div id="quickreplybuttons">
            <input type="button" value="Preview" onclick="QuickPreview('Preview','Editor','Submit');" />
            <input type="submit" value="Submit" />
        </div>
    </form>
</div>

        </div>
</div>
</div>
<div id="footer">
        <p>Site and design &copy; 2023 JPopsuki 2.0</p>
        <p>This page was created in 0.01540 second(s) on <span title="Just now">Mar 02 2023, 19:31</span></p>
        <p>

                <a href="http://en.wikipedia.org/wiki/Load_(computing)" target="_blank">Load average</a>:
                1.43, 0.97, 0.81                <br />
                (Average over 1 minute, 5 minutes and 15 minutes
 on 8 cores. Load is spiked by <a href="http://en.wikipedia.org/wiki/Cron" target="_blank">cron</a> every 15 minutes.)
        </p>
        <p>Powered by <a href="http://jpopsuki.eu/static/images/users/774/503x.jpg">Small Horse</a></p>
<!--    <script type="text/javascript" src="https://widgets.amung.us/colored.js"></script><script type="text/javascript">WAU_colored('l8tchbw95e38', 'e3f4fd000000')</script> -->
        <script type="text/javascript" src="https://widgets.amung.us/pro.js"></script>
        <script type="text/javascript" id="wau_scr_30b716e2">
        wau_add('d0t8', '30b716e2')
        </script>
        <noscript>
                <img src="https://whos.amung.us/piwidget/d0t8/" />
        </noscript>

</div>

</div>
<div id="lightbox" class="lightbox"></div>
<div id="curtain" class="curtain"></div>

<!-- Extra divs, for stylesheet developers to add imagery -->
<div id="extra1"><span></span></div>
<div id="extra2"><span></span></div>
<div id="extra3"><span></span></div>
<div id="extra4"><span></span></div>
<div id="extra5"><span></span></div>
<div id="extra6"><span></span></div>
</body>
</html>"""

    group_description = """2014.07.26, 27 Kanagawa Nissan Stadium
http://www.momoclo.net/discography/dvd32.html
http://www.cdjapan.co.jp/product/KIXM-90191


Setlist
---------------------------------------------------------

●Day1

Tojinsai no Theme(桃神祭のテーマ)
overture -Momoiro Clover Z Sanjo!!-(～ももいろクローバーZ参上！！～)
01. Ame no Tajikarao(天手力男)
02. Wani to Shampoo(ワニとシャンプー)
03. Kuroi Shumatsu(黒い週末)
04. D' No Junjou(D'の純情)
05. Doudou Heiwa Sengen(堂々平和宣言)
06. CONTRADICTION
07. Naitemo Ii n da yo(泣いてもいいんだよ)
Omatsuri Dai Koushin(お祭り大行進)
08. Nippon Egao Hyakkei(ニッポン笑顔百景)
09. Momoiro Taiko Dodonga Bushi(ももいろ太鼓どどんが節)
10. Koko☆Natsu(ココ☆ナツ)
11. Kimi to Sekai(キミとセカイ)
12. Saraba, Itoshiki Kanashimi-tachi Yo(サラバ、愛しき悲しみたちよ)
13. Rodo Sanka(労働讃歌)
14. My Dear Fellow
Momoclo Bon Odori(ももクロ盆踊り)
15. Neo STARGATE
16. LOST CHILD
17. MOON PRIDE
18. Gekko(月虹)
19. Kono Uta(コノウタ)
20. DNA Rhapsody(DNA狂詩曲)
21. Hashire!(走れ！)
＜ENCORE＞
22. Ikuze! Kaito Shojo(行くぜっ！怪盗少女)
23. Hagane no Ishi(鋼の意志)
24. Kimi no Ato(キミノアト)
25. Mouretsu Uchuu Koukyoukyoku Dai 7 Gakushou -Mugen no Ai-(猛烈宇宙交響曲・第七楽章「無限の愛」)

Eizo Tokuten(映像特典)
Tojin wo Matsuru. Sono Butaiura -Vol.2-(桃神を祀る。その舞台裏 ～vol.1～)


●Day2

Tojinsai no Theme(桃神祭のテーマ)
overture -Momoiro Clover Z Sanjo!!-(～ももいろクローバーZ参上！！～)
01. Ame no Tajikarao(天手力男)
02. Wani to Shampoo(ワニとシャンプー)
03. DNA Rhapsody(DNA狂詩曲)
04. D' No Junjou(D'の純情)
05. Doudou Heiwa Sengen(堂々平和宣言)
06. Hagane no Ishi(鋼の意志)
07. Naitemo Ii n da yo(泣いてもいいんだよ)
Omatsuri Dai Koushin(お祭り大行進)
08. Nippon Egao Hyakkei(ニッポン笑顔百景)
09. Momoiro Taiko Dodonga Bushi(ももいろ太鼓どどんが節)
10. Koko☆Natsu(ココ☆ナツ)
11. Tsuyoku Tsuyoku(ツヨクツヨク)
12. Chai Maxx
13. My Dear Fellow
14. Momoclo no Nippon Banzai!(ももクロのニッポン万歳！)
15. Neo STARGATE
16. MOON PRIDE
17. Hashire!(走れ！)
18. Kuroi Shumatsu(黒い週末)
19. Kimi no Ato(キミノアト)
＜ENCORE＞
20. Ikuze! Kaito Shojo(行くぜっ！怪盗少女)
21. PUSH
22. Hai to Diamond(灰とダイヤモンド)
23. Saraba, Itoshiki Kanashimi-tachi Yo(サラバ、愛しき悲しみたちよ)

Eizo Tokuten(映像特典)
Tojin wo Matsuru. Sono Butaiura -Vol.2-(桃神を祀る。その舞台裏 ～vol.2～)


Edition
---------------------------------------------------------

Limited Edition(初回限定版)

　KIXM-90191～90194　Day1/Day2 LIVE Blu-ray BOX (Blu-ray x 4)
　KIBM-90496～90501　Day1/Day2 LIVE DVD BOX (DVD x 6)

Regular Edition(通常版)

　KIXM-191～192　Day1 LIVE Blu-ray (Blu-ray x 2)
　KIBM-496～498　Day1 LIVE DVD (DVD x 3)
　KIXM-193～194　Day2 LIVE Blu-ray (Blu-ray x 2)
　KIBM-499～501　Day2 LIVE DVD (DVD x 3)"""

    with open("group-edit-page-176329", "r") as group_edit_page_176329:
        requests_mock.post("https://jpopsuki.eu/login.php", text=LoginParameters.jps_success)  # Mock the initial login with requestsloginsession()
        requests_mock.get("https://jpopsuki.eu/torrents.php?action=editgroup&groupid=176329", text=group_edit_page_176329.read())
        jps_group_info = GetGroupData(jps_group_id, jps_group_page_text)

    assert jps_group_info.category == "DVD"
    assert jps_group_info.artist == ["Momoiro Clover Z"]
    assert jps_group_info.date == "20150225"
    assert jps_group_info.title == "Momoclo Natsu no Baka Sawagi 2014 Nissan Stadium Taikai ~Tojinsai~"
    assert jps_group_info.originalartist == "\u3082\u3082\u3044\u308d\u30af\u30ed\u30fc\u30d0\u30fcZ"
    assert jps_group_info.imagelink == "https://jpopsuki.eu/static/images/torrents/176329.jpg"
    assert jps_group_info.tagsall == "japanese,pop,female.vocalist,idol"
    assert jps_group_info.contribartists == {}
    torrent_table_start = r'<tbody><tr class="colhead_dark">\n                                <td width="80%">'
    assert re.match(fr'^{torrent_table_start}', jps_group_info.torrent_table)
    assert jps_group_info.groupdescription == group_description


def collect_data():
    """
    Use this def to manually collect data for use in tests
    """

    jps_page = jpopsuki("https://jpopsuki.eu/torrents.php?action=editgroup&groupid=176329")
    with open("edit-page-text176329", "w") as file:
        file.write(jps_page.text)


if __name__ == "__main__":
    collect_data()
