import asyncio
import random
import time

from pyrogram import enums, filters
from pyrogram.enums import ChatType
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython import VideosSearch

import config
from config import BANNED_USERS
from Oneforall import app
from Oneforall.misc import SUDOERS, _boot_
from Oneforall.plugins.sudo.sudoers import sudoers_list
from Oneforall.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from Oneforall.utils.decorators.language import LanguageStart
from Oneforall.utils.formatters import get_readable_time
from Oneforall.utils.inline import help_pannel, private_panel, start_panel
from Oneforall.utils.inline.rich import deliver_rich, html_to_rich_blocks
from strings import get_string

# ==============================
# 🔒 FORCE SUB CHANNELS
# ==============================

FORCE_CHANNEL_1 = getattr(config, "FORCE_CHANNEL_1", None)
FORCE_CHANNEL_2 = getattr(config, "FORCE_CHANNEL_2", None)

NEXT_IMG = [
    "https://graph.org/file/04c9167f4c5f6c7263857-06574d12f7d9e655f8.jpg",
    "https://graph.org/file/1c82daf46ac2ec57b7827-3a05aa863a378ed34a.jpg",
    "https://graph.org/file/2f8e61c55d311070339c8-17b572b5c7c8ad0907.jpg",
    "https://graph.org/file/35f6ffeeac9c330200742-eecc5ab1977d58e06b.jpg",
]

STICKER = [
    "CAACAgEAAxkBAAEEfwtqKlNmy3Re9nllA-cfjb54aBp0MQACSAYAAi4OOERdxyGw1avZfTsE",
    "CAACAgEAAxkBAAEEfwpqKlNmi678qJqTEM4WrPq-1T270gAC1AsAAhn9UEVOjdDVW1r2EDsE",
    "CAACAgUAAxkBAAEQEGVpSR-TuCKHP8D69SvDAAH2Gn7QjXEAAtIEAAKP9uhXzLPwoqMKxuQ2BA",
]


# ==============================
# PRIVATE FORCE SUB CHECK
# ==============================

async def force_sub_private(message: Message):
    if not FORCE_CHANNEL_1 or not FORCE_CHANNEL_2:
        return False
    try:
        user_id = message.from_user.id
        member1 = await app.get_chat_member(f"@{FORCE_CHANNEL_1}", user_id)
        member2 = await app.get_chat_member(f"@{FORCE_CHANNEL_2}", user_id)

        if member1.status in ["left", "kicked"] or member2.status in ["left", "kicked"]:
            buttons = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "📢 Join Channel 1", url=f"https://t.me/{FORCE_CHANNEL_1}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "📢 Join Channel 2", url=f"https://t.me/{FORCE_CHANNEL_2}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "✅ I Have Joined", callback_data="check_sub"
                        )
                    ],
                ]
            )

            await message.reply_photo(
                photo=config.START_IMG_URL,
                caption="🔒 **Access Denied!**\n\nYou must join both channels to use this bot.",
                reply_markup=buttons,
            )
            return True
    except Exception as e:
        print(f"Force Sub Error: {e}")
    return False


