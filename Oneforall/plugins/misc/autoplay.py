import random
from pyrogram import filters, types, enums

from config import BANNED_USERS, lyrical
from Oneforall import YouTube, app
from Oneforall.core.mongo import mongodb
from Oneforall.utils.decorators.language import languageCB
from Oneforall.utils.inline.rich import (
    deliver_rich,
    edit_rich,
    rich_autoplay_mood_blocks,
    rich_autoplay_language_blocks,
    html_to_rich_blocks,
)

autoplaydb = mongodb.autoplay
previous_tracks = {}


# Database Helpers directly defined to prevent import errors
async def is_autoplay_on(chat_id: int) -> bool:
    mode = await autoplaydb.find_one({"chat_id": chat_id})
    if not mode:
        return False
    return mode.get("autoplay", False)


async def set_autoplay(chat_id: int, status: bool):
    await autoplaydb.update_one(
        {"chat_id": chat_id},
        {"$set": {"autoplay": status}},
        upsert=True,
    )


async def get_autoplay_mood(chat_id: int):
    mode = await autoplaydb.find_one({"chat_id": chat_id})
    if not mode:
        return {"mood": "chill", "language": "hindi"}
    return mode.get("mood_data", {"mood": "chill", "language": "hindi"})


async def set_autoplay_mood(chat_id: int, mood_data: dict):
    await autoplaydb.update_one(
        {"chat_id": chat_id},
        {"$set": {"mood_data": mood_data}},
        upsert=True,
    )


@app.on_message(filters.command("songconfig") & filters.group & ~BANNED_USERS)
@languageCB
async def songconfig_command(client, message, _):
    """Command to configure autoplay with mood and language"""
    caption = (
        "<blockquote><emoji id=5895705279416241926>🎵</emoji> <u><b>AUTOPLAY CONFIGURATION</b></u></blockquote>\n\n"
        "<blockquote expandable>"
        "<emoji id=5974235702701853774>✨</emoji> Select your desired mood vibe below.\n"
        "<emoji id=5409132617750555920>⚡</emoji> Bot will stream infinite matched songs automatically.</blockquote>"
    )
    blocks = rich_autoplay_mood_blocks(caption)
    await deliver_rich(client, message.chat.id, blocks)


@app.on_callback_query(filters.regex(r"^songconfig_mood:"))
@languageCB
async def handle_mood_selection(client, CallbackQuery, _):
    """Handle mood selection callback"""
    chat_id = CallbackQuery.message.chat.id

    try:
        mood = CallbackQuery.data.split(":", 1)[1]
    except Exception:
        return await CallbackQuery.answer("ɪɴᴠᴀʟɪᴅ ᴍᴏᴏᴅ sᴇʟᴇᴄᴛɪᴏɴ", show_alert=True)

    if chat_id not in lyrical:
        lyrical[chat_id] = {}

    lyrical[chat_id]["autoplay_mood"] = mood

    caption = (
        f"<blockquote><emoji id=5895705279416241926>🎵</emoji> <u><b>MOOD: {mood.upper()}</b></u></blockquote>\n\n"
        "<blockquote expandable>"
        "<emoji id=6066395745139824604>🌐</emoji> <b>Now select language preference:</b>\n"
        "Recommendations will be fetched based on your choice.</blockquote>"
    )
    blocks = rich_autoplay_language_blocks(caption)
    await edit_rich(CallbackQuery.message, blocks)


