from jps2sm.get_data import GetGroupData
from jps2sm.utils import get_valid_filename, GetConfig, HandleCfgOutputDirs
from pathlib import Path
from typing import Type

config = GetConfig()
output = HandleCfgOutputDirs(config.directories)


def save_sm_html_debug_output(content: str, torrent_group_data: Type[GetGroupData], jps_torrent_id: str) -> Path:
    """
    Save the html output from uploading the torrent to SM, for debug purposes

    """
    html_debug_output_filename = f"SMuploadresult." + \
                                 get_valid_filename(f"{torrent_group_data.artist[0]}.{torrent_group_data.title}.{torrent_group_data.date}."
                                                    f"JPS_ID{jps_torrent_id}") + \
                                 f".html"
    html_debug_output_path = Path(output.file_dir['html'], html_debug_output_filename)

    with open(html_debug_output_path, "w") as f:
        f.write(content)

    return html_debug_output_path