# ==============================
# PRIVATE START
# ==============================

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    # User message par Animated Fire Reaction
    try:
        await message.react("🔥")
    except Exception:
        pass

    # 🔒 Force Join check
    if await force_sub_private(message):
        return

    await add_served_user(message.from_user.id)

    # Deeplink Arguments (help, info, sudo)
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[0:4] == "help":
            keyboard = help_pannel(_)
            return await message.reply_photo(
                random.choice(NEXT_IMG),
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )
        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
                )
            return
        if name[0:3] == "inf":
            m = await message.reply_text("🔎")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=_["S_B_8"], url=link),
                        InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT),
                    ],
                ]
            )
            await m.delete()
            return await app.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
            )

    # 1. Premium Thinking / Streaming Animation Effect
    try:
        draft_thinking = "<tg-thinking>Initialising Music Core & Syncing Profile...</tg-thinking>"
        if hasattr(client, "send_rich_message_draft"):
            await client.send_rich_message_draft(message.chat.id, draft_thinking)
            await asyncio.sleep(1.0)
        else:
            await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
            await asyncio.sleep(0.8)
    except Exception:
        pass

    user = message.from_user
    bot_name = app.name if hasattr(app, "name") else "Roohi × Music"
    bot_username = app.username
    banner_img = random.choice(NEXT_IMG)

    # 2. Rich HTML Payload (Exact layout from screenshot with custom premium stickers)
    rich_caption = f"""
<figure>
    <img src="{banner_img}" />
</figure>

<blockquote>✦ <b>HEY {user.first_name.upper()}, WELCOME ABOARD! <tg-emoji id="6026256492619895014">🎵</tg-emoji></b></blockquote>

<blockquote><tg-emoji id="5438224604499819092">💞</tg-emoji> <b>I AM — <tg-emoji id="6026236216079290036">💜</tg-emoji> <i>{bot_name}</i> <tg-emoji id="6026236216079290036">💜</tg-emoji> — YOUR PERSONAL MUSIC COMPANION, LIVE 24/7. <tg-emoji id="5436346075998864232">🥰</tg-emoji></b></blockquote>

<details open>
<summary>✦ <b>KEY FEATURES</b> ✦</summary>
<table bordered striped compact>
    <tr>
        <th>✦ FEATURE</th>
        <th>DETAILS</th>
    </tr>
    <tr>
        <td>🎵 Streaming</td>
        <td><i>High-quality, zero lag</i></td>
    </tr>
    <tr>
        <td>🚀 Speed</td>
        <td><i>Instant response, always on</i></td>
    </tr>
    <tr>
        <td>🌐 Languages</td>
        <td><i>Multi-languages supported</i></td>
    </tr>
    <tr>
        <td>👑 VIP Care</td>
        <td><i>Priority support, smooth vibes</i></td>
    </tr>
</table>
</details>

<details>
<summary>✦ <b>WHY CHOOSE — <tg-emoji id="6026236216079290036">💜</tg-emoji> <i>{bot_name}</i> <tg-emoji id="6026236216079290036">💜</tg-emoji> ?</b> ✦</summary>
🎲 <b>USER-FRIENDLY COMMANDS FOR ANYONE.</b><br/>
🔊 <b>CRYSTAL-CLEAR AUDIO, EVERY TIME.</b><br/>
🏆 <b>TRUSTED BY THOUSANDS OF GROUPS.</b>
</details>

<blockquote>✦ <b>READY FOR THE BEST MUSIC EXPERIENCE?</b></blockquote>

🔗 <b><i>INVITE ME NOW AND ENJOY THE VIBE! 🎉</i></b>

<p>
<tg-button-row align="left">
    <tg-button type="url" style="primary" url="{config.SUPPORT_CHAT}">SUPPORT ↗</tg-button>
    <tg-button type="url" style="success" url="{config.SUPPORT_CHANNEL if hasattr(config, 'SUPPORT_CHANNEL') else config.SUPPORT_CHAT}">UPDATES ↗</tg-button>
</tg-button-row>
<tg-button-row align="center">
    <tg-button type="url" style="primary" url="https://t.me/{bot_username}?startgroup=true">➕ ADD ME TO YOUR GROUP ➕</tg-button>
</tg-button-row>
<tg-button-row align="left">
    <tg-button type="callback_data" style="link" data="settings_back_helper">HELP</tg-button>
    <tg-button type="url" style="link" url="https://t.me/{bot_username}">WEBAPP</tg-button>
    <tg-button type="callback_data" style="link" data="ADMIN Extra">CREDITS</tg-button>
</tg-button-row>
</p>
"""

    # 3. Deliver as Rich Message with fallback
    sent_msg = None
    try:
        blocks = html_to_rich_blocks(rich_caption)
        sent_msg = await deliver_rich(client, message.chat.id, blocks)
    except Exception:
        # Fallback to standard message if Rich block parser raises error
        out = private_panel(_)
        sent_msg = await message.reply_photo(
            banner_img,
            caption=_["start_2"].format(message.from_user.mention, app.mention),
            reply_markup=InlineKeyboardMarkup(out),
            has_spoiler=True,
        )

    # Bot ke response message par ❤️ Heart Reaction
    if sent_msg and hasattr(sent_msg, "react"):
        try:
            await sent_msg.react("❤️")
        except Exception:
            pass

    if await is_on_off(2):
        return await app.send_message(
            chat_id=config.LOGGER_ID,
            text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
        )


# ==============================
# FORCE JOIN CALLBACK
# ==============================

@app.on_callback_query(filters.regex("check_sub"))
async def check_subscription(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    member1 = await app.get_chat_member(f"@{FORCE_CHANNEL_1}", user_id)
    member2 = await app.get_chat_member(f"@{FORCE_CHANNEL_2}", user_id)

    if member1.status not in ["left", "kicked"] and member2.status not in ["left", "kicked"]:
        await callback_query.message.delete()
        await callback_query.message.reply_text("✅ Subscription Verified!\n\nNow send /start again.")
    else:
        await callback_query.answer("❌ You have not joined both channels!", show_alert=True)


# ==============================
# GROUP START (UNCHANGED)
# ==============================

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
    )
    return await add_served_chat(message.chat.id)
