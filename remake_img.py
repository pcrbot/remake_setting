import os
import random

from nonebot.exceptions import CQHttpError

from hoshino import R, Service, priv
from hoshino.util import FreqLimiter, DailyNumberLimiter

_max = 3
EXCEED_NOTICE = f'接受现实吧，不要再重开啦～ 要么等明早5点后再来吧'
_nlmt = DailyNumberLimiter(_max)
_flmt = FreqLimiter(5)

sv_help = '''
| 重开设定
- 重开
'''

sv = Service(
    name='重开设定',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.ADMIN,  # 管理权限
    visible=True,  # False隐藏
    enable_on_default=True,  # 是否默认启用
    bundle='娱乐',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


@sv.on_fullmatch(["帮助重开设定"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


remake_folder = R.img('remake_img/').path


def remake_gener():
    while True:
        filelist = os.listdir(remake_folder)
        random.shuffle(filelist)
        for filename in filelist:
            if os.path.isfile(os.path.join(remake_folder, filename)):
                yield R.img('remake_img/', filename)


remake_gener = remake_gener()


def get_remake():
    return remake_gener.__next__()


@sv.on_fullmatch('重开')
async def remake(bot, ev):
    """随机叫一份图片，对每个用户有冷却时间"""
    uid = ev['user_id']
    if not _nlmt.check(uid):
        await bot.send(ev, EXCEED_NOTICE, at_sender=True)
        return
    if not _flmt.check(uid):
        await bot.send(ev, '您获取得太快了，请稍候再来', at_sender=True)
        return
    _flmt.start_cd(uid)
    _nlmt.increase(uid)

    # conditions all ok, send a remake.
    pic = get_remake()
    try:
        await bot.send(ev, pic.cqcode)
    except CQHttpError:
        sv.logger.error(f"发送图片{pic.path}失败")
        try:
            await bot.send(ev, '图片被拦截了...')
        except:
            pass
