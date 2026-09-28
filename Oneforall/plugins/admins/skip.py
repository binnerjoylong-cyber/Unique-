from pyrogram import enums, filters, types
from pyrogram.types import Message

import config
from config import BANNED_USERS
from Oneforall import YouTube, app
from Oneforall.core.call import Hotty
from Oneforall.misc import db
from Oneforall.utils.database import get_loop
from Oneforall.utils.decorators import AdminRightsCheck
from Oneforall.utils.formatters import seconds_to_min
from Oneforall.utils.inline import close_markup
from Oneforall.utils.inline.rich import (
    deliver_rich,
    html_to_rich_blocks,
    send_now_playing_rich,
)
from Oneforall.utils.stream.autoclear import auto_clean
from Oneforall.utils.thumbnails import get_thumb


async def handle_autoplay_on_skip(chat_id, message, _):
    """Trigger next autoplay song if autoplay is ON when queue ends"""
    try:
        from Oneforall.plugins.misc.autoplay import (
            get_autoplay_mood,
            get_autoplay_recommendation,
            is_autoplay_on,
        )

        if await is_autoplay_on(chat_id):
            track_data, track_id = await get_autoplay_recommendation(chat_id)
            if track_data and track_id:
                mood_info = await get_autoplay_mood(chat_id)
                m_tag = mood_info.get("mood", "sad").title()
                l_tag = mood_info.get("language", "hindi").title()
                auto_requester = f"Autoplay [{m_tag} | {l_tag}]"
                title = track_data.get("title")
                dur_sec = track_data.get("duration_sec", 0)
                duration = seconds_to_min(dur_sec) or "03:00"

                # Clean previous autoplay card
                prev_auto_msg = getattr(Hotty, f"_auto_msg_{chat_id}", None)
                if prev_auto_msg:
                    try:
                        await prev_auto_msg.delete()
                    except Exception:
                        pass

                caption = (
                    "<blockquote><emoji id=5895705279416241926>🎲</emoji> <u><b>AUTOPLAY STREAMING</b></u></blockquote>\n\n"
                    "<blockquote expandable>"
                    f"🎵 <b>Track:</b> {title[:40]}\n"
                    f"⏱️ <b>Duration:</b> {duration}\n"
                    f"✨ <b>Vibe:</b> <code>{m_tag}</code> | <b>Language:</b> <code>{l_tag}</code>\n"
                    f"🤖 <b>Requested By:</b> <code>Autoplay Engine</code></blockquote>"
                )
                blocks = html_to_rich_blocks(caption)
                blocks.append(
                    types.InputRichBlockButtons(
                        buttons=[
                            types.RichMessageButton(
                                text="» Skip",
                                style=enums.ButtonStyle.PRIMARY,
                                callback_data=f"ADMIN Skip|{chat_id}",
                            ),
                            types.RichMessageButton(
                                text="❌ Disable Autoplay",
                                style=enums.ButtonStyle.DANGER,
                                callback_data=f"AutoPlay|{chat_id}",
                            ),
                        ]
                    )
                )
                auto_msg = await deliver_rich(app, chat_id, blocks)
                setattr(Hotty, f"_auto_msg_{chat_id}", auto_msg)

                db[chat_id] = [
                    {
                        "title": title,
                        "dur": duration,
                        "streamtype": "audio",
                        "by": auto_requester,
                        "chat_id": chat_id,
                        "file": f"vid_{track_id}",
                        "vidid": track_id,
                        "seconds": dur_sec,
                        "played": 0,
                    }
                ]
                return db.get(chat_id)
    except Exception as e:
        print(f"Skip Autoplay Error: {e}")
    return None


