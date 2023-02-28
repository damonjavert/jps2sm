"""
Run tests got get_release_data()
"""
import pytest

from jps2sm.get_data import get_release_data

def test_get_release_data_group_111284() -> None:
    """
    Test for group 11128
    """
    torrent_ids_whole_group = []
    torrent_ids_mp3_320 = ['147830']
    torrent_ids_flac_lossless_cd = ['148289']

    torrent_table = """
    <tbody><tr class="colhead_dark">
                                <td width="80%"><strong>Torrents</strong></td>
                                <td><strong>Size</strong></td>
                                <td class="sign"><img alt="Snatches" src="static/styles/layer_cake/images/snatched.png" title="Snatches"/></td>
                                <td class="sign"><img alt="Seeders" src="static/styles/layer_cake/images/seeders.png" title="Seeders"/></td>
                                <td class="sign"><img alt="Leechers" src="static/styles/layer_cake/images/leechers.png" title="Leechers"/></td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=147830&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=147830" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('147830');">» MP3 / 320 / CD</a>
                                </td>
                                <td class="nobr">340.05 MB</td>
                                <td>3,651</td>
                                <td>14</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_147830">
                <td colspan="5">

                                                        <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">11.01</span><br/>
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=151382">kiritani_chan</a>  on <span title="10 years, 6 months, 2 weeks ago">Aug 11 2012, 17:58</span>                     </blockquote>
                                                                                <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>COVER 1830m.jpg</td><td>288.73 KB</td></tr><tr><td>Disc 1/01 ファーストラビット.mp3</td><td>11.02 MB</td></tr><tr><td>Disc 1/02 黄金センタ ー.mp3</td><td>8.77 MB</td></tr><tr><td>Disc 1/03 ミニスカートの妖精.mp3</td><td>9.14 MB</td></tr><tr><td>Disc 1/04 上からマリコ.mp3</td><td>10.66 MB</td></tr><tr><td>Disc 1/05 ア ンチ.mp3</td><td>9.57 MB</td></tr><tr><td>Disc 1/06 檸檬の年頃.mp3</td><td>9.16 MB</td></tr><tr><td>Disc 1/07 恋愛総選挙.mp3</td><td>8.08 MB</td></tr><tr><td>Disc 1/08 野菜占い.mp3</td><td>8.81 MB</td></tr><tr><td>Disc 1/09 Everyday、カチューシャ.mp3</td><td>12.00 MB</td></tr><tr><td>Disc 1/10 走れ!ペンギン.mp3</td><td>9.30 MB</td></tr><tr><td>Disc 1/11 ロマンスかくれんぼ.mp3</td><td>7.83 MB</td></tr><tr><td>Disc 1/12 蕾たち.mp3</td><td>8.53 MB</td></tr><tr><td>Disc 1/13 ユングやフロイトの場合.mp3</td><td>10.28 MB</td></tr><tr><td>Disc 1/14 フライングケット.mp3</td><td>9.76 MB</td></tr><tr><td>Disc 1/15 風は吹いている.mp3</td><td>8.49 MB</td></tr><tr><td>Disc 1/16 桜の木になろう.mp3</td><td>12.63 MB</td></tr><tr><td>Disc 1/17 GIVE　ME　FIVE.mp3</td><td>11.46 MB</td></tr><tr><td>Disc 2/01 Hate.mp3</td><td>7.10 MB</td></tr><tr><td>Disc 2/02 プラスティックの唇.mp3</td><td>9.53 MB</td></tr><tr><td>Disc 2/03 思い出のほとんど.mp3</td><td>15.37 MB</td></tr><tr><td>Disc 2/04 家出の夜.mp3</td><td>11.12 MB</td></tr><tr><td>Disc 2/05 スキャンダラスに行こう!.mp3</td><td>7.79 MB</td></tr><tr><td>Disc 2/06 ノーカン.mp3</td><td>9.91 MB</td></tr><tr><td>Disc 2/07 アボガドじゃねーし・・・.mp3</td><td>9.18 MB</td></tr><tr><td>Disc 2/08 直角Sunshine.mp3</td><td>9.13 MB</td></tr><tr><td>Disc 2/09 僕たちは　今　話し合うべきなんだ.mp3</td><td>10.09 MB</td></tr><tr><td>Disc 2/10 さくらんぼと孤独.mp3</td><td>10.66 MB</td></tr><tr><td>Disc 2/11 大事な時間.mp3</td><td>10.09 MB</td></tr><tr><td>Disc 2/12 いつか見た海の底.mp3</td><td>9.01 MB</td></tr><tr><td>Disc 2/13 ぐーぐーおなか.mp3</td><td>9.21 MB</td></tr><tr><td>Disc 2/14 やさしさの地図.mp3</td><td>10.15 MB</td></tr><tr><td>Disc 2/15 行ってらっしゃい.mp3</td><td>12.50 MB</td></tr><tr><td>Disc 2/16 青空よ　寂しくないか .mp3</td><td>11.11 MB</td></tr><tr><td>Disc 2/17 桜の花びらたち　前田敦子ソロ.mp3</td><td>12.36 MB</td></tr></tbody></table>                  Peer List: (<a href="#" id="swapPeer_147830" onclick="return swapPeerList('147830', '356569986', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_147830" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_147830" onclick="return swapSnatchList('147830', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_147830" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=147982&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=147982" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('147982');">» MKV / DVD</a>
                                </td>
                                <td class="nobr">2.28 GB</td>
                                <td>305</td>
                                <td>0</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_147982">
                <td colspan="5">
                                <div id="linkbox" style="text-align: center">
                            <form action="" method="post">
                                <input id="action" name="action" type="hidden" value="reseed"/>
                                <input id="gid" name="gid" type="hidden" value="111284"/>
                                <input id="tid" name="tid" type="hidden" value="147982"/>
                                                                <input id="reseed" name="reseed" type="submit" value="Request a reseed"/>
                                                            </form>
                    </div>

                                                        <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">11.01</span><br/>
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=151382">kiritani_chan</a>  on <span title="10 years, 6 months, 2 weeks ago">Aug 13 2012, 02:20</span>                     <br/>Last active: <span title="2 years, 2 weeks, 5 days ago">Feb 09 2021, 04:33</span>                                   </blockquote>
                                                                                <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>Everyday、カチューシャ 振り付け映像 ＜230ver.＞/1A. Everyday、カチューシャ センター上カメラVer.mkv</td><td>33.84 MB</td></tr><tr><td>Everyday、カチューシャ 振り付け映像 ＜230ver.＞/1B. Everyday、カチューシャ ライトカメラVer.mkv</td><td>52.77 MB</td></tr><tr><td>Everyday、カチューシャ 振り付け映像 ＜230ver.＞/1C. Everyday、カチューシャ センターカメラVer.mkv</td><td>64.71 MB</td></tr><tr><td>Everyday、カチューシャ 振り付け映像 ＜230ver.＞/1D. Everyday、カチューシャ レフトカメラVer.mkv</td><td>52.55 MB</td></tr><tr><td>Everyday、カチューシャ 振り付け映像 ＜230ver.＞/1E. Everyday、カチューシャ マルチアングルVer (8方向視点).mkv</td><td>319.92 MB</td></tr><tr><td>Everyday、カ チューシャ 振り付け映像 ＜230ver.＞/1F. Everyday、カチューシャ １人Ver.mkv</td><td>30.45 MB</td></tr><tr><td>Everyday、カチューシャ 振り付け映像 ＜230ver.＞/1G. Everyday、カチュー シャ １人バクショットVer.mkv</td><td>26.11 MB</td></tr><tr><td>フライングゲット 振り付け映像 ＜230ver.＞/2A. フライングゲット センター上カメラVer.mkv</td><td>37.44 MB</td></tr><tr><td>フライングゲット 振り付け映像 ＜230ver.＞/2B. フライングゲット ライトカメラVer.mkv</td><td>53.95 MB</td></tr><tr><td>フライングゲット 振り付け映像 ＜230ver.＞/2C. フライングゲ ット センターカメラVer.mkv</td><td>65.02 MB</td></tr><tr><td>フライングゲット 振り付け映像 ＜230ver.＞/2D. フライングゲット レフトカメラVer.mkv</td><td>47.30 MB</td></tr><tr><td>フライングゲット 振り付け映像 ＜230ver.＞/2E. フライングゲット マルチアングルVer (8方向視点).mkv</td><td>322.85 MB</td></tr><tr><td>フライングゲット 振り付け映像 ＜230ver.＞/2F. フライングゲット １人Ver.mkv</td><td>29.43 MB</td></tr><tr><td>フライングゲット 振り付け映像 ＜230ver.＞/2G. フライングゲット １人バクショットVer.mkv</td><td>24.80 MB</td></tr><tr><td>上からマリコ 振り付け映像 ＜230ver.＞/4A. 上からマリコ センター上カメラVer.mkv</td><td>35.05 MB</td></tr><tr><td>上からマリコ 振り付け映像 ＜230ver.＞/4B. 上からマリコ ライトカメラVer.mkv</td><td>56.90 MB</td></tr><tr><td>上からマリコ 振り付け映像 ＜230ver.＞/4C. 上からマリコ センターカメラVer.mkv</td><td>66.57 MB</td></tr><tr><td>上からマリコ 振り付け映像  ＜230ver.＞/4D. 上からマリコ レフトカメラVer.mkv</td><td>55.43 MB</td></tr><tr><td>上からマリコ 振り付け映像 ＜230ver.＞/4E. 上からマリコ マルチアングルVer (8方向視点).mkv</td><td>328.77 MB</td></tr><tr><td>上からマリコ 振り付け映像 ＜230ver.＞/4F. 上からマリコ １人Ver.mkv</td><td>26.83 MB</td></tr><tr><td>上からマリコ 振り付け映像 ＜230ver.＞/4G. 上からマリコ １人バクショットVer.mkv</td><td>21.39 MB</td></tr><tr><td>風は吹いている 振り付け映像 ＜230ver.＞/3A. 風は吹いている センター上カメラVer.mkv</td><td>34.16 MB</td></tr><tr><td>風は吹いている 振り付け映像 ＜230ver.＞/3B. 風は吹いている ライトカメラVer.mkv</td><td>56.17 MB</td></tr><tr><td>風は吹いている 振り付け映像 ＜230ver.＞/3C. 風は吹いている センターカメラVer.mkv</td><td>61.99 MB</td></tr><tr><td>風は吹いている 振り付け映像 ＜230ver.＞/3D. 風は吹いている レフトカメラVer.mkv</td><td>55.45 MB</td></tr><tr><td>風は吹いている 振り付け映像 ＜230ver.＞/3E. 風は吹いている マルチアングルVer (8方向視点).mkv</td><td>321.58 MB</td></tr><tr><td>風は吹いている 振り付け映像 ＜230ver.＞/3F. 風は吹いている １人Ver.mkv</td><td>29.05 MB</td></tr><tr><td>風は吹いている 振り付け映像 ＜230ver.＞/3G. 風は吹いている １人バクショットVer.mkv</td><td>24.81 MB</td></tr></tbody></table>                   Peer List: (<a href="#" id="swapPeer_147982" onclick="return swapPeerList('147982', '2448738226', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_147982" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_147982" onclick="return swapSnatchList('147982', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_147982" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=151631&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=151631" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('151631');">» ISO / Lossless / DVD</a>
                                </td>
                                <td class="nobr">6.65 GB</td>
                                <td>219</td>
                                <td>3</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_151631">
                <td colspan="5">

                                                        <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">11.00</span><br/>
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=151064">paul_167</a>  on <span title="10 years, 5 months, 2 weeks ago">Sep 11 2012, 17:06</span>                          </blockquote>
                                                                                <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>AKB48 1830m DVD.iso</td><td>6.65 GB</td></tr></tbody></table>                  Peer List: (<a href="#" id="swapPeer_151631" onclick="return swapPeerList('151631', '7135860736', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_151631" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_151631" onclick="return swapSnatchList('151631', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_151631" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=484250&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=484250" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('484250');">» FLAC / 96-24 / WEB / Hi-Res - 2020</a>
                                </td>
                                <td class="nobr">4.81 GB</td>
                                <td>66</td>
                                <td>5</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_484250">
                <td colspan="5">

                                                        <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">11.00</span><br/>
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=182621">applevoice</a>  on <span title="1 year, 10 months, 1 day ago">Apr 28 2021, 04:32</span>                           </blockquote>
                                        <blockquote>mora<br/>
<a href="https://mora.jp/package/43000014/NOHR-218_F/" target="_blank">https://mora.jp/package/43000014/NOHR-218_F/</a></blockquote>                                    <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>01 ファースト・ラビット.flac</td><td>159.60 MB</td></tr><tr><td>02 黄金センター(歌 team研究生).flac</td><td>127.19 MB</td></tr><tr><td>03 ミニスカートの妖精(伊豆田莉奈、サイード横田絵玲奈、平田梨奈).flac</td><td>132.47 MB</td></tr><tr><td>04 上からマリコ.flac</td><td>154.43 MB</td></tr><tr><td>05 アンチ(歌 team研究生).flac</td><td>138.76 MB</td></tr><tr><td>06 檸檬の年頃(小林茉里奈、名取稚菜、佐々木優佳 里、武藤十夢).flac</td><td>132.74 MB</td></tr><tr><td>07 恋愛総選挙(YM7 高城亜樹、河西智美、小森美果、佐藤すみれ、宮崎美穂、竹内美宥、指原莉乃).flac</td><td>117.23 MB</td></tr><tr><td>08 野菜占い.flac</td><td>127.78 MB</td></tr><tr><td>09 Everyday、カチューシャ.flac</td><td>173.71 MB</td></tr><tr><td>10 走れ!ペンギン(歌 team 4).flac</td><td>134.74 MB</td></tr><tr><td>11 ロマンスかくれんぼ(大森美優).flac</td><td>113.65 MB</td></tr><tr><td>12 蕾たち(歌 Team 4+研究生).flac</td><td>123.62 MB</td></tr><tr><td>13 ユングやフロイトの 場合(歌 スペシャルガールズC).flac</td><td>148.98 MB</td></tr><tr><td>14 フライングゲット.flac</td><td>141.39 MB</td></tr><tr><td>15 風は吹いている.flac</td><td>123.13 MB</td></tr><tr><td>16 桜の木になろう.flac</td><td>182.86 MB</td></tr><tr><td>17 GIVE ME FIVE!.flac</td><td>165.91 MB</td></tr><tr><td>18 Hate(Team A).flac</td><td>103.06 MB</td></tr><tr><td>19 プラスティックの唇(篠田麻里子).flac</td><td>138.05 MB</td></tr><tr><td>20 思い出のほとんど(高橋みなみ、前田敦子).flac</td><td>222.28 MB</td></tr><tr><td>21 家出の夜(Team K).flac</td><td>160.98 MB</td></tr><tr><td>22 スキャンダラスに行こう! (小嶋陽菜、大島優子).flac</td><td>112.96 MB</td></tr><tr><td>23 ノーカン(Team B).flac</td><td>143.54 MB</td></tr><tr><td>24 アボガドじゃね～し…(渡辺麻友、指原莉乃).flac</td><td>132.99 MB</td></tr><tr><td>25 直角Sunshine(Team 4).flac</td><td>132.34 MB</td></tr><tr><td>26 僕たちは 今 話し合うべきなんだ(板野友美、柏木由紀).flac</td><td>146.12 MB</td></tr><tr><td>27 さくらんぼと孤独(研究生).flac</td><td>154.48 MB</td></tr><tr><td>28 大事な時間(小嶋 陽菜、篠田麻里子、高橋みなみ、前田敦子、板野友美、大島優子、柏木由紀、渡辺麻友).flac</td><td>146.16 MB</td></tr><tr><td>29 いつか見た海の底(Up and coming girls).flac</td><td>130.65 MB</td></tr><tr><td>30 ぐ～ぐ～おなか(岩佐美咲、前田敦子、前田亜美、仁藤萌乃、藤江れいな、石田晴香、小森美果、佐藤亜美菜、佐藤すみれ).flac</td><td>133.46 MB</td></tr><tr><td>31 やさしさの地図(篠田麻里子、高橋みなみ、横山由依、柏木由紀、入山杏奈、加藤玲奈、島崎遥香、木崎ゆりあ、城 恵理子、児玉 遥).flac</td><td>147.03 MB</td></tr><tr><td>32 行ってらっしゃい(小嶋陽菜、篠田麻里子、高城亜樹、高橋みなみ、前田敦子、板野友美、大島優子、峯岸みなみ、横山由依、柏木由紀、渡辺麻友、指原莉乃).flac</td><td>180.93 MB</td></tr><tr><td>33 青空よ  寂しくないか (AKB48+SKE48+NMB48+HKT48).flac</td><td>160.94 MB</td></tr><tr><td>34 桜の花びら ～前田敦子 solo ver.～.flac</td><td>178.92 MB</td></tr><tr><td>cover.jpg</td><td>68.89 KB</td></tr><tr><td>sleeve/cover big.jpg</td><td>2.15 MB</td></tr><tr><td>sleeve/cover mid.jpg</td><td>135.19 KB</td></tr></tbody></table>                    Peer List: (<a href="#" id="swapPeer_484250" onclick="return swapPeerList('484250', '5164653305', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_484250" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_484250" onclick="return swapSnatchList('484250', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_484250" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=148289&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=148289" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('148289');">» FLAC / Lossless / CD</a>
                                </td>
                                <td class="nobr">1.08 GB</td>
                                <td>728</td>
                                <td>11</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_148289">
                <td colspan="5">

                                                        <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">11.01</span><br/>
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=99098">liziyumai</a>  on <span title="10 years, 6 months, 2 weeks ago">Aug 15 2012, 08:30</span>                          </blockquote>
                                                                                <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>DISC1/01   AKB48   ファースト・ラビット.flac</td><td>36.21 MB</td></tr><tr><td>DISC1/02   AKB48   黄金センター.flac</td><td>29.38 MB</td></tr><tr><td>DISC1/03   AKB48   ミニスカートの妖精.flac</td><td>32.22 MB</td></tr><tr><td>DISC1/04   AKB48   上からマリコ.flac</td><td>36.02 MB</td></tr><tr><td>DISC1/05   AKB48   アンチ.flac</td><td>31.79 MB</td></tr><tr><td>DISC1/06   AKB48   檸檬の年頃.flac</td><td>28.51 MB</td></tr><tr><td>DISC1/07   AKB48   恋愛総選挙.flac</td><td>29.41 MB</td></tr><tr><td>DISC1/08   AKB48   野菜占い.flac</td><td>29.55 MB</td></tr><tr><td>DISC1/09   AKB48   Everyday、カチューシャ.flac</td><td>40.99 MB</td></tr><tr><td>DISC1/10   AKB48   走れ!ペンギン.flac</td><td>31.42 MB</td></tr><tr><td>DISC1/11   AKB48   ロマンスかくれんぼ.flac</td><td>22.81 MB</td></tr><tr><td>DISC1/12   AKB48   蕾たち.flac</td><td>29.07 MB</td></tr><tr><td>DISC1/13   AKB48   ユングやフロイトの場合.flac</td><td>31.87 MB</td></tr><tr><td>DISC1/14   AKB48   フライングケット.flac</td><td>34.08 MB</td></tr><tr><td>DISC1/15   AKB48    風は吹いている.flac</td><td>29.52 MB</td></tr><tr><td>DISC1/16   AKB48   桜の木になろう.flac</td><td>37.02 MB</td></tr><tr><td>DISC1/17   AKB48   GIVE　ME　FIVE.flac</td><td>40.24 MB</td></tr><tr><td>DISC1/AKB48   1830m DISC1.m3u</td><td>1.20 KB</td></tr><tr><td>DISC2/01   ＡＫＢ４８   Ｈａｔｅ.flac</td><td>23.47 MB</td></tr><tr><td>DISC2/02   ＡＫＢ４８    プラスッティックの唇.flac</td><td>33.28 MB</td></tr><tr><td>DISC2/03   ＡＫＢ４８   思い出のほとんど.flac</td><td>44.76 MB</td></tr><tr><td>DISC2/04   ＡＫＢ４８   家出の夜.flac</td><td>38.04 MB</td></tr><tr><td>DISC2/05   ＡＫＢ４８   スキャンダラスに行こう！.flac</td><td>26.21 MB</td></tr><tr><td>DISC2/06   ＡＫＢ４８   ノーカン.flac</td><td>34.49 MB</td></tr><tr><td>DISC2/07   ＡＫＢ４８   アボカドじゃね～し・・・.flac</td><td>30.74 MB</td></tr><tr><td>DISC2/08   ＡＫＢ４８   直角Ｓunshine.flac</td><td>30.90 MB</td></tr><tr><td>DISC2/09   ＡＫＢ４８   僕たちは　　今　話し合うべきなんだ.flac</td><td>29.69 MB</td></tr><tr><td>DISC2/10   ＡＫＢ４８   さくらんぼと孤独.flac</td><td>31.36 MB</td></tr><tr><td>DISC2/11   ＡＫＢ４８   大事な時間.flac</td><td>29.22 MB</td></tr><tr><td>DISC2/12   ＡＫＢ４８   いつか見た海の底.flac</td><td>31.24 MB</td></tr><tr><td>DISC2/13   ＡＫＢ４８   ぐ～ぐ ～おなか.flac</td><td>27.13 MB</td></tr><tr><td>DISC2/14   ＡＫＢ４８   やさしさの地図.flac</td><td>35.05 MB</td></tr><tr><td>DISC2/15   ＡＫＢ４８   行ってらしゃい.flac</td><td>37.83 MB</td></tr><tr><td>DISC2/16   ＡＫＢ４８   青空よ　寂しくないか？.flac</td><td>35.27 MB</td></tr><tr><td>DISC2/17   ＡＫＢ４８   桜の花びら～前田敦子solo ver.～.flac</td><td>33.93 MB</td></tr><tr><td>DISC2/ＡＫＢ４８   １８３０ｍ　ＤＩＳＣ２.m3u</td><td>745.00 B</td></tr><tr><td>cover.jpg</td><td>708.08 KB</td></tr></tbody></table>                  Peer List: (<a href="#" id="swapPeer_148289" onclick="return swapPeerList('148289', '1157031130', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_148289" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_148289" onclick="return swapSnatchList('148289', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_148289" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=266605&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=266605" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('266605');">» ALAC / Lossless / CD</a>
                                </td>
                                <td class="nobr">1.14 GB</td>
                                <td>19</td>
                                <td>1</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_266605">
                <td colspan="5">

                                                        <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">11.01</span><br/>
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=182468">DanielTwo2</a>  on <span title="7 years, 2 months, 4 weeks ago">Dec 01 2015, 11:47</span>                         </blockquote>
                                        <blockquote>Ripped and encoded with iTunes 11.3.1.2<br/>
Pardon for the mess lol.<br/>
<br/>
I forgot to provide the .jpg file for cover, sorry for that <img alt="sad.gif" border="0" src="static/common/smileys/sad.gif"/></blockquote>                                    <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>1 01 Hate.m4a</td><td>25.26 MB</td></tr><tr><td>1 01 ファースト・ラビット.m4a</td><td>38.14 MB</td></tr><tr><td>1 02 プラスティックの唇.m4a</td><td>35.07 MB</td></tr><tr><td>1 02 黄金センター.m4a</td><td>31.09 MB</td></tr><tr><td>1 03 ミニスカートの妖精.m4a</td><td>33.89 MB</td></tr><tr><td>1 03 思い出のほとんど.m4a</td><td>47.21 MB</td></tr><tr><td>1 04 上からマリコ.m4a</td><td>37.88 MB</td></tr><tr><td>1 04 家出の夜.m4a</td><td>39.78 MB</td></tr><tr><td>1 05 アンチ.m4a</td><td>33.57 MB</td></tr><tr><td>1 05 スキャンダラスに行こう!.m4a</td><td>27.94 MB</td></tr><tr><td>1 06  ノーカン.m4a</td><td>36.25 MB</td></tr><tr><td>1 06 檸檬の年頃.m4a</td><td>30.46 MB</td></tr><tr><td>1 07 アボガドじゃね～し….m4a</td><td>32.54 MB</td></tr><tr><td>1 07 恋愛総選挙.m4a</td><td>31.11 MB</td></tr><tr><td>1 08 直角Sunshine.m4a</td><td>32.70 MB</td></tr><tr><td>1 08 野菜占い.m4a</td><td>31.29 MB</td></tr><tr><td>1 09 Everyday、カチューシャ.m4a</td><td>42.94 MB</td></tr><tr><td>1 09 僕たちは 今 話し合うべきなんだ.m4a</td><td>31.76 MB</td></tr><tr><td>1 10 さくらんぼと孤独.m4a</td><td>33.31 MB</td></tr><tr><td>1 10 走れ! ペ ンギン.m4a</td><td>33.21 MB</td></tr><tr><td>1 11 ロマンスかくれんぼ.m4a</td><td>24.70 MB</td></tr><tr><td>1 11 大事な時間.m4a</td><td>31.22 MB</td></tr><tr><td>1 12 いつか見た海の底.m4a</td><td>32.99 MB</td></tr><tr><td>1 12 蕾たち.m4a</td><td>30.84 MB</td></tr><tr><td>1 13 ぐ～ぐ～おなか.m4a</td><td>29.23 MB</td></tr><tr><td>1 13 ユングやフロイトの場合.m4a</td><td>33.80 MB</td></tr><tr><td>1 14 やさしさの地図.m4a</td><td>36.78 MB</td></tr><tr><td>1 14 フライングゲット.m4a</td><td>35.85 MB</td></tr><tr><td>1 15 行ってらっしゃい.m4a</td><td>39.93 MB</td></tr><tr><td>1 15 風は吹いている.m4a</td><td>31.18 MB</td></tr><tr><td>1 16 桜の木になろう.m4a</td><td>39.10 MB</td></tr><tr><td>1 16 青空よ 寂しくないか .m4a</td><td>37.24 MB</td></tr><tr><td>1 17 GIVE ME FIVE!.m4a</td><td>39.82 MB</td></tr><tr><td>1 17 桜の花びらたち ～前田敦子 solo ver.～.m4a</td><td>36.00 MB</td></tr></tbody></table>Peer List: (<a href="#" id="swapPeer_266605" onclick="return swapPeerList('266605', '1220617482', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_266605" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_266605" onclick="return swapSnatchList('266605', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_266605" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=147784&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=147784" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('147784');">» AAC / 256 / CD</a>
                                </td>
                                <td class="nobr">280.39 MB</td>
                                <td>472</td>
                                <td>1</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_147784">
                <td colspan="5">

                                                        <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">11.01</span><br/>
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=99098">liziyumai</a>  on <span title="10 years, 6 months, 2 weeks ago">Aug 11 2012, 08:30</span>                          </blockquote>
                                        <blockquote>from 張小小樂@baidu</blockquote>                                    <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>91LxlpoxIlL.jpg</td><td>708.08 KB</td></tr><tr><td>D1/01 ファーストラビット.m4a</td><td>9.05 MB</td></tr><tr><td>D1/02 黄金センター.m4a</td><td>7.12 MB</td></tr><tr><td>D1/03 ミニスカートの妖精.m4a</td><td>7.43 MB</td></tr><tr><td>D1/04 上からマリコ.m4a</td><td>8.91 MB</td></tr><tr><td>D1/05 アンチ.m4a</td><td>7.81 MB</td></tr><tr><td>D1/06 檸檬の年頃.m4a</td><td>7.52 MB</td></tr><tr><td>D1/07 恋愛総選挙.m4a</td><td>6.58 MB</td></tr><tr><td>D1/08 野菜占い.m4a</td><td>7.17 MB</td></tr><tr><td>D1/09 Everyday、カチューシャ.m4a</td><td>9.79 MB</td></tr><tr><td>D1/10 走れ!ペンギン.m4a</td><td>7.54 MB</td></tr><tr><td>D1/11 ロマンスかく れんぼ.m4a</td><td>6.44 MB</td></tr><tr><td>D1/12 蕾たち.m4a</td><td>6.97 MB</td></tr><tr><td>D1/13 ユングやフロイトの場合.m4a</td><td>8.40 MB</td></tr><tr><td>D1/14 フライングケット.m4a</td><td>8.05 MB</td></tr><tr><td>D1/15 風は吹いている.m4a</td><td>7.26 MB</td></tr><tr><td>D1/16 桜の木になろう.m4a</td><td>10.36 MB</td></tr><tr><td>D1/17 GIVE　ME　FIVE.m4a</td><td>9.66 MB</td></tr><tr><td>D2/01 Hate.m4a</td><td>5.96 MB</td></tr><tr><td>D2/02 プラスティックの唇.m4a</td><td>7.77 MB</td></tr><tr><td>D2/03 思い出のほとんど.m4a</td><td>12.83 MB</td></tr><tr><td>D2/04 家出の夜.m4a</td><td>9.46 MB</td></tr><tr><td>D2/05 スキャンダラスに行こう!.m4a</td><td>6.46 MB</td></tr><tr><td>D2/06 ノーカン.m4a</td><td>8.06 MB</td></tr><tr><td>D2/07 アボガドじゃねーし・・・.m4a</td><td>7.44 MB</td></tr><tr><td>D2/08 直角Sunshine.m4a</td><td>7.33 MB</td></tr><tr><td>D2/09 僕たちは　今　話し合うべきなんだ.m4a</td><td>8.22 MB</td></tr><tr><td>D2/10 さくらんぼと孤独.m4a</td><td>8.71 MB</td></tr><tr><td>D2/11 大事な時間.m4a</td><td>8.23 MB</td></tr><tr><td>D2/12 いつか見た海の底.m4a</td><td>7.41 MB</td></tr><tr><td>D2/13 ぐーぐーおなか.m4a</td><td>7.64 MB</td></tr><tr><td>D2/14 やさしさの地図.m4a</td><td>8.27 MB</td></tr><tr><td>D2/15 行ってらっしゃい.m4a</td><td>10.16 MB</td></tr><tr><td>D2/16 青空よ　寂しくないか .m4a</td><td>9.51 MB</td></tr><tr><td>D2/17 桜の花びらたち　前田敦子ソロ.m4a</td><td>10.17 MB</td></tr></tbody></table>     Peer List: (<a href="#" id="swapPeer_147784" onclick="return swapPeerList('147784', '294008294', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_147784" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_147784" onclick="return swapSnatchList('147784', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_147784" style="text-align: center"></div>

                                </td>
                        </tr>
                </tbody>"""
    date = "20120815"

    # 147830 only
    assert get_release_data(torrentids=torrent_ids_mp3_320, torrent_table=torrent_table, date=date)\
           == {'147830':
                   {'slashdata': ['MP3', '320', 'CD'],
                    'uploaddate': 'Aug 11 2012, 17:58',
                    'size_no_units': '340.05',
                    'size_units': 'MB',
                    'completed': '3,651',
                    'seeders': '14', 'leechers': '0'}}

    # 148289 only
    assert get_release_data(torrentids=torrent_ids_flac_lossless_cd, torrent_table=torrent_table, date=date)\
           == {'148289': {'slashdata': ['FLAC', 'Lossless', 'CD'],
                          'uploaddate': 'Aug 15 2012, 08:30',
                          'size_no_units': '1.08',
                          'size_units': 'GB',
                          'completed': '728',
                          'seeders': '11',
                          'leechers': '0'}}

    # Whole group
    assert get_release_data(torrentids=torrent_ids_whole_group, torrent_table=torrent_table, date=date)\
           == {'147830':
                   {'slashdata': ['MP3', '320', 'CD'],
                    'uploaddate': 'Aug 11 2012, 17:58',
                    'size_no_units': '340.05',
                    'size_units': 'MB',
                    'completed': '3,651',
                    'seeders': '14', 'leechers': '0'},
               '147982':
                   {'slashdata': ['MKV', 'DVD'],
                    'uploaddate': 'Aug 13 2012, 02:20',
                    'size_no_units': '2.28',
                    'size_units': 'GB',
                    'completed': '305',
                    'seeders': '0',
                    'leechers': '0'},
               '151631': {'slashdata': ['ISO', 'Lossless', 'DVD'],
                          'uploaddate': 'Sep 11 2012, 17:06',
                          'size_no_units': '6.65',
                          'size_units': 'GB',
                          'completed': '219',
                          'seeders': '3',
                          'leechers': '0'},
               '484250': {'slashdata': ['FLAC', '96-24', 'WEB', 'Hi-Res - 2020'],
                          'uploaddate': 'Apr 28 2021, 04:32',
                          'size_no_units': '4.81',
                          'size_units': 'GB',
                          'completed': '66',
                          'seeders': '5',
                          'leechers': '0'},
               '148289': {'slashdata': ['FLAC', 'Lossless', 'CD'],
                          'uploaddate': 'Aug 15 2012, 08:30',
                          'size_no_units': '1.08',
                          'size_units': 'GB',
                          'completed': '728',
                          'seeders': '11',
                          'leechers': '0'},
               '266605': {'slashdata': ['ALAC', 'Lossless', 'CD'],
                          'uploaddate': 'Dec 01 2015, 11:47',
                          'size_no_units': '1.14',
                          'size_units': 'GB',
                          'completed': '19',
                          'seeders': '1',
                          'leechers': '0'},
               '147784': {'slashdata': ['AAC', '256', 'CD'],
                          'uploaddate': 'Aug 11 2012, 08:30',
                          'size_no_units': '280.39',
                          'size_units': 'MB',
                          'completed': '472',
                          'seeders': '1',
                          'leechers': '0'}}

