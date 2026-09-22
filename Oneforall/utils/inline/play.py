import math
from Oneforall import app
from Oneforall.utils.formatters import time_to_seconds


def rich_button(text, callback_data=None, url=None, style="default", custom_emoji_id=None):
    btn = {
        "text": {"text": text},
        "style": style,
    }
    if custom_emoji_id:
        btn["icon_custom_emoji_id"] = custom_emoji_id
    if url:
        btn["url"] = url
    elif callback_data:
        btn["callback_data"] = callback_data
    return btn


def track_markup(_, videoid, user_id, channel, fplay):
    return [
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button(_["P_B_1"], callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}", style="primary"),
                rich_button(_["P_B_2"], callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}", style="success"),
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button(_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}", style="danger")
            ],
        },
    ]


def stream_markup_timer(_, vidid, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100 if duration_sec > 0 else 0
    umm = math.floor(percentage)
    if 0 < umm <= 10:
        bar = "❍─────────"
    elif 10 < umm < 20:
        bar = "━❍────────"
    elif 20 <= umm < 30:
        bar = "━━❍───────"
    elif 30 <= umm < 40:
        bar = "━━━❍──────"
    elif 40 <= umm < 50:
        bar = "━━━━❍─────"
    elif 50 <= umm < 60:
        bar = "━━━━━❍────"
    elif 60 <= umm < 70:
        bar = "━━━━━━❍───"
    elif 70 <= umm < 80:
        bar = "━━━━━━━❍──"
    elif 80 <= umm < 95:
        bar = "━━━━━━━━❍─"
    else:
        bar = "━━━━━━━━━❍"

    return [
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button(
                    f"{played} {bar} {dur}",
                    callback_data="GetTimer",
                    style="primary",
                    custom_emoji_id=5204046146955153467,
                )
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style="primary"),
                rich_button("II", callback_data=f"ADMIN Pause|{chat_id}", style="danger"),
                rich_button("▷", callback_data=f"ADMIN Resume|{chat_id}", style="success"),
                rich_button("↻", callback_data=f"ADMIN Replay|{chat_id}", style="default"),
                rich_button("▢", callback_data=f"ADMIN Stop|{chat_id}", style="danger"),
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button(_["CLOSE_BUTTON"], callback_data="close", style="danger")
            ],
        },
    ]


def stream_markup(_, videoid, chat_id):
    return [
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("▷", callback_data=f"ADMIN Resume|{chat_id}", style="success"),
                rich_button("II", callback_data=f"ADMIN Pause|{chat_id}", style="danger"),
                rich_button("↻", callback_data=f"ADMIN Replay|{chat_id}", style="default"),
                rich_button("‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style="primary"),
                rich_button("▢", callback_data=f"ADMIN Stop|{chat_id}", style="danger"),
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button(_["CLOSE_BUTTON"], callback_data="close", style="danger")
            ],
        },
    ]


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    return [
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button(_["P_B_1"], callback_data=f"brandedPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}", style="success"),
                rich_button(_["P_B_2"], callback_data=f"brandedPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}", style="primary"),
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button(_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}", style="danger")
            ],
        },
    ]


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    return [
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button(_["P_B_3"], callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}", style="success")
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button(_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}", style="danger")
            ],
        },
    ]


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    return [
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button(_["P_B_1"], callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}", style="success"),
                rich_button(_["P_B_2"], callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}", style="primary"),
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("◁", callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}", style="primary"),
                rich_button(_["CLOSE_BUTTON"], callback_data=f"forceclose {query}|{user_id}", style="danger"),
                rich_button("▷", callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}", style="primary"),
            ],
        },
    ]


## Telegram Markup


def telegram_markup(_, chat_id):
    return [
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("Next", callback_data=f"PanelMarkup None|{chat_id}", style="primary"),
                rich_button(_["CLOSEMENU_BUTTON"], callback_data="close", style="danger"),
            ],
        }
    ]


## Queue Markup


