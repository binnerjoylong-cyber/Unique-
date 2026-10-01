import math
import os
import random
import re
import aiohttp
from pyrogram import enums, errors, types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from Oneforall.misc import db
from Oneforall.core.mongo import mongodb
from Oneforall.utils.database import get_lang
from Oneforall.utils.formatters import seconds_to_min, time_to_seconds
from strings import get_string

autoplaydb = mongodb.autoplay
_consumed = set()


async def _lang(chat_id):
    return get_string(await get_lang(chat_id))


def _progress_line(played, dur):
    played_sec = time_to_seconds(played) if played else 0
    duration_sec = time_to_seconds(dur) if dur else 0
    percentage = (played_sec / duration_sec) * 100 if duration_sec else 0
    umm = math.floor(percentage)

    if 0 < umm <= 10:
        bar = "────────●"
    elif 10 < umm < 20:
        bar = "─●───────"
    elif 20 <= umm < 30:
        bar = "──●──────"
    elif 30 <= umm < 40:
        bar = "───●─────"
    elif 40 <= umm < 50:
        bar = "────●────"
    elif 50 <= umm < 60:
        bar = "─────●───"
    elif 60 <= umm < 70:
        bar = "──────●──"
    elif 70 <= umm < 80:
        bar = "───────●─"
    else:
        bar = "────────●"

    current_p = played or "00:00"
    current_d = dur or "00:00"
    return f"{current_p}  {bar}  {current_d}"


def _queue_len(chat_id):
    tracks = db.get(chat_id)
    return max(len(tracks) - 1, 0) if tracks else 0


def _btn(text, emoji_id=None, style=enums.ButtonStyle.DEFAULT, **kwargs):
    try:
        if emoji_id:
            return InlineKeyboardButton(
                text=text,
                icon_custom_emoji_id=int(emoji_id),
                style=style,
                **kwargs,
            )
        return InlineKeyboardButton(text=text, style=style, **kwargs)
    except TypeError:
        return InlineKeyboardButton(text=text, **kwargs)


