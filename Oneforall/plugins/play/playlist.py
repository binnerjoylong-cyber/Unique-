import asyncio
import os
import time
from random import randint
from time import time
from typing import Dict, List, Union

import requests
from pyrogram import enums, filters, types
from pyrogram.types import Message
from youtube_search import YoutubeSearch

from config import BANNED_USERS, SERVER_PLAYLIST_LIMIT
from Oneforall import Carbon, app
from Oneforall.core.mongo import mongodb
from Oneforall.misc import db
from Oneforall.utils.decorators.language import language, languageCB
from Oneforall.utils.inline.playlist import (
    botplaylist_markup,
    get_playlist_markup,
    warning_markup,
)
from Oneforall.utils.inline.rich import (
    deliver_rich,
    edit_rich,
    html_to_rich_blocks,
)
from Oneforall.utils.pastebin import HottyBin
from Oneforall.utils.stream.stream import stream

playlistdb = mongodb.playlist
user_last_message_time = {}
user_command_count = {}
SPAM_THRESHOLD = 2
SPAM_WINDOW_SECONDS = 5

ADDPLAYLIST_COMMAND = "addplaylist"
PLAYLIST_COMMAND = "playlist"
DELETEPLAYLIST_COMMAND = "delplaylist"
DELETE_ALL_PLAYLIST_COMMAND = "delallplaylist"


async def _get_playlists(chat_id: int) -> Dict[str, int]:
    _notes = await playlistdb.find_one({"chat_id": chat_id})
    if not _notes:
        return {}
    return _notes.get("notes", {})


async def get_playlist_names(chat_id: int) -> List[str]:
    notes = await _get_playlists(chat_id)
    return list(notes.keys())


async def get_playlist(chat_id: int, name: str) -> Union[bool, dict]:
    _notes = await _get_playlists(chat_id)
    return _notes.get(name, False)


async def save_playlist(chat_id: int, name: str, note: dict):
    _notes = await _get_playlists(chat_id)
    _notes[name] = note
    await playlistdb.update_one(
        {"chat_id": chat_id}, {"$set": {"notes": _notes}}, upsert=True
    )


async def delete_playlist(chat_id: int, name: str) -> bool:
    notesd = await _get_playlists(chat_id)
    if name in notesd:
        del notesd[name]
        await playlistdb.update_one(
            {"chat_id": chat_id},
            {"$set": {"notes": notesd}},
            upsert=True,
        )
        return True
    return False


async def get_rich_del_blocks(_, user_id):
    _playlist = await get_playlist_names(user_id)
    count = len(_playlist)
    blocks = []
    
    # 5 tracks per row maximum or 1 per row for long titles
    for x in _playlist[:15]:
        _note = await get_playlist(user_id, x)
        title = _note["title"].title() if _note else str(x)
        blocks.append(
            types.InputRichBlockButtons(
                buttons=[
                    types.RichMessageButton(
                        text=f"🗑️ {title[:28]}",
                        style=enums.ButtonStyle.PRIMARY,
                        callback_data=f"del_playlist {x}",
                    )
                ]
            )
        )
    
    blocks.append(
        types.InputRichBlockButtons(
            buttons=[
                types.RichMessageButton(
                    text="⚠️ Delete All",
                    style=enums.ButtonStyle.DANGER,
                    callback_data="delete_warning",
                ),
                types.RichMessageButton(
                    text="✖ Close",
                    style=enums.ButtonStyle.DEFAULT,
                    callback_data="close",
                ),
            ]
        )
    )
    return blocks, count


@app.on_message(filters.command(PLAYLIST_COMMAND) & ~BANNED_USERS)
@language
async def check_playlist(client, message: Message, _):
    user_id = message.from_user.id
    current_time = time()
    last_message_time = user_last_message_time.get(user_id, 0)

    if current_time - last_message_time < SPAM_WINDOW_SECONDS:
        user_last_message_time[user_id] = current_time
        user_command_count[user_id] = user_command_count.get(user_id, 0) + 1
        if user_command_count[user_id] > SPAM_THRESHOLD:
            hu = await message.reply_text(
                f"**{message.from_user.mention} ᴘʟᴇᴀsᴇ ᴅᴏɴᴛ ᴅᴏ sᴘᴀᴍ, ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 5 sᴇᴄ**"
            )
            await asyncio.sleep(3)
            await hu.delete()
            return
    else:
        user_command_count[user_id] = 1
        user_last_message_time[user_id] = current_time

    _playlist = await get_playlist_names(user_id)
    if not _playlist:
        return await message.reply_text(_["playlist_3"])

    caption = (
        "<blockquote><emoji id=5895705279416241926>📑</emoji> <u><b>YOUR SAVED PLAYLIST</b></u></blockquote>\n\n"
        "<blockquote expandable>"
        f"<emoji id=6066395745139824604>👤</emoji> <b>User :</b> {message.from_user.mention}\n"
        f"📊 <b>Total Saved :</b> <code>{len(_playlist)} tracks</code>\n\n"
        "<emoji id=5409132617750555920>⚡</emoji> Choose an option below to stream directly:</blockquote>"
    )
    blocks = html_to_rich_blocks(caption)
    blocks += get_playlist_markup(_)
    await deliver_rich(client, message.chat.id, blocks)


