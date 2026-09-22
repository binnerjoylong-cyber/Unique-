import math
from pyrogram.types import InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from Oneforall import app
from Oneforall.utils.formatters import time_to_seconds


def track_markup(_, videoid, user_id, channel, fplay, *args, **kwargs):
    return [
        [
            InlineKeyboardButton(
                text="▷ Play Now",
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                style=ButtonStyle.SUCCESS,
            )
        ],
        [
            InlineKeyboardButton(
                text="» Skip",
                callback_data=f"ADMIN Skip|{user_id}",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text="⟲ End",
                callback_data=f"forceclose {videoid}|{user_id}",
                style=ButtonStyle.DANGER,
            ),
        ],
    ]


def stream_markup_timer(_, vidid, chat_id, played, dur, *args, **kwargs):
    played_sec = time_to_seconds(played) if played else 0
    duration_sec = time_to_seconds(dur) if dur else 0
    percentage = (played_sec / duration_sec) * 100 if duration_sec > 0 else 0
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

    return [
        [
            InlineKeyboardButton(
                text=f"{current_p} {bar} {current_d}",
                callback_data="GetTimer",
                style=ButtonStyle.DANGER,
            )
        ],
        [
            InlineKeyboardButton(
                text="↺ Replay",
                callback_data=f"ADMIN Replay|{chat_id}",
            ),
            InlineKeyboardButton(
                text="II Pause",
                callback_data=f"ADMIN Pause|{chat_id}",
                style=ButtonStyle.SUCCESS,
            ),
            InlineKeyboardButton(
                text="» Skip",
                callback_data=f"ADMIN Skip|{chat_id}",
                style=ButtonStyle.PRIMARY,
            ),
        ],
        [
            InlineKeyboardButton(
                text="≡ Queue · 0",
                callback_data=f"nowplaying_queue {chat_id}",
                style=ButtonStyle.PRIMARY,
            )
        ],
    ]


def stream_markup(_, videoid, chat_id, *args, **kwargs):
    return [
        [
            InlineKeyboardButton(
                text="00:00 ────────● 00:00",
                callback_data="GetTimer",
                style=ButtonStyle.DANGER,
            )
        ],
        [
            InlineKeyboardButton(
                text="↺ Replay",
                callback_data=f"ADMIN Replay|{chat_id}",
            ),
            InlineKeyboardButton(
                text="II Pause",
                callback_data=f"ADMIN Pause|{chat_id}",
                style=ButtonStyle.SUCCESS,
            ),
            InlineKeyboardButton(
                text="» Skip",
                callback_data=f"ADMIN Skip|{chat_id}",
                style=ButtonStyle.PRIMARY,
            ),
        ],
        [
            InlineKeyboardButton(
                text="≡ Queue · 0",
                callback_data=f"nowplaying_queue {chat_id}",
                style=ButtonStyle.PRIMARY,
            )
        ],
    ]


def stream_markup2(_, chat_id, *args, **kwargs):
    return stream_markup(_, None, chat_id, *args, **kwargs)


def stream_markup_timer2(_, chat_id, played, dur, *args, **kwargs):
    return stream_markup_timer(_, None, chat_id, played, dur, *args, **kwargs)


def playlist_markup(_, videoid, user_id, ptype, channel, fplay, *args, **kwargs):
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"brandedPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
                style=ButtonStyle.SUCCESS,
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"brandedPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
                style=ButtonStyle.PRIMARY,
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=ButtonStyle.DANGER,
            ),
        ],
    ]


def livestream_markup(_, videoid, user_id, mode, channel, fplay, *args, **kwargs):
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
                style=ButtonStyle.SUCCESS,
            )
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=ButtonStyle.DANGER,
            ),
        ],
    ]


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay, *args, **kwargs):
    query = f"{query[:20]}"
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                style=ButtonStyle.SUCCESS,
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
                style=ButtonStyle.PRIMARY,
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁",
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {query}|{user_id}",
                style=ButtonStyle.DANGER,
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}",
                style=ButtonStyle.PRIMARY,
            ),
        ],
    ]


def telegram_markup(_, chat_id, *args, **kwargs):
    return [
        [
            InlineKeyboardButton(
                text="Next",
                callback_data=f"PanelMarkup None|{chat_id}",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text=_["CLOSEMENU_BUTTON"],
                callback_data="close",
                style=ButtonStyle.DANGER,
            ),
        ],
    ]


def queue_markup(_, videoid, chat_id, *args, **kwargs):
    return [
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{app.username}?startgroup=true",
                style=ButtonStyle.PRIMARY,
            ),
        ],
        [
            InlineKeyboardButton(
                text="II Pause",
                callback_data=f"ADMIN Pause|{chat_id}",
                style=ButtonStyle.SUCCESS,
            ),
            InlineKeyboardButton(
                text="▢ Stop",
                callback_data=f"ADMIN Stop|{chat_id}",
                style=ButtonStyle.DANGER,
            ),
            InlineKeyboardButton(
                text="» Skip",
                callback_data=f"ADMIN Skip|{chat_id}",
                style=ButtonStyle.PRIMARY,
            ),
        ],
        [
            InlineKeyboardButton(
                text="▷ Resume",
                callback_data=f"ADMIN Resume|{chat_id}",
                style=ButtonStyle.SUCCESS,
            ),
            InlineKeyboardButton(
                text="↺ Replay",
                callback_data=f"ADMIN Replay|{chat_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="⛦ More ❥",
                callback_data=f"PanelMarkup None|{chat_id}",
                style=ButtonStyle.PRIMARY,
            ),
        ],
    ]
