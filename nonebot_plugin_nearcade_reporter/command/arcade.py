from typing import Any, cast

from config import Config
from network import NearcadeHttp
from nonebot import get_driver, on_regex
from nonebot.params import RegexGroup

config = get_driver().config
nearcade = NearcadeHttp(config.api_token)

arcade_attendance = on_regex(Config.update_attendance_match.pattern, priority=5)

@arcade_attendance.handle()
async def _(groups: Any = RegexGroup()):
    groups = cast("dict[str, str]", groups)
    arcade_name = groups[Config.update_attendance_match.arcade_alias]
    attendance_count = int(
        groups[Config.update_attendance_match.attendance_count]
    )
    arcade_id, arcade = config.find_arcade_by_alias(arcade_name)
    if nearcade.update_attendance(
        arcade_id=arcade_id,
        source=arcade.arcade_source,
        games=[(arcade.default_game_id, attendance_count)],
    ):
      # todo: use reply_message from config
      ...
    else:
        await arcade_attendance.finish("更新失败，请稍后重试")