def test_get_release_data_group_251299_torrent_358233() -> None:
    """
    Test for 251299 and 358233 only
    """
    torrent_ids = ['358233']
    torrent_table = """
    <tbody><tr class="colhead_dark">
                            <td width="80%"><strong>Torrents</strong></td>
                            <td><strong>Size</strong></td>
                            <td class="sign"><img alt="Snatches" src="static/styles/layer_cake/images/snatched.png" title="Snatches"/></td>
                            <td class="sign"><img alt="Seeders" src="static/styles/layer_cake/images/seeders.png" title="Seeders"/></td>
                            <td class="sign"><img alt="Leechers" src="static/styles/layer_cake/images/leechers.png" title="Leechers"/></td>
                    </tr>
                    <tr class="group_torrent" style="font-weight: normal;">
                            <td>
                                    <span>[
                                            <a href="torrents.php?action=download&amp;id=358233&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                            |                                               <a href="reports.php?action=report&amp;id=358233" title="Report">RP</a>

                                                                                    ]</span>
                                    <a href="#" onclick="return swapTorrent('358233');">» MP3 / V0 (VBR) / WEB</a>
                            </td>
                            <td class="nobr">31.90 MB</td>
                            <td>21</td>
                            <td>2</td>
                            <td>0</td>
                    </tr>

            <tr class="pad" id="torrent_358233">
            <td colspan="5">

                                                    <blockquote>
                                            New ratio after downloading (without uploading): <span class="r50">11.01</span><br/>
                                            <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                    </blockquote>
                                                        <blockquote>
                    Uploaded by <a href="user.php?id=183484">_averyisland_</a>  on <span title="4 years, 10 months, 3 weeks ago">Apr 06 2018, 19:55</span>                     </blockquote>
                                    <blockquote>Obtained from Bandcamp using download code included with cassette release.</blockquote>                                     <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>01   imai   WOOF 1.mp3</td><td>3.31 MB</td></tr><tr><td>02   KONCOS   Sunshower.mp3</td><td>5.28 MB</td></tr><tr><td>03   aaps   Tower.mp3</td><td>8.28 MB</td></tr><tr><td>04   THE FULL TEENZ   Baby (KONCOS cover).mp3</td><td>5.52 MB</td></tr><tr><td>05   台風クラブ   江ノ島.mp3</td><td>4.41 MB</td></tr><tr><td>06   imai   WOOF 2.mp3</td><td>4.23 MB</td></tr><tr><td>cover1.png</td><td>670.54 KB</td></tr><tr><td>cover2.jpg</td><td>202.29 KB</td></tr></tbody></table>                      Peer List: (<a href="#" id="swapPeer_358233" onclick="return swapPeerList('358233', '33453220', 'Show', 'Hide');">Show</a>)<br/>
                    <div id="ajax_peerlist_358233" style="text-align: center"></div><br/>
                    Snatch List: (<a href="#" id="swapSnatch_358233" onclick="return swapSnatchList('358233', 'Show', 'Hide');">Show</a>)<br/>
                    <div id="ajax_snatchlist_358233" style="text-align: center"></div>

                            </td>
                    </tr>
                    <tr class="group_torrent" style="font-weight: normal;">
                            <td>
                                    <span>[
                                            <a href="torrents.php?action=download&amp;id=358232&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                            |                                               <a href="reports.php?action=report&amp;id=358232" title="Report">RP</a>

                                                                                    ]</span>
                                    <a href="#" onclick="return swapTorrent('358232');">» FLAC / Lossless / WEB</a>
                            </td>
                            <td class="nobr">121.22 MB</td>
                            <td>24</td>
                            <td>2</td>
                            <td>0</td>
                    </tr>

            <tr class="pad hide" id="torrent_358232">
            <td colspan="5">

                                                    <blockquote>
                                            New ratio after downloading (without uploading): <span class="r50">11.01</span><br/>
                                            <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                    </blockquote>
                                                        <blockquote>
                    Uploaded by <a href="user.php?id=183484">_averyisland_</a>  on <span title="4 years, 10 months, 3 weeks ago">Apr 06 2018, 19:54</span>                     </blockquote>
                                    <blockquote>Obtained from Bandcamp using download code included with cassette release.</blockquote>                                     <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>01   imai   WOOF 1.flac</td><td>10.14 MB</td></tr><tr><td>02   KONCOS   Sunshower.flac</td><td>18.60 MB</td></tr><tr><td>03   aaps   Tower.flac</td><td>28.66 MB</td></tr><tr><td>04   THE FULL TEENZ   Baby (KONCOS cover).flac</td><td>18.09 MB</td></tr><tr><td>05   台風クラブ   江ノ島.flac</td><td>14.83 MB</td></tr><tr><td>06   imai   WOOF 2.flac</td><td>14.11 MB</td></tr><tr><td>Scans/Jcard back.jpg</td><td>2.90 MB</td></tr><tr><td>Scans/Jcard front.jpg</td><td>2.91 MB</td></tr><tr><td>Scans/sheet back.jpg</td><td>2.62 MB</td></tr><tr><td>Scans/sheet front.jpg</td><td>6.30 MB</td></tr><tr><td>Scans/tape sideA.jpg</td><td>620.85 KB</td></tr><tr><td>Scans/tape sideB.jpg</td><td>612.11 KB</td></tr><tr><td>cover1.png</td><td>670.54 KB</td></tr><tr><td>cover2.jpg</td><td>202.29 KB</td></tr></tbody></table>                        Peer List: (<a href="#" id="swapPeer_358232" onclick="return swapPeerList('358232', '127111198', 'Show', 'Hide');">Show</a>)<br/>
                    <div id="ajax_peerlist_358232" style="text-align: center"></div><br/>
                    Snatch List: (<a href="#" id="swapSnatch_358232" onclick="return swapSnatchList('358232', 'Show', 'Hide');">Show</a>)<br/>
                    <div id="ajax_snatchlist_358232" style="text-align: center"></div>

                            </td>
                    </tr>
            </tbody>"""
    date = "20180221"

    assert get_release_data(torrentids=torrent_ids, torrent_table=torrent_table, date=date)\
           == {'358233':
                   {'slashdata': ['MP3', 'V0 (VBR)', 'WEB'],
                    'uploaddate': 'Apr 06 2018, 19:55',
                    'size_no_units': '31.90',
                    'size_units': 'MB',
                    'completed': '21',
                    'seeders': '2',
                    'leechers': '0'}}