@app.on_message(filters.command(DELETEPLAYLIST_COMMAND) & ~BANNED_USERS)
@language
async def del_plist_msg(client, message: Message, _):
    user_id = message.from_user.id
    _playlist = await get_playlist_names(user_id)
    if not _playlist:
        return await message.reply_text(_["playlist_3"])

    del_buttons, count = await get_rich_del_blocks(_, user_id)
    caption = (
        "<blockquote><emoji id=5895705279416241926>🗑️</emoji> <u><b>MANAGE & REMOVE TRACKS</b></u></blockquote>\n\n"
        "<blockquote expandable>"
        f"Total <b>{count}</b> tracks in your playlist.\n"
        "Click on any track button to remove it individually.</blockquote>"
    )
    blocks = html_to_rich_blocks(caption)
    blocks += del_buttons
    await deliver_rich(client, message.chat.id, blocks)


@app.on_callback_query(filters.regex(r"^del_playlist\s+") & ~BANNED_USERS)
@languageCB
async def del_plist_cb(client, CallbackQuery, _):
    videoid = CallbackQuery.data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id
    deleted = await delete_playlist(user_id, videoid)
    if deleted:
        await CallbackQuery.answer(_["playlist_11"], show_alert=True)
    else:
        return await CallbackQuery.answer(_["playlist_12"], show_alert=True)

    del_buttons, count = await get_rich_del_blocks(_, user_id)
    if count == 0:
        caption = "<blockquote><emoji id=5895705279416241926>✨</emoji> <b>Your playlist is now empty.</b></blockquote>"
        blocks = html_to_rich_blocks(caption)
        return await edit_rich(CallbackQuery.message, blocks)

    caption = (
        "<blockquote><emoji id=5895705279416241926>🗑️</emoji> <u><b>MANAGE & REMOVE TRACKS</b></u></blockquote>\n\n"
        "<blockquote expandable>"
        f"Total <b>{count}</b> tracks in your playlist.\n"
        "Click on any track button to remove it individually.</blockquote>"
    )
    blocks = html_to_rich_blocks(caption)
    blocks += del_buttons
    await edit_rich(CallbackQuery.message, blocks)


@app.on_callback_query(filters.regex("play_playlist") & ~BANNED_USERS)
@languageCB
async def play_playlist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    mode = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id
    _playlist = await get_playlist_names(user_id)
    if not _playlist:
        try:
            return await CallbackQuery.answer(_["playlist_3"], show_alert=True)
        except Exception:
            return

    chat_id = CallbackQuery.message.chat.id
    user_name = CallbackQuery.from_user.first_name
    await CallbackQuery.message.delete()
    result = list(_playlist)

    try:
        await CallbackQuery.answer()
    except Exception:
        pass

    video = True if mode == "v" else None
    mystic = await CallbackQuery.message.reply_text(_["play_1"])
    try:
        await stream(
            _,
            mystic,
            user_id,
            result,
            chat_id,
            user_name,
            CallbackQuery.message.chat.id,
            video,
            streamtype="playlist",
        )
    except Exception as e:
        ex_type = type(e).__name__
        err = e if ex_type == "AssistantErr" else _["general_3"].format(ex_type)
        return await mystic.edit_text(err)
    return await mystic.delete()


@app.on_message(
    filters.command(["playplaylist", "vplayplaylist"]) & ~BANNED_USERS & filters.group
)
@languageCB
async def play_playlist_command(client, message, _):
    mode = message.command[0][0]
    user_id = message.from_user.id
    _playlist = await get_playlist_names(user_id)
    if not _playlist:
        try:
            return await message.reply(_["playlist_3"], quote=True)
        except Exception:
            return

    chat_id = message.chat.id
    user_name = message.from_user.first_name

    try:
        await message.delete()
    except Exception:
        pass

    result = list(_playlist)
    video = True if mode == "v" else None
    mystic = await message.reply_text(_["play_1"])

    try:
        await stream(
            _,
            mystic,
            user_id,
            result,
            chat_id,
            user_name,
            message.chat.id,
            video,
            streamtype="playlist",
        )
    except Exception as e:
        ex_type = type(e).__name__
        err = e if ex_type == "AssistantErr" else _["general_3"].format(ex_type)
        return await mystic.edit_text(err)

    return await mystic.delete()


