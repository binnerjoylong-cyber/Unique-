import math

from pyrogram.types import InlineKeyboardButton

from Oneforall import app
from Oneforall.utils.formatters import time_to_seconds


def is_bot_premium():
    # Telegram Bot API 7.0+ allows rich styling
    return True


# ---------------- TRACK MARKUP ---------------- #
def track_markup(_, videoid, user_id, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                style="primary",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
                style="success",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style="danger",
            )
        ],
    ]
    return buttons


# ---------------- MAIN STREAM MARKUPS (PAGE 1) ---------------- #
def stream_markup_timer(_, vidid, chat_id, played, dur, count=0):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100 if duration_sec > 0 else 0
    umm = math.floor(percentage)

    if 0 < umm <= 10:
        bar = "•----------"
    elif 10 < umm < 20:
        bar = "-•---------"
    elif 20 <= umm < 30:
        bar = "--•--------"
    elif 30 <= umm < 40:
        bar = "---•-------"
    elif 40 <= umm < 50:
        bar = "----•------"
    elif 50 <= umm < 60:
        bar = "-----•-----"
    elif 60 <= umm < 70:
        bar = "------•----"
    elif 70 <= umm < 80:
        bar = "-------•---"
    elif 80 <= umm < 95:
        bar = "--------•--"
    else:
        bar = "---------•"

    buttons = [
        [
            InlineKeyboardButton(
                text=f"{played}  {bar}  {dur}",
                callback_data="GetTimer",
                style="danger",
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
                style="success",
            ),
            InlineKeyboardButton(
                text="» Skip",
                callback_data=f"ADMIN Skip|{chat_id}",
                style="primary",
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"≡ Queue - {count}",
                callback_data=f"ADMIN Queue|{chat_id}",
                style="danger",
            ),
            InlineKeyboardButton(
                text="⚙ Controls",
                callback_data=f"PanelMarkup None|{chat_id}",
                style="primary",
            ),
        ],
    ]
    return buttons


def stream_markup(_, videoid, chat_id, count=0):
    buttons = [
        [
            InlineKeyboardButton(
                text="↺ Replay",
                callback_data=f"ADMIN Replay|{chat_id}",
            ),
            InlineKeyboardButton(
                text="II Pause",
                callback_data=f"ADMIN Pause|{chat_id}",
                style="success",
            ),
            InlineKeyboardButton(
                text="» Skip",
                callback_data=f"ADMIN Skip|{chat_id}",
                style="primary",
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"≡ Queue - {count}",
                callback_data=f"ADMIN Queue|{chat_id}",
                style="danger",
            ),
            InlineKeyboardButton(
                text="⚙ Controls",
                callback_data=f"PanelMarkup None|{chat_id}",
                style="primary",
            ),
        ],
    ]
    return buttons


def stream_markup2(_, chat_id, count=0):
    return stream_markup(_, None, chat_id, count)


def stream_markup_timer2(_, chat_id, played, dur):
    return stream_markup_timer(_, None, chat_id, played, dur)


# ---------------- EXTRA CONTROLS / PANELS (WAPAS RESTORE KIYE) ---------------- #
def panel_markup_1(_, videoid, chat_id):
    """Extra controls like Shuffle, Loop, Seek Forward/Backward"""
    buttons = [
        [
            InlineKeyboardButton(
                text="🎧 Shuffle",
                callback_data=f"ADMIN Shuffle|{chat_id}",
                style="primary",
            ),
            InlineKeyboardButton(
                text="🔄 Loop",
                callback_data=f"ADMIN Loop|{chat_id}",
                style="success",
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁ 10 Sec",
                callback_data=f"ADMIN 1|{chat_id}",
            ),
            InlineKeyboardButton(
                text="10 Sec ▷",
                callback_data=f"ADMIN 2|{chat_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="⚡ Speed Controls",
                callback_data=f"Pages Forw|2|{videoid}|{chat_id}",
                style="primary",
            ),
            InlineKeyboardButton(
                text="🔙 Back",
                callback_data=f"MainMarkup {videoid}|{chat_id}",
                style="danger",
            ),
        ],
    ]
    return buttons