@app.on_callback_query(filters.regex(r"^songconfig_language:"))
@languageCB
async def handle_language_selection(client, CallbackQuery, _):
    """Handle language selection callback"""
    chat_id = CallbackQuery.message.chat.id

    try:
        language = CallbackQuery.data.split(":", 1)[1]
    except Exception:
        return await CallbackQuery.answer("ɪɴᴠᴀʟɪᴅ ʟᴀɴɢᴜᴀɢᴇ sᴇʟᴇᴄᴛɪᴏɴ", show_alert=True)

    if chat_id not in lyrical:
        lyrical[chat_id] = {}

    mood = lyrical[chat_id].get("autoplay_mood", "chill")

    await set_autoplay(chat_id, True)
    await set_autoplay_mood(
        chat_id,
        {
            "mood": mood,
            "language": language,
        },
    )

    lyrical[chat_id].pop("autoplay_mood", None)

    caption = (
        "<blockquote><emoji id=5895705279416241926>✅</emoji> <u><b>AUTOPLAY ACTIVE</b></u></blockquote>\n\n"
        "<blockquote expandable>"
        f"<emoji id=6066395745139824604>🎵</emoji> <b>Mood :</b> <code>{mood.title()}</code>\n"
        f"<emoji id=5974235702701853774>🌐</emoji> <b>Language :</b> <code>{language.title()}</code>\n\n"
        "<emoji id=5409132617750555920>⚡</emoji> Bot will now automatically play matching tracks continuously!</blockquote>"
    )
    blocks = html_to_rich_blocks(caption)
    blocks.append(
        types.InputRichBlockButtons(
            buttons=[
                types.RichMessageButton(
                    text="⚙️ Re-Configure",
                    style=enums.ButtonStyle.PRIMARY,
                    callback_data="AutoPlay_reconfig",
                ),
                types.RichMessageButton(
                    text="❌ Disable",
                    style=enums.ButtonStyle.DANGER,
                    callback_data=f"AutoPlay|{chat_id}",
                ),
            ]
        )
    )
    await edit_rich(CallbackQuery.message, blocks)


@app.on_callback_query(filters.regex(r"^AutoPlay"))
@languageCB
async def toggle_autoplay(client, CallbackQuery, _):
    """Toggle autoplay on/off"""
    callback_data = CallbackQuery.data.strip()

    if callback_data == "AutoPlay_reconfig":
        caption = (
            "<blockquote><emoji id=5895705279416241926>🎵</emoji> <u><b>AUTOPLAY CONFIGURATION</b></u></blockquote>\n\n"
            "<blockquote expandable>"
            "<emoji id=5974235702701853774>✨</emoji> Select your desired mood vibe below:</blockquote>"
        )
        blocks = rich_autoplay_mood_blocks(caption)
        return await edit_rich(CallbackQuery.message, blocks)

    try:
        chat_id = int(callback_data.split("|")[1])
    except Exception:
        chat_id = CallbackQuery.message.chat.id

    autoplay_status = await is_autoplay_on(chat_id)

    if autoplay_status:
        await set_autoplay(chat_id, False)
        caption = (
            "<blockquote><emoji id=5895705279416241926>❌</emoji> <u><b>AUTOPLAY DISABLED</b></u></blockquote>\n\n"
            "<blockquote expandable>"
            "Queue khatam hone par bot music band kar dega.</blockquote>"
        )
        blocks = html_to_rich_blocks(caption)
        blocks.append(
            types.InputRichBlockButtons(
                buttons=[
                    types.RichMessageButton(
                        text="▶️ Turn On Autoplay",
                        style=enums.ButtonStyle.SUCCESS,
                        callback_data=f"AutoPlay|{chat_id}",
                    )
                ]
            )
        )
        return await edit_rich(CallbackQuery.message, blocks)

    caption = (
        "<blockquote><emoji id=5895705279416241926>🎵</emoji> <u><b>ENABLE AUTOPLAY</b></u></blockquote>\n\n"
        "<blockquote expandable>"
        "<emoji id=5974235702701853774>✨</emoji> Select your preferred mood:</blockquote>"
    )
    blocks = rich_autoplay_mood_blocks(caption)
    await edit_rich(CallbackQuery.message, blocks)


async def get_autoplay_recommendation(chat_id: int):
    """Get autoplay song recommendation"""
    if chat_id not in previous_tracks:
        previous_tracks[chat_id] = []

    mood_data = await get_autoplay_mood(chat_id)

    mood = "chill"
    language = "hindi"

    if isinstance(mood_data, dict):
        mood = mood_data.get("mood", "chill")
        language = mood_data.get("language", "hindi")

    query = f"best {language} {mood} songs"

    try:
        track_data, track_id = await YouTube.track(query)
        if not track_data or not track_id:
            return None, None

        used_ids = [x["vidid"] for x in previous_tracks[chat_id]]
        if track_id in used_ids:
            return None, None

        if len(previous_tracks[chat_id]) >= 10:
            previous_tracks[chat_id].pop(0)

        previous_tracks[chat_id].append(
            {
                "title": track_data.get("title"),
                "vidid": track_id,
                "mood": mood,
                "language": language,
            }
        )
        return track_data, track_id

    except Exception as e:
        print(f"Autoplay Error: {e}")
        return None, None
