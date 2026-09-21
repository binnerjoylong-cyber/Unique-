import math
from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardButton
from Oneforall import app
from Oneforall.utils.formatters import time_to_seconds


def stream_markup_timer(_, vidid, chat_id, played, dur, count=0):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100 if duration_sec > 0 else 0
    umm = math.floor(percentage)

    # Screenshot ke jaisa thin dash progress bar
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
        # Row 1: Dark / Red Timer Bar
        [
            InlineKeyboardButton(
                text=f"{played}  {bar}  {dur}",
                callback_data="GetTimer",
                style=ButtonStyle.DANGER,  # Dark red curve look
            )
        ],
        # Row 2: Replay | II Pause (Green) | » Skip (Blue)
        [
            InlineKeyboardButton(
                text="↺ Replay",
                callback_data=f"ADMIN Replay|{chat_id}",
            ),
            InlineKeyboardButton(
                text="II Pause",
                callback_data=f"ADMIN Pause|{chat_id}",
                style=ButtonStyle.SUCCESS,  # Green curve button
            ),
            InlineKeyboardButton(
                text="» Skip",
                callback_data=f"ADMIN Skip|{chat_id}",
                style=ButtonStyle.PRIMARY,  # Blue curve button
            ),
        ],
        # Row 3: Red Queue Bar
        [
            InlineKeyboardButton(
                text=f"≡ Queue - {count}",
                callback_data=f"ADMIN Queue|{chat_id}",
                style=ButtonStyle.DANGER,  # Dark red curve look
            )
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
                style=ButtonStyle.SUCCESS,  # Green
            ),
            InlineKeyboardButton(
                text="» Skip",
                callback_data=f"ADMIN Skip|{chat_id}",
                style=ButtonStyle.PRIMARY,  # Blue
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"≡ Queue - {count}",
                callback_data=f"ADMIN Queue|{chat_id}",
                style=ButtonStyle.DANGER,  # Red
            )
        ],
    ]
    return buttons
