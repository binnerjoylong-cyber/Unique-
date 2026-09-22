# Oneforall/utils/inline/rich.py
import math
import os
import random
import re
from pyrogram import enums, errors, types
from Oneforall.misc import db
from Oneforall.utils.database import get_lang
from Oneforall.utils.formatters import seconds_to_min, time_to_seconds
from strings import get_string

_TAG_RE = re.compile(
    r"<(/?)(b|u|a|emoji)(?:\s+(?:href|id)=([^>]+))?>",
    re.IGNORECASE,
)
_consumed = set()
_FORBIDDEN = (errors.ChatSendPhotosForbidden, errors.ChatSendMediaForbidden)


async def _lang(chat_id):
    return get_string(await get_lang(chat_id))


def _parse_inline(segment):
    if not segment:
        return ""
    parts = []
    stack = []
    pos = 0

    for m in _TAG_RE.finditer(segment):
        if m.start() > pos:
            parts.append(segment[pos : m.start()])
        pos = m.end()

        closing = m.group(1)
        tag = m.group(2).lower()
        attr = m.group(3)

        if not closing:
            clean_attr = attr.strip("\"'") if attr else None
            stack.append((tag, clean_attr, len(parts)))
        elif stack and stack[-1][0] == tag:
            open_tag, val, start = stack.pop()
            inner = parts[start:]
            del parts[start:]
            inner = inner[0] if len(inner) == 1 else inner if inner else ""

            if open_tag == "b":
                parts.append(types.RichTextBold(text=inner))
            elif open_tag == "u":
                parts.append(types.RichTextUnderline(text=inner))
            elif open_tag == "a":
                parts.append(types.RichTextUrl(text=inner, url=val))
            elif open_tag == "emoji":
                try:
                    eid = int(val)
                    parts.append(types.RichTextCustomEmoji(text=inner or "🌟", document_id=eid))
                except Exception:
                    parts.append(inner or "🌟")

    if pos < len(segment):
        parts.append(segment[pos:])

    if not parts:
        return ""
    return parts[0] if len(parts) == 1 else parts


def _html_caption_to_blocks(caption_html):
    blocks = []
    bq_pattern = re.compile(
        r"<(blockquote(?:\s+expandable)?)>(.*?)</\1>",
        re.DOTALL | re.IGNORECASE,
    )

    last_idx = 0
    for match in bq_pattern.finditer(caption_html):
        start, end = match.span()
        if start > last_idx:
            pre_text = caption_html[last_idx:start].strip()
            if pre_text:
                for line in pre_text.split("\n"):
                    if line.strip():
                        parsed = _parse_inline(line)
                        if parsed:
                            blocks.append(types.InputRichBlockParagraph(text=parsed))

        tag_name = match.group(1).lower()
        inner_content = match.group(2).strip()
        is_expandable = "expandable" in tag_name

        inner_items = []
        for line in inner_content.split("\n"):
            parsed = _parse_inline(line)
            if parsed:
                if isinstance(parsed, list):
                    inner_items.extend(parsed)
                else:
                    inner_items.append(parsed)
                inner_items.append("\n")

        if inner_items and inner_items[-1] == "\n":
            inner_items.pop()

        if is_expandable and hasattr(types, "InputRichBlockExpandableBlockQuotation"):
            try:
                blocks.append(types.InputRichBlockExpandableBlockQuotation(text=inner_items))
            except Exception:
                blocks.append(types.InputRichBlockParagraph(text=inner_items))
        elif hasattr(types, "InputRichBlockBlockQuotation"):
            try:
                blocks.append(types.InputRichBlockBlockQuotation(text=inner_items))
            except Exception:
                blocks.append(types.InputRichBlockParagraph(text=inner_items))
        else:
            blocks.append(types.InputRichBlockParagraph(text=inner_items))

        last_idx = end

    if last_idx < len(caption_html):
        post_text = caption_html[last_idx:].strip()
        if post_text:
            for line in post_text.split("\n"):
                if line.strip():
                    parsed = _parse_inline(line)
                    if parsed:
                        blocks.append(types.InputRichBlockParagraph(text=parsed))

    if not blocks:
        for line in caption_html.split("\n"):
            if line.strip():
                parsed = _parse_inline(line)
                if parsed:
                    blocks.append(types.InputRichBlockParagraph(text=parsed))

    return blocks


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
    elif 80 <= umm < 95:
        bar = "────────●"
    else:
        bar = "────────●"

    current_p = played or "00:00"
    current_d = dur or "00:00"
    return f"{current_p} {bar} {current_d}"


def _progress_row(played, dur):
    return types.InputRichBlockButtons(
        buttons=[
            types.RichMessageButton(
                text=_progress_line(played, dur),
                style=enums.ButtonStyle.DANGER,
                callback_data="GetTimer",
            )
        ]
    )


def _queue_len(chat_id):
    tracks = db.get(chat_id)
    return max(len(tracks) - 1, 0) if tracks else 0