@app.on_callback_query(filters.regex(r"^add_playlist\|") & ~BANNED_USERS)
@languageCB
async def add_current_playing_to_playlist(client, CallbackQuery, _):
    try:
        chat_id = int(CallbackQuery.data.split("|")[1])
    except Exception:
        chat_id = CallbackQuery.message.chat.id

    user_id = CallbackQuery.from_user.id
    tracks = db.get(chat_id)
    if not tracks:
        return await CallbackQuery.answer("❌ Currently no track is streaming.", show_alert=True)

    current_track = tracks[0]
    vidid = current_track.get("vidid")
    title = current_track.get("title", "Unknown Track")
    duration = current_track.get("dur", "00:00")

    if not vidid:
        return await CallbackQuery.answer("❌ Track ID not found.", show_alert=True)

    _check = await get_playlist(user_id, vidid)
    if _check:
        return await CallbackQuery.answer("⚠️ Already in your playlist!", show_alert=True)

    _count = await get_playlist_names(user_id)
    if len(_count) >= SERVER_PLAYLIST_LIMIT:
        return await CallbackQuery.answer(_["playlist_9"].format(SERVER_PLAYLIST_LIMIT), show_alert=True)

    plist = {
        "videoid": vidid,
        "title": title,
        "duration": duration,
    }
    await save_playlist(user_id, vidid, plist)
    await CallbackQuery.answer(f"✅ Added to playlist:\n{title[:30]}...", show_alert=True)


@app.on_message(filters.command(ADDPLAYLIST_COMMAND) & ~BANNED_USERS)
@language
async def add_playlist_cmd(client, message: Message, _):
    if len(message.command) < 2:
        return await message.reply_text(
            "**➻ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴍᴇ ᴀ sᴏɴɢ ɴᴀᴍᴇ ᴏʀ ʟɪɴᴋ ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ..**\n\n▷ `/addplaylist Blue Eyes`"
        )

    query = " ".join(message.command[1:])
    user_id = message.from_user.id
    _count = await get_playlist_names(user_id)
    if len(_count) >= SERVER_PLAYLIST_LIMIT:
        return await message.reply_text(_["playlist_9"].format(SERVER_PLAYLIST_LIMIT))

    m = await message.reply("**🔄 ᴀᴅᴅɪɴɢ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ... **")
    try:
        from Oneforall import YouTube

        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            return await m.edit_text("❌ No tracks found.")

        videoid = results[0]["id"]
        title, duration_min, _, _, _ = await YouTube.details(videoid, True)
        title = (title[:50]).title()
        plist = {
            "videoid": vidid,
            "title": title,
            "duration": duration_min,
        }
        await save_playlist(user_id, videoid, plist)
        await m.delete()

        caption = (
            "<blockquote><emoji id=5895705279416241926>✅</emoji> <u><b>ADDED TO PLAYLIST</b></u></blockquote>\n\n"
            "<blockquote expandable>"
            f"🎵 <b>Track :</b> {title}\n"
            f"⏱️ <b>Duration :</b> {duration_min}\n\n"
            "Use <code>/playlist</code> to view or <code>/play</code> in group!</blockquote>"
        )
        blocks = html_to_rich_blocks(caption)
        blocks += get_playlist_markup(_)
        await deliver_rich(client, message.chat.id, blocks)
    except Exception as e:
        await m.edit_text(f"Error: {e}")


@app.on_message(filters.command(DELETE_ALL_PLAYLIST_COMMAND) & ~BANNED_USERS)
@language
async def delete_all_playlists(client, message, _):
    user_id = message.from_user.id
    _playlist = await get_playlist_names(user_id)
    if _playlist:
        caption = "<blockquote>⚠️ <b>Are you sure you want to delete entire playlist?</b></blockquote>"
        blocks = html_to_rich_blocks(caption)
        blocks += warning_markup(_)
        await deliver_rich(client, message.chat.id, blocks)
    else:
        await message.reply_text(_["playlist_3"])


@app.on_callback_query(filters.regex("get_playlist_playmode") & ~BANNED_USERS)
@languageCB
async def get_playlist_playmode_(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except Exception:
        pass
    caption = "<blockquote><emoji id=5895705279416241926>🎵</emoji> <u><b>CHOOSE PLAY MODE</b></u></blockquote>"
    blocks = html_to_rich_blocks(caption)
    blocks += get_playlist_markup(_)
    return await edit_rich(CallbackQuery.message, blocks)


@app.on_callback_query(filters.regex("delete_warning") & ~BANNED_USERS)
@languageCB
async def delete_warning_message(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except Exception:
        pass
    caption = "<blockquote>⚠️ <b>Are you sure you want to delete entire playlist?</b></blockquote>"
    blocks = html_to_rich_blocks(caption)
    blocks += warning_markup(_)
    return await edit_rich(CallbackQuery.message, blocks)


@app.on_callback_query(filters.regex("home_play") & ~BANNED_USERS)
@languageCB
async def home_play_(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except Exception:
        pass
    caption = "<blockquote><emoji id=5895705279416241926>📑</emoji> <u><b>PLAYLIST MENU</b></u></blockquote>"
    blocks = html_to_rich_blocks(caption)
    blocks += botplaylist_markup(_)
    return await edit_rich(CallbackQuery.message, blocks)


@app.on_callback_query(filters.regex("delete_whole_playlist") & ~BANNED_USERS)
@languageCB
async def del_whole_playlist(client, CallbackQuery, _):
    _playlist = await get_playlist_names(CallbackQuery.from_user.id)
    for x in _playlist:
        await delete_playlist(CallbackQuery.from_user.id, x)
    await CallbackQuery.answer("✅ Playlist cleared!", show_alert=True)
    return await CallbackQuery.message.delete()
