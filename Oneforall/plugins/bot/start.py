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
from Oneforall.utils.inline import help_pannel, start_panel
from Oneforall.utils.inline.start import private_panel
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


async def force_sub_private(message: Message):
    if not FORCE_CHANNEL_1 or not FORCE_CHANNEL_2:
        return False
    try:
        user_id = message.from_user.id
        member1 = await app.get_chat_member(f"@{FORCE_CHANNEL_1}", user_id)
        member2 = await app.get_chat_member(f"@{FORCE_CHANNEL_2}", user_id)

        if member1.status in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED] or member2.status in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED]:
            buttons = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("📢 Join Channel 1", url=f"https://t.me/{FORCE_CHANNEL_1}")],
                    [InlineKeyboardButton("📢 Join Channel 2", url=f"https://t.me/{FORCE_CHANNEL_2}")],
                    [InlineKeyboardButton("✅ I Have Joined", callback_data="check_sub")],
                ]
            )
            await message.reply_photo(
                photo=config.START_IMG_URL,
                caption="🔒 **Access Denied!**\n\nYou must join both channels to use this bot.",
                reply_markup=buttons,
            )
            return True
    except Exception:
        return False
    return False


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    # 1. User Message Fire Reaction (Protected)
    try:
        if hasattr(message, "react"):
            await message.react("🔥")
    except Exception:
        pass

    # 2. Force Join check
    try:
        if await force_sub_private(message):
            return
    except Exception:
        pass

    try:
        await add_served_user(message.from_user.id)
    except Exception:
        pass

    # Deeplink Arguments Handling
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name.startswith("help"):
            keyboard = help_pannel(_)
            return await message.reply_photo(
                random.choice(NEXT_IMG),
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )
        if name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            return
        if name.startswith("inf"):
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

    user = message.from_user
    bot_name = app.name if hasattr(app, "name") else "𓆩ℛᴜ֟፝ʜɪ 𓆩ꨄ︎𓆪 𝐌ᴜ֟፝sɪᴄ𓆪˼"
    banner_img = random.choice(NEXT_IMG)

    # 3. Clean Standard Telegram HTML
    caption_text = (
        f"✦ <b>HEY {user.first_name.upper()}, WELCOME ABOARD!</b> <emoji id=6026256492619895014>🎵</emoji>\n\n"
        f"<blockquote><emoji id=5438224604499819092>💞</emoji> <b>I AM — <emoji id=6026236216079290036>💜</emoji> <i>{bot_name}</i> <emoji id=6026236216079290036>💜</emoji> — YOUR PERSONAL MUSIC COMPANION, LIVE 24/7. <emoji id=5436346075998864232>🥰</emoji></b></blockquote>\n\n"
        f"<b><emoji id=5974235702701853774>✨</emoji> <u>KEY FEATURES</u> :</b>\n"
        f"<blockquote expandable>"
        f"🎵 <b>Streaming :</b> <i>High-quality, zero lag</i>\n"
        f"🚀 <b>Speed :</b> <i>Instant response, always on</i>\n"
        f"🌐 <b>Languages :</b> <i>Multi-languages supported</i>\n"
        f"👑 <b>VIP Care :</b> <i>Priority support, smooth vibes</i></blockquote>\n\n"
        f"<b><emoji id=6066395745139824604>🌐</emoji> <u>WHY CHOOSE US</u> :</b>\n"
        f"<blockquote expandable>"
        f"🎲 <b>User-friendly commands for anyone.</b>\n"
        f"🔊 <b>Crystal-clear audio, every time.</b>\n"
        f"🏆 <b>Trusted by thousands of groups.</b></blockquote>\n\n"
        f"<blockquote>✦ <b>READY FOR THE BEST MUSIC EXPERIENCE?</b></blockquote>\n\n"
        f"🔗 <i><b>INVITE ME NOW AND ENJOY THE VIBE! 🎉</b></i>"
    )

    try:
        buttons = private_panel(_)
        keyboard = InlineKeyboardMarkup(buttons)
    except Exception:
        keyboard = None

    # Send Photo
    sent_msg = await message.reply_photo(
        photo=banner_img,
        caption=caption_text,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=keyboard,
    )

    # 4. Bot Reply Heart Reaction (Protected)
    try:
        if sent_msg and hasattr(sent_msg, "react"):
            await sent_msg.react("❤️")
    except Exception:
        pass

    try:
        if await is_on_off(2):
            await app.send_message(
                chat_id=config.LOGGER_ID,
                text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
            )
    except Exception:
        pass


@app.on_callback_query(filters.regex("check_sub"))
async def check_subscription(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    try:
        member1 = await app.get_chat_member(f"@{FORCE_CHANNEL_1}", user_id)
        member2 = await app.get_chat_member(f"@{FORCE_CHANNEL_2}", user_id)

        if member1.status not in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED] and member2.status not in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED]:
            await callback_query.message.delete()
            await callback_query.message.reply_text("✅ Subscription Verified!\n\nNow send /start again.")
        else:
            await callback_query.answer("❌ You have not joined both channels!", show_alert=True)
    except Exception:
        await callback_query.answer("❌ Verification failed. Please ensure you joined.", show_alert=True)


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
