import math
from pyrogram.types import InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from Oneforall import app
from Oneforall.utils.formatters import time_to_seconds


# Screenshot 1 ke hisab se (Queue add hone par buttons)
def track_markup(_, videoid, user_id, channel, fplay, *args, **kwargs):
    buttons = [
        # Full width Green Play Now button
        [
            InlineKeyboardButton(
                text="▷ Play Now",
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                style=ButtonStyle.SUCCESS,
            )
        ],
        # Blue Skip aur Red End buttons ek sath
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
    return buttons


# Screenshots 2, 3, 4, 5 ke hisab se (Live Streaming Player markup)
def stream_markup_timer(_, vidid, chat_id, played, dur, *args, **kwargs):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
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

    buttons = [
        # Row 1: Duration Timer Bar (Dark/Danger Accent)
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {dur}",
                callback_data="GetTimer",
                style=ButtonStyle.DANGER,
            )
        ],
        # Row 2: ↺ Replay | II Pause | » Skip
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
        # Row 3: Queue Count Button (Blue Full-Width)
        [
            InlineKeyboardButton(
                text="≡ Queue · 0",
                callback_data=f"queue {chat_id}",
                style=ButtonStyle.PRIMARY,
            )
        ],
    ]
    return buttons


def stream_markup(_, videoid, chat_id, *args, **kwargs):
    buttons = [
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
                callback_data=f"queue {chat_id}",
                style=ButtonStyle.PRIMARY,
            )
        ],
    ]
    return buttons


def playlist_markup(_, videoid, user_id, ptype, channel, fplay, *args, **kwargs):
    buttons = [
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
    return buttons


def livestream_markup(_, videoid, user_id, mode, channel, fplay, *args, **kwargs):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
                style=ButtonStyle.SUCCESS,
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
    return buttons


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay, *args, **kwargs):
    query = f"{query[:20]}"
    buttons = [
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
    return buttons


## Telegram Markup


def telegram_markup(_, chat_id, *args, **kwargs):
    buttons = [
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
    return buttons


## Queue Markup


def queue_markup(_, videoid, chat_id, *args, **kwargs):
    buttons = [
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
    return buttons


def stream_markup2(_, chat_id, *args, **kwargs):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
                style=ButtonStyle.PRIMARY,
            ),
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
                callback_data=f"queue {chat_id}",
                style=ButtonStyle.PRIMARY,
            )
        ],
    ]
    return buttons


def stream_markup_timer2(_, chat_id, played, dur, *args, **kwargs):
    return stream_markup_timer(_, None, chat_id, played, dur, *args, **kwargs)


def panel_markup_1(_, videoid, chat_id, *args, **kwargs):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{app.username}?startgroup=true",
                style=ButtonStyle.PRIMARY,
            ),
        ],
        [
            InlineKeyboardButton(
                text="🎧 Shuffle",
                callback_data=f"ADMIN Shuffle|{chat_id}",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text="Loop ↺",
                callback_data=f"ADMIN Loop|{chat_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁ 10 Sec",
                callback_data=f"ADMIN 1|{chat_id}",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text="10 Sec ▷",
                callback_data=f"ADMIN 2|{chat_id}",
                style=ButtonStyle.PRIMARY,
            ),
        ],
        [
            InlineKeyboardButton(
                text="Home",
                callback_data=f"Pages Back|2|{videoid}|{chat_id}",
                style=ButtonStyle.DANGER,
            ),
            InlineKeyboardButton(
                text="Next",
                callback_data=f"Pages Forw|2|{videoid}|{chat_id}",
                style=ButtonStyle.SUCCESS,
            ),
        ],
    ]
    return buttons


def panel_markup_2(_, videoid, chat_id, *args, **kwargs):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{app.username}?startgroup=true",
                style=ButtonStyle.PRIMARY,
            ),
        ],
        [
            InlineKeyboardButton(
                text="0.5x",
                callback_data=f"SpeedUP {chat_id}|0.5",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text="0.75x",
                callback_data=f"SpeedUP {chat_id}|0.75",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text="1.0x",
                callback_data=f"SpeedUP {chat_id}|1.0",
                style=ButtonStyle.SUCCESS,
            ),
        ],
        [
            InlineKeyboardButton(
                text="1.5x",
                callback_data=f"SpeedUP {chat_id}|1.5",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text="2.0x",
                callback_data=f"SpeedUP {chat_id}|2.0",
                style=ButtonStyle.DANGER,
            ),
        ],
        [
            InlineKeyboardButton(
                text="Back",
                callback_data=f"Pages Back|1|{videoid}|{chat_id}",
            ),
        ],
    ]
    return buttons


def panel_markup_3(_, videoid, chat_id, *args, **kwargs):
    return panel_markup_2(_, videoid, chat_id, *args, **kwargs)


def panel_markup_4(_, vidid, chat_id, played, dur, *args, **kwargs):
    return stream_markup_timer(_, vidid, chat_id, played, dur, *args, **kwargs)


def panel_markup_5(_, videoid, chat_id, *args, **kwargs):
    return stream_markup(_, videoid, chat_id, *args, **kwargs)


def panel_markup_clone(_, vidid, chat_id, *args, **kwargs):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{app.username}?startgroup=true",
                style=ButtonStyle.PRIMARY,
            ),
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
                text="📥 Video",
                callback_data=f"downloadvideo {vidid}",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text="📥 Audio",
                callback_data=f"downloadaudio {vidid}",
                style=ButtonStyle.PRIMARY,
            ),
        ],
        [
            InlineKeyboardButton(
                text="✚ Playlist",
                callback_data=f"branded_playlist {vidid}",
                style=ButtonStyle.SUCCESS,
            ),
        ],
    ]
    return buttons