def test_get_release_data_group_28034() -> None:
    """
    group-28034-music-in-video-group
    Test for music in a video group
    """
    torrent_ids_whole_group = []
    torrent_table = """
    <tbody><tr class="colhead_dark">
                                <td width="80%"><strong>Torrents</strong></td>
                                <td><strong>Size</strong></td>
                                <td class="sign"><img alt="Snatches" src="static/styles/layer_cake/images/snatched.png" title="Snatches"/></td>
                                <td class="sign"><img alt="Seeders" src="static/styles/layer_cake/images/seeders.png" title="Seeders"/></td>
                                <td class="sign"><img alt="Leechers" src="static/styles/layer_cake/images/leechers.png" title="Leechers"/></td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=405749&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=405749" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('405749');">» MKV / Blu-Ray</a>
                                </td>
                                <td class="nobr">7.45 GB</td>
                                <td>76</td>
                                <td>4</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_405749">
                <td colspan="5">

                                                        <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">11.00</span><br/>
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=205893">KakashiZ</a>  on <span title="3 years, 8 months, 4 weeks ago">Jun 03 2019, 00:43</span>                           </blockquote>
                                                                                <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>Logo.jpg</td><td>369.75 KB</td></tr><tr><td>Promotional Photo.jpg</td><td>69.75 KB</td></tr><tr><td>Suzuki Airi   LIVE TOUR 2018 “PARALLEL DATE” Bonus Footage [1080p   x264   FLAC].mkv</td><td>1.29 GB</td></tr><tr><td>Suzuki Airi   LIVE TOUR 2018 “PARALLEL DATE” [1080p   x264   FLAC].mkv</td><td>6.16 GB</td></tr><tr><td>Suzuki Airi   LIVE TOUR 2018 “PARALLEL DATE”.jpg</td><td>644.01 KB</td></tr></tbody></table>                 Peer List: (<a href="#" id="swapPeer_405749" onclick="return swapPeerList('405749', '7999990415', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_405749" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_405749" onclick="return swapSnatchList('405749', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_405749" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=405748&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=405748" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('405748');">» ISO / Blu-Ray / <strong>Freeleech!</strong></a>
                                </td>
                                <td class="nobr">45.77 GB</td>
                                <td>126</td>
                                <td>2</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_405748">
                <td colspan="5">

                                        <blockquote>
                        Uploaded by <a href="user.php?id=205893">KakashiZ</a>  on <span title="3 years, 8 months, 4 weeks ago">Jun 03 2019, 00:42</span>                           </blockquote>
                                                                                <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>Logo.jpg</td><td>369.75 KB</td></tr><tr><td>Promotional Photo.jpg</td><td>69.75 KB</td></tr><tr><td>Suzuki Airi   LIVE TOUR 2018 “PARALLEL DATE”.jpg</td><td>644.01 KB</td></tr><tr><td>Suzuki Airi LIVE TOUR 2018 “PARALLEL DATE” [2019.05.22] [BDISO].iso</td><td>45.77 GB</td></tr></tbody></table>                     Peer List: (<a href="#" id="swapPeer_405748" onclick="return swapPeerList('405748', '49146686990', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_405748" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_405748" onclick="return swapSnatchList('405748', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_405748" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=405767&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=405767" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('405767');">» FLAC / Blu-Ray</a>
                                </td>
                                <td class="nobr">1.53 GB</td>
                                <td>26</td>
                                <td>2</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_405767">
                <td colspan="5">

                                                        <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">11.01</span><br/>
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=205893">KakashiZ</a>  on <span title="3 years, 8 months, 3 weeks ago">Jun 03 2019, 08:23</span>                           </blockquote>
                                                                                <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>01 鈴木愛里   OPENING VTR.flac</td><td>12.43 MB</td></tr><tr><td>02 鈴木愛里   THE BRAND NEW LOOK.flac</td><td>39.42 MB</td></tr><tr><td>03 鈴木愛里   Candy Box.flac</td><td>49.58 MB</td></tr><tr><td>04 鈴木愛里   たぶんね、.flac</td><td>64.63 MB</td></tr><tr><td>05 鈴木愛里   光の方へ.flac</td><td>47.65 MB</td></tr><tr><td>06 鈴木愛里   MC1.flac</td><td>14.60 MB</td></tr><tr><td>07 鈴木愛里   VTR2.flac</td><td>6.23 MB</td></tr><tr><td>08 鈴木愛里   未完成ガール.flac</td><td>50.38 MB</td></tr><tr><td>09 鈴木愛里   Be Your Love.flac</td><td>61.15 MB</td></tr><tr><td>10 鈴木愛里   TRICK.flac</td><td>44.03 MB</td></tr><tr><td>11 鈴木愛里   BYE BYE.flac</td><td>53.09 MB</td></tr><tr><td>12 鈴木愛里   VTR3.flac</td><td>19.72 MB</td></tr><tr><td>13 鈴木愛里   気まぐれ.flac</td><td>66.09 MB</td></tr><tr><td>14 鈴木愛里   Moment.flac</td><td>55.47 MB</td></tr><tr><td>15 鈴木愛里   ハナウタ.flac</td><td>66.53 MB</td></tr><tr><td>16 鈴木愛里   VTR4.flac</td><td>14.36 MB</td></tr><tr><td>17 鈴木愛里   私の右側.flac</td><td>45.29 MB</td></tr><tr><td>18 鈴木愛里   VTR5.flac</td><td>16.05 MB</td></tr><tr><td>19 鈴木愛里   No Live, No Life.flac</td><td>97.57 MB</td></tr><tr><td>20 鈴木愛里   通学ベクトル☂.flac</td><td>56.08 MB</td></tr><tr><td>21 鈴木愛里   STORY.flac</td><td>51.37 MB</td></tr><tr><td>22 鈴木愛里   Good Night.flac</td><td>48.00 MB</td></tr><tr><td>23 鈴木愛里   DISTANCE.flac</td><td>52.55 MB</td></tr><tr><td>24 鈴木愛里   start again.flac</td><td>56.32 MB</td></tr><tr><td>25 鈴木愛里   パラレルデート.flac</td><td>61.66 MB</td></tr><tr><td>26 鈴木愛里   ENDING VTR.flac</td><td>14.38 MB</td></tr><tr><td>27 鈴木愛里   最高ミュジック【ENCORE】.flac</td><td>58.36 MB</td></tr><tr><td>28 鈴木愛里   初恋サイダー【ENCORE】.flac</td><td>59.66 MB</td></tr><tr><td>29 鈴木愛里   MC2【ENCORE】.flac</td><td>133.05 MB</td></tr><tr><td>30 鈴木愛里   君の好きな人【ENCORE】.flac</td><td>154.56 MB</td></tr><tr><td>Logo.jpg</td><td>369.75 KB</td></tr><tr><td>Promotional Photo.jpg</td><td>69.75 KB</td></tr><tr><td>Suzuki Airi   LIVE TOUR 2018 “PARALLEL DATE”.jpg</td><td>644.01 KB</td></tr></tbody></table>                     Peer List: (<a href="#" id="swapPeer_405767" onclick="return swapPeerList('405767', '1647657533', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_405767" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_405767" onclick="return swapSnatchList('405767', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_405767" style="text-align: center"></div>

                                </td>
                        </tr>
                </tbody>"""
    date = "20190522"

    assert get_release_data(torrentids=torrent_ids_whole_group, torrent_table=torrent_table, date=date)\
           == {"405749": {
    "slashdata": [
      "MKV",
      "Blu-Ray"
    ],
    "uploaddate": "Jun 03 2019, 00:43",
    "size_no_units": "7.45",
    "size_units": "GB",
    "completed": "76",
    "seeders": "4",
    "leechers": "0"
  },
  "405748": {
    "slashdata": [
      "ISO",
      "Blu-Ray"
    ],
    "uploaddate": "Jun 03 2019, 00:42",
    "size_no_units": "45.77",
    "size_units": "GB",
    "completed": "126",
    "seeders": "2",
    "leechers": "0"
  },
  "405767": {
    "slashdata": [
      "FLAC",
      "Blu-Ray"
    ],
    "uploaddate": "Jun 03 2019, 08:23",
    "size_no_units": "1.53",
    "size_units": "GB",
    "completed": "26",
    "seeders": "2",
    "leechers": "0"
  }
}