def _control_rows(chat_id, playing=True):
    toggle = (
        types.RichMessageButton(
            text="II Pause",
            style=enums.ButtonStyle.SUCCESS,
            callback_data=f"ADMIN Pause|{chat_id}",
        )
        if playing
        else types.RichMessageButton(
            text="▷ Resume",
            style=enums.ButtonStyle.SUCCESS,
            callback_data=f"ADMIN Resume|{chat_id}",
        )
    )
    return [
        types.InputRichBlockButtons(
            buttons=[
                types.RichMessageButton(
                    text="↺ Replay",
                    style=enums.ButtonStyle.DEFAULT,
                    callback_data=f"ADMIN Replay|{chat_id}",
                ),
                toggle,
                types.RichMessageButton(
                    text="» Skip",
                    style=enums.ButtonStyle.PRIMARY,
                    callback_data=f"ADMIN Skip|{chat_id}",
                ),
            ]
        ),
        types.InputRichBlockButtons(
            buttons=[
                types.RichMessageButton(
                    text=f"≡ Queue · {_queue_len(chat_id)}",
                    style=enums.ButtonStyle.PRIMARY,
                    callback_data=f"nowplaying_queue {chat_id}",
                ),
            ]
        ),
    ]


def build_now_playing_blocks(
    _, photo, caption_html, chat_id, played=None, dur=None, playing=True
):
    blocks = []
    
    # Text Blocks First
    blocks += _html_caption_to_blocks(caption_html)

    if not dur and db.get(chat_id):
        dur = db[chat_id][0].get("dur")

    cur_played = played if played else "00:00"
    cur_dur = dur if dur else "00:00"

    # Progress bar row
    blocks.append(_progress_row(cur_played, cur_dur))
    # Action buttons
    blocks += _control_rows(chat_id, playing)
    return blocks


def _message_key(message):
    return (message.chat.id, message.id)


async def _try_deliver(client, target_chat_id, blocks, replace):
    rich = types.InputRichMessage(blocks=blocks)
    if replace is not None:
        try:
            edited = await replace.edit_text(rich_message=rich)
            _consumed.add(_message_key(replace))
            return edited or replace
        except Exception:
            try:
                await replace.delete()
            except Exception:
                pass
    return await client.send_rich_message(target_chat_id, rich_message=rich)


async def _deliver(client, target_chat_id, blocks, replace=None):
    return await _try_deliver(client, target_chat_id, blocks, replace)


async def _edit_rich(message, blocks):
    return await message.edit_text(rich_message=types.InputRichMessage(blocks=blocks))


def caption_blocks(caption_html):
    return _html_caption_to_blocks(caption_html)


async def edit_rich(message, blocks):
    return await _edit_rich(message, blocks)


async def deliver_rich(client, target_chat_id, blocks, replace=None):
    result = await _deliver(client, target_chat_id, blocks, replace)
    if replace is not None:
        _consumed.discard(_message_key(replace))
    return result


async def send_now_playing_rich(
    client, chat_id, target_chat_id, photo, caption_html, replace=None
):
    _ = await _lang(chat_id)
    dur = db[chat_id][0].get("dur") if db.get(chat_id) else None
    blocks = build_now_playing_blocks(_, photo, caption_html, chat_id, played="00:00", dur=dur)
    msg = await _deliver(client, target_chat_id, blocks, replace)
    if db.get(chat_id):
        db[chat_id][0]["np_photo"] = photo
        db[chat_id][0]["np_caption"] = caption_html
    return msg


def build_queue_blocks(_, caption_html, chat_id, qid):
    blocks = _html_caption_to_blocks(caption_html)
    blocks.append(
        types.InputRichBlockButtons(
            buttons=[
                types.RichMessageButton(
                    text="▷ Play Now",
                    style=enums.ButtonStyle.SUCCESS,
                    callback_data=f"ADMIN PlayNow|{chat_id}_{qid}",
                ),
            ]
        )
    )
    blocks.append(
        types.InputRichBlockButtons(
            buttons=[
                types.RichMessageButton(
                    text="» Skip",
                    style=enums.ButtonStyle.PRIMARY,
                    callback_data=f"ADMIN Skip|{chat_id}",
                ),
                types.RichMessageButton(
                    text="⟲ End",
                    style=enums.ButtonStyle.DANGER,
                    callback_data=f"ADMIN Stop|{chat_id}",
                ),
            ]
        )
    )
    return blocks


async def send_queue_rich(
    client, chat_id, target_chat_id, caption_html, qid, replace=None
):
    _ = await _lang(chat_id)
    blocks = build_queue_blocks(_, caption_html, chat_id, qid)
    return await _deliver(client, target_chat_id, blocks, replace)


async def release_mystic(mystic):
    if mystic is None:
        return
    key = _message_key(mystic)
    if key in _consumed:
        _consumed.discard(key)
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
    if not caption_html:
        return None
    _ = await _lang(chat_id)
    blocks = build_now_playing_blocks(_, None, caption_html, chat_id, played, dur, playing)
    return await _edit_rich(mystic, blocks)


async def set_now_playing_state(chat_id, playing):
    info = db.get(chat_id)
    if not info:
        return None
    mystic = info[0].get("mystic")
    caption_html = info[0].get("np_caption")
    if not mystic or not caption_html:
        return None
    played = seconds_to_min(info[0].get("played", 0)) or None
    dur = info[0].get("dur")
    _ = await _lang(chat_id)
    blocks = build_now_playing_blocks(_, None, caption_html, chat_id, played, dur, playing)
    try:
        return await _edit_rich(mystic, blocks)
    except Exception:
        return None