@app.on_message(
    filters.command(["skip", "cskip", "next", "cnext"]) & filters.group & ~BANNED_USERS
)
@AdminRightsCheck
async def skip(cli, message: Message, _, chat_id):
    if not len(message.command) < 2:
        loop = await get_loop(chat_id)
        if loop != 0:
            return await message.reply_text(_["admin_8"])
        state = message.text.split(None, 1)[1].strip()
        if state.isnumeric():
            state = int(state)
            check = db.get(chat_id)
            if check:
                count = len(check)
                if count > 2:
                    count = int(count - 1)
                    if 1 <= state <= count:
                        for x in range(state):
                            popped = None
                            try:
                                popped = check.pop(0)
                            except:
                                return await message.reply_text(_["admin_12"])
                            if popped:
                                await auto_clean(popped)
                            if not check:
                                check = await handle_autoplay_on_skip(chat_id, message, _)
                                if not check:
                                    try:
                                        await message.reply_text(
                                            text=_["admin_6"].format(
                                                message.from_user.mention,
                                                message.chat.title,
                                            ),
                                            reply_markup=close_markup(_),
                                        )
                                        await Hotty.stop_stream(chat_id)
                                    except:
                                        return
                                    break
                    else:
                        return await message.reply_text(_["admin_11"].format(count))
                else:
                    return await message.reply_text(_["admin_10"])
            else:
                return await message.reply_text(_["queue_2"])
        else:
            return await message.reply_text(_["admin_9"])
    else:
        check = db.get(chat_id)
        popped = None
        try:
            popped = check.pop(0)
            if popped:
                await auto_clean(popped)
            if not check:
                check = await handle_autoplay_on_skip(chat_id, message, _)
                if not check:
                    await message.reply_text(
                        text=_["admin_6"].format(
                            message.from_user.mention, message.chat.title
                        ),
                        reply_markup=close_markup(_),
                    )
                    try:
                        return await Hotty.stop_stream(chat_id)
                    except:
                        return
        except:
            check = await handle_autoplay_on_skip(chat_id, message, _)
            if not check:
                try:
                    await message.reply_text(
                        text=_["admin_6"].format(
                            message.from_user.mention, message.chat.title
                        ),
                        reply_markup=close_markup(_),
                    )
                    return await Hotty.stop_stream(chat_id)
                except:
                    return

    if not check:
        return

    queued = check[0]["file"]
    title = (check[0]["title"]).title()
    user = check[0]["by"]
    streamtype = check[0]["streamtype"]
    videoid = check[0]["vidid"]
    status = True if str(streamtype) == "video" else None
    db[chat_id][0]["played"] = 0
    exis = (check[0]).get("old_dur")
    if exis:
        db[chat_id][0]["dur"] = exis
        db[chat_id][0]["seconds"] = check[0]["old_second"]
        db[chat_id][0]["speed_path"] = None
        db[chat_id][0]["speed"] = 1.0

    if "live_" in queued:
        n, link = await YouTube.video(videoid, True)
        if n == 0:
            return await message.reply_text(_["admin_7"].format(title))
        try:
            image = await YouTube.thumbnail(videoid, True)
        except:
            image = None
        try:
            await Hotty.skip_stream(chat_id, link, video=status, image=image)
        except:
            return await message.reply_text(_["call_6"])
        img = await get_thumb(videoid)
        run = await send_now_playing_rich(
            app,
            chat_id,
            message.chat.id,
            img,
            _["stream_1"].format(
                f"https://t.me/{app.username}?start=info_{videoid}",
                title[:23],
                check[0]["dur"],
                user,
            ),
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "tg"

    elif "vid_" in queued:
        mystic = await message.reply_text(_["call_7"], disable_web_page_preview=True)
        file_path = None
        try:
            file_path, direct = await YouTube.download(
                videoid,
                mystic,
                videoid=True,
                video=status,
            )
        except:
            return await mystic.edit_text(_["call_6"])
        try:
            image = await YouTube.thumbnail(videoid, True)
        except:
            image = None
        try:
            if not file_path:
                raise Exception("YT download failed: media_path=None")

            await Hotty.skip_stream(
                chat_id,
                file_path,
                video=status,
                image=image,
            )
        except:
            return await mystic.edit_text(_["call_6"])

        img = await get_thumb(videoid)
        run = await send_now_playing_rich(
            app,
            chat_id,
            message.chat.id,
            img,
            _["stream_1"].format(
                f"https://t.me/{app.username}?start=info_{videoid}",
                title[:23],
                check[0]["dur"],
                user,
            ),
            replace=mystic,
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "stream"

    elif "index_" in queued:
        try:
            await Hotty.skip_stream(chat_id, videoid, video=status)
        except:
            return await message.reply_text(_["call_6"])
        run = await send_now_playing_rich(
            app,
            chat_id,
            message.chat.id,
            config.STREAM_IMG_URL,
            _["stream_2"].format(user),
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "tg"

    else:
        if videoid == "telegram":
            image = None
        elif videoid == "soundcloud":
            image = None
        else:
            try:
                image = await YouTube.thumbnail(videoid, True)
            except:
                image = None
        try:
            await Hotty.skip_stream(chat_id, queued, video=status, image=image)
        except:
            return await message.reply_text(_["call_6"])

        if videoid == "telegram":
            thumb_url = (
                config.TELEGRAM_AUDIO_URL
                if str(streamtype) == "audio"
                else config.TELEGRAM_VIDEO_URL
            )
            run = await send_now_playing_rich(
                app,
                chat_id,
                message.chat.id,
                thumb_url,
                _["stream_1"].format(
                    config.SUPPORT_CHAT, title[:23], check[0]["dur"], user
                ),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"

        elif videoid == "soundcloud":
            run = await send_now_playing_rich(
                app,
                chat_id,
                message.chat.id,
                config.SOUNCLOUD_IMG_URL,
                _["stream_1"].format(
                    config.SUPPORT_CHAT, title[:23], check[0]["dur"], user
                ),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"

        else:
            img = await get_thumb(videoid)
            run = await send_now_playing_rich(
                app,
                chat_id,
                message.chat.id,
                img,
                _["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{videoid}",
                    title[:23],
                    check[0]["dur"],
                    user,
                ),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "stream"