def queue_markup(_, videoid, chat_id):
    return [
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button(_["S_B_5"], url=f"https://t.me/{app.username}?startgroup=true", style="primary")
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("II ᴘᴀᴜsᴇ", callback_data=f"ADMIN Pause|{chat_id}", style="danger"),
                rich_button("▢ sᴛᴏᴘ", callback_data=f"ADMIN Stop|{chat_id}", style="danger"),
                rich_button("sᴋɪᴘ ‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style="primary"),
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("▷ ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}", style="success"),
                rich_button("ʀᴇᴘʟᴀʏ ↺", callback_data=f"ADMIN Replay|{chat_id}", style="default"),
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("⛦ ᴍᴏʀᴇ ❥", callback_data=f"PanelMarkup None|{chat_id}", style="primary")
            ],
        },
    ]


def stream_markup2(_, chat_id):
    return [
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button(_["S_B_3"], url=f"https://t.me/{app.username}?startgroup=true", style="primary")
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("▷", callback_data=f"ADMIN Resume|{chat_id}", style="success"),
                rich_button("II", callback_data=f"ADMIN Pause|{chat_id}", style="danger"),
                rich_button("↻", callback_data=f"ADMIN Replay|{chat_id}", style="default"),
                rich_button("‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style="primary"),
                rich_button("▢", callback_data=f"ADMIN Stop|{chat_id}", style="danger"),
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button(_["CLOSEMENU_BUTTON"], callback_data="close", style="danger")
            ],
        },
    ]


def stream_markup_timer2(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100 if duration_sec > 0 else 0
    umm = math.floor(percentage)
    if 0 < umm <= 40:
        bar = "◉——————————"
    elif 10 < umm < 20:
        bar = "—◉—————————"
    elif 20 < umm < 30:
        bar = "——◉————————"
    elif 30 <= umm < 40:
        bar = "———◉———————"
    elif 40 <= umm < 50:
        bar = "————◉——————"
    elif 50 <= umm < 60:
        bar = "——————◉————"
    elif 50 <= umm < 70:
        bar = "———————◉———"
    else:
        bar = "——————————◉"

    return [
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button(f"{played} {bar} {dur}", callback_data="GetTimer", style="primary")
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("▷", callback_data=f"ADMIN Resume|{chat_id}", style="success"),
                rich_button("II", callback_data=f"ADMIN Pause|{chat_id}", style="danger"),
                rich_button("↻", callback_data=f"ADMIN Replay|{chat_id}", style="default"),
                rich_button("‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style="primary"),
                rich_button("▢", callback_data=f"ADMIN Stop|{chat_id}", style="danger"),
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button(
                    _["CLOSEMENU_BUTTON"],
                    callback_data="close",
                    style="danger",
                    custom_emoji_id=5409222721869459068,
                )
            ],
        },
    ]


def panel_markup_1(_, videoid, chat_id):
    return [
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button(_["S_B_5"], url=f"https://t.me/{app.username}?startgroup=true", style="primary")
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("🎧 sᴜғғʟᴇ ❥", callback_data=f"ADMIN Shuffle|{chat_id}", style="primary"),
                rich_button("ʟᴏᴏᴘ ↺", callback_data=f"ADMIN Loop|{chat_id}", style="default"),
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("◁ 10 sᴇᴄ", callback_data=f"ADMIN 1|{chat_id}", style="primary"),
                rich_button("10 sᴇᴄ ▷", callback_data=f"ADMIN 2|{chat_id}", style="primary"),
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("❥ ʜᴏᴍᴇ ❥", callback_data=f"Pages Back|2|{videoid}|{chat_id}", style="danger"),
                rich_button("❥ ɴᴇxᴛ ❥", callback_data=f"Pages Forw|2|{videoid}|{chat_id}", style="success"),
            ],
        },
    ]


def panel_markup_2(_, videoid, chat_id):
    return [
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button(_["S_B_5"], url=f"https://t.me/{app.username}?startgroup=true", style="primary")
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("🕒 0.5x", callback_data=f"SpeedUP {chat_id}|0.5", style="primary"),
                rich_button("🕓 0.75x", callback_data=f"SpeedUP {chat_id}|0.75", style="primary"),
                rich_button("🕤 1.0x", callback_data=f"SpeedUP {chat_id}|1.0", style="success"),
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("🕤 1.5x", callback_data=f"SpeedUP {chat_id}|1.5", style="primary"),
                rich_button("🕛 2.0x", callback_data=f"SpeedUP {chat_id}|2.0", style="danger"),
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("❥ ʙᴀᴄᴋ ❥", callback_data=f"Pages Back|1|{videoid}|{chat_id}", style="default")
            ],
        },
    ]


