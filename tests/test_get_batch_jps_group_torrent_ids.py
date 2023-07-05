"""
Run tests for get_batch_jps_group_torrent_ids
"""

from jps2sm.batch import get_batch_jps_group_torrent_ids
from jps2sm.myloginsession import LoginParameters


def test_get_batch_jps_group_torrent_ids(requests_mock, mocker):
    """
    Test for get_batch_jps_group_torrent_ids
    """
    mocker.patch("time.sleep")

    batch_uploads = {'1063': ['1224'], '130227': ['174720'], '91773': ['121554'], '119706': ['159337'], '87690': ['115827'], '114106': ['151692'],
                     '108864': ['144602'], '114673': ['152469'], '130939': ['175776'], '108190': ['143670'], '130015': ['174847', '174872'],
                     '136907': ['185534', '185534', '184100'], '113119': ['150324'], '79469': ['103843'], '79467': ['103839'],
                     '110535': ['146718', '146718'], '145416': ['196465'], '142614': ['192311'], '142247': ['191765'], '28408': ['66628'],
                     '11841': ['98611'], '23555': ['27788'], '125721': ['167996'], '54258': ['67849'], '128377': ['172049'], '132140': ['177486'],
                     '131159': ['177484'], '126451': ['169122'], '127887': ['171307'], '128550': ['172288'], '129089': ['173011'],
                     '130535': ['175163'], '129241': ['173250'], '129549': ['173723'], '83467': ['109524'], '128062': ['171547'],
                     '126453': ['169125'], '127126': ['172431'], '127858': ['171271'], '129825': ['174118'], '126552': ['169273'],
                     '125680': ['167910'], '129331': ['173398'], '129729': ['174629'], '126567': ['169293'], '126558': ['169280'],
                     '129346': ['173410'], '130970': ['175796'], '126396': ['169034'], '130208': ['174694'], '127846': ['171257'],
                     '128980': ['172853'], '130389': ['174942'], '129165': ['175576'], '126554': ['169275'], '126170': ['168700'],
                     '130605': ['175282'], '130879': ['175651'], '126055': ['168544'], '125820': ['168177'], '126996': ['169988'],
                     '129755': ['174023'], '130659': ['175357'], '129095': ['173019'], '126684': ['169458'], '130856': ['175761'],
                     '127103': ['170163'], '130382': ['174991'], '126898': ['170306'], '128670': ['172443'], '126334': ['168953'],
                     '129580': ['173776'], '126455': ['169128'], '129658': ['173866'], '128683': ['172457'], '126285': ['168879'],
                     '128459': ['172155'], '129571': ['173765'], '128481': ['172193'], '130526': ['175142'], '125296': ['167348'],
                     '129418': ['173520'], '130469': ['175140'], '129734': ['173990'], '129750': ['174015'], '130294': ['174819'],
                     '129939': ['174282'], '130878': ['175650'], '128100': ['171615'], '129282': ['173297'], '128859': ['173672'],
                     '127236': ['172890'], '130335': ['174941'], '126553': ['169274'], '130811': ['175562'], '129707': ['173960']}

    # with open("user-page-snatched-userid-1", "r", encoding="utf-8") as user_page_snatched_userid_file:
    #    user_page_snatched_userid_1 = user_page_snatched_userid_file.read()
    with open("tests/user-page-snatched-userid-1-page-1", "r", encoding="utf-8") as user_page_snatched_userid_1_page_1_file:
        user_page_snatched_userid_1_page_1 = user_page_snatched_userid_1_page_1_file.read()
    with open("tests/user-page-snatched-userid-1-page-2", "r", encoding="utf-8") as user_page_snatched_userid_1_page_2_file:
        user_page_snatched_userid_1_page_2 = user_page_snatched_userid_1_page_2_file.read()

    requests_mock.post("https://jpopsuki.eu/login.php", text=LoginParameters.jps_success)  # Mock the initial login with requestsloginsession()

    # Use this when in a test not specifying last
    # requests_mock.get("https://jpopsuki.eu/torrents.php?type=snatched&userid=1", text=user_page_snatched_userid_1)
    requests_mock.get("https://jpopsuki.eu/torrents.php?page=1&order_by=s3&order_way=DESC&type=snatched&userid=1&disablegrouping=1",
                      text=user_page_snatched_userid_1_page_1)
    requests_mock.get("https://jpopsuki.eu/torrents.php?page=2&order_by=s3&order_way=DESC&type=snatched&userid=1&disablegrouping=1",
                      text=user_page_snatched_userid_1_page_2)

    assert get_batch_jps_group_torrent_ids(mode="snatched", user=1, first=1, last=2, sort="time", order="desc") == batch_uploads