def panel_markup_2(_, videoid, chat_id):
    """Speed Controls (0.5x, 1.0x, 2.0x etc)"""
    buttons = [
        [
            InlineKeyboardButton(
                text="🕒 0.5x",
                callback_data=f"SpeedUP {chat_id}|0.5",
            ),
            InlineKeyboardButton(
                text="🕓 0.75x",
                callback_data=f"SpeedUP {chat_id}|0.75",
            ),
            InlineKeyboardButton(
                text="🕤 1.0x",
                callback_data=f"SpeedUP {chat_id}|1.0",
                style="success",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🕤 1.5x",
                callback_data=f"SpeedUP {chat_id}|1.5",
            ),
            InlineKeyboardButton(
                text="🕛 2.0x",
                callback_data=f"SpeedUP {chat_id}|2.0",
                style="danger",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔙 Back",
                callback_data=f"Pages Back|1|{videoid}|{chat_id}",
                style="primary",
            ),
        ],
    ]
    return buttons


def panel_markup_3(_, videoid, chat_id):
    return panel_markup_2(_, videoid, chat_id)


def panel_markup_4(_, vidid, chat_id, played, dur):
    return stream_markup_timer(_, vidid, chat_id, played, dur)


def panel_markup_5(_, videoid, chat_id):
    return panel_markup_1(_, videoid, chat_id)


def panel_markup_clone(_, vidid, chat_id):
    """Download audio/video & save to playlist buttons"""
    buttons = [
        [
            InlineKeyboardButton(
                text="↺ Replay",
                callback_data=f"ADMIN Replay|{chat_id}",
            ),
            InlineKeyboardButton(
                text="II Pause",
                callback_data=f"ADMIN Pause|{chat_id}",
                style="success",
            ),
            InlineKeyboardButton(
                text="» Skip",
                callback_data=f"ADMIN Skip|{chat_id}",
                style="primary",
            ),
        ],
        [
            InlineKeyboardButton(
                text="📥 Video",
                callback_data=f"downloadvideo {vidid}",
                style="primary",
            ),
            InlineKeyboardButton(
                text="📥 Audio",
                callback_data=f"downloadaudio {vidid}",
                style="success",
            ),
        ],
        [
            InlineKeyboardButton(
                text="✚ Playlist",
                callback_data=f"branded_playlist {vidid}",
                style="danger",
            ),
        ],
    ]
    return buttons


# ---------------- UTILITY & PLAYLIST MARKUPS ---------------- #
def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"brandedPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
                style="primary",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"brandedPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
                style="success",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style="danger",
            ),
        ],
    ]
    return buttons


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
                style="success",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style="danger",
            ),
        ],
    ]
    return buttons


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                style="primary",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
                style="success",
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁",
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {query}|{user_id}",
                style="danger",
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
        ],
    ]
    return buttons


def telegram_markup(_, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="Next ⚙",
                callback_data=f"PanelMarkup None|{chat_id}",
                style="primary",
            ),
            InlineKeyboardButton(
                text=_["CLOSEMENU_BUTTON"],
                callback_data="close",
                style="danger",
            ),
        ],
    ]
    return buttons


def queue_markup(_, videoid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="II Pause",
                callback_data=f"ADMIN Pause|{chat_id}",
                style="success",
            ),
            InlineKeyboardButton(
                text="▢ Stop",
                callback_data=f"ADMIN Stop|{chat_id}",
                style="danger",
            ),
            InlineKeyboardButton(
                text="Skip »",
                callback_data=f"ADMIN Skip|{chat_id}",
                style="primary",
            ),
        ],
        [
            InlineKeyboardButton(
                text="▷ Resume",
                callback_data=f"ADMIN Resume|{chat_id}",
            ),
            InlineKeyboardButton(
                text="Replay ↺",
                callback_data=f"ADMIN Replay|{chat_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="⚙ Controls Menu",
                callback_data=f"PanelMarkup None|{chat_id}",
                style="primary",
            ),
        ],
    ]
    return buttons