def panel_markup_3(_, videoid, chat_id):
    return [
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("🕒 0.5x", callback_data=f"SpeedUP {chat_id}|0.5", style="primary"),
                rich_button("🕓 0.75x", callback_data=f"SpeedUP {chat_id}|0.75", style="primary"),
                rich_button("🕤 1.0x", callback_data=f"SpeedUP {chat_id}|1.0", style="success"),
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("🕤 1.5x", callback_data=f"SpeedUP {chat_id}|1.5", style="primary"),
                rich_button("🕛 2.0x", callback_data=f"SpeedUP {chat_id}|2.0", style="danger"),
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("❥ ʙᴀᴄᴋ ❥", callback_data=f"Pages Back|2|{videoid}|{chat_id}", style="default")
            ],
        },
    ]


def panel_markup_4(_, vidid, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100 if duration_sec > 0 else 0
    umm = math.floor(percentage)
    if 0 < umm <= 40:
        bar = "◉——————————"
    elif 10 < umm < 20:
        bar = "—◉—————————"
    elif 20 < umm < 30:
        bar = "——◉————————"
    elif 30 <= umm < 40:
        bar = "———◉———————"
    elif 40 <= umm < 50:
        bar = "————◉——————"
    elif 50 <= umm < 60:
        bar = "——————◉————"
    elif 50 <= umm < 70:
        bar = "———————◉———"
    else:
        bar = "——————————◉"

    return [
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button(f"{played} {bar} {dur}", callback_data="GetTimer", style="primary")
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("II ᴘᴀᴜsᴇ", callback_data=f"ADMIN Pause|{chat_id}", style="danger"),
                rich_button("▢ sᴛᴏᴘ ▢", callback_data=f"ADMIN Stop|{chat_id}", style="danger"),
                rich_button("sᴋɪᴘ ‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style="primary"),
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("▷ ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}", style="success"),
                rich_button("ʀᴇᴘʟᴀʏ ↺", callback_data=f"ADMIN Replay|{chat_id}", style="default"),
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("❥ ʜᴏᴍᴇ ❥", callback_data=f"MainMarkup {vidid}|{chat_id}", style="default")
            ],
        },
    ]


def panel_markup_5(_, videoid, chat_id):
    return [
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button(_["S_B_5"], url=f"https://t.me/{app.username}?startgroup=true", style="primary")
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("ᴘᴀᴜsᴇ", callback_data=f"ADMIN Pause|{chat_id}", style="danger"),
                rich_button("sᴛᴏᴘ", callback_data=f"ADMIN Stop|{chat_id}", style="danger"),
                rich_button("sᴋɪᴘ", callback_data=f"ADMIN Skip|{chat_id}", style="primary"),
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}", style="success"),
                rich_button("ʀᴇᴘʟᴀʏ", callback_data=f"ADMIN Replay|{chat_id}", style="default"),
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("❥ ʜᴏᴍᴇ ❥", callback_data=f"MainMarkup {videoid}|{chat_id}", style="default"),
                rich_button("❥ ɴᴇxᴛ ❥", callback_data=f"Pages Forw|1|{videoid}|{chat_id}", style="success"),
            ],
        },
    ]


def panel_markup_clone(_, vidid, chat_id):
    return [
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button(_["S_B_5"], url=f"https://t.me/{app.username}?startgroup=true", style="primary")
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("▷", callback_data=f"ADMIN Resume|{chat_id}", style="success"),
                rich_button("II", callback_data=f"ADMIN Pause|{chat_id}", style="danger"),
                rich_button("↻", callback_data=f"ADMIN Replay|{chat_id}", style="default"),
                rich_button("‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style="primary"),
                rich_button("▢", callback_data=f"ADMIN Stop|{chat_id}", style="danger"),
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("📥 ᴠɪᴅᴇᴏ", callback_data=f"downloadvideo {vidid}", style="primary"),
                rich_button("📥 ᴀᴜᴅɪᴏ", callback_data=f"downloadaudio {vidid}", style="primary"),
            ],
        },
        {
            "type": "buttons",
            "align": "center",
            "buttons": [
                rich_button("✚ ᴘʟᴀʏʟɪsᴛ ✚", callback_data=f"branded_playlist {vidid}", style="success")
            ],
        },
    ]