def test_get_release_data_group_191144() -> None:
    """
    Test larger group with some FL
    """
    torrent_ids_whole_group = []
    torrent_table = """
    <tbody><tr class="colhead_dark">
                                <td width="80%"><strong>Torrents</strong></td>
                                <td><strong>Size</strong></td>
                                <td class="sign"><img alt="Snatches" src="static/styles/layer_cake/images/snatched.png" title="Snatches"/></td>
                                <td class="sign"><img alt="Seeders" src="static/styles/layer_cake/images/seeders.png" title="Seeders"/></td>
                                <td class="sign"><img alt="Leechers" src="static/styles/layer_cake/images/leechers.png" title="Leechers"/></td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=372210&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=372210" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('372210');">» Ogg / 128 (VBR) / CD</a>
                                </td>
                                <td class="nobr">211.94 MB</td>
                                <td>6</td>
                                <td>0</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_372210">
                <td colspan="5">
                                <div id="linkbox" style="text-align: center">
                            <form action="" method="post">
                                <input id="action" name="action" type="hidden" value="reseed"/>
                                <input id="gid" name="gid" type="hidden" value="191144"/>
                                <input id="tid" name="tid" type="hidden" value="372210"/>
                                                                <input id="reseed" name="reseed" type="submit" value="Request a reseed"/>
                                                            </form>
                    </div>

                                                        <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">11.01</span><br/>
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=1622">Menhera</a>  on <span title="4 years, 6 months, 3 weeks ago">Aug 08 2018, 21:06</span>                              <br/>Last active: <span title="3 years, 10 months, 2 weeks ago">Apr 11 2019, 23:20</span>                                        </blockquote>
                                        <blockquote>128VBR level Opus encode using foobar2000<br/>
<br/>
<a href="http://wiki.hydrogenaud.io/index.php?title=Opus" target="_blank">http://wiki.hydrogenaud.io/index.php?title=Opus</a></blockquote>                                      <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>Disc 1/01 桜の花びらたち (2015 BEST ver.).opus</td><td>5.23 MB</td></tr><tr><td>Disc 1/02 スカート、ひらり (2015 BEST ver.).opus</td><td>4.11 MB</td></tr><tr><td>Disc 1/03 会いたかった.opus</td><td>3.87 MB</td></tr><tr><td>Disc 1/04 制服が邪魔をする.opus</td><td>4.77 MB</td></tr><tr><td>Disc 1/05 軽蔑していた愛情.opus</td><td>4.26 MB</td></tr><tr><td>Disc 1/06 BINGO!.opus</td><td>4.18 MB</td></tr><tr><td>Disc 1/07 僕の太陽.opus</td><td>4.83 MB</td></tr><tr><td>Disc 1/08 夕陽を見ているか.opus</td><td>4.96 MB</td></tr><tr><td>Disc 1/09 ロマンス、イラネ.opus</td><td>4.58 MB</td></tr><tr><td>Disc 1/10 桜の花びらたち2008.opus</td><td>5.30 MB</td></tr><tr><td>Disc 1/11 Baby! Baby! Baby!.opus</td><td>3.98 MB</td></tr><tr><td>Disc 1/12 大声ダイヤモンド.opus</td><td>4.03 MB</td></tr><tr><td>Disc 1/13 10年桜.opus</td><td>4.08 MB</td></tr><tr><td>Disc 1/14 涙サプライズ!.opus</td><td>4.42 MB</td></tr><tr><td>Disc 1/15 言い訳Maybe.opus</td><td>4.15 MB</td></tr><tr><td>Disc 2/01 RIVER.opus</td><td>4.49 MB</td></tr><tr><td>Disc 2/02 桜の栞.opus</td><td>4.03 MB</td></tr><tr><td>Disc 2/03 ポニーテールとシュシュ.opus</td><td>4.46 MB</td></tr><tr><td>Disc 2/04 ヘビーローテーション.opus</td><td>4.50 MB</td></tr><tr><td>Disc 2/05 Beginner.opus</td><td>3.80 MB</td></tr><tr><td>Disc 2/06 チャンスの順番.opus</td><td>4.29 MB</td></tr><tr><td>Disc 2/07 桜の木になろう.opus</td><td>5.79 MB</td></tr><tr><td>Disc 2/08 Everyday、カチューシャ.opus</td><td>4.97 MB</td></tr><tr><td>Disc 2/09 フライングゲット.opus</td><td>4.12 MB</td></tr><tr><td>Disc 2/10  風は吹いている.opus</td><td>3.63 MB</td></tr><tr><td>Disc 2/11 上からマリコ.opus</td><td>4.57 MB</td></tr><tr><td>Disc 2/12 GIVE ME FIVE!.opus</td><td>4.87 MB</td></tr><tr><td>Disc 2/13 真夏のSounds good!.opus</td><td>4.39 MB</td></tr><tr><td>Disc 2/14 ギンガムチェック.opus</td><td>5.28 MB</td></tr><tr><td>Disc 2/15 UZA.opus</td><td>4.42 MB</td></tr><tr><td>Disc 2/16 永遠プレッシャー.opus</td><td>4.89 MB</td></tr><tr><td>Disc 3/01 So long!.opus</td><td>5.96 MB</td></tr><tr><td>Disc 3/02 さよならクロール.opus</td><td>4.76 MB</td></tr><tr><td>Disc 3/03 恋するフォーチュンクッキー.opus</td><td>4.65 MB</td></tr><tr><td>Disc 3/04 ハート・エレキ.opus</td><td>4.87 MB</td></tr><tr><td>Disc 3/05 鈴懸木の道で「君の微笑みを夢に見る」と言ってしまったら僕たちの関係はどうかわってしまうのか、僕なりに何日か考えた上でのやや気恥ずかしい結論 のようなもの.opus</td><td>5.37 MB</td></tr><tr><td>Disc 3/06 前しか向かねえ.opus</td><td>4.21 MB</td></tr><tr><td>Disc 3/07 ラブラドール・レトリバー.opus</td><td>4.90 MB</td></tr><tr><td>Disc 3/08 心のプラカード.opus</td><td>3.98 MB</td></tr><tr><td>Disc 3/09 希望的リフレイン.opus</td><td>4.73 MB</td></tr><tr><td>Disc 3/10 Green Flash.opus</td><td>4.69 MB</td></tr><tr><td>Disc 3/11 僕たちは戦わない.opus</td><td>5.24 MB</td></tr><tr><td>Disc 3/12 ハロウィン・ナイト.opus</td><td>4.93 MB</td></tr><tr><td>Disc 3/13 クリスマスイブに泣かな いように.opus</td><td>5.29 MB</td></tr><tr><td>Disc 3/14 始まりの雪.opus</td><td>4.66 MB</td></tr><tr><td>Disc 3/15 ロザリオ.opus</td><td>4.44 MB</td></tr></tbody></table>        Peer List: (<a href="#" id="swapPeer_372210" onclick="return swapPeerList('372210', '222232273', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_372210" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_372210" onclick="return swapSnatchList('372210', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_372210" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=265408&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=265408" style="font-weight: bold; color: red;" title="Report">Reported!</a>
                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('265408');">» MP4 / DVD / Complete Singles (handshake) - 2015</a>
                                </td>
                                <td class="nobr">1.36 GB</td>
                                <td>111</td>
                                <td>1</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_265408">
                <td colspan="5">

                                                <table style="overflow-x:auto;">
                                <tbody><tr class="colhead_dark">
                                    <td><strong>Reported on <span title="7 years, 3 months, 1 week ago">Nov 18 2015, 04:28</span></strong></td>
                                </tr>
                                <tr>
                                    <td>Probably only the handshake part of the DVD.<br/>
<br/>
Should be:<br/>
1. AKB48グループメンバー エア握手会2015 [AKB48 Group Members Air-Handshake 2015]<br/>
2. DECADE～AKB48 10年の軌跡～ [DECADE ~AKB48 Path of 10 Years~]</td>
                                </tr>
                            </tbody></table>
                                                        <table style="overflow-x:auto;">
                                <tbody><tr class="colhead_dark">
                                    <td><strong>Reported on <span title="7 years, 2 months, 3 weeks ago">Dec 08 2015, 07:39</span></strong></td>
                                </tr>
                                <tr>
                                    <td></td>
                                </tr>
                            </tbody></table>
                                                                <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">11.01</span><br/>
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=58030">LL</a>  on <span title="7 years, 3 months, 1 week ago">Nov 17 2015, 11:59</span>                                   </blockquote>
                                                                                <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>AKB48 研究生.mp4</td><td>76.99 MB</td></tr><tr><td>Team 4.mp4</td><td>193.44 MB</td></tr><tr><td>Team 8.mp4</td><td>530.68 MB</td></tr><tr><td>Team A.mp4</td><td>226.70 MB</td></tr><tr><td>Team B.mp4</td><td>168.84 MB</td></tr><tr><td>Team K.mp4</td><td>197.19 MB</td></tr></tbody></table>                  Peer List: (<a href="#" id="swapPeer_265408" onclick="return swapPeerList('265408', '1461551267', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_265408" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_265408" onclick="return swapSnatchList('265408', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_265408" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=265168&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=265168" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('265168');">» MP3 / 320 / CD / Complete Singles - 2015</a>
                                </td>
                                <td class="nobr">492.00 MB</td>
                                <td>1,531</td>
                                <td>10</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_265168">
                <td colspan="5">

                                                        <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">11.01</span><br/>
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=99098">liziyumai</a>  on <span title="7 years, 3 months, 2 weeks ago">Nov 14 2015, 11:06</span>                           </blockquote>
                                                                                <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>CD1/01. 桜の花びらたち(2015 BEST ver.).mp3</td><td>12.14 MB</td></tr><tr><td>CD1/02. スカート、ひらり(2015 BEST ver.).mp3</td><td>9.32 MB</td></tr><tr><td>CD1/03. 会いたかった.mp3</td><td>8.78 MB</td></tr><tr><td>CD1/04. 制服が邪魔をする.mp3</td><td>10.94 MB</td></tr><tr><td>CD1/05. 軽蔑していた愛情.mp3</td><td>9.83 MB</td></tr><tr><td>CD1/06. BINGO!.mp3</td><td>9.59 MB</td></tr><tr><td>CD1/07. 僕の太陽.mp3</td><td>11.26 MB</td></tr><tr><td>CD1/08. 夕陽を見ているか？.mp3</td><td>11.41 MB</td></tr><tr><td>CD1/09. ロマンス、イラネ.mp3</td><td>10.78 MB</td></tr><tr><td>CD1/10. 桜の花びらたち 2008.mp3</td><td>12.20 MB</td></tr><tr><td>CD1/11. Baby!Baby!Baby!.mp3</td><td>9.24 MB</td></tr><tr><td>CD1/12. 大声ダイヤモンド.mp3</td><td>9.49 MB</td></tr><tr><td>CD1/13. 10年桜.mp3</td><td>9.77 MB</td></tr><tr><td>CD1/14. 涙サプライズ.mp3</td><td>10.74 MB</td></tr><tr><td>CD1/15. 言い訳Maybe.mp3</td><td>9.55 MB</td></tr><tr><td>CD2/01. RIVER.mp3</td><td>10.82 MB</td></tr><tr><td>CD2/02. 桜の栞.mp3</td><td>9.13 MB</td></tr><tr><td>CD2/03. ポニーテールとシュシュ.mp3</td><td>10.34 MB</td></tr><tr><td>CD2/04. ヘビーローテーション.mp3</td><td>10.73 MB</td></tr><tr><td>CD2/05. Beginner.mp3</td><td>9.06 MB</td></tr><tr><td>CD2/06. チャンスの順番.mp3</td><td>9.88 MB</td></tr><tr><td>CD2/07. 桜の木になろう.mp3</td><td>12.63 MB</td></tr><tr><td>CD2/08. Everyday、カチューシャ.mp3</td><td>11.94 MB</td></tr><tr><td>CD2/09. フライングゲット.mp3</td><td>9.70 MB</td></tr><tr><td>CD2/10. 風は吹いている.mp3</td><td>8.46 MB</td></tr><tr><td>CD2/11. 上からマリコ.mp3</td><td>10.65 MB</td></tr><tr><td>CD2/12. GIVE ME FIVE!.mp3</td><td>11.50 MB</td></tr><tr><td>CD2/13. 真夏のSounds good!.mp3</td><td>10.45 MB</td></tr><tr><td>CD2/14. ギンガムチェック.mp3</td><td>12.32 MB</td></tr><tr><td>CD2/15. UZA.mp3</td><td>10.73 MB</td></tr><tr><td>CD2/16. 永遠プレッシャー.mp3</td><td>11.26 MB</td></tr><tr><td>CD3/01. So long!.mp3</td><td>13.74 MB</td></tr><tr><td>CD3/02. さよならクロール.mp3</td><td>11.24 MB</td></tr><tr><td>CD3/03. 恋するフォーチュンクッキー.mp3</td><td>10.87 MB</td></tr><tr><td>CD3/04. ハート・エレキ.mp3</td><td>11.31 MB</td></tr><tr><td>CD3/05. 鈴懸の木の道で「君の微笑みを夢に見る」と言ってしまったら僕たちの関係はどう変わってしまうのか、僕なりに何日か考えた上でのやや気恥ずかしい結論の ようなも.mp3</td><td>12.47 MB</td></tr><tr><td>CD3/06. 前しか向かねえ.mp3</td><td>9.89 MB</td></tr><tr><td>CD3/07. ラブラドール・レトリバー.mp3</td><td>11.22 MB</td></tr><tr><td>CD3/08. 心のプラカード.mp3</td><td>9.28 MB</td></tr><tr><td>CD3/09. 希望的リフレイン.mp3</td><td>11.16 MB</td></tr><tr><td>CD3/10. Green Flash.mp3</td><td>10.37 MB</td></tr><tr><td>CD3/11. 僕たちは戦わない.mp3</td><td>12.41 MB</td></tr><tr><td>CD3/12. ハロウィン・ナイト.mp3</td><td>11.64 MB</td></tr><tr><td>CD3/13. クリスマスイブに泣かないように.mp3</td><td>11.65 MB</td></tr><tr><td>CD3/14. 始まりの雪.mp3</td><td>10.12 MB</td></tr><tr><td>CD3/15. ロザリオ.mp3</td><td>9.97 MB</td></tr></tbody></table>                 Peer List: (<a href="#" id="swapPeer_265168" onclick="return swapPeerList('265168', '515903576', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_265168" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_265168" onclick="return swapSnatchList('265168', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_265168" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=266844&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=266844" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('266844');">» MP3 / 320 / CD / Million Singles - 2015 / <strong>Freeleech!</strong></a>
                                </td>
                                <td class="nobr">320.12 MB</td>
                                <td>798</td>
                                <td>14</td>
                                <td>1</td>
                        </tr>

                <tr class="pad hide" id="torrent_266844">
                <td colspan="5">

                                        <blockquote>
                        Uploaded by <a href="user.php?id=129451">Nefarious</a>  on <span title="7 years, 2 months, 3 weeks ago">Dec 03 2015, 07:43</span>                          </blockquote>
                                        <blockquote>Ripped from my own copy.</blockquote>                                       <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>1 01 Beginner.mp3</td><td>9.22 MB</td></tr><tr><td>1 02 桜の木になろう.mp3</td><td>12.78 MB</td></tr><tr><td>1 03 Everyday、カチューシャ.mp3</td><td>12.09 MB</td></tr><tr><td>1 04 フライングゲット.mp3</td><td>9.85 MB</td></tr><tr><td>1 05 風は吹いている.mp3</td><td>8.61 MB</td></tr><tr><td>1 06 上からマリコ.mp3</td><td>10.80 MB</td></tr><tr><td>1 07 GIVE ME FIVE!.mp3</td><td>11.66 MB</td></tr><tr><td>1 08 真夏のSounds good!.mp3</td><td>10.60 MB</td></tr><tr><td>1 09 ギンガムチェック.mp3</td><td>12.48 MB</td></tr><tr><td>1 10 UZA.mp3</td><td>10.88 MB</td></tr><tr><td>1 11 永遠プレッシャー.mp3</td><td>11.40 MB</td></tr><tr><td>1 12 So long!.mp3</td><td>13.89 MB</td></tr><tr><td>1 13 さよならクロール.mp3</td><td>11.40 MB</td></tr><tr><td>1 14 恋するフォーチュンクッキー.mp3</td><td>11.03 MB</td></tr><tr><td>1 15 ハート・エレキ.mp3</td><td>11.48 MB</td></tr><tr><td>2 01 鈴懸木の道で「君の微笑みを夢に見る」と言ってしまったら僕たちの関係はどうかわってしまうのか、僕なりに何日か考えた
上でのやや気恥ずかしい結論のようなもの.mp3</td><td>12.63 MB</td></tr><tr><td>2 02 前しか向かねえ.mp3</td><td>10.04 MB</td></tr><tr><td>2 03 ラブラドール・レトリバー.mp3</td><td>11.38 MB</td></tr><tr><td>2 04 心のプラカード.mp3</td><td>9.43 MB</td></tr><tr><td>2 05 希望的リフレイン.mp3</td><td>11.31 MB</td></tr><tr><td>2 06 Green Flash.mp3</td><td>10.52 MB</td></tr><tr><td>2 07 僕たちは戦わない.mp3</td><td>12.56 MB</td></tr><tr><td>2 08 ハロウィーン・ナイト.mp3</td><td>11.83 MB</td></tr><tr><td>2 09 Clap.mp3</td><td>10.04 MB</td></tr><tr><td>2 10 愛の使者.mp3</td><td>10.46 MB</td></tr><tr><td>2 11 ミュージックジャンキー.mp3</td><td>8.91 MB</td></tr><tr><td>2 12 泣き言タイム.mp3</td><td>11.03 MB</td></tr><tr><td>2 13 一生の間に何人と出逢えるのだろう.mp3</td><td>11.00 MB</td></tr><tr><td>2 14 LOVE ASH.mp3</td><td>10.65 MB</td></tr><tr><td>cover.jpg</td><td>160.12 KB</td></tr></tbody></table>                       Peer List: (<a href="#" id="swapPeer_266844" onclick="return swapPeerList('266844', '335670771', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_266844" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_266844" onclick="return swapSnatchList('266844', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_266844" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=266857&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=266857" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('266857');">» MP3 / 320 / CD / No.1 Singles - 2015 / <strong>Freeleech!</strong></a>
                                </td>
                                <td class="nobr">340.05 MB</td>
                                <td>727</td>
                                <td>15</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_266857">
                <td colspan="5">

                                        <blockquote>
                        Uploaded by <a href="user.php?id=129451">Nefarious</a>  on <span title="7 years, 2 months, 3 weeks ago">Dec 03 2015, 09:58</span>                          </blockquote>
                                        <blockquote>Ripped from my own copy.</blockquote>                                       <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>1 01 RIVER.mp3</td><td>10.97 MB</td></tr><tr><td>1 02 桜の栞.mp3</td><td>9.28 MB</td></tr><tr><td>1 03 ポニーテールとシュシュ.mp3</td><td>10.48 MB</td></tr><tr><td>1 04 ヘビーローテーション.mp3</td><td>10.88 MB</td></tr><tr><td>1 05 Beginner.mp3</td><td>9.21 MB</td></tr><tr><td>1 06 チャンスの順番.mp3</td><td>10.03 MB</td></tr><tr><td>1 07 桜の木になろう.mp3</td><td>12.78 MB</td></tr><tr><td>1 08 Everyday、カチューシャ.mp3</td><td>12.09 MB</td></tr><tr><td>1 09 フライングゲット.mp3</td><td>9.84 MB</td></tr><tr><td>1 10 風は吹いている.mp3</td><td>8.61 MB</td></tr><tr><td>1 11 上からマリコ.mp3</td><td>10.79 MB</td></tr><tr><td>1 12 GIVE ME FIVE!.mp3</td><td>11.65 MB</td></tr><tr><td>1 13 真夏のSounds good!.mp3</td><td>10.60 MB</td></tr><tr><td>1 14 ギンガムチェック.mp3</td><td>12.47 MB</td></tr><tr><td>1 15 UZA.mp3</td><td>10.88 MB</td></tr><tr><td>1 16 永遠プレッシャー.mp3</td><td>11.41 MB</td></tr><tr><td>2 01 So long!.mp3</td><td>13.89 MB</td></tr><tr><td>2 02 さよならクロー ル.mp3</td><td>11.39 MB</td></tr><tr><td>2 03 恋するフォーチュンクッキー.mp3</td><td>11.02 MB</td></tr><tr><td>2 04 ハート・エレキ.mp3</td><td>11.46 MB</td></tr><tr><td>2 05 鈴懸木の道で「君の微笑みを夢に見る」と言ってしまったら僕たちの関係はどうかわってしまうのか、僕なりに何日か考えた上でのやや気恥ずかしい結論のようなもの.mp3</td><td>12.62 MB</td></tr><tr><td>2 06 前しか向かねえ.mp3</td><td>10.04 MB</td></tr><tr><td>2 07 ラブラドール・レトリバー.mp3</td><td>11.37 MB</td></tr><tr><td>2 08 心のプラカード.mp3</td><td>9.43 MB</td></tr><tr><td>2 09 希望的リフレイン.mp3</td><td>11.30 MB</td></tr><tr><td>2 10 Green Flash.mp3</td><td>10.52 MB</td></tr><tr><td>2 11 僕たちは戦わない.mp3</td><td>12.56 MB</td></tr><tr><td>2 12 ハロウィーン・ナイト.mp3</td><td>11.81 MB</td></tr><tr><td>2 13 やさしくありたい.mp3</td><td>8.93 MB</td></tr><tr><td>2 14 トイプードルと君の物語.mp3</td><td>11.37 MB</td></tr><tr><td>2 15 あの頃、好きだった人.mp3</td><td>10.23 MB</td></tr><tr><td>cover.jpg</td><td>154.13 KB</td></tr></tbody></table>                 Peer List: (<a href="#" id="swapPeer_266857" onclick="return swapPeerList('266857', '356571076', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_266857" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_266857" onclick="return swapSnatchList('266857', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_266857" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=309925&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=309925" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('309925');">» MP3 / V0 (VBR) / CD / Complete Singles - 2015</a>
                                </td>
                                <td class="nobr">418.47 MB</td>
                                <td>24</td>
                                <td>0</td>
                                <td>1</td>
                        </tr>

                <tr class="pad hide" id="torrent_309925">
                <td colspan="5">
                                <div id="linkbox" style="text-align: center">
                            <form action="" method="post">
                                <input id="action" name="action" type="hidden" value="reseed"/>
                                <input id="gid" name="gid" type="hidden" value="191144"/>
                                <input id="tid" name="tid" type="hidden" value="309925"/>
                                                                <input id="reseed" name="reseed" type="submit" value="Request a reseed"/>
                                                            </form>
                    </div>

                                                        <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">11.01</span><br/>
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=196254">adamkex</a>  on <span title="6 years, 2 months, 6 days ago">Dec 23 2016, 07:58</span>                             <br/>Last active: <span title="3 years, 4 months, 6 days ago">Oct 24 2019, 04:32</span>                                  </blockquote>
                                                                                <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>Disc 1/01   桜の花びらたち (2015 BEST ver.).mp3</td><td>10.68 MB</td></tr><tr><td>Disc 1/02   スカート、ひらり (2015 BEST ver.).mp3</td><td>8.35 MB</td></tr><tr><td>Disc 1/03   会いたかった.mp3</td><td>7.30 MB</td></tr><tr><td>Disc 1/04   制服が邪魔をする.mp3</td><td>9.49 MB</td></tr><tr><td>Disc 1/05   軽蔑していた愛情.mp3</td><td>8.36 MB</td></tr><tr><td>Disc 1/06   BINGO!.mp3</td><td>8.03 MB</td></tr><tr><td>Disc 1/07   僕の太陽.mp3</td><td>9.91 MB</td></tr><tr><td>Disc 1/08   夕陽を見ているか.mp3</td><td>9.76 MB</td></tr><tr><td>Disc 1/09   ロマンス、イラネ.mp3</td><td>9.50 MB</td></tr><tr><td>Disc 1/10   桜の花びらたち2008.mp3</td><td>10.26 MB</td></tr><tr><td>Disc 1/11   Baby! Baby! Baby!.mp3</td><td>7.55 MB</td></tr><tr><td>Disc 1/12   大声ダイヤモンド.mp3</td><td>7.81 MB</td></tr><tr><td>Disc 1/13   10年桜.mp3</td><td>8.41 MB</td></tr><tr><td>Disc 1/14   涙サプライズ!.mp3</td><td>9.25 MB</td></tr><tr><td>Disc 1/15   言い訳Maybe.mp3</td><td>8.17 MB</td></tr><tr><td>Disc 1/cover.jpg</td><td>172.69 KB</td></tr><tr><td>Disc 2/01   RIVER.mp3</td><td>9.29 MB</td></tr><tr><td>Disc 2/02   桜の栞.mp3</td><td>7.13 MB</td></tr><tr><td>Disc 2/03   ポニーテールとシュシュ.mp3</td><td>8.71 MB</td></tr><tr><td>Disc 2/04   ヘビーローテーション.mp3</td><td>8.97 MB</td></tr><tr><td>Disc 2/05   Beginner.mp3</td><td>7.24 MB</td></tr><tr><td>Disc 2/06   チャンスの順番.mp3</td><td>8.28 MB</td></tr><tr><td>Disc 2/07   桜の木になろう.mp3</td><td>10.68 MB</td></tr><tr><td>Disc 2/08   Everyday、カチューシャ.mp3</td><td>9.27 MB</td></tr><tr><td>Disc 2/09   フライングゲット.mp3</td><td>8.12 MB</td></tr><tr><td>Disc 2/10   風は吹いている.mp3</td><td>7.23 MB</td></tr><tr><td>Disc 2/11   上からマリコ.mp3</td><td>8.99 MB</td></tr><tr><td>Disc 2/12   GIVE ME FIVE!.mp3</td><td>9.68 MB</td></tr><tr><td>Disc 2/13   真夏のSounds good!.mp3</td><td>8.66 MB</td></tr><tr><td>Disc 2/14   ギンガムチェック.mp3</td><td>10.82 MB</td></tr><tr><td>Disc 2/15   UZA.mp3</td><td>8.80 MB</td></tr><tr><td>Disc 2/16   永遠プレッシャー.mp3</td><td>9.87 MB</td></tr><tr><td>Disc 2/cover.jpg</td><td>172.69 KB</td></tr><tr><td>Disc 3/01   So long!.mp3</td><td>12.08 MB</td></tr><tr><td>Disc 3/02   さよならクロール.mp3</td><td>9.32 MB</td></tr><tr><td>Disc 3/03   恋するフォーチュンクッキー.mp3</td><td>9.43 MB</td></tr><tr><td>Disc 3/04   ハート・エレキ.mp3</td><td>9.71 MB</td></tr><tr><td>Disc 3/05   鈴懸木の道で「君の微笑みを夢に見る」と言ってしまったら僕たちの関係はどうかわってしまうのか、僕なりに何日か考えた上でのやや気恥ずかしい結論のようなもの.mp3</td><td>11.19 MB</td></tr><tr><td>Disc 3/06   前しか向かねえ.mp3</td><td>8.66 MB</td></tr><tr><td>Disc 3/07   ラブ ラドール・レトリバー.mp3</td><td>9.64 MB</td></tr><tr><td>Disc 3/08   心のプラカード.mp3</td><td>8.16 MB</td></tr><tr><td>Disc 3/09   希望的リフレイン.mp3</td><td>9.04 MB</td></tr><tr><td>Disc 3/10   Green Flash.mp3</td><td>8.74 MB</td></tr><tr><td>Disc 3/11   僕たちは戦わない.mp3</td><td>10.15 MB</td></tr><tr><td>Disc 3/12   ハロウィーン・ナイト.mp3</td><td>9.48 MB</td></tr><tr><td>Disc 3/13   クリスマスイブに泣かないように.mp3</td><td>10.53 MB</td></tr><tr><td>Disc 3/14   始まりの雪.mp3</td><td>8.88 MB</td></tr><tr><td>Disc 3/15    ロザリオ.mp3</td><td>8.38 MB</td></tr><tr><td>Disc 3/cover.jpg</td><td>172.69 KB</td></tr></tbody></table>                      Peer List: (<a href="#" id="swapPeer_309925" onclick="return swapPeerList('309925', '438800363', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_309925" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_309925" onclick="return swapSnatchList('309925', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_309925" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=267035&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=267035" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('267035');">» ISO / Lossless / DVD / <strong>Freeleech!</strong></a>
                                </td>
                                <td class="nobr">6.69 GB</td>
                                <td>269</td>
                                <td>2</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_267035">
                <td colspan="5">

                                        <blockquote>
                        Uploaded by <a href="user.php?id=129451">Nefarious</a>  on <span title="7 years, 2 months, 3 weeks ago">Dec 05 2015, 07:44</span>                          </blockquote>
                                        <blockquote>Ripped from my own copy.</blockquote>                                       <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>0to1noAida.iso</td><td>6.69 GB</td></tr></tbody></table>                       Peer List: (<a href="#" id="swapPeer_267035" onclick="return swapPeerList('267035', '7182551040', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_267035" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_267035" onclick="return swapSnatchList('267035', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_267035" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=350825&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=350825" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('350825');">» FLAC / 24bit 96khz / WEB</a>
                                </td>
                                <td class="nobr">6.95 GB</td>
                                <td>209</td>
                                <td>13</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_350825">
                <td colspan="5">

                                                        <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">11.00</span><br/>
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=170975">val</a>  on <span title="5 years, 1 month, 4 days ago">Jan 25 2018, 11:42</span>                                  </blockquote>
                                        <blockquote>Mora 24bit 96khz, [Complete Singles] Edition</blockquote>                                   <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>1 桜の花びらたち(RE EDIT ver.).flac</td><td>174.73 MB</td></tr><tr><td>10  桜の花びらたち2008.flac</td><td>176.47 MB</td></tr><tr><td>11 Baby! Baby! Baby!.flac</td><td>133.76 MB</td></tr><tr><td>12 大声ダイヤモンド.flac</td><td>137.27 MB</td></tr><tr><td>13 10年桜.flac</td><td>141.43 MB</td></tr><tr><td>14 涙サプライズ！.flac</td><td>155.33 MB</td></tr><tr><td>15 言い訳Maybe.flac</td><td>138.32 MB</td></tr><tr><td>16 RIVER.flac</td><td>156.57 MB</td></tr><tr><td>17 桜の栞.flac</td><td>132.19 MB</td></tr><tr><td>18 ポニーテールとシュシュ.flac</td><td>149.55 MB</td></tr><tr><td>19 ヘビーローテーション.flac</td><td>155.29 MB</td></tr><tr><td>2 スカート、ひらり(RE EDIT ver.).flac</td><td>134.88 MB</td></tr><tr><td>20 Beginner.flac</td><td>131.17 MB</td></tr><tr><td>21 チャンスの順番.flac</td><td>143.01 MB</td></tr><tr><td>22 桜の木になろう.flac</td><td>182.63 MB</td></tr><tr><td>23 Everyday、カチューシャ.flac</td><td>172.70 MB</td></tr><tr><td>24 風は吹いている.flac</td><td>140.31 MB</td></tr><tr><td>25 風は吹いている.flac</td><td>122.47 MB</td></tr><tr><td>26 上からマリコ.flac</td><td>154.01 MB</td></tr><tr><td>27 GIVE ME FIVE!.flac</td><td>166.36 MB</td></tr><tr><td>28 真夏のSounds good !.flac</td><td>151.17 MB</td></tr><tr><td>29 ギンガムチェック.flac</td><td>178.20 MB</td></tr><tr><td>3 会いたかった.flac</td><td>127.04 MB</td></tr><tr><td>30 UZA.flac</td><td>155.22 MB</td></tr><tr><td>31 永遠プレッシャー.flac</td><td>163.24 MB</td></tr><tr><td>32 So long !.flac</td><td>198.59 MB</td></tr><tr><td>33 さよならクロール.flac</td><td>162.62 MB</td></tr><tr><td>34 恋するフォーチュンクッキー.flac</td><td>157.26 MB</td></tr><tr><td>35 ハート・エレキ.flac</td><td>163.66 MB</td></tr><tr><td>36 鈴懸の木の道で「君の微笑みを夢に見る」と言ってしまったら僕たちの関係はどう変わってしまうのか、僕なりに何日か考えた上でのやや気恥ずかしい結論のようなもの.flac</td><td>180.31 MB</td></tr><tr><td>37 前しか向かねえ.flac</td><td>143.12 MB</td></tr><tr><td>38 ラブラドール・レトリバー.flac</td><td>162.31 MB</td></tr><tr><td>39 心のプラカード.flac</td><td>134.32 MB</td></tr><tr><td>4 制服が邪魔をする.flac</td><td>158.31 MB</td></tr><tr><td>40 希望的リフレイン.flac</td><td>161.37 MB</td></tr><tr><td>41 Green Flash.flac</td><td>149.98 MB</td></tr><tr><td>42 僕たちは戦わない.flac</td><td>179.43 MB</td></tr><tr><td>43 ハロウィン・ナイト.flac</td><td>168.35 MB</td></tr><tr><td>44 クリスマスイブに泣かないよ うに(宮脇咲良、渡辺麻友).flac</td><td>168.51 MB</td></tr><tr><td>45 始まりの雪(大島涼花、高橋朱里、田野優花、武藤十夢).flac</td><td>146.46 MB</td></tr><tr><td>46 ロザリオ(入山杏奈 、加藤玲奈、木﨑ゆりあ、兒玉遥).flac</td><td>144.25 MB</td></tr><tr><td>5 軽蔑していた愛情.flac</td><td>142.23 MB</td></tr><tr><td>6 BINGO!.flac</td><td>138.76 MB</td></tr><tr><td>7 僕の太陽.flac</td><td>162.94 MB</td></tr><tr><td>8 夕陽を見ているか？.flac</td><td>165.07 MB</td></tr><tr><td>9 ロマンス、イラネ.flac</td><td>155.90 MB</td></tr></tbody></table>Peer List: (<a href="#" id="swapPeer_350825" onclick="return swapPeerList('350825', '7462741832', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_350825" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_350825" onclick="return swapSnatchList('350825', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_350825" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=266249&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=266249" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('266249');">» FLAC / Lossless / CD / Theater Edition - 2015</a>
                                </td>
                                <td class="nobr">996.26 MB</td>
                                <td>314</td>
                                <td>8</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_266249">
                <td colspan="5">

                                                        <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">11.01</span><br/>
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=35927">y2kbug</a>  on <span title="7 years, 3 months, 2 days ago">Nov 27 2015, 17:29</span>                               </blockquote>
                                        <blockquote>Theater Edition</blockquote>                                        <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>CD 1/01. Beginner.flac</td><td>34.92 MB</td></tr><tr><td>CD 1/02. 桜の木になろう.flac</td><td>40.98 MB</td></tr><tr><td>CD 1/03. Everyday、カチューシャ.flac</td><td>46.15 MB</td></tr><tr><td>CD 1/04. フライングゲット.flac</td><td>36.53 MB</td></tr><tr><td>CD 1/05. 風は吹いている.flac</td><td>31.68 MB</td></tr><tr><td>CD 1/06. 上からマリコ.flac</td><td>39.08 MB</td></tr><tr><td>CD 1/07. GIVE ME FIVE!.flac</td><td>42.64 MB</td></tr><tr><td>CD 1/08. 真夏のSounds good!.flac</td><td>40.24 MB</td></tr><tr><td>CD 1/09. ギンガムチェック.flac</td><td>46.39 MB</td></tr><tr><td>CD 1/10. UZA.flac</td><td>42.44 MB</td></tr><tr><td>CD 1/11. 永遠プレッシャー.flac</td><td>41.30 MB</td></tr><tr><td>CD 1/12. So Long!.flac</td><td>47.41 MB</td></tr><tr><td>CD 1/13. さよならクロール.flac</td><td>41.83 MB</td></tr><tr><td>CD 1/14. 恋するフォーチュンクッキー.flac</td><td>37.76 MB</td></tr><tr><td>CD 1/15. ハート・エレキ.flac</td><td>41.21 MB</td></tr><tr><td>CD 2/01. 鈴懸の木の道で「君の微笑みを夢に見る」 と言ってしまったら僕たちの関係はどう変わってしまうのか、僕なりに何日か考えた上でのやや気恥ずかしい結論のようなもの.flac</td><td>44.97 MB</td></tr><tr><td>CD 2/02. 前しか向かねえ.flac</td><td>34.88 MB</td></tr><tr><td>CD 2/03. ラブラドール・レトリバー.flac</td><td>38.34 MB</td></tr><tr><td>CD 2/04. 心のプラカード.flac</td><td>33.02 MB</td></tr><tr><td>CD 2/05. 希望的リフレイン.flac</td><td>42.60 MB</td></tr><tr><td>CD 2/06. Green Flash.flac</td><td>34.39 MB</td></tr><tr><td>CD 2/07. 僕たちは戦わない.flac</td><td>46.13 MB</td></tr><tr><td>CD 2/08. ハロウィン・ナイト.flac</td><td>44.75 MB</td></tr><tr><td>CD 2/09. てんとうむChu!を探せ!.flac</td><td>30.29 MB</td></tr><tr><td>CD 2/10. あれから僕は勉強が手につかない.flac</td><td>36.34 MB</td></tr></tbody></table>                 Peer List: (<a href="#" id="swapPeer_266249" onclick="return swapPeerList('266249', '1044652762', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_266249" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_266249" onclick="return swapSnatchList('266249', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_266249" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=266832&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=266832" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('266832');">» FLAC / Lossless / CD / Complete Singles - 2015 / <strong>Freeleech!</strong></a>
                                </td>
                                <td class="nobr">1.62 GB</td>
                                <td>925</td>
                                <td>23</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_266832">
                <td colspan="5">

                                        <blockquote>
                        Uploaded by <a href="user.php?id=129451">Nefarious</a>  on <span title="7 years, 2 months, 3 weeks ago">Dec 03 2015, 05:45</span>                          </blockquote>
                                        <blockquote>Ripped from my own copy.</blockquote>                                       <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>Disc 1/01   桜の花びらたち (2015 BEST ver.).flac</td><td>39.54 MB</td></tr><tr><td>Disc 1/02   スカート、ひらり (2015 BEST ver.).flac</td><td>31.16 MB</td></tr><tr><td>Disc 1/03   会いたかった.flac</td><td>29.94 MB</td></tr><tr><td>Disc 1/04   制服が邪魔をする.flac</td><td>36.75 MB</td></tr><tr><td>Disc 1/05   軽蔑していた愛情.flac</td><td>32.90 MB</td></tr><tr><td>Disc 1/06   BINGO!.flac</td><td>30.87 MB</td></tr><tr><td>Disc 1/07   僕の太陽.flac</td><td>38.22 MB</td></tr><tr><td>Disc 1/08   夕陽を見ているか.flac</td><td>37.51 MB</td></tr><tr><td>Disc 1/09   ロマンス、イラネ.flac</td><td>36.26 MB</td></tr><tr><td>Disc 1/0 と1の間.cue</td><td>2.21 KB</td></tr><tr><td>Disc 1/10   桜の花びらたち2008.flac</td><td>40.45 MB</td></tr><tr><td>Disc 1/11   Baby! Baby! Baby!.flac</td><td>32.20 MB</td></tr><tr><td>Disc 1/12   大声ダイヤモンド.flac</td><td>32.64 MB</td></tr><tr><td>Disc 1/13   10年桜.flac</td><td>33.55 MB</td></tr><tr><td>Disc 1/14   涙サプライズ!.flac</td><td>37.40 MB</td></tr><tr><td>Disc 1/15   言い訳Maybe.flac</td><td>33.09 MB</td></tr><tr><td>Disc 1/AKB48   0と1の間.log</td><td>14.93 KB</td></tr><tr><td>Disc 1/AKB48   0と1の間.m3u</td><td>824.00 B</td></tr><tr><td>Disc 1/cover.jpg</td><td>172.69 KB</td></tr><tr><td>Disc 2/01   RIVER.flac</td><td>38.91 MB</td></tr><tr><td>Disc 2/02   桜の栞.flac</td><td>24.61 MB</td></tr><tr><td>Disc 2/03   ポニーテールとシュシュ.flac</td><td>35.08 MB</td></tr><tr><td>Disc 2/04   ヘビーローテーション.flac</td><td>36.93 MB</td></tr><tr><td>Disc 2/05   Beginner.flac</td><td>33.17 MB</td></tr><tr><td>Disc 2/06   チャンスの順番.flac</td><td>34.18 MB</td></tr><tr><td>Disc 2/07   桜の木になろう.flac</td><td>37.95 MB</td></tr><tr><td>Disc 2/08   Everyday、カチューシャ.flac</td><td>43.67 MB</td></tr><tr><td>Disc 2/09   フライングゲット.flac</td><td>34.34 MB</td></tr><tr><td>Disc 2/0と1の間.cue</td><td>2.30 KB</td></tr><tr><td>Disc 2/10   風は吹いている.flac</td><td>29.87 MB</td></tr><tr><td>Disc 2/11   上からマリコ.flac</td><td>36.49 MB</td></tr><tr><td>Disc 2/12   GIVE ME FIVE!.flac</td><td>40.33 MB</td></tr><tr><td>Disc 2/13   真夏のSounds good!.flac</td><td>37.71 MB</td></tr><tr><td>Disc 2/14   ギンガムチェック.flac</td><td>43.51 MB</td></tr><tr><td>Disc 2/15   UZA.flac</td><td>39.81 MB</td></tr><tr><td>Disc 2/16   永遠プレッシャー.flac</td><td>38.46 MB</td></tr><tr><td>Disc 2/AKB48   0と1の間.log</td><td>15.64 KB</td></tr><tr><td>Disc 2/AKB48   0と1 の間.m3u</td><td>821.00 B</td></tr><tr><td>Disc 2/cover.jpg</td><td>172.69 KB</td></tr><tr><td>Disc 3/01   So long!.flac</td><td>43.87 MB</td></tr><tr><td>Disc 3/02   さよならクロ ール.flac</td><td>40.00 MB</td></tr><tr><td>Disc 3/03   恋するフォーチュンクッキー.flac</td><td>34.52 MB</td></tr><tr><td>Disc 3/04   ハート・エレキ.flac</td><td>37.72 MB</td></tr><tr><td>Disc 3/05   鈴懸木の道で「君の微笑みを夢に見る」と言ってしまったら僕たちの関係はどうかわってしまうのか、僕なりに何日か考えた上でのやや気恥ずかしい結論のようなもの.flac</td><td>41.81 MB</td></tr><tr><td>Disc 3/06   前しか向かねえ.flac</td><td>31.48 MB</td></tr><tr><td>Disc 3/07   ラブラドール・レトリバー.flac</td><td>33.86 MB</td></tr><tr><td>Disc 3/08   心のプラカード.flac</td><td>31.10 MB</td></tr><tr><td>Disc 3/09   希望的リフレイン.flac</td><td>40.53 MB</td></tr><tr><td>Disc 3/0と1の間.cue</td><td>2.28 KB</td></tr><tr><td>Disc 3/10   Green Flash.flac</td><td>31.73 MB</td></tr><tr><td>Disc 3/11   僕たちは戦わない.flac</td><td>44.29 MB</td></tr><tr><td>Disc 3/12   ハロウィーン・ナイト.flac</td><td>42.48 MB</td></tr><tr><td>Disc 3/13   クリスマスイブに泣かないように.flac</td><td>38.86 MB</td></tr><tr><td>Disc 3/14   始まりの雪.flac</td><td>32.24 MB</td></tr><tr><td>Disc 3/15   ロザリオ.flac</td><td>30.82 MB</td></tr><tr><td>Disc 3/AKB48   0と1の間.log</td><td>14.95 KB</td></tr><tr><td>Disc 3/AKB48   0と1の間.m3u</td><td>915.00 B</td></tr><tr><td>Disc 3/cover.jpg</td><td>172.69 KB</td></tr></tbody></table>                      Peer List: (<a href="#" id="swapPeer_266832" onclick="return swapPeerList('266832', '1744216480', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_266832" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_266832" onclick="return swapSnatchList('266832', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_266832" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=266841&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=266841" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('266841');">» FLAC / Lossless / CD / Million Singles - 2015 / <strong>Freeleech!</strong></a>
                                </td>
                                <td class="nobr">1.05 GB</td>
                                <td>393</td>
                                <td>15</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_266841">
                <td colspan="5">

                                        <blockquote>
                        Uploaded by <a href="user.php?id=129451">Nefarious</a>  on <span title="7 years, 2 months, 3 weeks ago">Dec 03 2015, 06:57</span>                          </blockquote>
                                        <blockquote>Ripped from my own copy.</blockquote>                                       <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>Disc 1/01   Beginner.flac</td><td>33.17 MB</td></tr><tr><td>Disc 1/02   桜の木になろう.flac</td><td>37.95 MB</td></tr><tr><td>Disc 1/03   Everyday、カチューシャ.flac</td><td>43.67 MB</td></tr><tr><td>Disc 1/04   フライングゲット.flac</td><td>34.34 MB</td></tr><tr><td>Disc 1/05   風は吹いている.flac</td><td>29.87 MB</td></tr><tr><td>Disc 1/06   上からマリコ.flac</td><td>36.49 MB</td></tr><tr><td>Disc 1/07   GIVE ME FIVE!.flac</td><td>40.33 MB</td></tr><tr><td>Disc 1/08   真夏のSounds good!.flac</td><td>37.71 MB</td></tr><tr><td>Disc 1/09   ギンガムチェック.flac</td><td>43.51 MB</td></tr><tr><td>Disc 1/0と1の間.cue</td><td>2.18 KB</td></tr><tr><td>Disc 1/10   UZA.flac</td><td>39.81 MB</td></tr><tr><td>Disc 1/11   永遠プレッシャー.flac</td><td>38.46 MB</td></tr><tr><td>Disc 1/12   So long!.flac</td><td>43.87 MB</td></tr><tr><td>Disc 1/13   さよならクロール.flac</td><td>40.00 MB</td></tr><tr><td>Disc 1/14   恋するフォーチュンクッキー.flac</td><td>34.52 MB</td></tr><tr><td>Disc 1/15   ハート・エレキ.flac</td><td>37.72 MB</td></tr><tr><td>Disc 1/AKB48   0と1の間.log</td><td>14.87 KB</td></tr><tr><td>Disc 1/AKB48   0と1の間.m3u</td><td>787.00 B</td></tr><tr><td>Disc 1/cover.jpg</td><td>160.12 KB</td></tr><tr><td>Disc 2/01   鈴懸木の道で「君の微笑みを夢に見る」と言ってしまったら僕たちの関係はどうかわってしまうのか、僕なりに何日か考えた上でのやや気恥ずかしい結論のようなもの.flac</td><td>41.81 MB</td></tr><tr><td>Disc 2/02   前しか向かねえ.flac</td><td>31.48 MB</td></tr><tr><td>Disc 2/03   ラブラドール・レトリバー.flac</td><td>33.86 MB</td></tr><tr><td>Disc 2/04   心のプラカード.flac</td><td>31.10 MB</td></tr><tr><td>Disc 2/05   希望的リフレイン.flac</td><td>40.53 MB</td></tr><tr><td>Disc 2/06   Green Flash.flac</td><td>31.73 MB</td></tr><tr><td>Disc 2/07   僕たちは戦わない.flac</td><td>44.29 MB</td></tr><tr><td>Disc 2/08   ハロウィーン・ナイト.flac</td><td>42.48 MB</td></tr><tr><td>Disc 2/09   Clap.flac</td><td>33.68 MB</td></tr><tr><td>Disc 2/0と1の間.cue</td><td>2.16 KB</td></tr><tr><td>Disc 2/10   愛の使者.flac</td><td>32.78 MB</td></tr><tr><td>Disc 2/11   ミュージックジャンキー.flac</td><td>30.70 MB</td></tr><tr><td>Disc 2/12   泣き言タイム.flac</td><td>34.58 MB</td></tr><tr><td>Disc 2/13   一生の間に何人と出逢えるのだろう.flac</td><td>37.12 MB</td></tr><tr><td>Disc 2/14   LOVE ASH.flac</td><td>35.71 MB</td></tr><tr><td>Disc 2/AKB48   0と1の間.log</td><td>14.21 KB</td></tr><tr><td>Disc 2/AKB48   0と1の間.m3u</td><td>859.00 B</td></tr><tr><td>Disc 2/cover.jpg</td><td>160.12 KB</td></tr></tbody></table>                  Peer List: (<a href="#" id="swapPeer_266841" onclick="return swapPeerList('266841', '1125791289', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_266841" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_266841" onclick="return swapSnatchList('266841', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_266841" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=266856&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=266856" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('266856');">» FLAC / Lossless / CD / No.1 Singles - 2015 / <strong>Freeleech!</strong></a>
                                </td>
                                <td class="nobr">1.11 GB</td>
                                <td>454</td>
                                <td>13</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_266856">
                <td colspan="5">

                                        <blockquote>
                        Uploaded by <a href="user.php?id=129451">Nefarious</a>  on <span title="7 years, 2 months, 3 weeks ago">Dec 03 2015, 09:58</span>                          </blockquote>
                                        <blockquote>Ripped from my own copy.</blockquote>                                       <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>Disc 1/01   RIVER.flac</td><td>38.91 MB</td></tr><tr><td>Disc 1/02   桜の栞.flac</td><td>24.61 MB</td></tr><tr><td>Disc 1/03   ポニーテールとシュシュ.flac</td><td>35.08 MB</td></tr><tr><td>Disc 1/04   ヘビーローテーション.flac</td><td>36.93 MB</td></tr><tr><td>Disc 1/05   Beginner.flac</td><td>33.17 MB</td></tr><tr><td>Disc 1/06   チャンスの順番.flac</td><td>34.18 MB</td></tr><tr><td>Disc 1/07   桜の木になろう.flac</td><td>37.95 MB</td></tr><tr><td>Disc 1/08   Everyday、カチューシャ.flac</td><td>43.67 MB</td></tr><tr><td>Disc 1/09   フライングゲット.flac</td><td>34.34 MB</td></tr><tr><td>Disc 1/0と1の間.cue</td><td>2.30 KB</td></tr><tr><td>Disc 1/10   風は吹いている.flac</td><td>29.87 MB</td></tr><tr><td>Disc 1/11   上からマリコ.flac</td><td>36.49 MB</td></tr><tr><td>Disc 1/12   GIVE ME FIVE!.flac</td><td>40.33 MB</td></tr><tr><td>Disc 1/13   真夏のSounds good!.flac</td><td>37.71 MB</td></tr><tr><td>Disc 1/14   ギンガムチェック.flac</td><td>43.51 MB</td></tr><tr><td>Disc 1/15   UZA.flac</td><td>39.81 MB</td></tr><tr><td>Disc 1/16   永遠プレッシャー.flac</td><td>38.46 MB</td></tr><tr><td>Disc 1/AKB48   0と1の間.log</td><td>15.52 KB</td></tr><tr><td>Disc 1/AKB48   0と1の間.m3u</td><td>821.00 B</td></tr><tr><td>Disc 1/cover.jpg</td><td>154.13 KB</td></tr><tr><td>Disc 2/01   So long!.flac</td><td>43.87 MB</td></tr><tr><td>Disc 2/02   さよならクロール.flac</td><td>40.00 MB</td></tr><tr><td>Disc 2/03   恋するフォーチュンクッキー.flac</td><td>34.52 MB</td></tr><tr><td>Disc 2/04   ハート・エレキ.flac</td><td>37.72 MB</td></tr><tr><td>Disc 2/05   鈴懸木の道で「君の微笑みを夢に見る」と言ってしまったら僕たちの関係はどうかわってしまうのか、僕なりに何日か考えた上でのやや気恥ずかしい結論のような もの.flac</td><td>41.81 MB</td></tr><tr><td>Disc 2/06   前しか向かねえ.flac</td><td>31.48 MB</td></tr><tr><td>Disc 2/07   ラブラドール・レトリバー.flac</td><td>33.86 MB</td></tr><tr><td>Disc 2/08   心のプラカード.flac</td><td>31.10 MB</td></tr><tr><td>Disc 2/09   希望的リフレイン.flac</td><td>40.53 MB</td></tr><tr><td>Disc 2/0と1の間.cue</td><td>2.31 KB</td></tr><tr><td>Disc 2/10   Green Flash.flac</td><td>31.73 MB</td></tr><tr><td>Disc 2/11   僕たちは戦わない.flac</td><td>44.29 MB</td></tr><tr><td>Disc 2/12   ハロウィーン・ナイト.flac</td><td>42.49 MB</td></tr><tr><td>Disc 2/13   やさしくありたい.flac</td><td>27.94 MB</td></tr><tr><td>Disc 2/14   トイプードルと君の物語.flac</td><td>41.34 MB</td></tr><tr><td>Disc 2/15   あの頃、好きだった人.flac</td><td>30.42 MB</td></tr><tr><td>Disc 2/AKB48   0と1の間.log</td><td>14.90 KB</td></tr><tr><td>Disc 2/AKB48   0と1の間.m3u</td><td>925.00 B</td></tr><tr><td>Disc 2/cover.jpg</td><td>154.13 KB</td></tr></tbody></table>                      Peer List: (<a href="#" id="swapPeer_266856" onclick="return swapPeerList('266856', '1193753704', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_266856" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_266856" onclick="return swapSnatchList('266856', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_266856" style="text-align: center"></div>

                                </td>
                        </tr>
                </tbody>"""
    date = "20151118"

    assert get_release_data(torrentids=torrent_ids_whole_group, torrent_table=torrent_table, date=date)\
           == {
  "372210": {
    "slashdata": [
      "Ogg",
      "128 (VBR)",
      "CD"
    ],
    "uploaddate": "Aug 08 2018, 21:06",
    "size_no_units": "211.94",
    "size_units": "MB",
    "completed": "6",
    "seeders": "0",
    "leechers": "0"
  },
  "265408": {
    "slashdata": [
      "MP4",
      "DVD",
      "Complete Singles (handshake) - 2015"
    ],
    "uploaddate": "Nov 17 2015, 11:59",
    "size_no_units": "1.36",
    "size_units": "GB",
    "completed": "111",
    "seeders": "1",
    "leechers": "0"
  },
  "265168": {
    "slashdata": [
      "MP3",
      "320",
      "CD",
      "Complete Singles - 2015"
    ],
    "uploaddate": "Nov 14 2015, 11:06",
    "size_no_units": "492.00",
    "size_units": "MB",
    "completed": "1,531",
    "seeders": "10",
    "leechers": "0"
  },
  "266844": {
    "slashdata": [
      "MP3",
      "320",
      "CD",
      "Million Singles - 2015"
    ],
    "uploaddate": "Dec 03 2015, 07:43",
    "size_no_units": "320.12",
    "size_units": "MB",
    "completed": "798",
    "seeders": "14",
    "leechers": "1"
  },
  "266857": {
    "slashdata": [
      "MP3",
      "320",
      "CD",
      "No.1 Singles - 2015"
    ],
    "uploaddate": "Dec 03 2015, 09:58",
    "size_no_units": "340.05",
    "size_units": "MB",
    "completed": "727",
    "seeders": "15",
    "leechers": "0"
  },
  "309925": {
    "slashdata": [
      "MP3",
      "V0 (VBR)",
      "CD",
      "Complete Singles - 2015"
    ],
    "uploaddate": "Dec 23 2016, 07:58",
    "size_no_units": "418.47",
    "size_units": "MB",
    "completed": "24",
    "seeders": "0",
    "leechers": "1"
  },
  "267035": {
    "slashdata": [
      "ISO",
      "Lossless",
      "DVD"
    ],
    "uploaddate": "Dec 05 2015, 07:44",
    "size_no_units": "6.69",
    "size_units": "GB",
    "completed": "269",
    "seeders": "2",
    "leechers": "0"
  },
  "350825": {
    "slashdata": [
      "FLAC",
      "24bit 96khz",
      "WEB"
    ],
    "uploaddate": "Jan 25 2018, 11:42",
    "size_no_units": "6.95",
    "size_units": "GB",
    "completed": "209",
    "seeders": "13",
    "leechers": "0"
  },
  "266249": {
    "slashdata": [
      "FLAC",
      "Lossless",
      "CD",
      "Theater Edition - 2015"
    ],
    "uploaddate": "Nov 27 2015, 17:29",
    "size_no_units": "996.26",
    "size_units": "MB",
    "completed": "314",
    "seeders": "8",
    "leechers": "0"
  },
  "266832": {
    "slashdata": [
      "FLAC",
      "Lossless",
      "CD",
      "Complete Singles - 2015"
    ],
    "uploaddate": "Dec 03 2015, 05:45",
    "size_no_units": "1.62",
    "size_units": "GB",
    "completed": "925",
    "seeders": "23",
    "leechers": "0"
  },
  "266841": {
    "slashdata": [
      "FLAC",
      "Lossless",
      "CD",
      "Million Singles - 2015"
    ],
    "uploaddate": "Dec 03 2015, 06:57",
    "size_no_units": "1.05",
    "size_units": "GB",
    "completed": "393",
    "seeders": "15",
    "leechers": "0"
  },
  "266856": {
    "slashdata": [
      "FLAC",
      "Lossless",
      "CD",
      "No.1 Singles - 2015"
    ],
    "uploaddate": "Dec 03 2015, 09:58",
    "size_no_units": "1.11",
    "size_units": "GB",
    "completed": "454",
    "seeders": "13",
    "leechers": "0"
  }
}

