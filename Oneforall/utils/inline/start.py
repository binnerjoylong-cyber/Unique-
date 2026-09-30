import random
from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardButton
import config
from Oneforall import app


def btn(text, emoji_id, style=ButtonStyle.DEFAULT, **kwargs):
    """Specific icon_custom_emoji_id aur ButtonStyle ke sath button create karega."""
    try:
        return InlineKeyboardButton(
            text=text,
            icon_custom_emoji_id=emoji_id,
            style=style,
            **kwargs,
        )
    except TypeError:
        return InlineKeyboardButton(text=text, **kwargs)


def start_panel(_):
    return [
        [
            # Add to Group (Green Glow / Success)
            btn(
                _["S_B_1"],
                5438224604499819092,
                url=f"https://t.me/{app.username}?startgroup=true",
                style=ButtonStyle.SUCCESS,
            ),
            # Support Group (Deep Blue / Primary)
            btn(
                _["S_B_2"],
                6026236216079290036,
                url=config.SUPPORT_CHAT,
                style=ButtonStyle.PRIMARY,
            ),
        ],
    ]


def private_panel(_):
    channel_url = getattr(config, "SUPPORT_CHANNEL", config.SUPPORT_CHAT)

    return [
        [
            # Top Main CTA: Add to Group (Vibrant Green)
            btn(
                _["S_B_3"],
                5436346075998864232,
                url=f"https://t.me/{app.username}?startgroup=true",
                style=ButtonStyle.SUCCESS,
            )
        ],
        [
            # Support (Primary Blue) + Official Channel (Danger Red / Contrast)
            btn(
                _["S_B_2"],
                5438224604499819092,
                url=config.SUPPORT_CHAT,
                style=ButtonStyle.PRIMARY,
            ),
            btn(
                _["S_B_6"],
                6089090515540644835,
                url=channel_url,
                style=ButtonStyle.DANGER,
            ),
        ],
        [
            # Interactive Core: Help & Commands (Solid Primary Blue)
            btn(
                _["S_B_4"],
                6001604106190330097,
                callback_data="settings_back_helper",
                style=ButtonStyle.PRIMARY,
            )
        ],
        [
            # Profiles Dual Row (Danger Red & Primary Blue Contrast)
            btn(
                "˹ 𓆩Q֟፝υєєη𓆪 ˼",
                6026236216079290036,
                url="tg://openmessage?user_id=8676835917",
                style=ButtonStyle.DANGER,
            ),
            btn(
                _["S_B_5"],
                6026236216079290036,
                url="tg://openmessage?user_id=8285730532",
                style=ButtonStyle.PRIMARY,
            ),
        ],
        [
            # Bottom Signature: Web Portal / Tunes (Success Green)
            btn(
                "「 ⌯ ᴜᴘᴘєʀϻσσɴ ᴛᴜηєꜱ ⌯ 」",
                6026256492619895014,
                url="https://uppermooninfinity.jo3.org/",
                style=ButtonStyle.SUCCESS,
            )
        ],
    ]
