import asyncio
import os
from random import randint
from typing import Union
from uuid import uuid4

from youtubesearchpython.__future__ import VideosSearch

import config
from Oneforall import Carbon, YouTube, app
from Oneforall.core.call import Hotty
from Oneforall.misc import db
from Oneforall.utils.database import add_active_video_chat, is_active_chat
from Oneforall.utils.exceptions import AssistantErr
from Oneforall.utils.inline import close_markup
from Oneforall.utils.inline.rich import (
    release_mystic,
    send_now_playing_rich,
    send_queue_rich,
)
from Oneforall.utils.stream.queue import put_queue, put_queue_index


async def _fetch(_, chat_id, vidid, mystic, video):
    status = True if video else None
    task = asyncio.ensure_future(
        YouTube.download(vidid, mystic, videoid=True, video=status)
    )
    try:
        file_path, direct = await task
    except Exception:
        file_path, direct = None, False
    if not file_path:
        raise AssistantErr(_["play_14"] if "play_14" in _ else "Download failed.")
    return file_path, direct


async def _announce_queue(_, chat_id, original_chat_id, mystic, title, duration_min, user_name):
    position = len(db.get(chat_id)) - 1
    qid = uuid4().hex[:8]
    db[chat_id][-1]["qid"] = qid
    caption = _["queue_4"].format(position, title[:27], duration_min, user_name)
    await send_queue_rich(
        app,
        chat_id,
        original_chat_id,
        caption,
        qid,
        replace=mystic,
    )
    return position


async def stream(
    _,
    mystic,
    user_id,
    result,
    chat_id,
    user_name,
    original_chat_id,
    video: Union[bool, str] = None,
    streamtype: Union[bool, str] = None,
    spotify: Union[bool, str] = None,
    forceplay: Union[bool, str] = None,
):
    outcome = await _stream(
        _,
        mystic,
        user_id,
        result,
        chat_id,
        user_name,
        original_chat_id,
        video,
        streamtype,
        spotify,
        forceplay,
    )
    await release_mystic(mystic)
    return outcome


