from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg

arcade_attendence = on_command("机厅人数", aliases={"机厅人数"})

@arcade_attendence.handle()
async def _(message: Message = CommandArg()) -> None:
    args = message.extract_plain_text().strip().split(r"\s+")
    if not args:
        await arcade_attendence.finish("使用方法: 机厅人数 [机厅] [当前人数]")