async def _get_control_keyboard(chat_id, played=None, dur=None, playing=True):
    cur_played = played if played else "00:00"
    cur_dur = dur if dur else "00:00"
    q_len = _queue_len(chat_id)

    doc = await autoplaydb.find_one({"chat_id": chat_id})
    is_auto = doc.get("autoplay", False) if doc else False

    auto_text = "🟢 Autoplay On" if is_auto else "🔴 Autoplay Off"
    auto_style = enums.ButtonStyle.SUCCESS if is_auto else enums.ButtonStyle.DANGER

    toggle_btn = (
        _btn("II Pause", style=enums.ButtonStyle.SUCCESS, callback_data=f"ADMIN Pause|{chat_id}")
        if playing
        else _btn("▷ Resume", style=enums.ButtonStyle.SUCCESS, callback_data=f"ADMIN Resume|{chat_id}")
    )

    keyboard = [
        [
            _btn(_progress_line(cur_played, cur_dur), style=enums.ButtonStyle.DANGER, callback_data="GetTimer")
        ],
        [
            _btn("↺ Replay", style=enums.ButtonStyle.DEFAULT, callback_data=f"ADMIN Replay|{chat_id}"),
            toggle_btn,
            _btn("» Skip", style=enums.ButtonStyle.PRIMARY, callback_data=f"ADMIN Skip|{chat_id}"),
        ],
        [
            _btn("+ Playlist", style=enums.ButtonStyle.SUCCESS, callback_data=f"add_playlist|{chat_id}"),
            _btn(auto_text, style=auto_style, callback_data=f"open_autoplay_card|{chat_id}"),
            _btn(f"≡ Queue · {q_len}", style=enums.ButtonStyle.DEFAULT, callback_data=f"nowplaying_queue {chat_id}"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def _get_queue_keyboard(chat_id, qid):
    keyboard = [
        [
            _btn("▷ Play Now", style=enums.ButtonStyle.SUCCESS, callback_data=f"ADMIN PlayNow|{chat_id}_{qid}")
        ],
        [
            _btn("» Skip", style=enums.ButtonStyle.PRIMARY, callback_data=f"ADMIN Skip|{chat_id}"),
            _btn("⟲ End", style=enums.ButtonStyle.DANGER, callback_data=f"ADMIN Stop|{chat_id}"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


async def _download_photo_if_url(photo):
    if not photo or not isinstance(photo, str):
        return None
    if photo.startswith("http://") or photo.startswith("https://"):
        os.makedirs("cache", exist_ok=True)
        local_path = os.path.join("cache", f"thumb_{abs(hash(photo))}.jpg")
        if os.path.isfile(local_path) and os.path.getsize(local_path) > 0:
            return local_path
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(photo, timeout=5) as resp:
                    if resp.status == 200:
                        with open(local_path, "wb") as f:
                            f.write(await resp.read())
                        return local_path
        except Exception:
            return None
    if os.path.isfile(photo) and os.path.getsize(photo) > 0:
        return photo
    return None


def _clean_caption_html(caption_html: str) -> str:
    # Ensure closing tags are strictly valid Telegram HTML
    fixed = re.sub(r"</blockquote[^>]*>", "</blockquote>", caption_html, flags=re.IGNORECASE)
    # Ensure custom emoji tags are supported across forks
    fixed = re.sub(r"<tg-emoji\s+id=([^>]+)>", r"<emoji id=\1>", fixed, flags=re.IGNORECASE)
    fixed = re.sub(r"</tg-emoji>", r"</emoji>", fixed, flags=re.IGNORECASE)
    return fixed


async def send_now_playing_rich(client, chat_id, target_chat_id, photo, caption_html, replace=None):
    _ = await _lang(chat_id)
    local_photo = await _download_photo_if_url(photo)
    resolved_photo = local_photo or photo
    dur = db[chat_id][0].get("dur") if db.get(chat_id) else None

    clean_caption = _clean_caption_html(caption_html)
    reply_markup = await _get_control_keyboard(chat_id, played="00:00", dur=dur, playing=True)

    if replace:
        try:
            await replace.delete()
        except Exception:
            pass

    msg = None
    try:
        if resolved_photo:
            msg = await client.send_photo(
                chat_id=target_chat_id,
                photo=resolved_photo,
                caption=clean_caption,
                parse_mode=enums.ParseMode.HTML,
                reply_markup=reply_markup,
            )
        else:
            msg = await client.send_message(
                chat_id=target_chat_id,
                text=clean_caption,
                parse_mode=enums.ParseMode.HTML,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
            )
    except Exception:
        msg = await client.send_message(
            chat_id=target_chat_id,
            text=clean_caption,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )

    if db.get(chat_id):
        db[chat_id][0]["np_photo"] = resolved_photo
        db[chat_id][0]["np_caption"] = clean_caption
        db[chat_id][0]["mystic"] = msg

    return msg


async def send_queue_rich(client, chat_id, target_chat_id, caption_html, qid, replace=None):
    _ = await _lang(chat_id)
    clean_caption = _clean_caption_html(caption_html)
    reply_markup = _get_queue_keyboard(chat_id, qid)

    if replace:
        try:
            await replace.delete()
        except Exception:
            pass

    return await client.send_message(
        chat_id=target_chat_id,
        text=clean_caption,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )


async def release_mystic(mystic):
    if mystic is None:
        return
    try:
        await mystic.delete()
    except Exception:
        pass


async def update_now_playing_progress(mystic, chat_id, played, dur, playing=True):
    info = db.get(chat_id)
    if not info:
        return None
    caption_html = info[0].get("np_caption")
    if not caption_html or not mystic:
        return None

    reply_markup = await _get_control_keyboard(chat_id, played=played, dur=dur, playing=playing)
    try:
        return await mystic.edit_reply_markup(reply_markup=reply_markup)
    except Exception:
        return None


async def set_now_playing_state(chat_id, playing):
    info = db.get(chat_id)
    if not info:
        return None
    mystic = info[0].get("mystic")
    if not mystic:
        return None

    played = seconds_to_min(info[0].get("played", 0)) or "00:00"
    dur = info[0].get("dur")
    reply_markup = await _get_control_keyboard(chat_id, played=played, dur=dur, playing=playing)
    try:
        return await mystic.edit_reply_markup(reply_markup=reply_markup)
    except Exception:
        return None


async def update_now_playing_markup(client, chat_id: int, playing: bool = True):
    tracks = db.get(chat_id)
    if not tracks:
        return
    cur = tracks[0]
    msg = cur.get("mystic")
    dur = cur.get("dur")
    if not msg:
        return

    reply_markup = await _get_control_keyboard(chat_id, played="00:00", dur=dur, playing=playing)
    try:
        if isinstance(msg, types.Message):
            await msg.edit_reply_markup(reply_markup=reply_markup)
        else:
            await client.edit_message_reply_markup(chat_id=chat_id, message_id=msg, reply_markup=reply_markup)
    except Exception:
        pass


def rich_autoplay_mood_blocks(caption_html: str):
    caption = _clean_caption_html(caption_html)
    keyboard = [
        [
            InlineKeyboardButton("✨ Chill", callback_data="songconfig_mood:chill"),
            InlineKeyboardButton("⚡ Party", callback_data="songconfig_mood:party"),
        ],
        [
            InlineKeyboardButton("💔 Sad", callback_data="songconfig_mood:sad"),
            InlineKeyboardButton("💖 Romantic", callback_data="songconfig_mood:romantic"),
        ],
        [
            InlineKeyboardButton("✖ Close", callback_data="close_panel")
        ],
    ]
    return {"text": caption, "reply_markup": InlineKeyboardMarkup(keyboard)}


def rich_autoplay_language_blocks(caption_html: str):
    caption = _clean_caption_html(caption_html)
    keyboard = [
        [
            InlineKeyboardButton("🇮🇳 Hindi", callback_data="songconfig_language:hindi"),
            InlineKeyboardButton("🌐 English", callback_data="songconfig_language:english"),
        ],
        [
            InlineKeyboardButton("🎸 Punjabi", callback_data="songconfig_language:punjabi"),
            InlineKeyboardButton("💫 Haryanvi", callback_data="songconfig_language:haryanvi"),
        ],
        [
            InlineKeyboardButton("✖ Close", callback_data="close_panel")
        ],
    ]
    return {"text": caption, "reply_markup": InlineKeyboardMarkup(keyboard)}


# Compatibility wrappers
def caption_blocks(caption_html):
    return caption_html


def html_to_rich_blocks(caption_html):
    return []


async def edit_rich(message, blocks):
    if isinstance(blocks, dict):
        return await message.edit_text(
            text=blocks.get("text", ""),
            reply_markup=blocks.get("reply_markup"),
            parse_mode=enums.ParseMode.HTML,
        )
    return message


async def deliver_rich(client, target_chat_id, blocks, replace=None):
    if isinstance(blocks, dict):
        return await client.send_message(
            chat_id=target_chat_id,
            text=blocks.get("text", ""),
            reply_markup=blocks.get("reply_markup"),
            parse_mode=enums.ParseMode.HTML,
        )
    return None