async def _stream(
    _,
    mystic,
    user_id,
    result,
    chat_id,
    user_name,
    original_chat_id,
    video: Union[bool, str] = None,
    streamtype: Union[bool, str] = None,
    spotify: Union[bool, str] = None,
    forceplay: Union[bool, str] = None,
):
    if not result:
        return
    if forceplay:
        await Hotty.force_stop_stream(chat_id)

    if streamtype == "playlist":
        msg = f"{_['play_19']}\n\n"
        count = 0
        for search in result:
            if int(count) == config.PLAYLIST_FETCH_LIMIT:
                continue
            try:
                (
                    title,
                    duration_min,
                    duration_sec,
                    thumbnail,
                    vidid,
                ) = await YouTube.details(search, False if spotify else True)
            except Exception:
                continue
            if str(duration_min) == "None" or duration_sec > config.DURATION_LIMIT:
                continue
            if await is_active_chat(chat_id):
                await put_queue(
                    chat_id,
                    original_chat_id,
                    f"vid_{vidid}",
                    title,
                    duration_min,
                    user_name,
                    vidid,
                    user_id,
                    "video" if video else "audio",
                )
                position = len(db.get(chat_id)) - 1
                count += 1
                msg += f"{count}. {title[:70]}\n"
                msg += f"{_['play_20']} {position}\n\n"
            else:
                if not forceplay:
                    db[chat_id] = []
                status = True if video else None
                thumb_task = asyncio.ensure_future(get_thumb(vidid))
                file_path, direct = await _fetch(_, chat_id, vidid, mystic, video)
                await Hotty.join_call(
                    chat_id,
                    original_chat_id,
                    file_path,
                    video=status,
                    image=thumbnail,
                )
                await put_queue(
                    chat_id,
                    original_chat_id,
                    file_path if direct else f"vid_{vidid}",
                    title,
                    duration_min,
                    user_name,
                    vidid,
                    user_id,
                    "video" if video else "audio",
                    forceplay=forceplay,
                )
                img = await thumb_task
                caption = _["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{vidid}",
                    title[:23],
                    duration_min,
                    user_name,
                )
                run = await send_now_playing_rich(
                    app,
                    chat_id,
                    original_chat_id,
                    img,
                    caption,
                    replace=mystic,
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"
        if count == 0:
            return
        else:
            link = "https://bin.roohi.me"
            lines = msg.count("\n")
            car = os.linesep.join(msg.split(os.linesep)[:17]) if lines >= 17 else msg
            carbon = await Carbon.generate(car, randint(100, 10000000))
            upl = close_markup(_)
            return await app.send_photo(
                original_chat_id,
                photo=carbon,
                caption=_["play_21"].format(position, link),
                reply_markup=upl,
            )

    elif streamtype == "youtube":
        link = result["link"]
        vidid = result["vidid"]
        title = (result["title"]).title()
        duration_min = result["duration_min"]
        thumbnail = result["thumb"]
        status = True if video else None
        thumb_task = (
            None
            if await is_active_chat(chat_id)
            else asyncio.ensure_future(get_thumb(vidid))
        )
        file_path, direct = await _fetch(_, chat_id, vidid, mystic, video)
        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                file_path if direct else f"vid_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
            )
            await _announce_queue(
                _, chat_id, original_chat_id, mystic, title, duration_min, user_name
            )
        else:
            if not forceplay:
                db[chat_id] = []
            await Hotty.join_call(
                chat_id,
                original_chat_id,
                file_path,
                video=status,
                image=thumbnail,
            )
            await put_queue(
                chat_id,
                original_chat_id,
                file_path if direct else f"vid_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
            )
            img = await (thumb_task if thumb_task else get_thumb(vidid))
            caption = _["stream_1"].format(
                f"https://t.me/{app.username}?start=info_{vidid}",
                title[:23],
                duration_min,
                user_name,
            )
            run = await send_now_playing_rich(
                app,
                chat_id,
                original_chat_id,
                img,
                caption,
                replace=mystic,
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "stream"

    elif streamtype == "soundcloud":
        file_path = result["filepath"]
        title = result["title"]
        duration_min = result["duration_min"]
        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "audio",
            )
            await _announce_queue(
                _, chat_id, original_chat_id, mystic, title, duration_min, user_name
            )
        else:
            if not forceplay:
                db[chat_id] = []
            await Hotty.join_call(chat_id, original_chat_id, file_path, video=None)
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "audio",
                forceplay=forceplay,
            )
            caption = _["stream_1"].format(
                config.SUPPORT_CHAT, title[:23], duration_min, user_name
            )
            run = await send_now_playing_rich(
                app,
                chat_id,
                original_chat_id,
                config.SOUNCLOUD_IMG_URL,
                caption,
                replace=mystic,
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"

    elif streamtype == "telegram":
        file_path = result["path"]
        link = result["link"]
        title = (result["title"]).title()
        duration_min = result["dur"]
        status = True if video else None
        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "video" if video else "audio",
            )
            await _announce_queue(
                _, chat_id, original_chat_id, mystic, title, duration_min, user_name
            )
        else:
            if not forceplay:
                db[chat_id] = []
            await Hotty.join_call(chat_id, original_chat_id, file_path, video=status)
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
            )
            if video:
                await add_active_video_chat(chat_id)
            thumb = config.TELEGRAM_VIDEO_URL if video else config.TELEGRAM_AUDIO_URL
            caption = _["stream_1"].format(link, title[:23], duration_min, user_name)
            run = await send_now_playing_rich(
                app,
                chat_id,
                original_chat_id,
                thumb,
                caption,
                replace=mystic,
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"

    elif streamtype == "live":
        link = result["link"]
        vidid = result["vidid"]
        title = (result["title"]).title()
        thumbnail = result["thumb"]
        duration_min = "Live Track"
        status = True if video else None
        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                f"live_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
            )
            await _announce_queue(
                _, chat_id, original_chat_id, mystic, title, duration_min, user_name
            )
        else:
            if not forceplay:
                db[chat_id] = []
            n, file_path = await YouTube.video(link)
            if n == 0:
                raise AssistantErr(_["str_3"])
            await Hotty.join_call(
                chat_id,
                original_chat_id,
                file_path,
                video=status,
                image=thumbnail if thumbnail else None,
            )
            await put_queue(
                chat_id,
                original_chat_id,
                f"live_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
            )
            img = await get_thumb(vidid)
            caption = _["stream_1"].format(
                f"https://t.me/{app.username}?start=info_{vidid}",
                title[:23],
                duration_min,
                user_name,
            )
            run = await send_now_playing_rich(
                app,
                chat_id,
                original_chat_id,
                img,
                caption,
                replace=mystic,
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"

    elif streamtype == "index":
        link = result
        title = "ɪɴᴅᴇx ᴏʀ ᴍ3ᴜ8 ʟɪɴᴋ"
        duration_min = "00:00"
        if await is_active_chat(chat_id):
            await put_queue_index(
                chat_id,
                original_chat_id,
                "index_url",
                title,
                duration_min,
                user_name,
                link,
                "video" if video else "audio",
            )
            await _announce_queue(
                _, chat_id, original_chat_id, mystic, title, duration_min, user_name
            )
        else:
            if not forceplay:
                db[chat_id] = []
            await Hotty.join_call(
                chat_id,
                original_chat_id,
                link,
                video=True if video else None,
            )
            await put_queue_index(
                chat_id,
                original_chat_id,
                "index_url",
                title,
                duration_min,
                user_name,
                link,
                "video" if video else "audio",
                forceplay=forceplay,
            )
            caption = _["stream_2"].format(user_name)
            run = await send_now_playing_rich(
                app,
                chat_id,
                original_chat_id,
                config.STREAM_IMG_URL,
                caption,
                replace=mystic,
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"


async def get_thumb(vidid):
    try:
        query = f"https://www.youtube.com/watch?v={vidid}"
        results = VideosSearch(query, limit=1)
        res = await results.next()
        for result in res["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            return thumbnail
    except Exception:
        pass
    return config.YOUTUBE_IMG_URL