def test_get_release_data_group_273366() -> None:
    """
    Test Freeleech remastered in a video group, issue #oldrepo43
    """
    torrent_ids_whole_group = []
    torrent_table = """
    <tbody><tr class="colhead_dark">
                                <td width="80%"><strong>Torrents</strong></td>
                                <td><strong>Size</strong></td>
                                <td class="sign"><img alt="Snatches" src="static/styles/layer_cake/images/snatched.png" title="Snatches"/></td>
                                <td class="sign"><img alt="Seeders" src="static/styles/layer_cake/images/seeders.png" title="Seeders"/></td>
                                <td class="sign"><img alt="Leechers" src="static/styles/layer_cake/images/leechers.png" title="Leechers"/></td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=435401&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=435401" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('435401');">» MPEG2 / HDTV / M-ON! HD - <strong>Freeleech!</strong></a>
                                </td>
                                <td class="nobr">311.93 MB</td>
                                <td>67</td>
                                <td>5</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_435401">
                <td colspan="5">

                                        <blockquote>
                        Uploaded by <a href="user.php?id=198954">Nachti</a>  on <span title="2 years, 11 months, 2 weeks ago">Mar 11 2020, 20:24</span>                            </blockquote>
                                        <blockquote>Great thanks goes to Mattthecat!!<br/>
<br/>
<img alt="https://i.imgur.com/bo1zzAH.jpg" onclick="Scale(this);" onload="Scale(this);" src="https://i.imgur.com/bo1zzAH.jpg"/></blockquote>                                    <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>AKB48   Jiwaru DAYS [1440x1080 MPEG2 M ON! HD].ts</td><td>311.93 MB</td></tr></tbody></table>                      Peer List: (<a href="#" id="swapPeer_435401" onclick="return swapPeerList('435401', '327077888', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_435401" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_435401" onclick="return swapSnatchList('435401', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_435401" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=393883&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=393883" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('393883');">» MP4 / WEB / YouTube (1080p) - 2019</a>
                                </td>
                                <td class="nobr">140.88 MB</td>
                                <td>81</td>
                                <td>3</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_393883">
                <td colspan="5">

                                                        <blockquote>
                                                New ratio after downloading (without uploading): <span class="r50">11.01</span><br/>
                                                <em>Estimated Calculation. This assumes you're not downloading any other torrent.</em>
                                        </blockquote>
                                                            <blockquote>
                        Uploaded by <a href="user.php?id=202239">leonrdf</a>  on <span title="4 years, 3 days, 3 hours ago">Feb 26 2019, 04:36</span>                              </blockquote>
                                                                                <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>【MV】 ジワるDAYS   AKB48.mp4</td><td>140.88 MB</td></tr></tbody></table>                      Peer List: (<a href="#" id="swapPeer_393883" onclick="return swapPeerList('393883', '147725312', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_393883" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_393883" onclick="return swapSnatchList('393883', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_393883" style="text-align: center"></div>

                                </td>
                        </tr>
                        <tr class="group_torrent" style="font-weight: normal;">
                                <td>
                                        <span>[
                                                <a href="torrents.php?action=download&amp;id=394173&amp;authkey=00000000000000000000000000000000&amp;torrent_pass=11111111111111111111111111111111" title="Download">DL</a>
                                                |                                               <a href="reports.php?action=report&amp;id=394173" title="Report">RP</a>

                                                                                        ]</span>
                                        <a href="#" onclick="return swapTorrent('394173');">» h264 / HDTV / SSTV - <strong>Freeleech!</strong></a>
                                </td>
                                <td class="nobr">308.80 MB</td>
                                <td>213</td>
                                <td>9</td>
                                <td>0</td>
                        </tr>

                <tr class="pad hide" id="torrent_394173">
                <td colspan="5">

                                        <blockquote>
                        Uploaded by <a href="user.php?id=181287">Nakiame</a>  on <span title="4 years, 12 hours and 25 minutes ago">Feb 28 2019, 20:04</span>                      </blockquote>
                                        <blockquote><img alt="https://i.imgur.com/qgYR059.jpg" onclick="Scale(this);" onload="Scale(this);" src="https://i.imgur.com/qgYR059.jpg"/></blockquote>                                    <table style="overflow-x:auto;"><tbody><tr class="colhead_dark"><td><strong>Filename</strong></td><td><strong>Size</strong></td></tr><tr><td>AKB48   Jiwaru DAYS [1440x1080i h264 SSTV].ts</td><td>308.80 MB</td></tr></tbody></table>                      Peer List: (<a href="#" id="swapPeer_394173" onclick="return swapPeerList('394173', '323805184', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_peerlist_394173" style="text-align: center"></div><br/>
                        Snatch List: (<a href="#" id="swapSnatch_394173" onclick="return swapSnatchList('394173', 'Show', 'Hide');">Show</a>)<br/>
                        <div id="ajax_snatchlist_394173" style="text-align: center"></div>

                                </td>
                        </tr>
                </tbody>"""
    date = "20190313"

    assert get_release_data(torrentids=torrent_ids_whole_group, torrent_table=torrent_table, date=date)\
           == {
  "435401": {
    "slashdata": [
      "MPEG2",
      "HDTV",
      "M-ON! HD - 2019"
    ],
    "uploaddate": "Mar 11 2020, 20:24",
    "size_no_units": "311.93",
    "size_units": "MB",
    "completed": "67",
    "seeders": "5",
    "leechers": "0"
  },
  "393883": {
    "slashdata": [
      "MP4",
      "WEB",
      "YouTube (1080p) - 2019"
    ],
    "uploaddate": "Feb 26 2019, 04:36",
    "size_no_units": "140.88",
    "size_units": "MB",
    "completed": "81",
    "seeders": "3",
    "leechers": "0"
  },
  "394173": {
    "slashdata": [
      "h264",
      "HDTV",
      "SSTV - 2019"
    ],
    "uploaddate": "Feb 28 2019, 20:04",
    "size_no_units": "308.80",
    "size_units": "MB",
    "completed": "213",
    "seeders": "9",
    "leechers": "0"
  }
}

